"""Server information and capability registration for the API."""

import logging
from copy import deepcopy

from django.conf import settings
from djblets.siteconfig.models import SiteConfiguration

from reviewboard import get_version_string, get_package_version, is_release
from reviewboard.admin.server import get_server_url
from reviewboard.diffviewer.features import dvcs_feature
from reviewboard.reviews.ui import review_ui_registry
from reviewboard.scmtools import scmtools_registry


logger = logging.getLogger(__name__)


_registered_capabilities = {}
_capabilities_defaults = {
    'authentication': {
        # Whether to allow clients to authenticate to Review Board
        # via a web browser.
        'client_web_login': True,
    },
    'diffs': {
        'base_commit_ids': True,
        'file_attachments': True,
        'moved_files': True,
        'validation': {
            'base_commit_ids': True,
        }
    },
    'extra_data': {
        'json_patching': True,
    },
    'review_requests': {
        'commit_ids': True,
        'trivial_publish': True,
    },
    'review_uis': {
        'supported_mimetypes': [],
    },
    'scmtools': {
        'git': {
            'empty_files': True,
            'symlinks': True,
        },
        'mercurial': {
            'empty_files': True,
        },
        'perforce': {
            'moved_files': True,
            'empty_files': True,
        },
        'svn': {
            'empty_files': True,
        },
    },
    'text': {
        'markdown': True,
        'per_field_text_types': True,
        'can_include_raw_values': True,
    },
}
_feature_gated_capabilities = {
    'review_requests': {
        'supports_history': dvcs_feature,
    },
}


def get_server_info(request=None):
    """Return server information for use in the API.

    This is used for the root resource and for the deprecated server
    info resource.

    Args:
        request (django.http.HttpRequest, optional):
            The HTTP request from the client.

    Returns:
        dict:
        A dictionary of information about the server and its capabilities.
    """
    return {
        'product': {
            'name': 'Review Board',
            'version': get_version_string(),
            'package_version': get_package_version(),
            'is_release': is_release(),
        },
        'site': {
            'url': get_server_url(request=request),
            'administrators': [
                {
                    'name': name,
                    'email': email,
                }
                for name, email in settings.ADMINS
            ],
            'time_zone': settings.TIME_ZONE,
        },
        'capabilities': get_capabilities(request=request),
    }


def get_capabilities(request=None):
    """Return the capabilities made available in the API.

    Args:
        request (django.http.HttpRequest, optional):
            The http request from the client.

    Returns:
        dict:
        The dictionary of capabilities.
    """
    capabilities = deepcopy(_capabilities_defaults)
    capabilities.update(_registered_capabilities)

    for category, cap, enabled in get_feature_gated_capabilities(request):
        capabilities.setdefault(category, {})[cap] = enabled

    siteconfig = SiteConfiguration.objects.get_current()
    capabilities['authentication']['client_web_login'] = \
        siteconfig.get('client_web_login')

    capabilities['diffs'].update({
        'max_binary_size': siteconfig.get('diffviewer_max_binary_size'),
        'max_diff_size': siteconfig.get('diffviewer_max_diff_size'),
    })

    # We always report support for Power Pack-provided types, so that clients
    # can upload these files, even if Power Pack is not (yet) licensed.
    mimetypes = {
        'application/msword',
        'application/pdf',
        'application/vnd.ms-excel',
        'application/vnd.ms-powerpoint',
        'application/vnd.oasis.opendocument.presentation',
        'application/vnd.oasis.opendocument.spreadsheet',
        'application/vnd.oasis.opendocument.text',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/x-pdf',
    }

    for review_ui_class in review_ui_registry:
        mimetypes.update(review_ui_class.supported_mimetypes)

    capabilities['review_uis']['supported_mimetypes'] = sorted(mimetypes)
    capabilities['scmtools']['supported_tools'] = sorted(
        scmtool.scmtool_id
        for scmtool in scmtools_registry
    )

    return capabilities


def get_feature_gated_capabilities(request=None):
    """Return the capabilities gated behind enabled features.

    Args:
        request (django.http.HttpRequest, optional):
            The HTTP request from the client.

    Yields:
        tuple:
        A 3-tuple of the following:

        * The category of the capability (:py:class:`unicode`).
        * The capability name (:py:class:`unicode`).
        * Whether or not the capability is enabled (:py:class:`bool`).
    """
    for category, caps in _feature_gated_capabilities.items():
        for cap, required_feature in caps.items():
            if required_feature.is_enabled(request=request):
                yield category, cap, True


def register_webapi_capabilities(capabilities_id, caps):
    """Register a set of web API capabilities.

    These capabilities will appear in the dictionary of available
    capabilities with the ID as their key.

    A capabilities_id attribute passed in, and can only be registered once.
    A KeyError will be thrown if attempting to register a second time.

    Args:
        capabilities_id (unicode):
            A unique ID representing this collection of capabilities.
            This can only be used once until unregistered.

        caps (dict):
            The dictionary of capabilities to register. Each key msut
            be a string, and each value should be a boolean or a
            dictionary of string keys to booleans.

    Raises:
        KeyError:
            The capabilities ID has already been used.
    """
    if not capabilities_id:
        raise ValueError('The capabilities_id attribute must not be None')

    if capabilities_id in _registered_capabilities:
        raise KeyError('"%s" is already a registered set of capabilities'
                       % capabilities_id)

    if capabilities_id in _capabilities_defaults:
        raise KeyError('"%s" is reserved for the default set of capabilities'
                       % capabilities_id)

    _registered_capabilities[capabilities_id] = caps


def unregister_webapi_capabilities(capabilities_id):
    """Unregister a previously registered set of web API capabilities.

    Args:
        capabilities_id (unicode):
            The unique ID representing a registered collection of capabilities.

    Raises:
        KeyError:
            A set of capabilities matching the ID were not found.
    """
    try:
        del _registered_capabilities[capabilities_id]
    except KeyError:
        logger.error('Failed to unregister unknown web API capabilities '
                     '"%s".',
                     capabilities_id)
        raise KeyError('"%s" is not a registered web API capabilities set'
                       % capabilities_id)
