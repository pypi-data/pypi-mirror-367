"""Tags related to review requests."""

from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING

from django.template import Library, TemplateSyntaxError
from django.template.defaultfilters import stringfilter
from django.template.loader import render_to_string
from django.utils.html import escapejs, format_html
from django.utils.safestring import SafeString, mark_safe
from django.utils.translation import gettext_lazy as _
from djblets.siteconfig.models import SiteConfiguration
from djblets.util.decorators import blocktag
from djblets.util.humanize import humanize_list
from djblets.util.templatetags.djblets_js import json_dumps_items
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

from reviewboard.accounts.models import Profile, Trophy
from reviewboard.accounts.trophies import UnknownTrophy
from reviewboard.admin.read_only import is_site_read_only_for
from reviewboard.diffviewer.diffutils import get_displayed_diff_line_ranges
from reviewboard.reviews.builtin_fields import FileAttachmentsField
from reviewboard.reviews.fields import (get_review_request_field,
                                        get_review_request_fieldset,
                                        get_review_request_fieldsets)
from reviewboard.reviews.markdown_utils import (is_rich_text_default_for_user,
                                                render_markdown,
                                                normalize_text_for_edit)
from reviewboard.reviews.models import (BaseComment, Group,
                                        ReviewRequest, ScreenshotComment,
                                        FileAttachmentComment,
                                        GeneralComment)
from reviewboard.reviews.ui.base import FileAttachmentReviewUI
from reviewboard.site.urlresolvers import local_site_reverse

if TYPE_CHECKING:
    from reviewboard.attachments.models import FileAttachment
    from reviewboard.reviews.context import ReviewRequestContext


logger = logging.getLogger(__name__)


register = Library()


@register.simple_tag(takes_context=True)
def display_review_request_trophies(context, review_request):
    """Returns the HTML for the trophies awarded to a review request."""
    trophy_models = Trophy.objects.get_trophies(review_request)

    if not trophy_models:
        return ''

    trophies = []

    for trophy_model in trophy_models:
        trophy_type_cls = trophy_model.trophy_type

        if trophy_type_cls is not UnknownTrophy:
            try:
                trophy_type = trophy_type_cls()
                text = trophy_type.format_display_text(context['request'],
                                                       trophy_model)

                trophies.append({
                    'image_urls': trophy_type.image_urls,
                    'image_width': trophy_type.image_width,
                    'image_height': trophy_type.image_height,
                    'name': trophy_type.name,
                    'text': text,
                })
            except Exception as e:
                logger.error('Error when rendering trophy %r (%r): %s',
                             trophy_model.pk, trophy_type_cls, e,
                             exc_info=True)

    return render_to_string(
        template_name='reviews/trophy_box.html',
        context={
            'trophies': trophies,
        })


def _generate_reply_html(context, user, context_id, review, reply, timestamp,
                         last_visited, text, rich_text, anchor_name,
                         use_avatars, extra_context={}):
    """Generate HTML for a single reply.

    Args:
        context (django.template.RequestContext):
            The template context for the page.

        user (django.contrib.auth.models.User):
            The user who is viewing the replies.

        context_id (unicode):
            An internal ID used by the JavaScript code for storing and
            categorizing replies.

        review (reviewboard.reviews.models.review.Review):
            The review being replied to.

        reply (reviewboard.reviews.models.review.Review):
            The reply to the review.

        timestamp (datetime.datetime):
            The timestamp of the reply.

        last_visited (datetime.datetime):
            The last time the user visited the page containing the replies.

        text (unicode):
            The reply text.

        rich_text (bool):
            Whether the reply text is in Markdown format.

        anchor_name (unicode):
            The name of the anchor for the comment, for use in linking to
            this reply.

        use_avatars (bool):
            Whether avatars are enabled on Review Board. This will control
            whether avatars are shown in the replies.

        extra_context (dict):
            Extra template context to include when rendering the page.

    Returns:
        django.utils.safestring.SafeText:
        The HTML for the reply.
    """
    # Note that update() implies push().
    context.update(dict({
        'anchor_name': anchor_name,
        'context_id': context_id,
        'draft': not reply.public,
        'id': reply.pk,
        'reply_is_new': (
            user is not None and
            last_visited is not None and
            reply.is_new_for_user(user, last_visited) and
            not review.is_new_for_user(user, last_visited)),
        'reply_user': reply.user,
        'rich_text': rich_text,
        'text': text,
        'timestamp': timestamp,
        'use_avatars': use_avatars,
    }, **extra_context))

    try:
        return render_to_string(
            template_name='reviews/review_reply.html',
            context=context.flatten())
    finally:
        context.pop()


@register.simple_tag(takes_context=True)
def comment_replies(context, review, comment, context_id):
    """Render a list of replies to a comment.

    This loads all the replies made to a particular comment and renders
    them in order by timestamp, showing the author of each comment, the
    timestamp, and the text in the appropriate format.

    Args:
        context (django.template.RequestContext):
            The template context for the page.

        review (reviewboard.reviews.models.review.Review):
            The review being replied to.

        comment (reviewboard.reviews.models.base_comment.BaseComment):
            The comment being replied to.

        context_id (unicode):
            An internal ID used by the JavaScript code for storing and
            categorizing replies.

    Returns:
        django.utils.safestring.SafeText:
        The resulting HTML for the replies.
    """
    siteconfig = SiteConfiguration.objects.get_current()
    use_avatars = siteconfig.get('avatars_enabled')
    user = context['request'].user
    last_visited = context.get('last_visited')

    return mark_safe(''.join(
        _generate_reply_html(
            anchor_name='%s%d' % (reply_comment.anchor_prefix,
                                  reply_comment.pk),
            context=context,
            context_id=context_id,
            last_visited=last_visited,
            reply=reply_comment.get_review(),
            review=review,
            rich_text=reply_comment.rich_text,
            text=reply_comment.text,
            timestamp=reply_comment.timestamp,
            use_avatars=use_avatars,
            user=user,
            extra_context={
                'comment_id': reply_comment.pk,
            })
        for reply_comment in comment.public_replies(user)
    ))


@register.simple_tag(takes_context=True)
def review_body_replies(context, review, body_field, context_id):
    """Render a list of replies to a body field of a review.

    This loads all the replies made to a review's header/footer body field and
    renders them in order by timestamp, showing the author of each comment,
    the timestamp, and the text in the appropriate format.

    Args:
        context (django.template.RequestContext):
            The template context for the page.

        review (reviewboard.reviews.models.review.Review):
            The review being replied to.

        body_field (unicode):
            The body field to look up replies to. This can be either
            ``body_top`` or ``body_bottom``.

        context_id (unicode):
            An internal ID used by the JavaScript code for storing and
            categorizing replies.

    Returns:
        django.utils.safestring.SafeText:
        The resulting HTML for the replies.

    Raises:
        django.template.TemplateSyntaxError:
            There was an invalid ``body_field`` provided.
    """
    if body_field not in ('body_top', 'body_bottom'):
        raise TemplateSyntaxError('Invalid body field "%s" provided.'
                                  % body_field)

    siteconfig = SiteConfiguration.objects.get_current()
    use_avatars = siteconfig.get('avatars_enabled')
    user = context['request'].user
    last_visited = context.get('last_visited')
    anchor_field_alias = {
        'body_top': 'header',
        'body_bottom': 'footer',
    }

    replies = getattr(review, 'public_%s_replies' % body_field)(user)

    return mark_safe(''.join(
        _generate_reply_html(
            anchor_name='%s-reply%d' % (anchor_field_alias[body_field],
                                        reply.pk),
            context=context,
            context_id=context_id,
            last_visited=last_visited,
            reply=reply,
            review=review,
            rich_text=getattr(reply, '%s_rich_text' % body_field),
            text=getattr(reply, body_field),
            timestamp=reply.timestamp,
            use_avatars=use_avatars,
            user=user)
        for reply in replies
    ))


@register.inclusion_tag('reviews/review_reply_section.html',
                        takes_context=True)
def reply_section(context, review, comment, context_type, context_id,
                  reply_to_text=''):
    """Render a template for displaying a reply.

    This takes the same parameters as :py:func:`reply_list`. The template
    rendered by this function, ``reviews/review_reply_section.html``,
    is responsible for invoking :py:func:`reply_list` and as such passes these
    variables through. It does not make use of them itself.

    Args:
        context (django.template.Context):
            The collection of key-value pairs available in the template.

        review (reviewboard.reviews.models.Review):
            The review being replied to.

        comment (reviewboard.reviews.models.BaseComment):
            The comment being replied to.

        context_type (unicode):
            The type of comment being replied to. This is one of
            ``diff_comments``, ``screenshot_comments``,
            ``file_attachment_comments``, ``general_comments`` (if the reply is
            to a comment), or ``body_top`` or ``body_bottom`` if the reply is
            to the header or footer text of the review.

        context_id (unicode):
            The internal ID used by the JavaScript code for storing and
            categorizing comments.

        reply_to_text (unicode):
            The text in the review being replied to.

    Returns:
        dict:
        The context to use when rendering the template included by the
        inclusion tag.
    """
    user = context.get('user')

    if context_type == 'body_top':
        anchor_prefix = 'header-reply'
    elif context_type == 'body_bottom':
        anchor_prefix = 'footer-reply'
    else:
        assert comment
        comment_cls = type(comment)

        if comment_cls is FileAttachmentComment:
            context_id += 'f'
        elif comment_cls is GeneralComment:
            context_id += 'g'
        elif comment_cls is ScreenshotComment:
            context_id += 's'

        anchor_prefix = comment.anchor_prefix
        context_id += str(comment.id)

    return {
        'reply_anchor_prefix': anchor_prefix,
        'review': review,
        'comment': comment,
        'context_type': context_type,
        'context_id': context_id,
        'user': user,
        'local_site_name': context.get('local_site_name'),
        'is_read_only': is_site_read_only_for(user),
        'reply_to_is_empty': reply_to_text == '',
        'request': context['request'],
        'last_visited': context.get('last_visited'),
    }


@register.simple_tag
def reviewer_list(review_request):
    """
    Returns a humanized list of target reviewers in a review request.
    """
    return humanize_list([group.display_name or group.name
                          for group in review_request.target_groups.all()] +
                         [user.get_full_name() or user.username
                          for user in review_request.target_people.all()])


@register.tag
@blocktag(end_prefix='end_')
def for_review_request_field(context, nodelist, review_request_details,
                             fieldset):
    """Loops through all fields in a fieldset.

    This can take a fieldset instance or a fieldset ID.
    """
    s = []

    request = context.get('request')

    if isinstance(fieldset, str):
        fieldset_cls = get_review_request_fieldset(fieldset)

        try:
            fieldset = fieldset_cls(
                review_request_details=review_request_details,
                request=request)
        except Exception as e:
            logger.exception(
                'Error instantiating ReviewRequestFieldset %r: %s',
                fieldset_cls, e)
            return ''

    for field in fieldset.fields:
        if field.should_render:
            context.push()
            context['field'] = field
            s.append(nodelist.render(context))
            context.pop()

    return mark_safe(''.join(s))


@register.tag
@blocktag(end_prefix='end_')
def for_review_request_fieldset(context, nodelist, review_request_details):
    """Loop through all fieldsets.

    Args:
        context (dict):
            The render context.

        nodelist (django.template.NodeList):
            The contents of the template inside the blocktag.

        review_request_details (reviewboard.reviews.models.
                                base_review_request_details.
                                BaseReviewRequestDetails):
            The review request or draft being rendered.

    Returns:
        unicode:
        The rendered tag contents.
    """
    s = []
    is_first = True
    review_request = review_request_details.get_review_request()
    request = context['request']
    user = request.user

    is_review_request_mutable = (
        review_request.status == ReviewRequest.PENDING_REVIEW and
        review_request.is_mutable_by(user)
    )

    for fieldset_cls in get_review_request_fieldsets():
        try:
            try:
                fieldset = fieldset_cls(
                    review_request_details=review_request_details,
                    request=request)
            except Exception as e:
                logger.exception(
                    'Error instantiating ReviewRequestFieldset %r: %s',
                    fieldset_cls, e,
                    extra={'request': request})
            else:
                if fieldset.should_render:
                    # Note that update() implies push().
                    context.update({
                        'fieldset': fieldset,
                        'show_fieldset_required': (
                            fieldset.show_required and
                            is_review_request_mutable
                        ),
                        'forloop': {
                            'first': is_first,
                        }
                    })

                    try:
                        s.append(nodelist.render(context))
                    finally:
                        context.pop()

                    is_first = False
        except Exception as e:
            logger.error('Error running is_empty for ReviewRequestFieldset '
                         '%r: %s', fieldset_cls, e, exc_info=True,
                         extra={'request': request})

    return mark_safe(''.join(s))


@register.tag
@blocktag(end_prefix='end_')
def review_request_field(context, nodelist, review_request_details, field_id):
    """Render a block with a specific review request field.

    Args:
        context (dict):
            The render context.

        nodelist (django.template.NodeList):
            The contents of the template inside the blocktag.

        review_request_details (reviewboard.reviews.models.
                                base_review_request_details.
                                BaseReviewRequestDetails):
            The review request or draft being rendered.

        field_id (unicode):
            The ID of the field to add to the render context.

    Returns:
        unicode:
        The rendered block.
    """
    request = context.get('request')

    try:
        field_cls = get_review_request_field(field_id)
        field = field_cls(review_request_details, request=request)
    except Exception as e:
        logger.exception('Error instantiating field %r: %s',
                         field_id, e,
                         extra={'request': request})
        return ''

    context.push()

    try:
        context['field'] = field
        return nodelist.render(context)
    finally:
        context.pop()


@register.filter
def bug_url(bug_id, review_request):
    """
    Returns the URL based on a bug number on the specified review request.

    If the repository the review request belongs to doesn't have an
    associated bug tracker, this returns None.
    """
    if (review_request.repository and
        review_request.repository.bug_tracker and
        '%s' in review_request.repository.bug_tracker):
        try:
            return review_request.repository.bug_tracker % bug_id
        except TypeError:
            logger.error("Error creating bug URL. The bug tracker URL '%s' "
                         "is likely invalid." %
                         review_request.repository.bug_tracker)

    return None


@register.simple_tag(takes_context=True)
def star(context, obj):
    """Render the code for displaying a star used for starring items.

    The rendered code should handle click events so that the user can toggle
    the star. The star is rendered by the template ``reviews/star.html``.

    Args:
        context (django.template.RequestContext):
            The template context for the page.

        obj (reviewboard.reviews.models.review_request.ReviewRequest or
             reviewboard.reviews.models.group.Group):

    Returns:
        django.utils.safestring.SafeText:
        The rendered HTML for the star.
    """
    return render_star(context.get('user', None), obj)


def render_star(user, obj):
    """
    Does the actual work of rendering the star. The star tag is a wrapper
    around this.
    """
    if user.is_anonymous:
        return ""

    profile = None

    if not hasattr(obj, 'starred'):
        try:
            profile = user.get_profile(create_if_missing=False)
        except Profile.DoesNotExist:
            return ''

    if isinstance(obj, ReviewRequest):
        obj_info = {
            'type': 'reviewrequests',
            'id': obj.display_id
        }

        if hasattr(obj, 'starred'):
            starred = obj.starred
        else:
            starred = \
                profile.starred_review_requests.filter(pk=obj.id).exists()
    elif isinstance(obj, Group):
        obj_info = {
            'type': 'groups',
            'id': obj.name
        }

        if hasattr(obj, 'starred'):
            starred = obj.starred
        else:
            starred = profile.starred_groups.filter(pk=obj.id).exists()
    else:
        raise TemplateSyntaxError(
            "star tag received an incompatible object type (%s)" %
            type(obj))

    if starred:
        image_alt = _("Starred")
    else:
        image_alt = _("Click to star")

    return render_to_string(
        template_name='reviews/star.html',
        context={
            'object': obj_info,
            'starred': int(starred),
            'alt': image_alt,
            'user': user,
        })


@register.inclusion_tag('reviews/comment_issue.html',
                        takes_context=True)
def comment_issue(context, review_request, comment, comment_type):
    """
    Renders the code responsible for handling comment issue statuses.
    """

    issue_status = BaseComment.issue_status_to_string(comment.issue_status)
    user = context.get('user', None)

    return {
        'comment': comment,
        'comment_type': comment_type,
        'issue_status': issue_status,
        'review': comment.get_review(),
        'interactive': comment.can_change_issue_status(user),
        'can_verify': comment.can_verify_issue_status(user),
    }


@register.filter
@stringfilter
def pretty_print_issue_status(status):
    """Turns an issue status code into a human-readable status string."""
    return BaseComment.issue_status_to_string(status)


@register.filter
@stringfilter
def issue_status_icon(status):
    """Return an icon name for the issue status.

    Args:
        status (unicode):
            The stored issue status for the comment.

    Returns:
        unicode: The icon name for the issue status.
    """
    if status == BaseComment.OPEN:
        return 'rb-icon-issue-open'
    elif status == BaseComment.RESOLVED:
        return 'rb-icon-issue-resolved'
    elif status == BaseComment.DROPPED:
        return 'rb-icon-issue-dropped'
    elif status in (BaseComment.VERIFYING_RESOLVED,
                    BaseComment.VERIFYING_DROPPED):
        return 'rb-icon-issue-verifying'
    else:
        raise ValueError('Unknown comment issue status "%s"' % status)


@register.filter('render_markdown')
def _render_markdown(text, is_rich_text):
    if is_rich_text:
        return mark_safe(render_markdown(text))
    else:
        return text


@register.simple_tag(takes_context=True)
def expand_fragment_link(context, expanding, tooltip,
                         expand_above, expand_below, text=None):
    """Renders a diff comment fragment expansion link.

    This link will expand the context by the supplied `expanding_above` and
    `expanding_below` values.

    `expanding` is expected to be one of 'above', 'below', or 'line'."""

    lines_of_context = context['lines_of_context']

    image_class = 'rb-icon-diff-expand-%s' % expanding
    expand_pos = (lines_of_context[0] + expand_above,
                  lines_of_context[1] + expand_below)

    return render_to_string(
        template_name='reviews/expand_link.html',
        context={
            'tooltip': tooltip,
            'text': text,
            'comment_id': context['comment'].id,
            'expand_pos': expand_pos,
            'image_class': image_class,
        })


@register.simple_tag(takes_context=True)
def expand_fragment_header_link(context, header):
    """Render a diff comment fragment header expansion link.

    This link expands the context to contain the given line number.
    """
    lines_of_context = context['lines_of_context']
    offset = context['first_line'] - header['line']

    return render_to_string(
        template_name='reviews/expand_link.html',
        context={
            'tooltip': _('Expand to header'),
            'text': format_html('<code>{0}</code>', header['text']),
            'comment_id': context['comment'].id,
            'expand_pos': (lines_of_context[0] + offset,
                           lines_of_context[1]),
            'image_class': 'rb-icon-diff-expand-header',
        })


@register.simple_tag(name='normalize_text_for_edit', takes_context=True)
def _normalize_text_for_edit(context, text, rich_text, escape_js=False):
    text = normalize_text_for_edit(context['request'].user, text, rich_text,
                                   escape_html=not escape_js)

    if escape_js:
        text = escapejs(text)

    return text


@register.simple_tag(takes_context=True)
def rich_text_classname(context, rich_text):
    if rich_text or is_rich_text_default_for_user(context['request'].user):
        return 'rich-text'

    return ''


@register.simple_tag(takes_context=True)
def diff_comment_line_numbers(context, chunks, comment):
    """Render the changed line number ranges for a diff, for use in e-mail.

    This will display the original and patched line ranges covered by a
    comment, transforming the comment's stored virtual line ranges into
    human-readable ranges. It's intended for use in e-mail.

    The template tag's output will list the original line ranges only if
    there are ranges to show, and same with the patched line ranges.

    Args:
        context (django.template.Context):
            The template context.

        chunks (list):
            The list of chunks for the diff.

        comment (reviewboard.reviews.models.diff_comment.Comment):
            The comment containing the line ranges.

    Returns:
        unicode:
        A string representing the line ranges for the comment.
    """
    if comment.first_line is None:
        # Comments without a line number represent the entire file.
        return ''

    orig_range_info, patched_range_info = get_displayed_diff_line_ranges(
        chunks, comment.first_line, comment.last_line)

    if orig_range_info:
        orig_start_linenum, orig_end_linenum = \
            orig_range_info['display_range']

        if orig_start_linenum == orig_end_linenum:
            orig_lines_str = '%s' % orig_start_linenum
            orig_lines_prefix = 'Line'
        else:
            orig_lines_str = '%s-%s' % (orig_start_linenum, orig_end_linenum)
            orig_lines_prefix = 'Lines'
    else:
        orig_lines_str = None
        orig_lines_prefix = None

    if patched_range_info:
        patched_start_linenum, patched_end_linenum = \
            patched_range_info['display_range']

        if patched_start_linenum == patched_end_linenum:
            patched_lines_str = '%s' % patched_start_linenum
            patched_lines_prefix = 'Lines'
        else:
            patched_lines_str = '%s-%s' % (patched_start_linenum,
                                           patched_end_linenum)
            patched_lines_prefix = 'Lines'
    else:
        patched_lines_str = None
        patched_lines_prefix = None

    if orig_lines_str and patched_lines_str:
        return '%s %s (original), %s (patched)' % (
            orig_lines_prefix, orig_lines_str, patched_lines_str)
    elif orig_lines_str:
        return '%s %s (original)' % (orig_lines_prefix, orig_lines_str)
    elif patched_lines_str:
        return '%s %s (patched)' % (patched_lines_prefix, patched_lines_str)
    else:
        return ''


@register.simple_tag(takes_context=True)
def reviewable_page_model_data(
    context: ReviewRequestContext,
) -> SafeString:
    """Output JSON-serialized data for a RB.ReviewablePage model.

    The data will be used by :js:class:`RB.ReviewablePage` in order to
    populate the review request and editor with the necessary state.

    Args:
        context (django.template.RequestContext):
            The current template context.

    Returns:
        django.utils.safestring.SafeString:
        The resulting JSON-serialized data. This consists of keys that are
        meant to be injected into an existing dictionary.
    """
    request = context['request']
    user = request.user
    review_request = context['review_request']
    review_request_details = context['review_request_details']
    draft = context['draft']
    close_description = context['close_description']
    close_description_rich_text = context['close_description_rich_text']

    if review_request.local_site:
        local_site_prefix = 's/%s/' % review_request.local_site.name
    else:
        local_site_prefix = ''

    # Build data for the RB.ReviewRequest
    if review_request.status == review_request.PENDING_REVIEW:
        state_data = 'PENDING'
    elif review_request.status == review_request.SUBMITTED:
        state_data = 'CLOSE_SUBMITTED'
    elif review_request.status == review_request.DISCARDED:
        state_data = 'CLOSE_DISCARDED'
    else:
        raise ValueError('Unexpected ReviewRequest.status value "%s"'
                         % review_request.status)

    review_request_data = {
        'id': review_request.display_id,
        'localSitePrefix': local_site_prefix,
        'branch': review_request_details.branch,
        'bugsClosed': review_request_details.get_bug_list(),
        'closeDescription': normalize_text_for_edit(
            user=user,
            text=close_description,
            rich_text=close_description_rich_text,
            escape_html=False),
        'closeDescriptionRichText': close_description_rich_text,
        'description': normalize_text_for_edit(
            user=user,
            text=review_request_details.description,
            rich_text=review_request_details.description_rich_text,
            escape_html=False),
        'descriptionRichText': review_request_details.description_rich_text,
        'hasDraft': draft is not None,
        'lastUpdatedTimestamp': review_request.last_updated,
        'public': review_request.public,
        'reviewURL': review_request.get_absolute_url(),
        'state': state_data,
        'summary': review_request_details.summary,
        'targetGroups': [
            {
                'name': group.name,
                'url': group.get_absolute_url(),
            }
            for group in review_request_details.target_groups.all()
        ],
        'targetPeople': [
            {
                'username': target_user.username,
                'url': local_site_reverse('user',
                                          args=[target_user],
                                          request=request),
            }
            for target_user in review_request_details.target_people.all()
        ],
        'testingDone': normalize_text_for_edit(
            user=user,
            text=review_request_details.testing_done,
            rich_text=review_request_details.testing_done_rich_text,
            escape_html=False),
        'testingDoneRichText': review_request_details.testing_done_rich_text,
    }

    if user.is_authenticated:
        review_request_visit = context['review_request_visit']

        if review_request_visit.visibility == review_request_visit.VISIBLE:
            visibility_data = 'VISIBLE'
        elif review_request_visit.visibility == review_request_visit.ARCHIVED:
            visibility_data = 'ARCHIVED'
        elif review_request_visit.visibility == review_request_visit.MUTED:
            visibility_data = 'MUTED'
        else:
            raise ValueError(
                'Unexpected ReviewRequestVisit.visibility value "%s"'
                % review_request_visit.visibility)

        review_request_data['visibility'] = visibility_data

    repository = review_request.repository

    if repository:
        review_request_data['repository'] = {
            'id': repository.pk,
            'name': repository.name,
            'scmtoolName': repository.scmtool_class.name,
            'requiresBasedir': not repository.diffs_use_absolute_paths,
            'requiresChangeNumber': repository.supports_pending_changesets,
            'supportsPostCommit': repository.supports_post_commit,
        }

        if repository.bug_tracker:
            review_request_data['bugTrackerURL'] = \
                local_site_reverse(
                    'bug_url',
                    args=[review_request.display_id, '--bug_id--'],
                    request=request)

    if draft:
        review_request_data['submitter'] = {
            'title': draft.submitter.username,
            'url': draft.submitter.get_absolute_url(),
        }

    # Build the data for the RB.ReviewRequestEditor.
    editor_data = {
        'closeDescriptionRenderedText': _render_markdown(
            close_description,
            close_description_rich_text),
        'commits': None,
        'forceViewUserDraft': context['force_view_user_draft'],
        'hasDraft': draft is not None,
        'mutableByUser': context['mutable_by_user'],
        'showSendEmail': context['send_email'],
        'statusMutableByUser': context['status_mutable_by_user'],
        'userDraftExists': context['user_draft_exists'],
        'viewingUserDraft': context['viewing_user_draft'],
    }

    if review_request.created_with_history:
        diffset = review_request_details.get_latest_diffset()

        if diffset is None:
            diffset = review_request.get_latest_diffset()

        if diffset is not None:
            editor_data['commits'] = [
                commit.serialize()
                for commit in diffset.commits.all()
            ]

    # Build extra data for the RB.ReviewRequest.
    extra_review_request_draft_data = {}

    if draft and draft.changedesc:
        extra_review_request_draft_data.update({
            'changeDescription': normalize_text_for_edit(
                user=user,
                text=draft.changedesc.text,
                rich_text=draft.changedesc.rich_text,
                escape_html=False),
            'changeDescriptionRichText': draft.changedesc.rich_text,
        })

        editor_data['changeDescriptionRenderedText'] = _render_markdown(
            draft.changedesc.text, draft.changedesc.rich_text)

        if draft.diffset and draft.diffset.revision > 1:
            extra_review_request_draft_data['interdiffLink'] = \
                local_site_reverse(
                    'view-interdiff',
                    args=[
                        review_request.display_id,
                        draft.diffset.revision - 1,
                        draft.diffset.revision,
                    ],
                    request=request)

    # Build the file attachments data for the editor data.
    #
    # We're going to explicitly create a new FileAttachmentsField here for
    # the purpose of building model data. We don't want to use the one on the
    # review request, in case that has been tampered with.
    file_attachments_field = FileAttachmentsField(
        review_request_details=review_request_details,
        request=request)

    all_file_attachments: list[FileAttachment] = context.get(
        'all_file_attachments', [])
    file_attachments: list[FileAttachment] = context.get(
        'file_attachments', [])
    file_attachment_ids: set[Any] = {
        file_attachment.pk for file_attachment in file_attachments
    }

    # This will contain data for the file attachments that will be displayed
    # on the review request.
    file_attachments_data: list[dict[str, Any]] = [
        file_attachments_field.get_attachment_js_model_attrs(
            attachment=file_attachment,
            draft=draft)
        for file_attachment in file_attachments
    ]

    # This will contain data for all file attachments related to the review
    # request, including ones that won't be displayed.
    all_file_attachments_data: list[dict[str, Any]] = [
        file_attachments_field.get_attachment_js_model_attrs(
            attachment=file_attachment,
            draft=draft)
        for file_attachment in all_file_attachments
        if file_attachment.pk not in file_attachment_ids
    ] + file_attachments_data

    if all_file_attachments_data:
        editor_data['allFileAttachments'] = all_file_attachments_data

    if file_attachments_data:
        editor_data['fileAttachments'] = file_attachments_data

    # Build the file attachment comments data for the editor data.
    file_attachment_comments_data = {}

    for file_attachment in all_file_attachments:
        review_ui = file_attachment.review_ui

        if not review_ui:
            # For the purposes of serialization, we'll create a dummy ReviewUI.
            review_ui = FileAttachmentReviewUI(file_attachment.review_request,
                                               file_attachment)

        # NOTE: We're setting this here because file attachments serialization
        #       requires this to be set, but we don't necessarily have it set
        #       by this time. We should rethink parts of this down the road,
        #       but it requires dealing with some compatibility issues for
        #       subclasses.
        review_ui.request = request

        file_attachment_comments_data[file_attachment.pk] = \
            review_ui.serialize_comments(file_attachment.get_comments())

    if file_attachment_comments_data:
        editor_data['fileAttachmentComments'] = file_attachment_comments_data

    # And we're done! Assemble it together and chop off the outer dictionary
    # so it can be injected correctly.
    json_items = json_dumps_items({
        'checkForUpdates': True,
        'reviewRequestData': review_request_data,
        'extraReviewRequestDraftData': extra_review_request_draft_data,
        'editorData': editor_data,
        'lastActivityTimestamp': context['last_activity_time'],
    })
    assert isinstance(json_items, SafeString)

    return json_items


@register.simple_tag(takes_context=True)
def render_review_request_entries(context, entries):
    """Render a series of entries on the page.

    Args:
        context (django.template.RequestContext):
            The existing template context on the page.

        entries (list of
                 reviewboard.reviews.detail.BaseReviewRequestPageEntry):
            The entries to render.

    Returns:
        unicode:
        The resulting HTML for the entries.
    """
    request = context['request']

    return mark_safe(''.join(
        entry.render_to_string(request, context)
        for entry in entries
    ))


@register.tag
@blocktag(end_prefix='end_')
def code_block(context, nodelist, lexer_name):
    """Syntax-highlight a block of code using the given Pygments lexer name.

    Version Added:
        5.0

    Args:
        context (dict):
            The render context.

        nodelist (django.template.NodeList):
            The contents of the template inside the blocktag.

        lexer_name (str):
            The lexer to use for syntax highlighting.

    Returns:
        django.utils.safestring.SafeString:
        The resulting HTML.

    Example:
        .. code-block:: html+django

           {% code_block "python" %}
           def my_func(a, b=1):
               pass
           {% end_code_block %}
    """
    lexer = get_lexer_by_name(lexer_name)
    lexer.add_filter('codetagify')

    return highlight(nodelist.render(context), lexer, HtmlFormatter())


@register.filter
def add_view_draft_query(
    url: str,
    viewing_user_draft: bool,
) -> str:
    """Add the ?view-draft=1 querystring to a URL.

    When a user is viewing a draft owned by someone else, we want links within
    the review request to include the query parameter so that they stay within
    the draft view.

    Args:
        url (str):
            The URL to manipulate.

        viewing_user_draft (bool):
            Whether the user is viewing a draft owned by another user.

    Returns:
        str:
        The new URL to use, including the ?view-draft=1 query parameter.
    """
    if viewing_user_draft:
        if '#' in url:
            parts = url.split('#', 1)

            return f'{parts[0]}?view-draft=1#{parts[1]}'
        else:
            return f'{url}?view-draft=1'
    else:
        return url
