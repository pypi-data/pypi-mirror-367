"""Tests for reviewboard.reviews.signal_handlers.

Version Added:
    6.0
"""

from __future__ import annotations

import kgb
from django.contrib.auth.models import User

from reviewboard.attachments.models import (FileAttachment,
                                            FileAttachmentHistory)
from reviewboard.changedescs.models import ChangeDescription
from reviewboard.diffviewer.models import DiffSet, DiffSetHistory, FileDiff
from reviewboard.reviews.models import Screenshot
from reviewboard.reviews.signal_handlers import (
    _on_review_request_deleted,
    _on_review_request_draft_deleted)
from reviewboard.testing import TestCase


class OnReviewRequestDraftDeletedTests(kgb.SpyAgency, TestCase):
    """Tests _on_review_request_draft_deleted() signal handler.

    Version Added:
        6.0
    """

    fixtures = ['test_scmtools', 'test_users']

    def setUp(self) -> None:
        """Set up the test case."""
        super().setUp()
        self.review_request = self.create_review_request(
            create_repository=True,
            publish=True)
        self.draft = self.create_review_request_draft(self.review_request)

    def test_with_file_attachments(self) -> None:
        """Testing _on_review_request_draft_deleted deletes new and new
        revision draft file attachments
        """
        self.spy_on(_on_review_request_draft_deleted)

        published = self.create_file_attachment(self.review_request)
        new = self.create_file_attachment(self.review_request, draft=True)
        new_revision = self.create_file_attachment(
            self.review_request,
            attachment_history=published.attachment_history,
            attachment_revision=published.attachment_revision + 1,
            draft=True)

        # 39 queries:
        #
        #   1-7. Fetch review request draft info and relations
        #  8-13. Fetch file attachments info
        # 14-17. Build file attachments data for getting states
        # 18-32. Delete the file attachments from the review request draft
        # 33-37. Delete the change description
        #    38. Delete the file attachments
        #    39. Delete the review request draft
        with self.assertNumQueries(39):
            self.draft.delete()

        all_attachments = FileAttachment.objects.all()

        self.assertSpyCalled(_on_review_request_draft_deleted)
        self.assertNotIn(new, all_attachments)
        self.assertNotIn(new_revision, all_attachments)
        self.assertIn(published, all_attachments)

    def test_with_one_file_attachment(self) -> None:
        """Testing _on_review_request_draft_deleted deletes a new file
        attachment
        """
        self.spy_on(_on_review_request_draft_deleted)

        published = self.create_file_attachment(self.review_request)
        new = self.create_file_attachment(self.review_request, draft=True)

        # 28 queries:
        #
        #   1-7. Fetch review request draft info and relations
        #  8-13. Fetch file attachments info
        # 14-17. Build file attachments data for getting states
        # 18-21. Delete the file attachment from the review request draft
        # 22-26. Delete the change description
        #    27. Delete the file attachment
        #    28. Delete the review request draft
        with self.assertNumQueries(28):
            self.draft.delete()

        all_attachments = FileAttachment.objects.all()

        self.assertSpyCalled(_on_review_request_draft_deleted)
        self.assertNotIn(new, all_attachments)
        self.assertIn(published, all_attachments)

    def test_with_no_file_attachments(self) -> None:
        """Testing _on_review_request_draft_deleted when there's no
        draft file attachments on the review request
        """
        self.spy_on(_on_review_request_draft_deleted)

        # 13 queries:
        #
        #   1-7. Fetch review request draft info and relations
        #  8-12. Delete the change description
        #    13. Delete the review request draft
        with self.assertNumQueries(13):
            self.draft.delete()

        self.assertSpyCalled(_on_review_request_draft_deleted)

    def test_with_change_description(self) -> None:
        """Testing _on_review_request_draft_deleted with a change description
        """
        self.spy_on(_on_review_request_draft_deleted)
        changedesc = ChangeDescription.objects.create(
            user=User.objects.get(username='doc'),
            public=False,
            text='x')

        self.draft.changedesc = changedesc
        self.draft.save()

        # 13 queries:
        #
        #  1-7. Fetch review request draft info and relations
        # 8-12. Delete the change description
        #   13. Delete the review request draft
        with self.assertNumQueries(13):
            self.draft.delete()

        self.assertNotIn(changedesc, ChangeDescription.objects.all())

    def test_with_diff_and_diff_file_attachment(self) -> None:
        """Testing _on_review_request_draft_deleted with a diff and diff file
        attachment
        """
        self.spy_on(_on_review_request_draft_deleted)

        diffset = self.create_diffset(
            repository=self.review_request.repository)
        self.draft.diffset = diffset
        self.draft.save()

        filediff = self.create_filediff(diffset)
        attachment = self.create_diff_file_attachment(filediff)

        # 35 queries:
        #
        #   1-7. Fetch review request draft info and relations
        #  8-10. Fetch file attachments info
        # 11-14. Delete the change description
        # 15-34. Delete the diffset, filediffs, and linked file attachment
        #    35. Delete the review request draft
        with self.assertNumQueries(35):
            self.draft.delete()

        self.assertNotIn(attachment, FileAttachment.objects.all())
        self.assertNotIn(filediff, FileDiff.objects.all())
        self.assertNotIn(diffset, DiffSet.objects.all())

    def test_handler_does_not_delete_published_data(self) -> None:
        """Testing that _on_review_request_draft_deleted running after a draft
        publish does not delete data that is now part of the review request
        """
        self.spy_on(_on_review_request_draft_deleted)

        user = User.objects.get(username='doc')

        diffset = self.create_diffset(
            repository=self.review_request.repository)
        self.draft.diffset = diffset

        changedesc = ChangeDescription.objects.create(
            user=user,
            public=False,
            text='x')
        self.draft.changedesc = changedesc

        attachment = self.create_file_attachment(self.review_request,
                                                 draft=True)

        self.draft.save()

        self.draft.target_people.add(user)
        self.review_request.publish(user)

        self.assertIn(diffset, DiffSet.objects.all())
        self.assertIn(changedesc, ChangeDescription.objects.all())
        self.assertTrue(attachment, FileAttachment.objects.all())


class OnReviewRequestDeletedTests(kgb.SpyAgency, TestCase):
    """Tests for the _on_review_request_deleted signal handler.

    Version Added:
        7.0
    """

    fixtures = ['test_scmtools', 'test_users']

    def test_cleans_up_related_changedescs(self) -> None:
        """Testing _on_review_request_deleted deletes related ChangeDescription
        objects
        """
        self.spy_on(_on_review_request_deleted)

        review_request = self.create_review_request(
            publish=True)

        c = ChangeDescription.objects.create(
            user=User.objects.get(username='doc'),
            public=True,
            text='x')
        review_request.changedescs.add(c)

        self.assertEqual(ChangeDescription.objects.count(), 1)

        # 36 queries:
        #
        #  1-11. Update profiles and counts.
        # 12-29. Fetch review request and related object data.
        # 30-31. Delete change description and relation.
        # 32-35. Delete other related data.
        #    36. Delete review request.
        with self.assertNumQueries(36):
            review_request.delete()

        self.assertSpyCalled(_on_review_request_deleted)
        self.assertEqual(ChangeDescription.objects.count(), 0)

    def test_cleans_up_related_diffset_history(self) -> None:
        """Testing _on_review_request_deleted deletes related DiffSetHistory
        object
        """
        self.spy_on(_on_review_request_deleted)

        review_request = self.create_review_request(
            create_repository=True,
            publish=True)

        self.create_diffset(review_request)
        self.create_diffset(review_request, revision=2)

        self.assertEqual(DiffSetHistory.objects.count(), 1)

        # 35 queries:
        #
        #  1-11. Update profiles and counts.
        # 12-31. Fetch review request and related object data.
        #    32. Set diffset_history relation to NULL.
        #    33. Delete diffset history.
        #    34. Delete diffsets.
        #    35. Delete review request.
        with self.assertNumQueries(35):
            review_request.delete()

        self.assertSpyCalled(_on_review_request_deleted)
        self.assertEqual(DiffSetHistory.objects.count(), 0)

    def test_cleans_up_related_file_attachments(self) -> None:
        """Testing _on_review_request_deleted deletes related file attachments
        """
        self.spy_on(_on_review_request_deleted)

        review_request = self.create_review_request(
            create_repository=True,
            publish=True)

        self.create_file_attachment(review_request, active=True)
        self.create_file_attachment(review_request, active=False)

        self.assertEqual(FileAttachment.objects.count(), 2)
        self.assertEqual(FileAttachmentHistory.objects.count(), 2)
        self.assertEqual(review_request.file_attachments_count, 1)
        self.assertEqual(review_request.inactive_file_attachments_count, 1)

        # 51 queries:
        #
        #  1-11. Update profiles and counts.
        # 12-35. Fetch review request and related object data.
        # 36-39. Remove file attachment and file attachment history relations.
        #    40. Delete file attachments.
        # 41-44. Perform file attachment relation bookkeeping.
        # 45-47. Delete diffset history.
        # 48-50. Clean up file attachment relations.
        #    51. Delete review request.
        with self.assertNumQueries(51):
            review_request.delete()

        self.assertSpyCalled(_on_review_request_deleted)
        self.assertEqual(FileAttachment.objects.count(), 0)
        self.assertEqual(FileAttachmentHistory.objects.count(), 0)

    def test_cleans_up_related_screenshots(self) -> None:
        """Testing _on_review_request_deleted deletes related screenshots"""
        self.spy_on(_on_review_request_deleted)

        review_request = self.create_review_request(
            create_repository=True,
            publish=True)

        self.create_screenshot(review_request, active=True)
        self.create_screenshot(review_request, active=False)

        self.assertEqual(Screenshot.objects.count(), 2)
        self.assertEqual(review_request.screenshots_count, 1)
        self.assertEqual(review_request.inactive_screenshots_count, 1)

        # 51 queries:
        #
        #  1-11. Update profiles and counts.
        # 12-35. Fetch review request and related object data.
        # 36-41. Remove screenshot relations.
        #    42. Delete screenshots.
        # 43-45. Delete diffset history.
        # 46-47. Clean up screenshot relations..
        #    48. Delete review request.
        with self.assertNumQueries(48):
            review_request.delete()

        self.assertSpyCalled(_on_review_request_deleted)
        self.assertEqual(Screenshot.objects.count(), 0)
