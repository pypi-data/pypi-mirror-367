"""Definitions for the review request detail view."""

from __future__ import annotations

import hashlib
import logging
from collections import Counter, defaultdict
from datetime import datetime, timezone
from itertools import chain
from typing import (Any, ClassVar, Final, Iterable, Mapping, Optional,
                    Sequence, TYPE_CHECKING, Type, TypeVar, Union)

from django.db.models import Model, Q
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from djblets.registries.registry import (ALREADY_REGISTERED,
                                         ATTRIBUTE_REGISTERED,
                                         NOT_REGISTERED)
from djblets.util.dates import get_latest_timestamp
from djblets.util.decorators import cached_property

from reviewboard.diffviewer.models import DiffCommit
from reviewboard.registries.registry import OrderedRegistry
from reviewboard.reviews.builtin_fields import (CommitListField,
                                                ReviewRequestPageDataMixin)
from reviewboard.reviews.context import should_view_draft
from reviewboard.reviews.features import status_updates_feature
from reviewboard.reviews.fields import get_review_request_fieldsets
from reviewboard.reviews.models import (BaseComment,
                                        Comment,
                                        FileAttachmentComment,
                                        Review,
                                        ReviewRequest,
                                        ScreenshotComment,
                                        StatusUpdate)

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django.http import HttpRequest
    from django.template.context import Context
    from django.utils.safestring import SafeString
    from djblets.util.typing import JSONDict

    from reviewboard.changedescs.models import ChangeDescription
    from reviewboard.reviews.models import ReviewRequestDraft


logger = logging.getLogger(__name__)


_TModel = TypeVar('_TModel', bound=Model)


class ReviewRequestPageData:
    """Data for the review request page.

    The review request detail page needs a lot of data from the database, and
    going through the standard model relations will result in a lot more
    queries than necessary. This class bundles all that data together and
    handles pre-fetching and re-associating as necessary to limit the required
    number of queries.

    All of the attributes within the class may not be available until both
    :py:meth:`query_data_pre_etag` and :py:meth:`query_data_post_etag` are
    called.

    This object is not meant to be public API, and may change at any time. You
    should not use it in extension code.

    Attributes:
        body_bottom_replies (dict):
            A mapping from a top-level review ID to a list of the
            :py:class:`~reviewboard.reviews.models.Review` objects which reply
            to it.

        body_top_replies (dict):
            A mapping from a top-level review ID to a list of the
            :py:class:`~reviewboard.reviews.models.Review` objects which reply
            to it.

        review_comments (dict):
            A dictionary of comments across all reviews. The keys are
            :py:class:`~reviewboard.reviews.models.review.Review` IDs and the
            values are lists of comments.

        draft_body_top_replies (dict):
            A dictionary of draft replies to ``body_top`` fields across all
            reviews. The keys are are
            :py:class:`~reviewboard.reviews.models.review.Review` IDs that are
            being replied to and the values are lists of replies.

        draft_body_bottom_replies (dict):
            A dictionary of draft replies to ``body_bottom`` fields across all
            reviews. The keys are are
            :py:class:`~reviewboard.reviews.models.review.Review` IDs that are
            being replied to and the values are lists of replies.

        draft_reply_comments (dict):
            A dictionary of draft reply comments across all reviews. The keys
            are :py:class:`~reviewboard.reviews.models.review.Review` IDs that
            are being replied to and the values are lists of reply comments.

        changedescs (list of reviewboard.changedescs.models.ChangeDescription):
            All the change descriptions to be shown on the page.

        diffsets (list of reviewboard.diffviewer.models.diffset.DiffSet):
            All of the diffsets associated with the review request.

        diffsets_by_id (dict):
            A mapping from ID to
            :py:class:`~reviewboard.diffviewer.models.diffset.DiffSet`.

        draft (reviewboard.reviews.models.ReviewRequestDraft):
            The active draft of the review request, if any. May be ``None``.

        active file_attachments (list of reviewboard.attachments.models.
                                 FileAttachment):
            All the active file attachments associated with the review request.

        all_file_attachments (list of reviewboard.attachments.models.
                              FileAttachment):
            All the file attachments associated with the review request.

        file_attachments_by_id (dict):
            A mapping from ID to
            :py:class:`~reviewboard.attachments.models.FileAttachment`

        issues (list of reviewboard.reviews.models.BaseComment):
            A list of all the comments (of all types) which are marked as
            issues.

        issue_counts (dict):
            A dictionary storing counts of the various issue states throughout
            the page.

        latest_changedesc_timestamp (datetime.datetime):
            The timestamp of the most recent change description on the page.

        latest_review_timestamp (datetime.datetime):
            The timestamp of the most recent review on the page.

        latest_timestamps_by_review_id (dict):
            A mapping from top-level review ID to the latest timestamp of the
            thread.

        active_screenshots (list of reviewboard.reviews.models.screenshots.
                            Screenshot):
            All the active screenshots associated with the review request.

        all_screenshots (list of reviewboard.reviews.models.Screenshot):
            All the screenshots associated with the review request.

        screenshots_by_id (dict):
            A mapping from ID to
            :py:class:`~reviewboard.reviews.models.Screenshot`.

        all_status_updates (list of reviewboard.reviews.models.
                            status_updates.StatusUpdate):
            All status updates recorded for the review request.

        initial_status_updates (list of reviewboard.reviews.models.
                                status_updates.StatusUpdate):
            The status updates recorded on the initial publish of the
            review request.

        change_status_updates (dict):
            The status updates associated with change descriptions. Each key
            in the dictionary is a
            :py:class:`~reviewboard.changedescs.models.ChangeDescription` ID,
            and each key is a list of
            :py:class:`reviewboard.reviews.models. status_updates.StatusUpdate`
            instances.

        status_updates_enabled (bool):
            Whether the status updates feature is enabled for this
            review request. This does not necessarily mean that there are
            status updates on the review request.
    """

    ######################
    # Instance variables #
    ######################

    #: The current HTTP request.
    request: HttpRequest

    #: The review request.
    review_request: ReviewRequest

    #: The object to use for showing the review request data.
    review_request_details: Optional[Union[ReviewRequest, ReviewRequestDraft]]

    #: All reviews to be shown on the page.
    #:
    #: This includes any draft reviews owned by the requesting user, but not
    #: drafts owned by others.
    reviews: list[Review]

    #: A mapping from the review ID to the review object.
    reviews_by_id: dict[int, Review]

    #: The timestamp of the most recent comment, for the issue summary table.
    #:
    #: Version Added:
    #:     6.0
    latest_issue_timestamp: Optional[datetime]

    def __init__(
        self,
        review_request: ReviewRequest,
        request: HttpRequest,
        last_visited: Optional[datetime] = None,
        entry_classes: Optional[Sequence[BaseReviewRequestPageEntry]] = None,
    ) -> None:
        """Initialize the data object.

        Args:
            review_request (reviewboard.reviews.models.ReviewRequest):
                The review request.

            request (django.http.HttpRequest):
                The HTTP request object.

            last_visited (datetime.datetime, optional):
                The date/time when the user last visited the review request.

            entry_classes (list of BaseReviewRequestPageEntry, optional):
                The list of entry classes that should be used for data
                generation. If not provided, all registered entry classes
                will be used.
        """
        self.review_request = review_request
        self.request = request
        self.last_visited = last_visited
        self.entry_classes = entry_classes or list(entry_registry)

        # These are populated in query_data_pre_etag().
        self.reviews = []
        self.changedescs = []
        self.diffsets = []
        self.commits_by_diffset_id = {}
        self.diffsets_by_id = {}
        self.all_status_updates = []
        self.latest_review_timestamp = None
        self.latest_changedesc_timestamp = None
        self.draft = None

        # These are populated in query_data_post_etag().
        self.initial_status_updates = []
        self.change_status_updates = {}
        self.reviews_by_id = {}
        self.latest_timestamps_by_review_id = {}
        self.latest_issue_timestamp = None
        self.body_top_replies = defaultdict(list)
        self.body_bottom_replies = defaultdict(list)
        self.review_request_details = None
        self.active_file_attachments = []
        self.all_file_attachments = []
        self.file_attachments_by_id = {}
        self.active_screenshots = []
        self.all_comments = []
        self.all_screenshots = []
        self.screenshots_by_id = {}
        self.review_comments = {}
        self.draft_reply_comments = {}
        self.draft_body_top_replies = defaultdict(list)
        self.draft_body_bottom_replies = defaultdict(list)
        self.issues = []
        self.issue_counts = {
            'total': 0,
            'open': 0,
            'resolved': 0,
            'dropped': 0,
            'verifying': 0,
        }

        self.status_updates_enabled = status_updates_feature.is_enabled(
            local_site=review_request.local_site)

        self._needs_draft = False
        self._needs_reviews = False
        self._needs_changedescs = False
        self._needs_status_updates = False
        self._needs_file_attachments = False
        self._needs_screenshots = False

        # There's specific entries being used for the data collection.
        # Loop through them and determine what sets of data we need.
        for entry_cls in self.entry_classes:
            self._needs_draft = self._needs_draft or entry_cls.needs_draft
            self._needs_reviews = (self._needs_reviews or
                                   entry_cls.needs_reviews)
            self._needs_changedescs = (self._needs_changedescs or
                                       entry_cls.needs_changedescs)
            self._needs_status_updates = (self._needs_status_updates or
                                          entry_cls.needs_status_updates)
            self._needs_file_attachments = (self._needs_file_attachments or
                                            entry_cls.needs_file_attachments)
            self._needs_screenshots = (self._needs_screenshots or
                                       entry_cls.needs_screenshots)

    def query_data_pre_etag(self) -> None:
        """Perform initial queries for the page.

        This method will populate only the data needed to compute the ETag. We
        avoid everything else until later so as to do the minimum amount
        possible before reporting to the client that they can just use their
        cached copy.
        """
        user = self.request.user
        review_request = self.review_request

        # Query for all the reviews that should be shown on the page (either
        # ones which are public or draft reviews owned by the current user).
        reviews_query = Q(public=True)

        if user.is_authenticated:
            reviews_query |= Q(user_id=user.pk)

        if self._needs_reviews or self._needs_status_updates:
            self.reviews = list(
                review_request.reviews
                .filter(reviews_query)
                .order_by('-timestamp')
                .select_related('user', 'user__profile')
            )

        if len(self.reviews) == 0:
            self.latest_review_timestamp = \
                datetime.fromtimestamp(0, timezone.utc)
        else:
            self.latest_review_timestamp = self.reviews[0].timestamp

        # Get all the public ChangeDescriptions.
        if self._needs_changedescs:
            self.changedescs = list(
                review_request.changedescs.filter(public=True))

        if self.changedescs:
            self.latest_changedesc_timestamp = self.changedescs[0].timestamp

        # Get the active draft (if any).
        if self._needs_draft:
            draft = review_request.get_draft(user=user)

            if not should_view_draft(request=self.request,
                                     review_request=review_request,
                                     draft=draft):
                draft = None

            if draft:
                self.draft = draft

        # Get diffsets.
        if self._needs_reviews:
            self.diffsets = self.review_request.get_diffsets()
            self.diffsets_by_id = self._build_id_map(self.diffsets)

        # Get all status updates.
        if self.status_updates_enabled and self._needs_status_updates:
            self.all_status_updates = list(
                self.review_request.status_updates.order_by('summary'))

    def query_data_post_etag(self) -> None:
        """Perform remaining queries for the page.

        This method will populate everything else needed for the display of the
        review request page other than that which was required to compute the
        ETag.
        """
        self.reviews_by_id = self._build_id_map(self.reviews)

        for status_update in self.all_status_updates:
            if status_update.review_id is not None:
                review = self.reviews_by_id[status_update.review_id]
                review.status_update = status_update
                status_update.review = review

            if status_update.change_description_id:
                self.change_status_updates.setdefault(
                    status_update.change_description_id,
                    []).append(status_update)
            else:
                self.initial_status_updates.append(status_update)

        for review in self.reviews:
            review._body_top_replies = []
            review._body_bottom_replies = []

            body_reply_info = (
                (review.body_top_reply_to_id,
                 self.body_top_replies,
                 self.draft_body_top_replies),
                (review.body_bottom_reply_to_id,
                 self.body_bottom_replies,
                 self.draft_body_bottom_replies),
            )

            for reply_to_id, replies, draft_replies in body_reply_info:
                if reply_to_id is not None:
                    replies[reply_to_id].append(review)

                    if not review.public:
                        draft_replies[reply_to_id].append(review)

            # Find the latest reply timestamp for each top-level review.
            parent_id = review.base_reply_to_id

            if parent_id is not None:
                new_timestamp = review.timestamp.replace(tzinfo=timezone.utc)

                if parent_id in self.latest_timestamps_by_review_id:
                    old_timestamp = \
                        self.latest_timestamps_by_review_id[parent_id]

                    if old_timestamp < new_timestamp:
                        self.latest_timestamps_by_review_id[parent_id] = \
                            new_timestamp
                else:
                    self.latest_timestamps_by_review_id[parent_id] = \
                        new_timestamp

            # We've already attached all the status updates above, but
            # any reviews that don't have status updates can still result
            # in a query. We want to null those out.
            if not hasattr(review, '_status_update_cache'):
                review._status_update_cache = None

        # Link up all the review body replies.
        for reply_id, replies in self.body_top_replies.items():
            self.reviews_by_id[reply_id]._body_top_replies = reversed(replies)

        for reply_id, replies in self.body_bottom_replies.items():
            self.reviews_by_id[reply_id]._body_bottom_replies = \
                reversed(replies)

        if should_view_draft(request=self.request,
                             review_request=self.review_request,
                             draft=self.draft):
            review_request_details = self.draft or self.review_request
        else:
            review_request_details = self.review_request

        self.review_request_details = review_request_details

        # Get all the file attachments and screenshots.
        #
        # Note that we fetch both active and inactive file attachments and
        # screenshots. We do this because even though they've been removed,
        # they still will be rendered in change descriptions.
        if self._needs_file_attachments or self._needs_reviews:
            self.active_file_attachments = \
                list(review_request_details.get_file_attachments())
            self.all_file_attachments = (
                self.active_file_attachments + list(
                    review_request_details
                    .get_inactive_file_attachments()))
            self.file_attachments_by_id = \
                self._build_id_map(self.all_file_attachments)

            for attachment in self.all_file_attachments:
                attachment._comments = []

        if self._needs_screenshots or self._needs_reviews:
            self.active_screenshots = \
                list(review_request_details.get_screenshots())
            self.all_screenshots = (
                self.active_screenshots +
                list(review_request_details.get_inactive_screenshots()))
            self.screenshots_by_id = self._build_id_map(self.all_screenshots)

            for screenshot in self.all_screenshots:
                screenshot._comments = []

        if self.reviews:
            review_ids = list(self.reviews_by_id.keys())

            for review_field_name, key, ordering in (
                ('general_comments',
                 'general_comments',
                 ('generalcomment__timestamp',)),
                ('screenshot_comments',
                 'screenshot_comments',
                 ('screenshotcomment__timestamp',)),
                ('file_attachment_comments',
                 'file_attachment_comments',
                 ('fileattachmentcomment__timestamp',)),
                ('comments',
                 'diff_comments',
                 ('comment__filediff',
                  'comment__first_line',
                  'comment__timestamp'))):
                # Due to mistakes in how we initially made the schema, we have
                # a ManyToManyField in between comments and reviews, instead of
                # comments having a ForeignKey to the review. This makes it
                # difficult to easily go from a comment to a review ID.
                #
                # The solution to this is to not query the comment objects, but
                # rather the through table. This will let us grab the review
                # and comment in one go, using select_related.
                #
                # Note that we must always order it by something or we'll get
                # the indexed order of the through table's entry, which may
                # not align with the correct order of comments.
                related_field = Review._meta.get_field(review_field_name)
                comment_field_name = related_field.m2m_reverse_field_name()
                through = related_field.remote_field.through
                objs = list(
                    through.objects.filter(review__in=review_ids)
                    .select_related()
                    .order_by(*ordering)
                )

                # We do two passes. One to build a mapping, and one to actually
                # process comments.
                comment_map = {}

                for obj in objs:
                    comment = getattr(obj, comment_field_name)
                    comment._type = key
                    comment._replies = []
                    comment_map[comment.pk] = comment

                for obj in objs:
                    comment = getattr(obj, comment_field_name)

                    self.all_comments.append(comment)

                    # Short-circuit some object fetches for the comment by
                    # setting some internal state on them.
                    assert obj.review_id in self.reviews_by_id
                    review = self.reviews_by_id[obj.review_id]
                    comment.review_obj = review
                    comment._review = review
                    comment._review_request = self.review_request

                    # If the comment has an associated object (such as a file
                    # attachment) that we've already fetched, attach it to
                    # prevent future queries.
                    if isinstance(comment, FileAttachmentComment):
                        attachment_id = comment.file_attachment_id
                        f = self.file_attachments_by_id[attachment_id]
                        comment.file_attachment = f
                        f._comments.append(comment)

                        diff_against_id = \
                            comment.diff_against_file_attachment_id

                        if diff_against_id is not None:
                            f = self.file_attachments_by_id[diff_against_id]
                            comment.diff_against_file_attachment = f
                    elif isinstance(comment, ScreenshotComment):
                        screenshot = \
                            self.screenshots_by_id[comment.screenshot_id]
                        comment.screenshot = screenshot
                        screenshot._comments.append(comment)

                    # We've hit legacy database cases where there were entries
                    # that weren't a reply, and were just orphaned. Check and
                    # ignore anything we don't expect.
                    is_reply = review.is_reply()

                    if is_reply == comment.is_reply():
                        if is_reply:
                            replied_comment = comment_map[comment.reply_to_id]
                            replied_comment._replies.append(comment)

                            if not review.public:
                                self.draft_reply_comments.setdefault(
                                    review.base_reply_to_id, []).append(
                                        comment)
                        else:
                            self.review_comments.setdefault(
                                review.pk, []).append(comment)

                    if review.public and comment.issue_opened:
                        status_key = comment.issue_status_to_string(
                            comment.issue_status)

                        # Both "verifying" states get lumped together in the
                        # same section in the issue summary table.
                        if status_key in ('verifying-resolved',
                                          'verifying-dropped'):
                            status_key = 'verifying'

                        self.issue_counts[status_key] += 1
                        self.issue_counts['total'] += 1
                        self.issues.append(comment)

        if self.all_comments:
            self.latest_issue_timestamp = max(
                comment.timestamp
                for comment in self.all_comments)
        else:
            self.latest_issue_timestamp = \
                datetime.fromtimestamp(0, timezone.utc)

        if self.review_request.created_with_history:
            pks = [diffset.pk for diffset in self.diffsets]

            if self.draft and self.draft.diffset_id is not None:
                pks.append(self.draft.diffset_id)

            self.commits_by_diffset_id = DiffCommit.objects.by_diffset_ids(pks)

    def get_entries(
        self,
    ) -> Mapping[str, Sequence[BaseReviewRequestPageEntry]]:
        """Return all entries for the review request page.

        This will create and populate entries for the page (based on the
        entry classes provided in :py:attr:`entry_classes`). The entries can
        then be injected into the review request page.

        Returns:
            dict:
            A dictionary of entries. This has ``initial`` and ``main`` keys,
            corresponding to
            :py:attr:`BaseReviewRequestPageEntry.ENTRY_POS_INITIAL` and
            :py:attr:`BaseReviewRequestPageEntry.ENTRY_POS_MAIN` entries,
            respectively.

            The ``initial`` entries are sorted in registered entry order,
            while the ``main`` entries are sorted in timestamp order.
        """
        initial_entries: list[BaseReviewRequestPageEntry] = []
        main_entries: list[BaseReviewRequestPageEntry] = []

        for entry_cls in self.entry_classes:
            new_entries = entry_cls.build_entries(self)

            if new_entries is not None:
                if entry_cls.entry_pos == entry_cls.ENTRY_POS_INITIAL:
                    initial_entries += new_entries
                elif entry_cls.entry_pos == entry_cls.ENTRY_POS_MAIN:
                    main_entries += new_entries

        for entry in initial_entries:
            entry.finalize()

        for entry in main_entries:
            entry.finalize()

        # Sort all the main entries (such as reviews and change descriptions)
        # by their timestamp. We don't sort the initial entries, which are
        # displayed in registration order.
        main_entries.sort(key=lambda item: item.added_timestamp)

        return {
            'initial': initial_entries,
            'main': main_entries,
        }

    def _build_id_map(
        self,
        objects: Sequence[_TModel],
    ) -> Mapping[int, _TModel]:
        """Return an ID map from a list of objects.

        Args:
            objects (list):
                A list of objects queried via django.

        Returns:
            dict:
            A dictionary mapping each ID to the resulting object.
        """
        return {
            obj.pk: obj
            for obj in objects
        }


class BaseReviewRequestPageEntry:
    """An entry on the review detail page.

    This contains backend logic and frontend templates for one of the boxes
    that appears below the main review request box on the review request detail
    page.
    """

    #: An initial entry appearing above the review-like boxes.
    ENTRY_POS_INITIAL: Final[int] = 1

    #: An entry appearing in the main area along with review-like boxes.
    ENTRY_POS_MAIN: Final[int] = 2

    #: The ID used for entries of this type.
    entry_type_id: ClassVar[Optional[str]] = None

    #: The type of entry on the page.
    #:
    #: By default, this is a box type, which will appear along with other
    #: reviews and change descriptions.
    entry_pos: ClassVar[int] = ENTRY_POS_MAIN

    #: Whether the entry needs a review request draft to be queried.
    #:
    #: If set, :py:attr:`ReviewRequestPageData.draft` will be set (if a draft
    #: exists).
    needs_draft: ClassVar[bool] = False

    #: Whether the entry needs reviews, replies, and comments to be queried.
    #:
    #: If set, :py:attr:`ReviewRequestPageData.reviews`,
    #: :py:attr:`ReviewRequestPageData.diffsets`,
    #: :py:attr:`ReviewRequestPageData.diffsets_by_id`,
    #: :py:attr:`ReviewRequestPageData.active_file_attachments`,
    #: :py:attr:`ReviewRequestPageData.all_file_attachments`,
    #: :py:attr:`ReviewRequestPageData.file_attachments_by_id`,
    #: :py:attr:`ReviewRequestPageData.active_file_screenshots`,
    #: :py:attr:`ReviewRequestPageData.all_file_screenshots`, and
    #: :py:attr:`ReviewRequestPageData.file_screenshots_by_id` will be set.
    needs_reviews: ClassVar[bool] = False

    #: Whether the entry needs change descriptions to be queried.
    #:
    #: If set, :py:attr:`ReviewRequestPageData.changedescs` will be queried.
    needs_changedescs: ClassVar[bool] = False

    #: Whether the entry needs status updates-related data to be queried.
    #:
    #: This will also fetch the reviews, but will not automatically fetch any
    #: comments or other related data. For that, set :py:attr:`needs_reviews`.
    #:
    #: If set, :py:attr:`ReviewRequestPageData.reviews`,
    #: If set, :py:attr:`ReviewRequestPageData.all_status_updates`,
    #: If set, :py:attr:`ReviewRequestPageData.initial_status_updates`, and
    #: If set, :py:attr:`ReviewRequestPageData.change_status_updates` will be
    #: set.
    needs_status_updates: ClassVar[bool] = False

    #: Whether the entry needs file attachment data to be queried.
    #:
    #: If set, :py:attr:`ReviewRequestPageData.active_file_attachments`,
    #: :py:attr:`ReviewRequestPageData.all_file_attachments`, and
    #: :py:attr:`ReviewRequestPageData.file_attachments_by_id` will be set.
    needs_file_attachments: ClassVar[bool] = False

    #: Whether the entry needs screenshot data to be queried.
    #:
    #: Most entries should never need this, as screenshots are deprecated.
    #:
    #: If set, :py:attr:`ReviewRequestPageData.active_screenshots`,
    #: :py:attr:`ReviewRequestPageData.all_screenshots`, and
    #: :py:attr:`ReviewRequestPageData.screenshots_by_id` will be set.
    needs_screenshots: ClassVar[bool] = False

    #: The template to render for the HTML.
    template_name: ClassVar[Optional[str]] = None

    #: The template to render for any JavaScript.
    js_template_name: ClassVar[Optional[str]] = 'reviews/entries/entry.js'

    #: The name of the JavaScript Backbone.Model class for this entry.
    js_model_class: ClassVar[Optional[str]] = 'RB.ReviewRequestPage.Entry'

    #: The name of the JavaScript Backbone.View class for this entry.
    js_view_class: ClassVar[Optional[str]] = 'RB.ReviewRequestPage.EntryView'

    #: Whether this entry has displayable content.
    #:
    #: This can be overridden as a property to calculate whether to render
    #: the entry, or disabled altogether.
    has_content: ClassVar[bool] = True

    ######################
    # Instance variables #
    ######################

    #: The timestamp of the entry.
    #:
    #: This represents the added time for the entry, and is used for sorting
    #: the entry in the page. This timestamp should never change.
    added_timestamp: Optional[datetime]

    #: The user to display an avatar for.
    #:
    #: This can be ``None``, in which case no avatar will be displayed.
    #: Templates can also override the avatar HTML instead of using this.
    avatar_user: Optional[User]

    #: The ID of the entry.
    #:
    #: This will be unique across this type of entry, and may refer to a
    #: database object ID.
    entry_id: str

    #: The timestamp when the entry was last updated.
    #:
    #: This reflects new updates or activity on the entry.
    updated_timestamp: Optional[datetime]

    @classmethod
    def build_entries(
        cls,
        data: ReviewRequestPageData,
    ) -> Iterable[BaseReviewRequestPageEntry]:
        """Generate entry instances from review request page data.

        Subclasses should override this to yield any entries needed, based on
        the page data.

        Args:
            data (ReviewRequestPageData):
                The data used for the entries on the page.

        Yields:
            BaseReviewRequestPageEntry:
            An entry to include on the page.
        """

    @classmethod
    def build_etag_data(
        cls,
        data: ReviewRequestPageData,
        entry: Optional[BaseReviewRequestPageEntry] = None,
        **kwargs,
    ) -> str:
        """Build ETag data for the entry.

        This will be incorporated into the ETag for the page.

        Version Changed:
            4.0.4:
            Added ``entry`` and ``**kwargs`` arguments.

        Args:
            data (ReviewRequestPageData):
                The computed data (pre-ETag) for the page.

            entry (BaseReviewRequestPageEntry, optional):
                A specific entry to build ETags for.

            **kwargs (dict, unused):
                Additional keyword arguments for future expansion.

        Returns:
            str:
            The ETag data for the entry.
        """
        return ''

    @cached_property
    def collapsed(self) -> bool:
        """Whether the entry is collapsed.

        This will consist of a cached value computed from
        :py:meth:`calculate_collapsed`. Subclasses should override that
        method.
        """
        return self.calculate_collapsed()

    def __init__(
        self,
        data: ReviewRequestPageData,
        entry_id: str,
        added_timestamp: Optional[datetime],
        updated_timestamp: Optional[datetime] = None,
        avatar_user: Optional[User] = None,
    ) -> None:
        """Initialize the entry.

        Args:
            data (ReviewRequestPageData):
                The computed data for the page.

            entry_id (str):
                The ID of the entry. This must be unique across this type
                of entry, and may refer to a database object ID.

            added_timestamp (datetime.datetime):
                The timestamp of the entry. This represents the added time
                for the entry, and is used for sorting the entry in the page.
                This timestamp should never change.

            updated_timestamp (datetime.datetime, optional):
                The timestamp when the entry was last updated. This should
                reflect new updates or activity on the entry.

            avatar_user (django.contrib.auth.models.User, optional):
                The user to display an avatar for. This can be ``None``, in
                which case no avatar will be displayed. Templates can also
                override the avatar HTML instead of using this.
        """
        self.data = data
        self.entry_id = entry_id
        self.added_timestamp = added_timestamp
        self.updated_timestamp = updated_timestamp or added_timestamp
        self.avatar_user = avatar_user

    def __repr__(self) -> str:
        """Return a string representation for this entry.

        Returns:
            str:
            A string representation for the entry.
        """
        return (
            f'{self.__class__.__name__}('
            f'entry_type_id={self.entry_type_id}, '
            f'entry_id={self.entry_id}, '
            f'added_timestamp={self.added_timestamp}, '
            f'updated_timestamp={self.updated_timestamp}, '
            f'collapsed={self.collapsed})'
        )

    def is_entry_new(
        self,
        last_visited: datetime,
        user: User,
        **kwargs,
    ) -> bool:
        """Return whether the entry is new, from the user's perspective.

        By default, this compares the last visited time to the timestamp
        on the object. Subclasses can override this to provide additional
        logic.

        Args:
            last_visited (datetime.datetime):
                The last visited timestamp.

            user (django.contrib.auth.models.User):
                The user viewing the page.

            **kwargs (dict):
                Additional keyword arguments.

        Returns:
            bool:
            ``True`` if the entry will be shown as new. ``False`` if it
            will be shown as an existing entry.
        """
        return (self.added_timestamp is not None and
                last_visited < self.added_timestamp)

    def calculate_collapsed(self) -> bool:
        """Calculate whether the entry should currently be collapsed.

        By default, this will collapse the entry if the last update is older
        than the last time the user visited the entry and older than the last
        Change Description (or there isn't one on the page yet).

        Subclasses can augment or replace this logic as needed.

        Returns:
            bool:
            ``True`` if the entry should be collapsed. ``False`` if it should
            be expanded.
        """
        data = self.data

        return bool(
            self.updated_timestamp is not None and

            # Collapse if older than the most recent review request
            # change and there's no recent activity.
            data.latest_changedesc_timestamp and
            self.updated_timestamp < data.latest_changedesc_timestamp and

            # Collapse if the page was previously visited and this entry is
            # older than the last visited time.
            data.last_visited and self.updated_timestamp < data.last_visited
        )

    def get_dom_element_id(self) -> str:
        """Return the ID used for the DOM element for this entry.

        By default, this returns :py:attr:`entry_type_id` and
        :py:attr:`entry_id` concatenated. Subclasses should override this if
        they need something custom.

        Returns:
            str:
            The ID used for the element.
        """
        return f'{self.entry_type_id}{self.entry_id}'

    def get_js_model_data(self) -> JSONDict:
        """Return data to pass to the JavaScript Model during instantiation.

        The data returned from this function will be provided to the model
        when constructed.

        Returns:
            dict:
            A dictionary of attributes to pass to the Model instance. By
            default, it will be empty.
        """
        return {}

    def get_js_view_data(self) -> JSONDict:
        """Return data to pass to the JavaScript View during instantiation.

        The data returned from this function will be provided to the view when
        constructed.

        Returns:
            dict:
            A dictionary of options to pass to the View instance. By
            default, it will be empty.
        """
        return {}

    def get_extra_context(
        self,
        request: HttpRequest,
        context: Context,
    ) -> dict[str, Any]:
        """Return extra template context for the entry.

        Subclasses can override this to provide additional context needed by
        the template for the page. By default, this returns an empty
        dictionary.

        Args:
            request (django.http.HttpRequest):
                The HTTP request from the client.

            context (django.template.context.Context):
                The existing template context on the page.

        Returns:
            dict:
            Extra context to use for the entry's template.
        """
        return {}

    def render_to_string(
        self,
        request: HttpRequest,
        context: Context,
    ) -> SafeString:
        """Render the entry to a string.

        If the entry doesn't have a template associated, or doesn't have
        any content (as determined by :py:attr:`has_content`), then this
        will return an empty string.

        Args:
            request (django.http.HttpRequest):
                The HTTP request from the client.

            context (django.template.context.Context):
                The existing template context on the page.

        Returns:
            django.utils.safestring.SafeString:
            The resulting HTML for the entry.
        """
        if not self.template_name or not self.has_content:
            return mark_safe('')

        user = request.user
        last_visited = context.get('last_visited')

        new_context = context.flatten()

        try:
            new_context.update({
                'entry': self,
                'entry_is_new': (
                    user.is_authenticated and
                    last_visited is not None and
                    self.is_entry_new(last_visited=last_visited,
                                      user=user)),
                'show_entry_statuses_area': (
                    self.entry_pos !=
                    BaseReviewRequestPageEntry.ENTRY_POS_INITIAL),
            })
            new_context.update(self.get_extra_context(request, context))
        except Exception as e:
            logger.exception('Error generating template context for %s '
                             '(ID=%s): %s',
                             self.__class__.__name__, self.entry_id, e,
                             extra={'request': request})
            return mark_safe('')

        try:
            return render_to_string(template_name=self.template_name,
                                    context=new_context,
                                    request=request)
        except Exception as e:
            logger.exception('Error rendering template for %s (ID=%s): %s',
                             self.__class__.__name__, self.entry_id, e,
                             extra={'request': request})
            return mark_safe('')

    def finalize(self) -> None:
        """Perform final computations after all comments have been added."""


if TYPE_CHECKING:
    ReviewEntryMixinParent = BaseReviewRequestPageEntry
else:
    ReviewEntryMixinParent = object


class ReviewEntryMixin(ReviewEntryMixinParent):
    """Mixin to provide functionality for entries containing reviews."""

    def is_review_collapsed(
        self,
        review: Review,
    ) -> bool:
        """Return whether a review should be collapsed.

        A review is collapsed if all the following conditions are true:

        * There are no issues currently waiting to be resolved.
        * There are no draft replies to any comments or the body fields.
        * The review has not been seen since the latest activity on it
          (or seen at all).

        Args:
            review (reviewboard.reviews.models.review.Review):
                The review to compute the collapsed state for.

        Returns:
            bool:
            ``True`` if the review should be collapsed. ``False`` if not.
        """
        data = self.data
        latest_reply_timestamp = \
            data.latest_timestamps_by_review_id.get(review.pk)

        has_comments_with_issues = any(
            (comment.issue_opened and
             comment.issue_status in (comment.OPEN,
                                      comment.VERIFYING_RESOLVED,
                                      comment.VERIFYING_DROPPED))
            for comment in data.review_comments.get(review.pk, [])
        )

        return bool(
            # Reviews containing comments with open issues should never be
            # collapsed.
            not has_comments_with_issues and

            # Draft reviews with replies should never be collapsed.
            not data.draft_body_top_replies.get(review.pk) and
            not data.draft_body_bottom_replies.get(review.pk) and
            not data.draft_reply_comments.get(review.pk) and

            # Don't collapse unless the user has visited the page before
            # and the review is older than their last visit.
            data.last_visited and (
                review.timestamp < data.last_visited and
                (not latest_reply_timestamp or
                 latest_reply_timestamp < data.last_visited)
            )
        )

    def serialize_review_js_model_data(
        self,
        review: Review,
    ) -> JSONDict:
        """Serialize information on a review for JavaScript models.

        Args:
            review (reviewboard.reviews.models.review.Review):
                The review to serialize.

        Returns:
            dict:
            The serialized data for the JavaScript model.
        """
        return {
            'authorName': review.user.get_profile().get_display_name(
                viewing_user=self.data.request.user),
            'id': review.pk,
            'shipIt': review.ship_it,
            'public': True,
            'bodyTop': review.body_top,
            'bodyBottom': review.body_bottom,
        }


class DiffCommentsSerializerMixin:
    """Mixin to provide diff comment data serialization."""

    def serialize_diff_comments_js_model_data(
        self,
        diff_comments: Iterable[Comment],
    ) -> list[tuple[str, str]]:
        """Serialize information on diff comments for JavaScript models.

        Args:
            diff_comments (list of reviewboard.reviews.models.Comment):
                The list of comments to serialize.

        Returns:
            list of tuple:
            The serialized data for the JavaScript model.
        """
        diff_comments_data: list[tuple[str, str]] = []

        for comment in diff_comments:
            key = f'{comment.filediff_id}'

            if comment.interfilediff_id:
                key = f'{key}-{comment.interfilediff_id}'

            diff_comments_data.append((str(comment.pk), key))

        return diff_comments_data


class StatusUpdatesEntryMixin(DiffCommentsSerializerMixin, ReviewEntryMixin):
    """A mixin for any entries which can include status updates.

    This provides common functionality for the two entries that include status
    updates (the initial status updates entry and change description entries).

    Attributes:
        status_updates (list of reviewboard.reviews.models.StatusUpdate):
            The status updates in this entry.

        status_updates_by_review (dict):
            A mapping from review ID to the matching status update.
    """

    needs_reviews = True
    needs_status_updates = True

    @classmethod
    def build_etag_data(
        cls,
        data: ReviewRequestPageData,
        entry: Optional[StatusUpdatesEntryMixin] = None,
        **kwargs,
    ) -> str:
        """Build ETag data for the entry.

        This will be incorporated into the ETag for the page and for
        page updates.

        ETags are influenced by a status update's service ID, state,
        timestamp, and description.

        The result will be encoded as a SHA1 hash.

        Args:
            data (ReviewRequestPageData):
                The computed data (pre-ETag) for the page.

            entry (StatusUpdatesEntryMixin, optional):
                A specific entry to build ETags for.

            **kwargs (dict, unused):
                Additional keyword arguments for future expansion.

        Returns:
            str:
            The ETag data for the entry.
        """
        if entry is not None:
            status_updates = entry.status_updates
        elif data.status_updates_enabled:
            status_updates = data.all_status_updates
        else:
            status_updates = []

        if status_updates:
            etag = ':'.join(
                (
                    f'{status_update.service_id}:{status_update.state}:'
                    f'{status_update.timestamp}:{status_update.description}'
                )
                for status_update in status_updates
            )
        else:
            etag = ''

        etag = f'{super().build_etag_data(data)}:{etag}'

        return hashlib.sha1(etag.encode('utf-8')).hexdigest()

    def __init__(self) -> None:
        """Initialize the entry."""
        self.status_updates = []
        self.status_updates_by_review = {}
        self.state_counts = Counter()

    def are_status_updates_collapsed(
        self,
        status_updates: Sequence[StatusUpdate],
    ) -> bool:
        """Return whether all status updates should be collapsed.

        This considers all provided status updates when computing the
        collapsed state. It's meant to be used along with other logic to
        compute an entry's collapsed state.

        Status updates that are pending or have not yet been seen by the user
        (assuming they've viewed the page at least once) are not collapsed.

        Otherwise, the result is based off the review's collapsed state for
        each status update. Status updates not containing a review are
        considered collapsible, and ones containing a review defer to
        :py:meth:`ReviewEntryMixin.is_review_collapsed` for a result.

        Args:
            status_updates (list of reviewboard.reviews.models.StatusUpdate):
                The list of status updates to compute the collapsed state for.

        Returns:
            bool:
            ``True`` if all status updates are marked as collapsed. ``False``
            if any are not marked as collapsed.
        """
        data = self.data

        for status_update in status_updates:
            if (data.last_visited and
                status_update.timestamp > data.last_visited):
                return False

            if (status_update.effective_state in (status_update.PENDING,
                                                  status_update.NOT_YET_RUN)):
                return False

            if status_update.review_id is not None:
                review = data.reviews_by_id[status_update.review_id]

                if not self.is_review_collapsed(review):
                    return False

        return True

    def add_update(
        self,
        update: StatusUpdate,
    ) -> None:
        """Add a status update to the entry.

        Args:
            update (reviewboard.reviews.models.StatusUpdate):
                The status update to add.
        """
        self.status_updates.append(update)
        self.status_updates_by_review[update.review_id] = update

        update.comments = {
            'diff_comments': [],
            'screenshot_comments': [],
            'file_attachment_comments': [],
            'general_comments': [],
        }

        state = update.effective_state

        if state in (StatusUpdate.DONE_FAILURE,
                     StatusUpdate.ERROR,
                     StatusUpdate.TIMEOUT):
            update.header_class = 'status-update-state-failure'
        elif state == StatusUpdate.PENDING:
            update.header_class = 'status-update-state-pending'
        elif state == StatusUpdate.NOT_YET_RUN:
            update.header_class = 'status-update-state-not-yet-run'
        elif state == StatusUpdate.DONE_SUCCESS:
            update.header_class = 'status-update-state-success'
        else:
            raise ValueError('Unexpected state "%s"' % state)

        if state == StatusUpdate.TIMEOUT:
            description = _('timed out.')
        elif state == StatusUpdate.NOT_YET_RUN:
            description = _('not yet run.')
        else:
            description = update.description

        update.summary_html = render_to_string(
            template_name='reviews/status_update_summary.html',
            context={
                'action_name': update.action_name,
                'can_run': update.can_run,
                'description': description,
                'header_class': update.header_class,
                'status_update_id': update.pk,
                'summary': update.summary,
                'url': update.url,
                'url_text': update.url_text,
            })

    def populate_status_updates(
        self,
        status_updates: Sequence[StatusUpdate],
    ) -> None:
        """Populate the list of status updates for the entry.

        This will add all the provided status updates and all comments from
        their reviews. It will also uncollapse the entry if there are any
        draft replies owned by the user.

        Args:
            status_updates (list of reviewboard.reviews.models.StatusUpdate):
                The list of status updates to add.
        """
        data = self.data

        for update in status_updates:
            self.add_update(update)

            # Add all the comments for the review on this status
            # update.
            for comment in data.review_comments.get(update.review_id, []):
                self.add_comment(comment._type, comment)

    def add_comment(
        self,
        comment_type: str,
        comment: BaseComment,
    ) -> None:
        """Add a comment to the entry.

        This will associate the comment with the correct status update.

        Args:
            comment_type (str):
                The type of comment (an index into the :py:attr:`comments`
                dictionary).

            comment (reviewboard.reviews.models.BaseComment):
                The comment to add.
        """
        update = self.status_updates_by_review[comment.review_obj.pk]
        update.comments[comment_type].append(comment)

    def finalize(self) -> None:
        """Perform final computations after all comments have been added."""
        for update in self.status_updates:
            self.state_counts[update.effective_state] += 1

        summary_parts = []

        if self.state_counts[StatusUpdate.DONE_FAILURE] > 0:
            summary_parts.append(
                _('%s failed') % self.state_counts[StatusUpdate.DONE_FAILURE])

        if self.state_counts[StatusUpdate.DONE_SUCCESS] > 0:
            summary_parts.append(
                _('%s succeeded')
                % self.state_counts[StatusUpdate.DONE_SUCCESS])

        if self.state_counts[StatusUpdate.PENDING] > 0:
            summary_parts.append(
                _('%s pending') % self.state_counts[StatusUpdate.PENDING])

        if self.state_counts[StatusUpdate.NOT_YET_RUN] > 0:
            summary_parts.append(
                _('%s not yet run')
                % self.state_counts[StatusUpdate.NOT_YET_RUN])

        if self.state_counts[StatusUpdate.ERROR] > 0:
            summary_parts.append(
                _('%s failed with error')
                % self.state_counts[StatusUpdate.ERROR])

        if self.state_counts[StatusUpdate.TIMEOUT] > 0:
            summary_parts.append(
                _('%s timed out')
                % self.state_counts[StatusUpdate.TIMEOUT])

        if (self.state_counts[StatusUpdate.DONE_FAILURE] > 0 or
            self.state_counts[StatusUpdate.ERROR] > 0 or
            self.state_counts[StatusUpdate.TIMEOUT] > 0):
            self.state_summary_class = 'status-update-state-failure'
        elif (self.state_counts[StatusUpdate.PENDING] > 0 or
              self.state_counts[StatusUpdate.NOT_YET_RUN] > 0):
            self.state_summary_class = 'status-update-state-pending'
        elif self.state_counts[StatusUpdate.DONE_SUCCESS]:
            self.state_summary_class = 'status-update-state-success'

        self.state_summary = ', '.join(summary_parts)

    def get_js_model_data(self) -> JSONDict:
        """Return data to pass to the JavaScript Model during instantiation.

        The data returned from this function will be provided to the model
        when constructed. This consists of information on the reviews for
        status updates and the comments made on diffs.

        Returns:
            dict:
            A dictionary of attributes to pass to the Model instance.
        """
        diff_comments_data = list(chain.from_iterable(
            self.serialize_diff_comments_js_model_data(
                update.comments['diff_comments'])
            for update in self.status_updates
            if update.comments['diff_comments']
        ))

        reviews_data = [
            self.serialize_review_js_model_data(update.review)
            for update in self.status_updates
            if update.review_id is not None
        ]

        model_data: JSONDict = {
            'pendingStatusUpdates': (
                self.state_counts[StatusUpdate.PENDING] > 0),
        }
        model_data.update({
            key: value
            for key, value in (('diffCommentsData', diff_comments_data),
                               ('reviewsData', reviews_data))
            if value
        })

        return model_data


class ReviewRequestEntry(BaseReviewRequestPageEntry):
    """An entry for the main review request box.

    This is used to control the data queried by
    :py:class:`ReviewRequestPageData` for display in the main review request
    box. It does not render onto the page.
    """

    entry_type_id = 'review-request'
    entry_pos = BaseReviewRequestPageEntry.ENTRY_POS_INITIAL
    js_template_name = None
    js_model_class = None
    js_view_class = None
    needs_draft = True

    # These are needed for the file attachments/screenshots area.
    needs_file_attachments = True
    needs_screenshots = True

    # Reviews, comments, etc. are needed for the issue summary table.
    needs_reviews = True

    has_content = False


class InitialStatusUpdatesEntry(StatusUpdatesEntryMixin,
                                BaseReviewRequestPageEntry):
    """An entry for any status updates posted against the initial state.

    :py:class:`~reviewboard.reviews.models.StatusUpdate` reviews (those created
    by automated tools like static analysis checkers or CI systems) are shown
    separately from ordinary reviews. When status updates are related to a
    :py:class:`~reviewboard.changedescs.models.ChangeDescription`, they're
    displayed within the change description box. Otherwise, they're shown in
    their own box (immediately under the review request box), which is handled
    by this class.
    """

    entry_type_id = 'initial_status_updates'
    entry_pos = BaseReviewRequestPageEntry.ENTRY_POS_INITIAL
    template_name = 'reviews/entries/initial_status_updates.html'
    js_model_class = 'RB.ReviewRequestPage.StatusUpdatesEntry'
    js_view_class = 'RB.ReviewRequestPage.InitialStatusUpdatesEntryView'

    @classmethod
    def build_entries(
        cls,
        data: ReviewRequestPageData,
    ) -> Iterable[BaseReviewRequestPageEntry]:
        """Generate the entry instance from review request page data.

        This will only generate a single instance.

        Args:
            data (ReviewRequestPageData):
                The data used for the initial status update entry.

        Yields:
            InitialStatusUpdatesEntry:
            The entry to include on the page.
        """
        entry = cls(data=data)
        entry.populate_status_updates(data.initial_status_updates)

        yield entry

    def __init__(
        self,
        data: ReviewRequestPageData,
    ) -> None:
        """Initialize the entry.

        Args:
            data (ReviewRequestPageData):
                Pre-queried data for the review request page.
        """
        timestamps = [data.review_request.time_added] + [
            status_update.timestamp
            for status_update in data.initial_status_updates
        ]

        StatusUpdatesEntryMixin.__init__(self)
        BaseReviewRequestPageEntry.__init__(
            self,
            data=data,
            entry_id='0',
            added_timestamp=data.review_request.time_added,
            updated_timestamp=get_latest_timestamp(timestamps))

    @property
    def has_content(self) -> bool:
        """Whether there are any items to display in the entry.

        Returns:
            bool:
            True if there are any initial status updates to display.
        """
        return len(self.status_updates) > 0

    def get_dom_element_id(self) -> str:
        """Return the ID used for the DOM element for this entry.

        Returns:
            str:
            The ID used for the element.
        """
        return self.entry_type_id

    def is_entry_new(
        self,
        last_visited: datetime,
        user: User,
        **kwargs,
    ) -> bool:
        """Return whether the entry is new, from the user's perspective.

        The initial status updates entry is basically part of the review
        request, and is never shown as new.

        Args:
            last_visited (datetime.datetime, unused):
                The last visited timestamp.

            user (django.contrib.auth.models.User, unused):
                The user viewing the page.

            **kwargs (dict, unused):
                Additional keyword arguments.

        Returns:
            bool:
            ``False``, always.
        """
        return False

    def calculate_collapsed(self) -> bool:
        """Calculate whether the entry should currently be collapsed.

        The entry will be collapsed if there aren't yet any Change Descriptions
        on the page and if there aren't any status updates with reviews that
        should be expanded. See :py:meth:`ReviewEntryMixin.is_review_collapsed`
        for the collapsing rules for reviews.

        Returns:
            bool:
            ``True`` if the entry should be collapsed. ``False`` if it should
            be expanded.
        """
        data = self.data

        return (
            # Don't collapse if the user has not seen this page before (or
            # are anonymous) and there aren't any change descriptions yet.
            (data.last_visited or len(data.changedescs) > 0) and

            # Don't collapse if there are status updates containing reviews
            # that should not be collapsed.
            self.are_status_updates_collapsed(data.initial_status_updates)
        )


class ReviewEntry(ReviewEntryMixin, DiffCommentsSerializerMixin,
                  BaseReviewRequestPageEntry):
    """A review box."""

    entry_type_id = 'review'
    needs_reviews = True
    template_name = 'reviews/entries/review.html'
    js_model_class = 'RB.ReviewRequestPage.ReviewEntry'
    js_view_class = 'RB.ReviewRequestPage.ReviewEntryView'

    ######################
    # Instance variables #
    ######################

    #: A dictionary of comments.
    #:
    #: Each key in this represents a comment type, and the values are lists of
    #: comment objects.
    comments: dict[str, list[BaseComment]]

    #: Whether there are any issues (open or not).
    has_issues: bool

    #: The count of open issues within this review.
    issue_open_count: int

    #: The review for this entry.
    review: Review

    @classmethod
    def build_entries(cls, data):
        """Generate review entry instances from review request page data.

        Args:
            data (ReviewRequestPageData):
                The data used for the entries on the page.

        Yields:
            ReviewEntry:
            A review entry to include on the page.
        """
        for review in data.reviews:
            if (not review.public or
                review.is_reply() or
                (data.status_updates_enabled and
                 hasattr(review, 'status_update'))):
                continue

            entry = cls(data=data,
                        review=review)

            for comment in data.review_comments.get(review.pk, []):
                entry.add_comment(comment._type, comment)

            yield entry

    def __init__(
        self,
        data: ReviewRequestPageData,
        review: Review,
    ) -> None:
        """Initialize the entry.

        Args:
            data (ReviewRequestPageData):
                Pre-queried data for the review request page.

            review (reviewboard.reviews.models.Review):
                The review.
        """
        self.review = review
        self.issue_open_count = 0
        self.has_issues = False
        self.comments = {
            'diff_comments': [],
            'screenshot_comments': [],
            'file_attachment_comments': [],
            'general_comments': [],
        }

        updated_timestamp = \
            data.latest_timestamps_by_review_id.get(review.pk,
                                                    review.timestamp)

        super().__init__(
            data=data,
            entry_id=str(review.pk),
            added_timestamp=review.timestamp,
            updated_timestamp=updated_timestamp,
            avatar_user=review.user)

    @property
    def can_revoke_ship_it(self) -> bool:
        """Whether the Ship It can be revoked by the current user."""
        return self.review.can_user_revoke_ship_it(self.data.request.user)

    def get_dom_element_id(self) -> str:
        """Return the ID used for the DOM element for this entry.

        Returns:
            str:
            The ID used for the element.
        """
        return f'{self.entry_type_id}{self.review.pk}'

    def is_entry_new(
        self,
        last_visited: datetime,
        user: User,
        **kwargs,
    ) -> bool:
        """Return whether the entry is new, from the user's perspective.

        Args:
            last_visited (datetime.datetime):
                The last visited timestamp.

            user (django.contrib.auth.models.User):
                The user viewing the page.

            **kwargs (dict, unused):
                Additional keyword arguments.

        Returns:
            bool:
            ``True`` if the entry will be shown as new. ``False`` if it
            will be shown as an existing entry.
        """
        return self.review.is_new_for_user(user=user,
                                           last_visited=last_visited)

    def add_comment(
        self,
        comment_type: str,
        comment: BaseComment,
    ) -> None:
        """Add a comment to this entry.

        Args:
            comment_type (str):
                The type of comment (an index into the :py:attr:`comments`
                dictionary).

            comment (reviewboard.reviews.models.BaseComment):
                The comment to add.
        """
        self.comments[comment_type].append(comment)

        if comment.issue_opened:
            self.has_issues = True

            if comment.issue_status in (BaseComment.OPEN,
                                        BaseComment.VERIFYING_RESOLVED,
                                        BaseComment.VERIFYING_DROPPED):
                self.issue_open_count += 1

    def get_js_model_data(self) -> JSONDict:
        """Return data to pass to the JavaScript Model during instantiation.

        The data returned from this function will be provided to the model
        when constructed. This consists of information on the review and the
        comments made on diffs.

        Returns:
            dict:
            A dictionary of attributes to pass to the Model instance.
        """
        model_data: JSONDict = {
            'reviewData': self.serialize_review_js_model_data(self.review),
        }

        diff_comments_data = self.serialize_diff_comments_js_model_data(
            self.comments['diff_comments'])

        if diff_comments_data:
            model_data['diffCommentsData'] = diff_comments_data

        return model_data

    def calculate_collapsed(self) -> bool:
        """Calculate whether the entry should currently be collapsed.

        The entry will be collapsed if the review is marked as collapsed. See
        :py:meth:`ReviewEntryMixin.is_review_collapsed` for the collapsing
        rules for reviews.

        Returns:
            bool:
            ``True`` if the entry should be collapsed. ``False`` if it should
            be expanded.
        """
        return self.is_review_collapsed(self.review)


class ChangeEntry(StatusUpdatesEntryMixin, BaseReviewRequestPageEntry):
    """A change description box."""

    entry_type_id = 'changedesc'
    js_model_class = 'RB.ReviewRequestPage.ChangeEntry'
    js_view_class = 'RB.ReviewRequestPage.ChangeEntryView'
    needs_changedescs = True
    needs_file_attachments = True
    needs_screenshots = True
    template_name = 'reviews/entries/change.html'

    ######################
    # Instance variables #
    ######################

    #: The change description.
    changedesc: ChangeDescription

    @classmethod
    def build_entries(
        cls,
        data: ReviewRequestPageData,
    ) -> Iterable[ChangeEntry]:
        """Generate change entry instances from review request page data.

        Args:
            data (ReviewRequestPageData):
                The data used for the entries on the page.

        Yields:
            ChangeEntry:
            A change entry to include on the page.
        """
        for changedesc in data.changedescs:
            entry = cls(data=data,
                        changedesc=changedesc)
            entry.populate_status_updates(
                data.change_status_updates.get(changedesc.pk, []))

            yield entry

    def __init__(
        self,
        data: ReviewRequestPageData,
        changedesc: ChangeDescription,
    ) -> None:
        """Initialize the entry.

        Args:
            data (ReviewRequestPageData):
                Pre-queried data for the review request page.

            changedesc (reviewboard.changedescs.models.ChangeDescription):
                The change description for this entry.
        """
        self.changedesc = changedesc
        self.fields_changed_groups = []

        status_updates = data.change_status_updates.get(changedesc.pk, [])
        review_request = data.review_request
        request = data.request

        timestamps = [changedesc.timestamp] + [
            status_update.timestamp
            for status_update in status_updates
        ]

        BaseReviewRequestPageEntry.__init__(
            self,
            data=data,
            entry_id=str(changedesc.pk),
            added_timestamp=changedesc.timestamp,
            updated_timestamp=get_latest_timestamp(timestamps),
            avatar_user=changedesc.get_user(review_request))

        if data.status_updates_enabled:
            StatusUpdatesEntryMixin.__init__(self)

        cur_field_changed_group = None

        # See if there was a review request status change.
        status_change = changedesc.fields_changed.get('status')

        if status_change:
            assert 'new' in status_change
            self.new_status = ReviewRequest.status_to_string(
                status_change['new'][0])
        else:
            self.new_status = None

        # Process the list of fields, in order by fieldset. These will be
        # put into groups composed of inline vs. full-width field values,
        # for render into the box.
        fieldsets = get_review_request_fieldsets(
            include_change_entries_only=True)

        for fieldset in fieldsets:
            for field_cls in fieldset.field_classes:
                field_id = field_cls.field_id

                if field_id not in changedesc.fields_changed:
                    continue

                inline = field_cls.change_entry_renders_inline

                if (not cur_field_changed_group or
                    cur_field_changed_group['inline'] != inline):
                    # Begin a new group of fields.
                    cur_field_changed_group = {
                        'inline': inline,
                        'fields': [],
                    }
                    self.fields_changed_groups.append(cur_field_changed_group)

                if issubclass(field_cls, ReviewRequestPageDataMixin):
                    field = field_cls(review_request, request=request,
                                      data=data)
                else:
                    field = field_cls(review_request, request=request)

                cur_field_changed_group['fields'] += \
                    field.get_change_entry_sections_html(
                        changedesc.fields_changed[field_id])

    def get_dom_element_id(self) -> str:
        """Return the ID used for the DOM element for this entry.

        Returns:
            str:
            The ID used for the element.
        """
        return '%s%s' % (self.entry_type_id, self.changedesc.pk)

    def is_entry_new(
        self,
        last_visited: datetime,
        user: User,
        **kwargs,
    ) -> bool:
        """Return whether the entry is new, from the user's perspective.

        Args:
            last_visited (datetime.datetime):
                The last visited timestamp.

            user (django.contrib.auth.models.User):
                The user viewing the page.

            **kwargs (dict, unused):
                Additional keyword arguments.

        Returns:
            bool:
            ``True`` if the entry will be shown as new. ``False`` if it
            will be shown as an existing entry.
        """
        return self.changedesc.is_new_for_user(user=user,
                                               last_visited=last_visited,
                                               model=self.data.review_request)

    def calculate_collapsed(self) -> bool:
        """Calculate whether the entry should currently be collapsed.

        The entry will be collapsed if the timestamp of the Change Description
        is older than that of the most recent Change Description and there
        aren't any status updates with reviews that should be expanded. see
        :py:meth:`ReviewEntryMixin.is_review_collapsed` for the collapsing
        rules for reviews.

        Returns:
            bool:
            ``True`` if the entry should be collapsed. ``False`` if it should
            be expanded.
        """
        data = self.data
        changedesc = self.changedesc
        status_updates = data.change_status_updates.get(changedesc.pk, [])

        return (
            # If the change is older than the newest change, consider it
            # for collapsing.
            changedesc.timestamp < data.latest_changedesc_timestamp and

            # Don't collapse if there are status updates containing reviews
            # that should not be collapsed.
            (not status_updates or
             self.are_status_updates_collapsed(status_updates))
        )

    def get_js_model_data(self) -> JSONDict:
        """Return data to pass to the JavaScript Model during instantiation.

        This will serialize commit information if present for the
        :js:class:`RB.DiffCommitListView`.

        Returns:
            dict:
            A dictionary of model data.
        """
        model_data = super().get_js_model_data()

        commit_info = self.changedesc.fields_changed.get(
            CommitListField.field_id)

        if commit_info:
            commits = self.data.commits_by_diffset_id

            if commit_info['old']:
                old_commits = commits[commit_info['old']]
            else:
                old_commits = []

            new_commits = commits[commit_info['new']]

            model_data['commits'] = [
                commit.serialize()
                for commit in chain(old_commits, new_commits)
            ]

        return model_data


class ReviewRequestPageEntryRegistry(
    OrderedRegistry[Type[BaseReviewRequestPageEntry]]):
    """A registry for types of entries on the review request page."""

    lookup_attrs = ['entry_type_id']
    errors = {
        ALREADY_REGISTERED: _(
            'This review request page entry is already registered.'
        ),
        ATTRIBUTE_REGISTERED: _(
            'A review request page entry with the entry_type_id '
            '"%(attr_value)s" is already registered by another entry '
            '(%(duplicate)s).'
        ),
        NOT_REGISTERED: _(
            '"%(attr_value)s" is not a registered review request page entry '
            'ID.'
        ),
    }

    def get_entry(
        self,
        entry_type_id: str,
    ) -> Optional[type[BaseReviewRequestPageEntry]]:
        """Return an entry with the given type ID.

        Args:
            entry_type_id (str):
                The ID of the entry type to return.

        Returns:
            type:
            The registered page entry type matching the ID, or ``None`` if
            it could not be found.
        """
        return self.get('entry_type_id', entry_type_id)

    def get_defaults(self) -> Iterable[type[BaseReviewRequestPageEntry]]:
        """Return the default review request page entry types for the registry.

        This is used internally by the registry to populate the list of
        built-in types of entries that should be used on the review request
        page.

        Returns:
            list of BaseReviewRequestPageEntry:
            The list of default entry types.
        """
        return [
            ReviewRequestEntry,
            InitialStatusUpdatesEntry,
            ChangeEntry,
            ReviewEntry,
        ]


entry_registry = ReviewRequestPageEntryRegistry()
