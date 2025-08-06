"""Sphinx plugins for web API docs."""

import ast
import inspect
import json
import logging
import os
import re
import sys
from importlib import import_module

# Initialize Review Board before we load anything from Django.
import reviewboard
reviewboard.initialize(load_extensions=False,
                       setup_logging=False,
                       setup_templates=False)

from beanbag_docutils.sphinx.ext.http_role import (
    DEFAULT_HTTP_STATUS_CODES_URL, HTTP_STATUS_CODES)
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, QueryDict
from django.template.defaultfilters import title
from djblets.features import get_features_registry
from djblets.features.testing import override_feature_checks
from djblets.util.http import is_mimetype_a
from djblets.webapi.fields import (BaseAPIFieldType,
                                   ChoiceFieldType,
                                   DateTimeFieldType,
                                   ResourceFieldType,
                                   ResourceListFieldType)
from djblets.webapi.resources import get_resource_from_class, WebAPIResource
from djblets.webapi.responses import WebAPIResponseError
from docutils import nodes
from docutils.parsers.rst import Directive, DirectiveError, directives
from docutils.statemachine import StringList, ViewList, string2lines
from reviewboard.scmtools.models import Repository
from reviewboard.webapi.resources import resources
from sphinx import addnodes
from sphinx.util import docname_join
from sphinx.util.docstrings import prepare_docstring


# Mapping of mimetypes to language names for syntax highlighting.
MIMETYPE_LANGUAGES = [
    ('application/json', 'javascript'),
    ('application/xml', 'xml'),
    ('text/x-patch', 'diff'),
]


EXAMPLE_SERVER_URL = 'https://reviews.example.com/'


# Build the list of parents.
resources.root.get_url_patterns()


features_registry = get_features_registry()


class ResourceNotFound(Exception):
    def __init__(self, directive, classname):
        self.classname = classname
        self.error_node = [
            directive.state_machine.reporter.error(
                str(self),
                line=directive.lineno)
        ]

    def __str__(self):
        return ('Unable to import the web API resource class "%s"'
                % self.classname)


class ErrorNotFound(Exception):
    def __init__(self, directive, classname):
        self.error_node = [
            directive.state_machine.reporter.error(
                'Unable to import the web API error class "%s"' % classname,
                line=directive.lineno)
        ]


class DummyRequest(HttpRequest):
    """A dummy HTTP request used for introspecting the API."""

    def __init__(self, user=None, *args, **kwargs):
        """Initialize the request.

        Args:
            user (django.contrib.auth.models.User, optional):
                An optional user to use for the request.

            *args (tuple):
                Positional arguments to pass to the parent class.

            **kwargs (dict):
                Keyword argumetns to pass to the parent class.
        """
        super(DummyRequest, self).__init__(*args, **kwargs)
        self.method = 'GET'
        self.path = ''
        self.user = user or User.objects.all()[0]
        self.session = {}
        self._local_site_name = None
        self.local_site = None

        # This is normally set internally by Djblets, but we don't
        # go through the standard __call__ flow.
        self._djblets_webapi_object_cache = {}

    def build_absolute_uri(self, location=None):
        if not self.path and not location:
            return '/api/'

        if not location:
            location = self.path

        if not location.startswith('http://'):
            location = '%s%s' % (EXAMPLE_SERVER_URL, location.lstrip('/'))

        return location


class ResourceDirective(Directive):
    has_content = True
    required_arguments = 0
    option_spec = {
        'classname': directives.unchanged_required,
        'is-list': directives.flag,
        'hide-links': directives.flag,
        'hide-examples': directives.flag,
        'example-url-keys': directives.unchanged,
        'request-username': directives.unchanged,
        'url-query': directives.unchanged,
    }

    item_http_methods = set(['GET', 'DELETE', 'PUT'])
    list_http_methods = set(['GET', 'POST'])

    FILTERED_MIMETYPES = [
        'application/json',
        'application/xml',
    ]

    def run(self):
        try:
            resource_class = self.get_resource_class(self.options['classname'])
        except ResourceNotFound as e:
            return e.error_node

        # Add the class's file and this extension to the dependencies.
        env = self.state.document.settings.env
        env.note_dependency(__file__)
        env.note_dependency(sys.modules[resource_class.__module__].__file__)

        resource = get_resource_from_class(resource_class)

        is_list = 'is-list' in self.options

        # Load any keys used for example URLs.
        url_keys = self.options.get('example-url-keys')

        if url_keys:
            self.url_keys = json.loads(url_keys)
        else:
            self.url_keys = None

        # Fetch any requesting user.
        request_username = self.options.get('request-username')

        if request_username:
            self.request_user = User.objects.get(username=request_username)
        else:
            self.request_user = None

        # Begin creating the main documentation.
        docname = 'webapi2.0-%s-resource' % \
            get_resource_docname(env.app, resource, is_list)
        resource_title = get_resource_title(resource, is_list)

        targetnode = nodes.target('', '', ids=[docname], names=[docname])
        self.state.document.note_explicit_target(targetnode)
        main_section = nodes.section(ids=[docname])

        # Main section
        main_section += nodes.title(text=resource_title)

        for attr_name, text_fmt in (('added_in', 'Added in %s'),
                                    ('deprecated_in', 'Deprecated in %s'),
                                    ('removed_in', 'Removed in %s')):
            version = getattr(resource, attr_name, None)

            if not version:
                if is_list:
                    prefix = 'list_resource'
                else:
                    prefix = 'item_resource'

                version = getattr(resource, '%s_%s' % (prefix, attr_name),
                                  None)

            if version:
                paragraph = nodes.paragraph()
                paragraph += nodes.emphasis(text=text_fmt % version,
                                            classes=['resource-versioning'])

                main_section += paragraph

        main_section += parse_text(
            self, inspect.getdoc(resource),
            where='%s class docstring' % self.options['classname'])

        # Determine which required features must be opted into in this release.
        non_default_required_features = [
            feature
            for feature in getattr(resource, 'required_features', [])
            if not feature.is_enabled()
        ]

        if non_default_required_features:
            required_features = nodes.important()
            required_features += nodes.inline(
                text='Using this resource requires extra features to be '
                     'enabled on the server. See "Required Features" below.')
            main_section += non_default_required_features

        # Details section
        details_section = nodes.section(ids=['details'])
        main_section += details_section

        details_section += nodes.title(text='Details')
        details_section += self.build_details_table(resource)

        # Fields section
        if (resource.fields and
            (not is_list or resource.singleton)):
            fields_section = nodes.section(ids=['fields'])
            main_section += fields_section

            fields_section += nodes.title(text='Fields')
            fields_section += self.build_fields_table(resource.fields)

        # Links section
        if 'hide-links' not in self.options:
            fields_section = nodes.section(ids=['links'])
            main_section += fields_section

            fields_section += nodes.title(text='Links')
            fields_section += self.build_links_table(resource)

        # HTTP method descriptions
        for http_method in self.get_http_methods(resource, is_list):
            method_section = nodes.section(ids=[http_method])
            main_section += method_section

            method_section += nodes.title(text='HTTP %s' % http_method)
            method_section += self.build_http_method_section(resource,
                                                             http_method)

        if 'hide-examples' not in self.options:
            examples_section = nodes.section(ids=['examples'])
            examples_section += nodes.title(text='Examples')

            has_examples = False

            if is_list:
                mimetype_key = 'list'
            else:
                mimetype_key = 'item'

            for mimetype in resource.allowed_mimetypes:
                try:
                    mimetype = mimetype[mimetype_key]
                except KeyError:
                    continue

                if mimetype in self.FILTERED_MIMETYPES:
                    # Resources have more specific mimetypes. We want to
                    # filter out the general ones (like application/json)
                    # so we don't show redundant examples.
                    continue

                if mimetype.endswith('xml'):
                    # JSON is preferred. While we support XML, let's not
                    # continue to advertise it.
                    continue

                url, headers, data = \
                    self.fetch_resource_data(resource, mimetype)

                if headers or data:
                    example_node = build_example_payload_node(
                        data=data,
                        mimetype=mimetype)

                    example_section = \
                        nodes.section(ids=['example_' + mimetype],
                                      classes=['examples', 'requests-example'])
                    examples_section += example_section

                    example_section += nodes.title(text=mimetype)

                    accept_mimetype = mimetype

                    if (mimetype.startswith('application/') and
                        mimetype.endswith('+json')):
                        # Instead of telling the user to ask for a specific
                        # mimetype on the request, show them that asking for
                        # application/json works fine.
                        accept_mimetype = 'application/json'

                    if not url.startswith(EXAMPLE_SERVER_URL):
                        url = '%s%s' % (EXAMPLE_SERVER_URL, url.lstrip('/'))

                    curl_text = (
                        '$ curl %s -H "Accept: %s"'
                        % (url, accept_mimetype)
                    )
                    example_section += nodes.literal_block(
                        curl_text, curl_text, classes=['cmdline'])

                    example_section += nodes.literal_block(
                        headers, headers, classes=['http-headers'])

                    if example_node:
                        example_section += example_node

                    has_examples = True

            if has_examples:
                main_section += examples_section

        return [targetnode, main_section]

    def build_details_table(self, resource):
        env = self.state.document.settings.env
        app = env.app

        is_list = 'is-list' in self.options

        table = nodes.table(classes=['resource-info'])

        tgroup = nodes.tgroup(cols=2)
        table += tgroup

        tgroup += nodes.colspec(colwidth=30, classes=['field'])
        tgroup += nodes.colspec(colwidth=70, classes=['value'])

        tbody = nodes.tbody()
        tgroup += tbody

        # Name
        if is_list:
            resource_name = resource.name_plural
        else:
            resource_name = resource.name

        append_detail_row(tbody, "Name", nodes.literal(text=resource_name))

        # URI
        uri_template = get_resource_uri_template(resource, not is_list)
        append_detail_row(tbody, "URI", nodes.literal(text=uri_template))

        # Required features
        if getattr(resource, 'required_features', False):
            feature_list = nodes.bullet_list()

            for feature in resource.required_features:
                item = nodes.list_item()
                paragraph = nodes.paragraph()

                paragraph += nodes.inline(text=feature.feature_id)
                item += paragraph
                feature_list += item

            append_detail_row(tbody, 'Required Features', feature_list)

        # Token Policy ID
        if hasattr(resource, 'policy_id'):
            append_detail_row(tbody, "Token Policy ID",
                              nodes.literal(text=resource.policy_id))

        # HTTP Methods
        allowed_http_methods = self.get_http_methods(resource, is_list)
        bullet_list = nodes.bullet_list()

        for http_method in allowed_http_methods:
            item = nodes.list_item()
            bullet_list += item

            paragraph = nodes.paragraph()
            item += paragraph

            ref = nodes.reference(text=http_method, refid=http_method)
            paragraph += ref

            doc_summary = self.get_doc_for_http_method(resource, http_method)
            i = doc_summary.find('.')

            if i != -1:
                doc_summary = doc_summary[:i + 1]

            paragraph += nodes.inline(text=" - ")
            paragraph += parse_text(
                self, doc_summary,
                wrapper_node_type=nodes.inline,
                where='HTTP %s handler summary for %s'
                      % (http_method, self.options['classname']))

        append_detail_row(tbody, "HTTP Methods", bullet_list)

        # Parent Resource
        if is_list or resource.uri_object_key is None:
            parent_resource = resource._parent_resource
            is_parent_list = False
        else:
            parent_resource = resource
            is_parent_list = True

        if parent_resource:
            paragraph = nodes.paragraph()
            paragraph += get_ref_to_resource(app, parent_resource,
                                             is_parent_list)
        else:
            paragraph = 'None.'

        append_detail_row(tbody, "Parent Resource", paragraph)

        # Child Resources
        if is_list:
            child_resources = list(resource.list_child_resources)

            if resource.name != resource.name_plural:
                if resource.uri_object_key:
                    child_resources.append(resource)

                are_children_lists = False
            else:
                are_children_lists = True
        else:
            child_resources = resource.item_child_resources
            are_children_lists = True

        if child_resources:
            tocnode = addnodes.toctree()
            tocnode['glob'] = None
            tocnode['maxdepth'] = 1
            tocnode['hidden'] = False

            docnames = sorted([
                docname_join(env.docname,
                             get_resource_docname(app, child_resource,
                                                  are_children_lists))
                for child_resource in child_resources
            ])

            tocnode['includefiles'] = docnames
            tocnode['entries'] = [(None, docname) for docname in docnames]
        else:
            tocnode = nodes.paragraph(text="None")

        append_detail_row(tbody, "Child Resources", tocnode)

        return table

    def build_fields_table(self, fields, required_field_names=None):
        """Build a table representing a list of fields.

        Args:
            fields (dict):
                The fields to display.

            required_field_names (set of unicode, optional):
                The field names that are required.

        Returns:
            list of docutils.nodes.Node:
            The resulting list of nodes for the fields table.
        """
        options = {
            'fields': fields,
        }

        if required_field_names is not None:
            options.update({
                'show-requirement-labels': True,
                'required-field-names': set(required_field_names),
            })

        return run_directive(self, 'webapi-resource-field-list',
                             options=options)

    def build_links_table(self, resource):
        is_list = 'is-list' in self.options

        table = nodes.table()

        tgroup = nodes.tgroup(cols=3)
        table += tgroup

        tgroup += nodes.colspec(colwidth=25)
        tgroup += nodes.colspec(colwidth=15)
        tgroup += nodes.colspec(colwidth=60)

        thead = nodes.thead()
        tgroup += thead
        append_row(thead, ['Name', 'Method', 'Resource'])

        tbody = nodes.tbody()
        tgroup += tbody

        # First, try to figure out what the API path to this resource should
        # be.
        request = DummyRequest(user=self.request_user)

        if is_list:
            child_resources = resource.list_child_resources
        else:
            child_resources = resource.item_child_resources

        names_to_resource = {}

        for child in child_resources:
            names_to_resource[child.name_plural] = (child, True)

        child_keys = {}
        request.path = create_fake_resource_path(
            request=request,
            resource=resource,
            child_keys=child_keys,
            include_child=bool(not is_list and resource.model),
            url_keys=self.url_keys)

        if not is_list and resource.model:
            obj = resource.get_queryset(request, **child_keys)[0]
        else:
            obj = None

        # Now build the list of related links. This will be used below when
        # we build the final list of links.
        related_links = resource.get_related_links(request=request, obj=obj)

        for key, info in related_links.items():
            if 'resource' in info:
                names_to_resource[key] = \
                    (info['resource'], info.get('list-resource', False))

        # Now fetch the links from the resource, based on the path.
        links = resource.get_links(child_resources,
                                   request=request,
                                   obj=obj,
                                   **child_keys)

        # Finally, assemble this into generated ReST nodes.
        app = self.state.document.settings.env.app

        for linkname in sorted(links.keys()):
            info = links[linkname]
            child, is_child_link = \
                names_to_resource.get(linkname, (resource, is_list))

            paragraph = nodes.paragraph()
            paragraph += get_ref_to_resource(app, child, is_child_link)

            append_row(tbody,
                       [nodes.strong(text=linkname),
                        info['method'],
                        paragraph])

        return table

    def build_http_method_section(self, resource, http_method):
        doc = self.get_doc_for_http_method(resource, http_method)
        http_method_func = self.get_http_method_func(resource, http_method)

        # Description text
        returned_nodes = [
            parse_text(self, doc,
                       wrapper_node_type=nodes.paragraph,
                       where='HTTP %s doc' % http_method),
        ]

        # Request Parameters section
        required_fields = getattr(http_method_func, 'required_fields', [])
        optional_fields = getattr(http_method_func, 'optional_fields', [])

        if required_fields or optional_fields:
            all_fields = dict(required_fields)
            all_fields.update(optional_fields)

            fields_section = nodes.section(ids=['%s_params' % http_method])
            returned_nodes.append(fields_section)

            fields_section += nodes.title(text='Request Parameters')

            table = self.build_fields_table(
                all_fields,
                required_field_names=set(required_fields.keys()))
            fields_section += table

        # Errors section
        errors = getattr(http_method_func, 'response_errors', [])

        if errors:
            errors_section = nodes.section(ids=['%s_errors' % http_method])
            returned_nodes.append(errors_section)

            errors_section += nodes.title(text='Errors')
            errors_section += self.build_errors_table(errors)

        return returned_nodes

    def build_errors_table(self, errors):
        """Build a table representing a list of errors.

        Args:
            errors (list of djblets.webapi.errors.WebAPIError):
                The errors to display.

        Returns:
            list of docutils.nodes.Node:
            The resulting list of nodes for the errors table.
        """
        table = nodes.table(classes=['api-errors'])

        tgroup = nodes.tgroup(cols=2)
        table += tgroup

        tgroup += nodes.colspec(colwidth=25)
        tgroup += nodes.colspec(colwidth=75)

        tbody = nodes.tbody()
        tgroup += tbody

        for error in sorted(errors, key=lambda x: x.code):
            http_code = nodes.inline(classes=['http-error'])
            http_code += nodes.reference(
                text='HTTP %s - %s' % (error.http_status,
                                       HTTP_STATUS_CODES[error.http_status]),
                refuri=(DEFAULT_HTTP_STATUS_CODES_URL
                        % error.http_status)),

            error_code = nodes.inline(classes=['api-error'])
            error_code += get_ref_to_error(error)

            error_info = nodes.inline()
            error_info += error_code
            error_info += http_code

            append_row(
                tbody,
                [
                    error_info,
                    nodes.inline(text=error.msg),
                ])

        return table

    def fetch_resource_data(self, resource, mimetype):
        features = {
            feature.feature_id: True
            for feature in resource.required_features
        }

        with override_feature_checks(features):
            kwargs = {}
            request = DummyRequest(user=self.request_user)
            request.path = create_fake_resource_path(
                request=request,
                resource=resource,
                child_keys=kwargs,
                include_child='is-list' not in self.options,
                url_keys=self.url_keys)

            query = self.options.get('url-query')

            if query:
                request.path = '%s?%s' % (request.path, query)
                request.GET = QueryDict(query_string=query,
                                        mutable=True)

            headers, data = fetch_response_data(
                response_class=resource,
                mimetype=mimetype,
                request=request,
                **kwargs)

            return request.path, headers, data

    def get_resource_class(self, classname):
        try:
            return get_from_module(classname)
        except ImportError:
            raise ResourceNotFound(self, classname)

    def get_http_method_func(self, resource, http_method):
        if (http_method == 'GET' and 'is-list' in self.options and
            not resource.singleton):
            method_name = 'get_list'
        else:
            method_name = resource.method_mapping[http_method]

            # Change "put" and "post" to "update" and "create", respectively.
            # "put" and "post" are just wrappers and we don't want to show
            # their documentation.
            if method_name == 'put':
                method_name = 'update'
            elif method_name == 'post':
                method_name = 'create'

        return getattr(resource, method_name)

    def get_doc_for_http_method(self, resource, http_method):
        return inspect.getdoc(self.get_http_method_func(resource,
                                                        http_method)) or ''

    def get_http_methods(self, resource, is_list):
        if is_list:
            possible_http_methods = self.list_http_methods
        else:
            possible_http_methods = self.item_http_methods

        return sorted(
            set(resource.allowed_methods).intersection(possible_http_methods))


class ResourceFieldListDirective(Directive):
    """Directive for listing fields in a resource.

    This directive can be used to list the fields belonging to a resource,
    the fields within part of a resource's payload, or fields accepted by
    an operation on a resource.

    The fields can be provided directly (if being called by Python code)
    through the ``fields`` and ``required-field-names`` options. Otherwise,
    this will parse the content of the directive for any
    ``webapi-resource-field`` directives and use those instead.
    """

    has_content = True
    option_spec = {
        'fields': directives.unchanged,
        'required-field-names': directives.unchanged,
    }

    def run(self):
        """Run the directive and render the resulting fields.

        Returns:
            list of docutils.nodes.Node:
            The resulting nodes.
        """
        fields = self.options.get('fields')
        required_fields = self.options.get('required-field-names')

        table = nodes.table(classes=['resource-fields'])

        tgroup = nodes.tgroup(cols=3)
        table += tgroup

        tgroup += nodes.colspec(colwidth=15, classes=['field'])
        tgroup += nodes.colspec(colwidth=85, classes=['description'])

        tbody = nodes.tbody()
        tgroup += tbody

        if fields is not None:
            assert isinstance(fields, dict)

            if required_fields is not None:
                field_keys = sorted(
                    fields.keys(),
                    key=lambda field: (field not in required_fields, field))
            else:
                field_keys = sorted(fields.keys())

            for field in field_keys:
                info = fields[field]

                options = {
                    'name': field,
                    'type': info['type'],
                    'field-info': info,
                }

                if info.get('supports_text_types'):
                    options['supports-text-types'] = True

                if required_fields is not None and field in required_fields:
                    options['show-required'] = True

                if info.get('added_in'):
                    options['added-in'] = info['added_in']

                if info.get('deprecated_in'):
                    options['deprecated-in'] = info['deprecated_in']

                if info.get('removed_in'):
                    options['removed-in'] = info['removed_in']

                field_row = run_directive(
                    self,
                    'webapi-resource-field',
                    content='\n'.join(prepare_docstring(info['description'])),
                    options=options)

                tbody += field_row
        elif self.content:
            node = nodes.Element()
            self.state.nested_parse(self.content, self.content_offset,
                                    node)

            # ResourceFieldDirective outputs two fields (two table cells) per
            # field. We want to loop through and grab each.
            tbody += node.children

        return [table]


class ResourceFieldDirective(Directive):
    """Directive for displaying information on a field in a resource.

    This directive can be used to display details about a specific field
    belonging to a resource, a part of a resource's payload, or a field
    accepted by an operation on a resource.

    This is expected to be added into a ``webapi-resource-field-list``
    directive. The resulting node is a table row.
    """

    has_content = True
    option_spec = {
        'name': directives.unchanged_required,
        'type': directives.unchanged_required,
        'field-info': directives.unchanged,
        'show-required': directives.flag,
        'supports-text-types': directives.flag,
        'added-in': directives.unchanged,
        'deprecated-in': directives.unchanged,
        'removed-in': directives.unchanged,
    }

    type_mapping = {
        int: 'Integer',
        bytes: 'Byte String',
        str: 'String',
        bool: 'Boolean',
        dict: 'Dictionary',
        list: 'List',
    }

    type_name_mapping = {
        'int': int,
        'bytes': bytes,
        'str': str,
        'unicode': str,
        'bool': bool,
        'dict': dict,
        'list': list,
    }

    def run(self):
        """Run the directive and render the resulting fields.

        Returns:
            list of docutils.nodes.Node:
            The resulting nodes.
        """
        self.assert_has_content()

        name = self.options['name']

        # Field/type information
        field_node = nodes.inline()
        field_node += nodes.strong(text=name, classes=['field-name'])

        type_node = nodes.inline(classes=['field-type'])
        field_node += type_node

        if 'supports-text-types' in self.options:
            type_node += get_ref_to_doc('webapi2.0-text-fields', 'Rich Text')
        else:
            type_node += self._get_type_name(
                self.options['type'],
                self.options.get('field-info', {}))

        # Description/required/versioning information
        description_node = nodes.inline()

        if 'show-required' in self.options:
            description_node += nodes.inline(text='Required',
                                             classes=['field-required'])

        if 'deprecated-in' in self.options:
            description_node += nodes.inline(text='Deprecated',
                                             classes=['field-deprecated'])

        if isinstance(self.content, StringList):
            description = '\n'.join(self.content)
        else:
            description = self.content

        description_node += parse_text(self, description)

        if 'added-in' in self.options:
            paragraph = nodes.paragraph()
            paragraph += nodes.emphasis(
                text='Added in %s\n' % self.options['added-in'],
                classes=['field-versioning'])
            description_node += paragraph

        if 'deprecated-in' in self.options:
            paragraph = nodes.paragraph()
            paragraph += nodes.emphasis(
                text='Deprecated in %s\n' % self.options['deprecated-in'],
                classes=['field-versioning'])
            description_node += paragraph

        if 'removed-in' in self.options:
            paragraph = nodes.paragraph()
            paragraph += nodes.emphasis(
                text='Removed in %s\n' % self.options['removed-in'],
                classes=['field-versioning'])
            description_node += paragraph

        row = nodes.row()

        entry = nodes.entry()
        entry += field_node
        row += entry

        entry = nodes.entry()
        entry += description_node
        row += entry

        return [row]

    def _get_type_name(self, field_type, field_info, nested=False):
        """Return the displayed name for a given type.

        This will attempt to take a type (either a string representation or
        a Python structure) and return a string that can be used for display
        in the API docs.

        This may also be provided a Python class path for a resource.

        Args:
            field_type (object):
                The type of field (as a Python structure), a string
                representing a Python structure, or the class path to a
                resource.

            field_info (dict):
                The metadata on the field.

            nested (bool, optional):
                Whether this call is nested within another call to this
                function.

        Returns:
            unicode:
            The resulting string used for display.

        Raises:
            ResourceNotFound:
                A resource path appeared to be provided, but a resource was
                not found.

            ValueError:
                The type is unsupported.
        """
        if (inspect.isclass(field_type) and
            issubclass(field_type, BaseAPIFieldType)):
            field_type = field_type(field_info)

            if isinstance(field_type, ResourceFieldType):
                result = []

                if isinstance(field_type, ResourceListFieldType):
                    result.append(nodes.inline(text='List of '))

                result.append(get_ref_to_resource(
                    self.state.document.settings.env.app,
                    field_type.resource,
                    False))

                return result
            elif isinstance(field_type, ChoiceFieldType):
                value_nodes = []

                for value in field_type.choices:
                    if value_nodes:
                        value_nodes.append(nodes.inline(text=', '))

                    value_nodes.append(nodes.literal(text=value))

                return [nodes.inline(text='One of ')] + value_nodes
            elif isinstance(field_type, DateTimeFieldType):
                return parse_text(self,
                                  ':term:`%s <ISO8601 format>`' % field_type)
            else:
                return [
                    nodes.inline(text=str(field_type)),
                ]

        if (isinstance(field_type, str) and
            field_type is not str):
            # First see if this is a string name for a type. This would be
            # coming from a docstring.
            try:
                field_type = self.type_name_mapping[field_type]
            except KeyError:
                if '.' in field_type:
                    # We may be dealing with a forward-declared class.
                    try:
                        field_type = get_from_module(field_type)
                    except ImportError:
                        raise ResourceNotFound(self, field_type)
                else:
                    # Maybe we can parse this?
                    field_type = self._parse_type_string(field_type)

        if type(field_type) is list:
            result = []

            if not nested:
                result.append(nodes.inline(text='List of '))

            if len(field_type) > 1:
                result.append(nodes.inline(text='['))

            first = True

            for item in field_type:
                if not first:
                    result.append(nodes.inline(text=', '))

                result += self._get_type_name(item, field_info, nested=True)

                first = False

            if len(field_type) > 1:
                result.append(nodes.inline(text=']'))

            return result
        elif type(field_type) is tuple:
            value_nodes = []

            for value in field_type:
                if value_nodes:
                    value_nodes.append(nodes.inline(text=', '))

                value_nodes.append(nodes.literal(text=value))

            return [nodes.inline(text='One of ')] + value_nodes
        elif field_type in self.type_mapping:
            return [nodes.inline(text=self.type_mapping[field_type])]
        else:
            raise ValueError('Unsupported type %r' % (field_type,))

    def _parse_type_string(self, type_str):
        """Parse a string representing a given type.

        The string can represent a simple Python primitive (``list``, ``dict``,
        etc.) or a nested structure (``list[dict]``, ``list[[int, unicode]]``,
        etc.).

        Args:
            type_str (unicode):
                The string to parse.

        Returns:
            object
            The resulting Python structure for the given type string.

        Raises:
            ValueError:
                The type is unsupported.
        """
        def _parse_node(node):
            if isinstance(node, ast.Str):
                return node.s
            elif isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.Tuple):
                return tuple(_parse_node(item) for item in node.elts)
            elif isinstance(node, ast.List):
                return list(_parse_node(item) for item in node.elts)
            elif isinstance(node, ast.Dict):
                return dict(
                    (_parse_node(key), _parse_node(value))
                    for key, value in node.elts.items()
                )
            elif isinstance(node, ast.Name):
                try:
                    return self.type_name_mapping[node.id]
                except KeyError:
                    raise ValueError(
                        'Unsupported node name "%s" for type string %r'
                        % (node.id, type_str))
            elif isinstance(node, ast.Subscript):
                if isinstance(node.slice, ast.Index):
                    slice_value = node.slice.value
                else:
                    slice_value = node.slice

                return _parse_node(node.value)([_parse_node(slice_value)])

            raise ValueError('Unsupported node type %r for type string %r'
                             % (node, type_str))

        return _parse_node(ast.parse(type_str, mode='eval').body)


class ResourceTreeDirective(Directive):
    has_content = True

    def run(self):
        bullet_list = nodes.bullet_list()
        self._output_resource(resources.root, bullet_list, True)

        return [bullet_list]

    def _output_resource(self, resource, parent, is_list):
        item = nodes.list_item()
        parent += item

        paragraph = nodes.paragraph()
        item += paragraph

        paragraph += parse_text(
            self,
            ':ref:`%s <%s>`' %
            (get_resource_title(resource, is_list, False),
             'webapi2.0-%s-resource'
             % get_resource_docname(self.state.document.settings.env.app,
                                    resource, is_list)))

        bullet_list = nodes.bullet_list()
        item += bullet_list

        if is_list:
            if resource.uri_object_key:
                self._output_resource(resource, bullet_list, False)

            for child in resource.list_child_resources:
                self._output_resource(child, bullet_list, True)
        else:
            for child in resource.item_child_resources:
                self._output_resource(child, bullet_list, True)


class ErrorDirective(Directive):
    has_content = True
    final_argument_whitespace = True
    option_spec = {
        'instance': directives.unchanged_required,
        'example-data': directives.unchanged,
        'title': directives.unchanged,
    }

    MIMETYPES = [
        'application/json',
    ]

    def run(self):
        try:
            error_obj = self.get_error_object(self.options['instance'])
        except ErrorNotFound as e:
            return e.error_node

        # Add the class's file and this extension to the dependencies.
        self.state.document.settings.env.note_dependency(__file__)
        self.state.document.settings.env.note_dependency(
            sys.modules[error_obj.__module__].__file__)

        docname = 'webapi2.0-error-%s' % error_obj.code
        error_title = self.get_error_title(error_obj)

        targetnode = nodes.target('', '', ids=[docname], names=[docname])
        self.state.document.note_explicit_target(targetnode)
        main_section = nodes.section(ids=[docname])

        # Details section
        main_section += nodes.title(text=error_title)
        main_section += self.build_details_table(error_obj)

        # Example section
        examples_section = nodes.section(ids=['examples'])
        examples_section += nodes.title(text='Examples')
        extra_params = {}

        if 'example-data' in self.options:
            extra_params = json.loads(self.options['example-data'])

        has_examples = False

        for mimetype in self.MIMETYPES:
            headers, data = fetch_response_data(
                WebAPIResponseError, mimetype,
                err=error_obj,
                request=DummyRequest(),
                extra_params=extra_params)

            if headers or data:
                example_node = build_example_payload_node(
                    data=data,
                    mimetype=mimetype)

                if example_node:
                    example_section = nodes.section(
                        ids=['example_' + mimetype])
                    examples_section += example_section

                    example_section += nodes.title(text=mimetype)
                    example_section += example_node
                    has_examples = True

        if has_examples:
            main_section += examples_section

        return [targetnode, main_section]

    def build_details_table(self, error_obj):
        table = nodes.table()

        tgroup = nodes.tgroup(cols=2)
        table += tgroup

        tgroup += nodes.colspec(colwidth=20)
        tgroup += nodes.colspec(colwidth=80)

        tbody = nodes.tbody()
        tgroup += tbody

        # API Error Code
        append_detail_row(tbody, 'API Error Code',
                          nodes.literal(text=error_obj.code))

        # HTTP Status Code
        ref = parse_text(self, ':http:`%s`' % error_obj.http_status)
        append_detail_row(tbody, 'HTTP Status Code', ref)

        # Error Text
        append_detail_row(tbody, 'Error Text',
                          nodes.literal(text=error_obj.msg))

        if error_obj.headers:
            if callable(error_obj.headers):
                headers = error_obj.headers(DummyRequest())

            # HTTP Headers
            header_keys = list(headers.keys())

            if len(header_keys) == 1:
                content = nodes.literal(text=header_keys[0])
            else:
                content = nodes.bullet_list()

                for header in header_keys:
                    item = nodes.list_item()
                    content += item

                    literal = nodes.literal(text=header)
                    item += literal

            append_detail_row(tbody, 'HTTP Headers', content)

        # Description
        append_detail_row(
            tbody, 'Description',
            parse_text(self, '\n'.join(self.content),
                       where='API error %s description' % error_obj.code))

        return table

    def get_error_title(self, error_obj):
        if 'title' in self.options:
            error_title = self.options['title']
        else:
            name = self.options['instance'].split('.')[-1]
            error_title = name.replace('_', ' ').title()

        return '%s - %s' % (error_obj.code, error_title)

    def get_error_object(self, name):
        try:
            return get_from_module(name)
        except ImportError:
            raise ErrorNotFound(self, name)


def parse_text(directive, text, wrapper_node_type=None, where=None):
    """Parse text in ReST format and return a node with the content.

    Args:
        directive (docutils.parsers.rst.Directive):
            The directive that will contain the resulting nodes.

        text (unicode):
            The text to parse.

        wrapper_node_type (docutils.nodes.Node, optional):
            An optional node type used to contain the children.

        where (unicode, optional):
            Information on the location being parsed in case there's a
            failure.

    Returns:
        list of docutils.nodes.Node:
        The resulting list of parsed nodes.
    """
    assert text is not None, 'Missing text during parse_text in %s' % where

    if wrapper_node_type:
        node_type = wrapper_node_type
    else:
        node_type = nodes.container

    node = node_type(rawsource=text)
    directive.state.nested_parse(ViewList(string2lines(text), source=''),
                                 0, node)

    if not wrapper_node_type:
        return node.children
    elif issubclass(wrapper_node_type, nodes.inline):
        result_node = wrapper_node_type()

        for child in node.children:
            if isinstance(child, nodes.paragraph):
                result_node += child.children
            else:
                result_node += child

        return result_node
    else:
        return node


def run_directive(parent_directive, name, content='', options={}):
    """Run and render a directive.

    Args:
        parent_directive (docutils.parsers.rst.Directive):
            The directive running another directive.

        name (unicode):
            The name of the directive to run.

        content (unicode, optional):
            The content to pass to the directive.

        options (dict, optional):
            The options to pass to the directive.

    Returns:
        list of docutils.nodes.Node:
        The resulting list of nodes from the directive.
    """
    state = parent_directive.state
    directive_class, messages = directives.directive(name,
                                                     state.memo.language,
                                                     state.document)
    state.parent += messages

    if not directive_class:
        return state.unknown_directive(name)

    state_machine = state.state_machine
    lineno = state_machine.abs_line_number()

    directive = directive_class(
        name=name,
        arguments=[],
        options=options,
        content=content,
        lineno=lineno,
        content_offset=0,
        block_text='',
        state=parent_directive.state,
        state_machine=state_machine)

    try:
        return directive.run()
    except DirectiveError as e:
        return [
            parent_directive.reporter.system_message(e.level, e.msg,
                                                     line=lineno),
        ]


def get_from_module(name):
    i = name.rfind('.')
    module, attr = name[:i], name[i + 1:]

    try:
        mod = import_module(module)
        return getattr(mod, attr)
    except AttributeError:
        raise ImportError('Unable to load "%s" from "%s"' % (attr, module))


def append_row(tbody, cells):
    row = nodes.row()
    tbody += row

    for cell in cells:
        entry = nodes.entry()
        row += entry

        if isinstance(cell, str):
            node = nodes.paragraph(text=cell)
        else:
            node = cell

        entry += node


def append_detail_row(tbody, header_text, detail):
    header_node = nodes.strong(text=header_text)

    if isinstance(detail, str):
        detail_node = [nodes.paragraph(text=text)
                       for text in detail.split('\n\n')]
    else:
        detail_node = detail

    append_row(tbody, [header_node, detail_node])


FIRST_CAP_RE = re.compile(r'(.)([A-Z][a-z]+)')
ALL_CAP_RE = re.compile(r'([a-z0-9])([A-Z])')


def uncamelcase(name, separator='_'):
    """
    Converts a string from CamelCase into a lowercase name separated by
    a provided separator.
    """
    s1 = FIRST_CAP_RE.sub(r'\1%s\2' % separator, name)
    return ALL_CAP_RE.sub(r'\1%s\2' % separator, s1).lower()


def get_resource_title(resource, is_list, append_resource=True):
    """Returns a human-readable name for the resource."""
    if hasattr(resource, 'verbose_name'):
        normalized_title = resource.verbose_name
    else:
        class_name = resource.__class__.__name__
        class_name = class_name.replace('Resource', '')
        normalized_title = title(uncamelcase(class_name, ' '))

    if is_list:
        s = '%s List' % normalized_title
    else:
        s = normalized_title

    if append_resource:
        s += ' Resource'

    return s


def get_resource_docname(app, resource, is_list):
    """Returns the name of the page used for a resource's documentation."""
    if inspect.isclass(resource):
        class_name = resource.__name__
    else:
        class_name = resource.__class__.__name__

    class_name = class_name.replace('Resource', '')
    docname = uncamelcase(class_name, '-')
    docname = app.config.webapi_docname_map.get(docname, docname)

    if is_list and resource.name != resource.name_plural:
        docname = '%s-list' % docname

    return docname


def get_ref_to_doc(refname, title=''):
    """Returns a node that links to a document with the given ref name."""
    ref = addnodes.pending_xref(reftype='ref', reftarget=refname,
                                refexplicit=(title != ''), refdomain='std')
    ref += nodes.literal(title, title, classes=['xref'])
    return ref


def get_ref_to_resource(app, resource, is_list):
    """Returns a node that links to a resource's documentation."""
    return get_ref_to_doc('webapi2.0-%s-resource' %
                          get_resource_docname(app, resource, is_list))


def get_ref_to_error(error, title=''):
    """Returns a node that links to an error's documentation."""
    return get_ref_to_doc('webapi2.0-error-%s' % error.code,
                          title=title)


def get_resource_uri_template(resource, include_child):
    """Returns the URI template for a resource.

    This will go up the resource tree, building a URI based on the URIs
    of the parents.
    """
    if resource.name == 'root':
        path = '/api/'
    else:
        if resource._parent_resource:
            path = get_resource_uri_template(
                resource=resource._parent_resource,
                include_child=True)

        path += '%s/' % resource.uri_name

        if not resource.singleton and include_child:
            path += '{%s}/' % resource.uri_object_key

    return path


def create_fake_resource_path(request, resource, child_keys, include_child,
                              url_keys=None):
    """Create a fake path to a resource.

    Args:
        request (DummyRequest):
            A request-like object that will be passed to resources to generate
            the path.

        resource (reviewboard.webapi.resources.base.WebAPIResource):
            The resource to generate the path to.

        child_keys (dict):
            A dictionary that will contain the URI object keys and their values
            corresponding to the generated path.

        include_child (bool):
            Whether or not to include child resources.

        url_keys (dict, optional):
            Specific URL keys used to populate the resource's URL.

            If provided, this won't need to attempt to guess a suitable object
            and generate a URL.

    Returns:
        unicode:
        The generated path.

    Raises:
        django.core.exceptions.ObjectDoesNotExist:
            A required model does not exist.
    """
    if url_keys:
        if include_child:
            path = resource.get_item_url(request=request, **url_keys)
        else:
            path = resource.get_list_url(**url_keys)

        child_keys.update(url_keys)
    else:
        # This should be considered legacy. We should be moving toward
        # explicit example payloads, rather than trying to deducate a payload.
        iterator = iterate_fake_resource_paths(request=request,
                                               resource=resource,
                                               child_keys=child_keys,
                                               include_child=include_child)

        try:
            path, new_child_keys = next(iterator)
        except ObjectDoesNotExist as e:
            logging.critical('Could not generate path for resource %r: %s',
                             resource, e)
            raise

        child_keys.update(new_child_keys)

    return path


def iterate_fake_resource_paths(request, resource, child_keys, include_child):
    """Iterate over all possible fake resource paths using backtracking.

    Args:
        request (DummyRequest):
            A request-like object that will be passed to resources to generate
            the path.

        resource (reviewboard.webapi.resources.base.WebAPIResource):
            The resource to generate the path to.

        child_keys (dict):
            A dictionary that will contain the URI object keys and their values
            corresponding to the generated path.

        include_child (bool):
            Whether or not to include child resources.

    Yields:
        tuple:
        A 2-tuple of:

        * The generated path (:py:class:`unicode`).
        * The new child keys (:py:class:`dict`).

    Raises:
        django.core.exceptions.ObjectDoesNotExist:
            A required model does not exist.
    """
    if resource.name == 'root':
        yield '/api/', child_keys
    else:
        if (resource._parent_resource and
            resource._parent_resource.name != 'root'):
            parents = iterate_fake_resource_paths(
                request=request,
                resource=resource._parent_resource,
                child_keys=child_keys,
                include_child=True)
        else:
            parents = [('/api/', child_keys)]

        iterate_children = (
            not resource.singleton and
            include_child and
            resource.uri_object_key and
            'GET' in resource.allowed_methods
        )

        for parent_path, parent_keys in parents:
            if iterate_children:
                # BaseResource.get_object has a bug with singleton resources
                # where it tries to cache the resulting object inside the
                # request, but it doesn't take into account any parent
                # resources. Ideally we *should* be able to just keep the same
                # request object everywhere, but we were hitting a bug where
                # the ReviewRequestDraftResource was returning the same draft
                # no matter what the value of the review_request_id kwarg was.
                #
                # Once the caching bug has been fixed in djblets' BaseResource,
                # we can switch back to reusing the same request here.
                new_request = DummyRequest(user=request.user)
                q = resource.get_queryset(new_request, **parent_keys)

                for obj in q:
                    value = getattr(obj, resource.model_object_key)
                    parent_keys[resource.uri_object_key] = value
                    path = '%s%s/%s/' % (parent_path, resource.uri_name, value)

                    yield path, parent_keys
            else:
                yield '%s%s/' % (parent_path, resource.uri_name), child_keys

        # Only the non-recursive calls to this function will reach here. This
        # means that there is no suitable set of parent models that match this
        # resource.
        raise ObjectDoesNotExist(
            'No %s objects in the database match %s.get_queryset().'
            % (resource.model, type(resource).__name__))


def build_example_payload_node(data, mimetype):
    """Return a node representing an example payload.

    Args:
        data (str)
            The payload contents.

        mimetype (str):
            The mimetype of the payload.

    Returns:
        nodes.literal_block:
        The resulting node for the payload content, or ``None`` if there's
        no data to display.
    """
    if not data:
        return None

    language = None

    for base_mimetype, lang in MIMETYPE_LANGUAGES:
        if is_mimetype_a(mimetype, base_mimetype):
            language = lang
            break

    if language == 'javascript':
        code = json.dumps(json.loads(data), sort_keys=True, indent=2)
    else:
        code = data

    return nodes.literal_block(code, code, language=language or 'text',
                               classes=['example-payload'])


def fetch_response_data(response_class, mimetype, request, **kwargs):
    """Simulate a call to an API, returning displayable response data.

    Args:
        response_class (type):
            The class generating a response. This will be a resource or an
            API error.

        mimetype (str):
            The mimetype used for the request.

        request (DummyRequest):
            The HTTP request to make.

        **kwargs (dict):
            Additional keyword arguments to pass to ``response_class``.

    Returns:
        tuple:
        A 2-tuple containing:

        1 (str):
            Displayable HTTP response code/header data.

            This will be ``None`` for HTTP 405 status codes.

        2 (str):
            Displayable HTTP response content.

            This will be ``None`` for HTTP 302 and 405 status codes.
    """
    request.META['HTTP_ACCEPT'] = mimetype

    response = response_class(request=request, **kwargs)
    headers = response.headers
    status_code = response.status_code

    data = response.content.decode('utf-8')

    if status_code == 302:
        # There's no content, so delete Content-Type from the response.
        del headers['Content-Type']
        data = None
    elif status_code == 405:
        # There's nothing at all to show here. This method isn't allowed.
        return None, None

    # This is normally set later in the response processing.
    headers.setdefault('Content-Length', len(response.content))

    headers_str = 'HTTP %s %s\n%s' % (
        status_code,
        HTTP_STATUS_CODES[status_code],
        '\n'.join(
            '%s: %s' % (key, value)
            for key, value in sorted(headers.items())
        ),
    )

    return headers_str, data


def setup(app):
    app.add_config_value(str('webapi_docname_map'), {}, str('env'))

    app.add_directive('webapi-resource', ResourceDirective)
    app.add_directive('webapi-resource-field-list', ResourceFieldListDirective)
    app.add_directive('webapi-resource-field', ResourceFieldDirective)
    app.add_directive('webapi-resource-tree', ResourceTreeDirective)
    app.add_directive('webapi-error', ErrorDirective)
    app.add_crossref_type(str('webapi2.0'), str('webapi2.0'),
                          str('single: %s'), nodes.emphasis)

    # Filter out some additional log messages.
    for name in ('djblets.util.templatetags.djblets_images',):
        logging.getLogger(name).disabled = True

    # Our fixtures include a Git Repository that is intended to point at the
    # git_repo test data. However, the path field of a repository *must*
    # contain an absolute path, so we cannot include the real path in the
    # fixtures. Instead we include a placeholder path and replace it when we go
    # to build docs, as we know then what the path will be.
    Repository.objects.filter(name='Git Repo', path='/placeholder').update(
        path=os.path.abspath(os.path.join(
            os.path.dirname(reviewboard.__file__),
            'scmtools',
            'testdata',
            'git_repo')))
