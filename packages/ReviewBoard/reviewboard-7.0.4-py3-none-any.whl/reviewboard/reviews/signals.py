"""Signals related to review requests, reviews, and replies."""

from __future__ import annotations

from django.dispatch import Signal


#: Emitted when a diffset has been uploaded to a review request.
#:
#: Version Added:
#:     5.0.7
#:
#: Args:
#:     diffset (reviewboard.diffviewer.models.DiffSet):
#:         The diffset that has been uploaded.
#:
#:     review_request_draft (reviewboard.reviews.models.ReviewRequestDraft):
#:         The review request draft that the diffset has been uploaded to.
review_request_diffset_uploaded = Signal()


#: Emitted when a review request is publishing.
#:
#: Args:
#:     user (django.contrib.auth.models.User):
#:         The user publishing the review request.
#:
#:     review_request_draft (reviewboard.reviews.models.ReviewRequestDraft):
#:         The review request draft being published.
review_request_publishing = Signal()


#: Emitted when a review request is published.
#:
#: Args:
#:     user (django.contrib.auth.models.User):
#:         The user who published the review request.
#:
#:     review_request (reviewboard.reviews.models.ReviewRequest):
#:         The review request that was published.
#:
#:     trivial (bool):
#          Whether or not the review request was published trivially or not.
#:
#:     changedesc (reviewboard.changedescs.models.ChangeDescription):
#:         The change description associated with the publish, if any.
review_request_published = Signal()


#: Emitted when a review request is about to be closed.
#:
#: Args:
#:     user (django.contrib.auth.models.User):
#:         The user closing the review request.
#:
#:     review_request (reviewboard.reviews.models.ReviewRequest):
#:         The review request being closed.
#:
#:     close_type (unicode):
#:         Describes how the review request is being closed. It is one of
#:         :py:data:`~reviewboard.reviews.models.ReviewRequest.SUBMITTED` or
#:         :py:data:`~reviewboard.reviews.models.ReviewRequest.DISCARDED`.
#:
#:     description (unicode):
#:         The provided closing description.
#:
#:     rich_text (bool):
#:         Whether or not the description is rich text (Markdown).
review_request_closing = Signal()


#: Emitted when a review request has been closed.
#:
#: Args:
#:     user (django.contrib.auth.models.User):
#:         The user who closed the review request.
#:
#:     review_request (reviewboard.reviews.models.ReviewRequest):
#:         The review request that was closed.
#:
#:     close_type (unicode):
#:         Describes how the review request was closed. It is one of
#:         :py:data:`~reviewboard.reviews.models.ReviewRequest.SUBMITTED` or
#:         :py:data:`~reviewboard.reviews.models.ReviewRequest.DISCARDED`.
#:
#:     description (unicode):
#:         The provided closing description.
#:
#:     rich_text (bool):
#:         Whether or not the description is rich text (Markdown).
review_request_closed = Signal()


#: Emitted when a review request is about to be reopened.
#:
#: Args:
#:     user (django.contrib.auth.models.User):
#:         The user re-opening the review request.
#:
#:     review_request (reviewboard.reviews.models.ReviewRequest):
#:         The review request being reopened.
review_request_reopening = Signal()


#: Emitted when a review request has been reopened.
#:
#: Args:
#:     user (django.contrib.auth.models.User):
#:         The user who re-opened the review request.
#:
#:     review_request (reviewboard.reviews.models.ReviewRequest):
#:         The review request that was reopened.
#:
#:     old_status (unicode):
#:         The old status for the review request. This will be
#:         :py:attr:`~reviewboard.reviews.models.ReviewRequest.PENDING_REVIEW`,
#:         :py:attr:`~reviewboard.reviews.models.ReviewRequest.SUBMITTED`, or
#:         :py:attr:`~reviewboard.reviews.models.ReviewRequest.DISCARDED`.
#:
#:     old_public (bool):
#:         The old public state for the review request.
review_request_reopened = Signal()


#: Emitted when a review is being published.
#:
#: Args:
#:     user (django.contrib.auth.models.User):
#:         The user publishing the review.
#:
#:     review (reviewboard.reviews.models.Review):
#:         The review that's being published.
#:
#:     to_owner_only (bool):
#:         Whether the review e-mail should be sent only to the review request
#:         submitter.
review_publishing = Signal()


#: Emitted when a Ship It is about to be revoked from a review.
#:
#: Listeners can raise a
#: :py:exc:`~reviewboard.reviews.errors.RevokeShipItError` to stop the Ship It
#: from being revoking.
#:
#: Args:
#:     user (django.contrib.auth.models.User):
#:         The user who requested to revoke the Ship It.
#:
#:     review (reviewboard.reviews.models.review.Review):
#:         The review that will have its Ship It revoked.
review_ship_it_revoking = Signal()


#: Emitted when a Ship It has been revoked from a review.
#:
#: Args:
#:     user (django.contrib.auth.models.User):
#:         The user who revoked the Ship It.
#:
#:     review (reviewboard.reviews.models.review.Review):
#:         The review that had its Ship It revoked.
review_ship_it_revoked = Signal()


#: Emitted when a review has been published.
#:
#: Args:
#:     user (django.contrib.auth.models.User):
#:         The user who published the review.
#:
#:     review (reviewboard.reviews.models.Review):
#:         The review that was published.
#:
#:     to_owner_only (bool):
#:         Whether the review e-mail should be sent only to the review request
#:         submitter.
#:
#:     trivial (bool):
#:         Whether to skip e-mail notifications entirely.
#:
#:     request (django.http.HttpRequest):
#:         The request object if the review was published from an HTTP request.
review_published = Signal()


#: Emitted when a reply to a review is being published.
#:
#: Args:
#:     user (django.contrib.auth.models.User):
#:         The user publishing the reply.
#:
#:     review (reviewboard.reviews.models.Review):
#:         The reply that's being published.
reply_publishing = Signal()


#: Emitted when a reply to a review has ben published.
#:
#: Args:
#:     user (django.contrib.auth.models.User):
#:         The user who published the reply.
#:
#:     review (reviewboard.reviews.models.Review):
#:         The reply that was published.
#:
#:     trivial (bool):
#:         Whether the reply was considered trivial.
reply_published = Signal()


#: Emitted when a StatusUpdate should run or re-run.
#:
#: Version Changed:
#:     5.0.3:
#:     Added the ``config`` argument.
#:
#: Args:
#:     status_update (reviewboard.reviews.models.StatusUpdate):
#:         The StatusUpdate associated with the tool that should be run.
#:
#:     config (reviewboard.integrations.models.IntegrationConfig):
#:         The associated integration configuration being run.
#:
#:         If provided and set, this should be used instead of scanning for
#:         a matching configuration.
#:
#:         Version Added:
#:             5.0.3
status_update_request_run = Signal()
