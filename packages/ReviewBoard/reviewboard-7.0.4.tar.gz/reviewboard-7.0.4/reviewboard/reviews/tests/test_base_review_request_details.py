"""Unit tests for BaseReviewRequestDetails."""

from __future__ import annotations

from django.contrib.auth.models import User
from django.db.models import Max, Q
from djblets.testing.decorators import add_fixtures

from reviewboard.attachments.models import (
    FileAttachment,
    FileAttachmentHistory)
from reviewboard.reviews.models import DefaultReviewer, ReviewRequest
from reviewboard.testing import TestCase


class BaseReviewRequestDetailsTests(TestCase):
    """Unit tests for BaseReviewRequestDetails."""

    fixtures = ['test_scmtools']

    def test_add_default_reviewers_with_users(self):
        """Testing BaseReviewRequestDetails.add_default_reviewers with users"""
        user1 = User.objects.create_user(username='user1',
                                         email='user1@example.com')
        user2 = User.objects.create(username='user2',
                                    email='user2@example.com')
        user3 = User.objects.create(username='user3',
                                    email='user3@example.com',
                                    is_active=False)

        # Create the default reviewers.
        default_reviewer1 = DefaultReviewer.objects.create(name='Test 1',
                                                           file_regex='.*')
        default_reviewer1.people.add(user1, user2, user3)

        # Create the review request and accompanying diff.
        review_request = self.create_review_request(create_repository=True,
                                                    submitter=user1)
        diffset = self.create_diffset(review_request)
        self.create_filediff(diffset)

        # The following queries will be executed:
        #
        # 1. Diffset
        # 2. The default reviewer list
        # 3. The file list
        # 4. User list for all matched default reviewers
        # 5. Update users (m2m.add())
        # 6. Group list for all matched default reviewers
        with self.assertNumQueries(6):
            review_request.add_default_reviewers()

        self.assertEqual(list(review_request.target_people.all()),
                         [user1, user2])
        self.assertEqual(list(review_request.target_groups.all()),
                         [])

    def test_add_default_reviewers_with_groups(self):
        """Testing BaseReviewRequestDetails.add_default_reviewers with groups
        """
        user1 = User.objects.create_user(username='user1',
                                         email='user1@example.com')

        group1 = self.create_review_group(name='Group 1')
        group2 = self.create_review_group(name='Group 2')

        # Create the default reviewers.
        default_reviewer1 = DefaultReviewer.objects.create(name='Test 1',
                                                           file_regex='.*')
        default_reviewer1.groups.add(group1, group2)

        # Create the review request and accompanying diff.
        review_request = self.create_review_request(create_repository=True,
                                                    submitter=user1)
        diffset = self.create_diffset(review_request)
        self.create_filediff(diffset)

        # The following queries will be executed:
        #
        # 1. Diffset
        # 2. The default reviewer list
        # 3. The file list
        # 4. User list for all matched default reviewers
        # 5. Group list for all matched default reviewers
        # 6. Update groups (m2m.add())
        with self.assertNumQueries(6):
            review_request.add_default_reviewers()

        self.assertEqual(list(review_request.target_groups.all()),
                         [group1, group2])
        self.assertEqual(list(review_request.target_people.all()),
                         [])

    def test_add_default_reviewers_with_users_and_groups(self):
        """Testing BaseReviewRequestDetails.add_default_reviewers with both
        users and groups
        """
        user1 = User.objects.create_user(username='user1',
                                         email='user1@example.com')
        user2 = User.objects.create(username='user2',
                                    email='user2@example.com')

        group1 = self.create_review_group(name='Group 1')
        group2 = self.create_review_group(name='Group 2')

        # Create the default reviewers.
        default_reviewer1 = DefaultReviewer.objects.create(name='Test 1',
                                                           file_regex='.*')
        default_reviewer1.people.add(user1, user2)

        default_reviewer2 = DefaultReviewer.objects.create(name='Test 2',
                                                           file_regex='.*')
        default_reviewer2.groups.add(group1, group2)

        # Create the review request and accompanying diff.
        review_request = self.create_review_request(create_repository=True,
                                                    submitter=user1)
        diffset = self.create_diffset(review_request)
        self.create_filediff(diffset)

        # The following queries will be executed:
        #
        # 1. Diffset
        # 2. The default reviewer list
        # 3. The file list
        # 4. User list for all matched default reviewers
        # 5. Update users (m2m.add())
        # 6. Group list for all matched default reviewers
        # 7. Update groups (m2m.add())
        with self.assertNumQueries(7):
            review_request.add_default_reviewers()

        self.assertEqual(list(review_request.target_people.all()),
                         [user1, user2])
        self.assertEqual(list(review_request.target_groups.all()),
                         [group1, group2])

    def test_add_default_reviewers_with_no_matches(self):
        """Testing BaseReviewRequestDetails.add_default_reviewers with no
        matches
        """
        user1 = User.objects.create_user(username='user1',
                                         email='user1@example.com')
        user2 = User.objects.create(username='user2',
                                    email='user2@example.com')

        group1 = self.create_review_group(name='Group 1')
        group2 = self.create_review_group(name='Group 2')

        # Create the default reviewers.
        default_reviewer1 = DefaultReviewer.objects.create(name='Test 1',
                                                           file_regex='/foo')
        default_reviewer1.people.add(user1, user2)

        default_reviewer2 = DefaultReviewer.objects.create(name='Test 2',
                                                           file_regex='/bar')
        default_reviewer2.groups.add(group1, group2)

        # Create the review request and accompanying diff.
        review_request = self.create_review_request(create_repository=True,
                                                    submitter=user1)
        diffset = self.create_diffset(review_request)
        self.create_filediff(diffset)

        # The following queries will be executed:
        #
        # 1. Diffset
        # 2. The file list
        # 3. The default reviewer list
        with self.assertNumQueries(3):
            review_request.add_default_reviewers()

        self.assertEqual(list(review_request.target_people.all()), [])
        self.assertEqual(list(review_request.target_groups.all()), [])

    def test_add_default_reviewers_with_no_repository(self):
        """Testing BaseReviewRequestDetails.add_default_reviewers with no
        repository
        """
        user1 = User.objects.create_user(username='user1',
                                         email='user1@example.com')

        # Create the review request and accompanying diff.
        review_request = self.create_review_request(submitter=user1)

        with self.assertNumQueries(0):
            review_request.add_default_reviewers()

    @add_fixtures(['test_users'])
    def test_get_file_attachments(self) -> None:
        """Testing BaseReviewRequestDetails.get_file_attachments"""
        review_request = self.create_review_request()

        active = self.create_file_attachment(review_request)
        active_2 = self.create_file_attachment(review_request)

        self.create_file_attachment(review_request, active=False)

        # 3 queries:
        #
        # 1. Fetch active file attachments.
        # 2. Fetch display position for the first attachment
        # 3. Fetch display position for the second attachment
        queries = [
            {
                'join_types': {
                    'reviews_reviewrequest_file_attachments': 'INNER JOIN',
                },
                'model': FileAttachment,
                'num_joins': 1,
                'tables': {
                    'attachments_fileattachment',
                    'reviews_reviewrequest_file_attachments',
                },
                'where': Q(review_request__id=review_request.pk),
            },
            {
                'model': FileAttachmentHistory,
                'where': Q(id=active.pk),
            },
            {
                'model': FileAttachmentHistory,
                'where': Q(id=active_2.pk),
            },
        ]

        with self.assertQueries(queries):
            attachments = review_request.get_file_attachments()

        self.assertListEqual(attachments, [active, active_2])

    @add_fixtures(['test_users'])
    def test_get_file_attachments_with_sort_false(self) -> None:
        """Testing BaseReviewRequestDetails.get_file_attachments with
        sort=False
        """
        review_request = self.create_review_request()

        active = self.create_file_attachment(review_request)
        active_2 = self.create_file_attachment(review_request)

        self.create_file_attachment(review_request, active=False)

        # 1 query:
        #
        # 1. Fetch active file attachments.
        queries = [
            {
                'join_types': {
                    'reviews_reviewrequest_file_attachments': 'INNER JOIN',
                },
                'model': FileAttachment,
                'num_joins': 1,
                'tables': {
                    'attachments_fileattachment',
                    'reviews_reviewrequest_file_attachments',
                },
                'where': Q(review_request__id=review_request.pk),
            },
        ]

        with self.assertQueries(queries):
            attachments = review_request.get_file_attachments(sort=False)

        self.assertListEqual(attachments, [active, active_2])

    @add_fixtures(['test_users'])
    def test_get_file_attachments_legacy(self) -> None:
        """Testing BaseReviewRequestDetails.get_file_attachments with legacy
        attachments that don't have an associated FileAttachmentHistory
        """
        review_request = self.create_review_request()

        active = self.create_file_attachment(
            review_request,
            with_history=False)
        active_2 = self.create_file_attachment(
            review_request,
            with_history=False)

        self.create_file_attachment(review_request, active=False)

        # 9 queries:
        #
        #   1. Fetch active file attachments.
        # 2-5. Create a FileAttachmentHistory for the first attachment.
        # 6-9. Create a FileAttachmentHistory for the second attachment.
        queries = [
            {
                'join_types': {
                    'reviews_reviewrequest_file_attachments': 'INNER JOIN',
                },
                'model': FileAttachment,
                'num_joins': 1,
                'tables': {
                    'attachments_fileattachment',
                    'reviews_reviewrequest_file_attachments',
                },
                'where': Q(review_request__id=review_request.pk),
            },
            {
                'join_types': {
                    'reviews_reviewrequest_file_attachment_histories':
                        'INNER JOIN',
                },
                'model': FileAttachmentHistory,
                'annotations': {
                    'display_position__max': Max('display_position'),
                },
                'num_joins': 1,
                'tables': {
                    'attachments_fileattachmenthistory',
                    'reviews_reviewrequest_file_attachment_histories',
                },
                'where': Q(review_request=review_request),
            },
            {
                'model': FileAttachmentHistory,
                'type': 'INSERT',
            },
            {
                'model': ReviewRequest.file_attachment_histories.through,
                'type': 'INSERT',
            },
            {
                'model': FileAttachment,
                'type': 'UPDATE',
                'where': Q(pk=active.pk)
            },
            {
                'join_types': {
                    'reviews_reviewrequest_file_attachment_histories':
                        'INNER JOIN',
                },
                'model': FileAttachmentHistory,
                'annotations': {
                    'display_position__max': Max('display_position'),
                },
                'num_joins': 1,
                'tables': {
                    'attachments_fileattachmenthistory',
                    'reviews_reviewrequest_file_attachment_histories',
                },
                'where': Q(review_request=review_request),
            },
            {
                'model': FileAttachmentHistory,
                'type': 'INSERT',
            },
            {
                'model': ReviewRequest.file_attachment_histories.through,
                'type': 'INSERT',
            },
            {
                'model': FileAttachment,
                'type': 'UPDATE',
                'where': Q(pk=active_2.pk)
            },
        ]

        with self.assertQueries(queries):
            attachments = review_request.get_file_attachments()

        self.assertListEqual(attachments, [active, active_2])

    @add_fixtures(['test_users'])
    def test_get_file_attachments_with_no_attachments(self) -> None:
        """Testing BaseReviewRequestDetails.get_file_attachments with
        no active attachments
        """
        review_request = self.create_review_request()

        self.create_file_attachment(review_request, active=False)

        with self.assertNumQueries(0):
            attachments = review_request.get_file_attachments(sort=False)

        self.assertListEqual(attachments, [])
