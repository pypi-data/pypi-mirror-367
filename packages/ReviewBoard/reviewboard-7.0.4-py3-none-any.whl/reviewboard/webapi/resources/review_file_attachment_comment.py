from typing import Optional

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from djblets.util.decorators import augment_method_from
from djblets.webapi.decorators import (webapi_login_required,
                                       webapi_response_errors,
                                       webapi_request_fields)
from djblets.webapi.errors import (DOES_NOT_EXIST, INVALID_FORM_DATA,
                                   NOT_LOGGED_IN, PERMISSION_DENIED)
from djblets.webapi.fields import IntFieldType

from reviewboard.attachments.models import FileAttachment
from reviewboard.reviews.models import ReviewRequest
from reviewboard.webapi.decorators import webapi_check_local_site
from reviewboard.webapi.resources import resources
from reviewboard.webapi.resources.base_file_attachment_comment import \
    BaseFileAttachmentCommentResource


class ReviewFileAttachmentCommentResource(BaseFileAttachmentCommentResource):
    """Provides information on file comments made on a review.

    If the review is a draft, then comments can be added, deleted, or
    changed on this list. However, if the review is already published,
    then no changes can be made.
    """
    added_in = '1.6'

    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    policy_id = 'review_file_attachment_comment'
    model_parent_key = 'review'
    uri_template_name = 'file_attachment_comment'

    def get_queryset(self, request, review_id, *args, **kwargs):
        q = super(ReviewFileAttachmentCommentResource, self).get_queryset(
            request, *args, **kwargs)
        return q.filter(review=review_id)

    def _get_file_attachment(
        self,
        file_attachment_id: int,
        review_request: ReviewRequest,
        user: User,
    ) -> Optional[FileAttachment]:
        """Return the file attachment matching the given ID.

        Args:
            file_attachment_id (int):
                The PK of the file attechment.

            review_request (reviewboard.reviews.models.ReviewRequest):
                The review request.

            user (django.contrib.auth.models.User):
                The user making the request.

        Returns:
            reviewboard.attachments.models.FileAttachment:
            The matching file attachment, if it exists.
        """
        try:
            return FileAttachment.objects.get(pk=file_attachment_id,
                                              review_request=review_request)
        except ObjectDoesNotExist:
            pass

        draft = review_request.get_draft(user)

        if draft:
            try:
                return FileAttachment.objects.get(pk=file_attachment_id,
                                                  drafts=draft)
            except ObjectDoesNotExist:
                pass

        return None

    @webapi_check_local_site
    @webapi_login_required
    @webapi_response_errors(DOES_NOT_EXIST, INVALID_FORM_DATA,
                            PERMISSION_DENIED, NOT_LOGGED_IN)
    @webapi_request_fields(
        required=dict({
            'file_attachment_id': {
                'type': IntFieldType,
                'description': 'The ID of the file attachment being '
                               'commented on.',
            },
        }, **BaseFileAttachmentCommentResource.REQUIRED_CREATE_FIELDS),
        optional=dict({
            'diff_against_file_attachment_id': {
                'type': IntFieldType,
                'description': 'The ID of the file attachment that '
                               '``file_attachment_id`` is diffed against. The '
                               'comment applies to the diff between these two '
                               'attachments.',
                'added_in': '2.0',
            },
        }, **BaseFileAttachmentCommentResource.OPTIONAL_CREATE_FIELDS),
        allow_unknown=True
    )
    def create(self, request, file_attachment_id=None,
               diff_against_file_attachment_id=None, *args, **kwargs):
        """Creates a file comment on a review.

        This will create a new comment on a file as part of a review.
        The comment contains text only.

        Extra data can be stored later lookup. See
        :ref:`webapi2.0-extra-data` for more information.
        """
        try:
            review_request = \
                resources.review_request.get_object(request, *args, **kwargs)
            review = resources.review.get_object(request, *args, **kwargs)
        except ObjectDoesNotExist:
            return DOES_NOT_EXIST

        if not resources.review.has_modify_permissions(request, review):
            return self.get_no_access_error(request)

        file_attachment = self._get_file_attachment(
            file_attachment_id,
            review_request,
            request.user)

        if file_attachment is None:
            return INVALID_FORM_DATA, {
                'fields': {
                    'file_attachment_id': ['This is not a valid file '
                                           'attachment ID'],
                }
            }

        diff_against_file_attachment = None

        if diff_against_file_attachment_id:
            diff_against_file_attachment = self._get_file_attachment(
                diff_against_file_attachment_id,
                review_request,
                request.user)

            if diff_against_file_attachment is None:
                return INVALID_FORM_DATA, {
                    'fields': {
                        'diff_against_file_attachment_id': [
                            'This is not a valid file attachment ID'
                        ],
                    }
                }

        return self.create_comment(
            review=review,
            comments_m2m=review.file_attachment_comments,
            file_attachment=file_attachment,
            diff_against_file_attachment=diff_against_file_attachment,
            fields=('file_attachment', 'diff_against_file_attachment'),
            **kwargs)

    @webapi_check_local_site
    @webapi_login_required
    @webapi_response_errors(DOES_NOT_EXIST, NOT_LOGGED_IN, PERMISSION_DENIED)
    @webapi_request_fields(
        optional=BaseFileAttachmentCommentResource.OPTIONAL_UPDATE_FIELDS,
        allow_unknown=True
    )
    def update(self, request, *args, **kwargs):
        """Updates a file comment.

        This can update the text or region of an existing comment. It
        can only be done for comments that are part of a draft review.

        Extra data can be stored later lookup. See
        :ref:`webapi2.0-extra-data` for more information.
        """
        try:
            resources.review_request.get_object(request, *args, **kwargs)
            review = resources.review.get_object(request, *args, **kwargs)
            file_comment = self.get_object(request, *args, **kwargs)
        except ObjectDoesNotExist:
            return DOES_NOT_EXIST

        return self.update_comment(request=request,
                                   review=review,
                                   comment=file_comment,
                                   **kwargs)

    @augment_method_from(BaseFileAttachmentCommentResource)
    def delete(self, *args, **kwargs):
        """Deletes the comment.

        This will remove the comment from the review. This cannot be undone.

        Only comments on draft reviews can be deleted. Attempting to delete
        a published comment will return a Permission Denied error.

        Instead of a payload response on success, this will return :http:`204`.
        """
        pass

    @augment_method_from(BaseFileAttachmentCommentResource)
    def get_list(self, *args, **kwargs):
        """Returns the list of file comments made on a review."""
        pass


review_file_attachment_comment_resource = ReviewFileAttachmentCommentResource()
