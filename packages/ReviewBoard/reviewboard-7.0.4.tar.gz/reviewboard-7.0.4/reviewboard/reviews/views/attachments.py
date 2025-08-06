"""Views for reviewing file attachments (and legacy screenshots)."""

from __future__ import annotations

import logging
from typing import Optional, TYPE_CHECKING

from django.db.models import Q
from django.http import (Http404,
                         HttpRequest,
                         HttpResponse,
                         HttpResponseRedirect)
from django.shortcuts import get_object_or_404
from django.views.generic.base import View

from reviewboard.accounts.mixins import UserProfileRequiredViewMixin
from reviewboard.attachments.models import FileAttachment
from reviewboard.reviews.context import should_view_draft
from reviewboard.reviews.models import Screenshot
from reviewboard.reviews.ui.base import (DiffMismatchReviewUI,
                                         ReviewUI)
from reviewboard.reviews.ui.screenshot import LegacyScreenshotReviewUI
from reviewboard.reviews.views.mixins import ReviewRequestViewMixin


if TYPE_CHECKING:
    from reviewboard.reviews.models import (ReviewRequest,
                                            ReviewRequestDraft)


logger = logging.getLogger(__name__)


class _FileAttachmentViewMixin:
    """Mixin for file attachment views.

    Version Added:
        7.0
    """

    def get_file_attachment(
        self,
        *,
        review_request: ReviewRequest,
        draft: Optional[ReviewRequestDraft],
        file_attachment_id: int,
        extra_q: Optional[Q] = None,
    ) -> FileAttachment:
        """Return a file attachment accessible on the review request.

        This will check for the file attachment on the review request or
        draft, both active and inactive file attachments.

        If the file attachment could not be found, this will raise a
        :http:`404`.

        Args:
            review_request (reviewboard.reviews.models.ReviewRequest):
                The review request the file attachment is on.

            draft (reviewboard.reviews.models.ReviewRequestDraft):
                The optional draft that the file attachment may (or may not)
                be on.

            file_attachment_id (int):
                The ID of the file attachment.

            extra_q (django.db.models.Q, optional):
                Extra query arguments to include for filtering.

        Returns:
            reviewboard.attachments.models.FileAttachment:
            The file attachment matching the criteria.

        Raises:
            django.http.Http404:
                The file attachment was not found.
        """
        # Make sure the attachment returned is part of either the review
        # request or an accessible draft.
        review_request_q = (Q(review_request=review_request) |
                            Q(inactive_review_request=review_request))

        if extra_q is None:
            extra_q = Q()

        if draft is not None:
            review_request_q |= Q(drafts=draft) | Q(inactive_drafts=draft)

        return get_object_or_404(
            FileAttachment,
            Q(pk=file_attachment_id) & extra_q & review_request_q)


class DownloadFileAttachmentView(_FileAttachmentViewMixin,
                                 ReviewRequestViewMixin,
                                 View):
    """Redirects the request to the file attachment on the storage backend.

    This will check first for an accessible file attachment matching the
    URL and the user's access to the review request and draft. If found, the
    client will be redirected to the location of the file attachment in the
    storage backend.

    The redirected file may or may not be cacheable, and may only be
    accessible temporarily, depending on the backend.

    Version Added:
        7.0
    """

    def get(
        self,
        request: HttpRequest,
        *,
        file_attachment_id: int,
        **kwargs,
    ) -> HttpResponse:
        """Handle HTTP GET requests for this view.

        Args:
            request (django.http.HttpRequest):
                The HTTP request from the client.

            file_attachment_id (int):
                The revision of the file attachment to download the file from.

            **kwargs (dict):
                Keyword arguments passed to the handler.

        Returns:
            django.http.HttpResponse:
            The HTTP response to send to the client.
        """
        user = request.user
        review_request = self.review_request

        if user is not None:
            draft = review_request.get_draft(user)
        else:
            draft = None

        file_attachment = self.get_file_attachment(
            review_request=review_request,
            draft=draft,
            file_attachment_id=file_attachment_id)

        download_url: Optional[str] = None

        if request.GET.get('thumbnail'):
            # The caller requested a thumbnail. Determine the requested size.
            try:
                thumbnail_width = int(request.GET.get('width', ''))
            except ValueError:
                thumbnail_width = None

            try:
                thumbnail_height = int(request.GET.get('height', ''))
            except ValueError:
                thumbnail_height = None

            if thumbnail_width or thumbnail_height:
                download_url = file_attachment.get_raw_thumbnail_image_url(
                    width=thumbnail_width,
                    height=thumbnail_height)
        else:
            download_url = file_attachment.get_raw_download_url()

        if download_url:
            return HttpResponseRedirect(download_url)

        raise Http404


class ReviewFileAttachmentView(_FileAttachmentViewMixin,
                               ReviewRequestViewMixin,
                               UserProfileRequiredViewMixin,
                               View):
    """Displays a file attachment with a review UI."""

    def get(
        self,
        request: HttpRequest,
        file_attachment_id: int,
        file_attachment_diff_id: Optional[int] = None,
        *args,
        **kwargs,
    ) -> HttpResponse:
        """Handle a HTTP GET request.

        Args:
            request (django.http.HttpRequest):
                The HTTP request from the client.

            file_attachment_id (int):
                The ID of the file attachment to review.

            file_attachment_diff_id (int, optional):
                The ID of the file attachment to diff against.

            *args (tuple):
                Positional arguments passed to the handler.

            **kwargs (dict):
                Keyword arguments passed to the handler.

        Returns:
            django.http.HttpResponse:
            The resulting HTTP response from the handler.
        """
        review_request = self.review_request
        user = request.user
        draft = review_request.get_draft(user)

        if should_view_draft(request=request, review_request=review_request,
                             draft=draft):
            file_attachment = self.get_file_attachment(
                review_request=review_request,
                draft=draft,
                file_attachment_id=file_attachment_id)
        else:
            file_attachment = self.get_file_attachment(
                review_request=review_request,
                draft=None,
                file_attachment_id=file_attachment_id)

        diff_against_attachment: Optional[FileAttachment] = None

        review_ui_class = ReviewUI.for_object(file_attachment)

        if file_attachment_diff_id:
            diff_against_attachment = self.get_file_attachment(
                review_request=review_request,
                draft=draft,
                file_attachment_id=file_attachment_diff_id,
                extra_q=Q(
                    attachment_history=file_attachment.attachment_history
                ))

            diff_review_ui_class = ReviewUI.for_object(diff_against_attachment)

            if review_ui_class is not diff_review_ui_class:
                # The file types between the original and modified attachments
                # don't match. Just use the base ReviewUI to render, which will
                # show an error message.
                dummy_review_ui = DiffMismatchReviewUI(
                    review_request=review_request,
                    obj=file_attachment)
                dummy_review_ui.set_diff_against(diff_against_attachment)

                return dummy_review_ui.render_to_response(request)

        if (review_ui_class is None or
            (diff_against_attachment and
             not review_ui_class.supports_diffing)):
            raise Http404

        review_ui = review_ui_class(
            review_request=review_request,
            obj=file_attachment)

        if diff_against_attachment:
            review_ui.set_diff_against(diff_against_attachment)

        if not file_attachment.is_review_ui_accessible_by(user):
            raise Http404

        if (diff_against_attachment and
            not diff_against_attachment.is_review_ui_accessible_by(user)):
            raise Http404

        return review_ui.render_to_response(request)


class ReviewScreenshotView(ReviewRequestViewMixin,
                           UserProfileRequiredViewMixin,
                           View):
    """Displays a review UI for a screenshot.

    Screenshots are a legacy feature, predating file attachments. While they
    can't be created anymore, this view does allow for reviewing screenshots
    uploaded in old versions.
    """

    def get(
        self,
        request: HttpRequest,
        screenshot_id: int,
        *args,
        **kwargs,
    ) -> HttpResponse:
        """Handle a HTTP GET request.

        Args:
            request (django.http.HttpRequest):
                The HTTP request from the client.

            screenshot_id (int):
                The ID of the screenshot to review.

            *args (tuple):
                Positional arguments passed to the handler.

            **kwargs (dict):
                Keyword arguments passed to the handler.

        Returns:
            django.http.HttpResponse:
            The resulting HTTP response from the handler.
        """
        review_request = self.review_request
        draft = review_request.get_draft(request.user)

        # Make sure the screenshot returned is part of either the review
        # request or an accessible draft.
        review_request_q = (Q(review_request=review_request) |
                            Q(inactive_review_request=review_request))

        if draft:
            review_request_q |= Q(drafts=draft) | Q(inactive_drafts=draft)

        screenshot = get_object_or_404(Screenshot,
                                       Q(pk=screenshot_id) & review_request_q)
        review_ui = LegacyScreenshotReviewUI(review_request, screenshot)

        return review_ui.render_to_response(request)
