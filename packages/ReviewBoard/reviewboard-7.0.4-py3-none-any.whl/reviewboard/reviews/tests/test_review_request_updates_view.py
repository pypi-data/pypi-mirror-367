# coding: utf-8
"""Unit tests for ReviewRequestUpdatesView."""

import json
import struct
from datetime import datetime, timedelta, timezone

from django.urls import reverse

from reviewboard.reviews.views import ReviewRequestUpdatesView
from reviewboard.testing import TestCase


class ReviewRequestUpdatesViewTests(TestCase):
    """Unit tests for ReviewRequestUpdatesView."""

    fixtures = ['test_users']

    def setUp(self):
        super(ReviewRequestUpdatesViewTests, self).setUp()

        self.review_request = self.create_review_request(
            publish=True,
            time_added=datetime(2017, 9, 7, 17, 0, 0, tzinfo=timezone.utc),
            last_updated=datetime(2017, 9, 7, 23, 10, 0, tzinfo=timezone.utc))

        # Create the first review.
        self.review1 = self.create_review(
            self.review_request,
            timestamp=self.review_request.time_added + timedelta(days=10),
            publish=True)
        self.general_comment = self.create_general_comment(
            self.review1,
            issue_opened=True,
            timestamp=self.review1.timestamp + timedelta(days=5))

        # Create the second review (10 days later).
        self.review2 = self.create_review(
            self.review_request,
            timestamp=self.review1.timestamp + timedelta(days=10),
            publish=True)

        # This one shouldn't appear in any updates, since it's not published.
        self.review3 = self.create_review(
            self.review_request,
            timestamp=self.review2.timestamp + timedelta(days=10),
            publish=False)

        self.view = ReviewRequestUpdatesView.as_view()

    def test_get(self):
        """Testing ReviewRequestUpdatesView GET"""
        updates = self._get_updates()
        self.assertEqual(len(updates), 4)

        metadata, html = updates[0]
        self.assertEqual(
            metadata,
            {
                'addedTimestamp': '2017-09-17T17:00:00Z',
                'entryID': '1',
                'entryType': 'review',
                'etag': '',
                'modelData': {
                    'reviewData': {
                        'authorName': 'dopey',
                        'id': self.review1.pk,
                        'public': True,
                        'bodyTop': self.review1.body_top,
                        'bodyBottom': self.review1.body_bottom,
                        'shipIt': self.review1.ship_it,
                    },
                },
                'type': 'entry',
                'updatedTimestamp': '2017-09-17T17:00:00Z',
                'viewOptions': {},
            })
        self.assertTrue(html.startswith('<div id="review1"'))
        self.assertTrue(html.endswith('\n</div>'))

        metadata, html = updates[1]
        self.assertEqual(
            metadata,
            {
                'addedTimestamp': '2017-09-27T17:00:00Z',
                'entryID': '2',
                'entryType': 'review',
                'etag': '',
                'modelData': {
                    'reviewData': {
                        'authorName': 'dopey',
                        'id': self.review2.pk,
                        'public': True,
                        'bodyTop': self.review2.body_top,
                        'bodyBottom': self.review2.body_bottom,
                        'shipIt': self.review2.ship_it,
                    },
                },
                'type': 'entry',
                'updatedTimestamp': '2017-09-27T17:00:00Z',
                'viewOptions': {},
            })
        self.assertTrue(html.startswith('<div id="review2"'))
        self.assertTrue(html.endswith('\n</div>'))

        metadata, html = updates[2]
        self.assertEqual(
            metadata,
            {
                'addedTimestamp': '2017-09-07T17:00:00Z',
                'entryID': '0',
                'entryType': 'initial_status_updates',
                'etag': '05a79f06cf3f67f726dae68d18a2290f6c9a50c9',
                'modelData': {
                    'pendingStatusUpdates': False,
                },
                'type': 'entry',
                'updatedTimestamp': '2017-09-07T17:00:00Z',
                'viewOptions': {},
            })
        self.assertTrue(html.startswith('<div id="initial_status_updates"'))
        self.assertTrue(html.endswith('\n</div>'))

        metadata, html = updates[3]
        self.assertEqual(
            metadata,
            {
                'type': 'issue-summary-table',
                'updatedTimestamp': '2017-09-22T17:00:00Z',
            })
        self.assertRegex(
            html,
            r'^<div class="rb-c-review-request__field"'
            r'\s+id="issue-summary"')
        self.assertTrue(html.endswith('\n</div>'))

    def test_get_with_unicode(self):
        """Testing ReviewRequestUpdatesView GET with Unicode content"""
        # Add some Unicode content.
        self.review1.body_top = 'áéíóú'
        self.review1.save(update_fields=('body_top',))

        self.review2.body_top = 'ÄËÏÖÜŸ'
        self.review2.save(update_fields=('body_top',))

        self.general_comment.text = 'ĀĒĪŌ'
        self.general_comment.save(update_fields=('text',))

        updates = self._get_updates()
        self.assertEqual(len(updates), 4)

        metadata, html = updates[0]
        self.assertEqual(
            metadata,
            {
                'addedTimestamp': '2017-09-17T17:00:00Z',
                'entryID': '1',
                'entryType': 'review',
                'etag': '',
                'modelData': {
                    'reviewData': {
                        'authorName': 'dopey',
                        'id': self.review1.pk,
                        'public': True,
                        'bodyTop': self.review1.body_top,
                        'bodyBottom': self.review1.body_bottom,
                        'shipIt': self.review1.ship_it,
                    },
                },
                'type': 'entry',
                'updatedTimestamp': '2017-09-17T17:00:00Z',
                'viewOptions': {},
            })
        self.assertTrue(html.startswith('<div id="review1"'))
        self.assertTrue(html.endswith('\n</div>'))
        self.assertIn('áéíóú', html)

        metadata, html = updates[1]
        self.assertEqual(
            metadata,
            {
                'addedTimestamp': '2017-09-27T17:00:00Z',
                'entryID': '2',
                'entryType': 'review',
                'etag': '',
                'modelData': {
                    'reviewData': {
                        'authorName': 'dopey',
                        'id': self.review2.pk,
                        'public': True,
                        'bodyTop': self.review2.body_top,
                        'bodyBottom': self.review2.body_bottom,
                        'shipIt': self.review2.ship_it,
                    },
                },
                'type': 'entry',
                'updatedTimestamp': '2017-09-27T17:00:00Z',
                'viewOptions': {},
            })
        self.assertTrue(html.startswith('<div id="review2"'))
        self.assertTrue(html.endswith('\n</div>'))
        self.assertIn('ÄËÏÖÜŸ', html)

        metadata, html = updates[2]
        self.assertEqual(
            metadata,
            {
                'addedTimestamp': '2017-09-07T17:00:00Z',
                'entryID': '0',
                'entryType': 'initial_status_updates',
                'etag': '05a79f06cf3f67f726dae68d18a2290f6c9a50c9',
                'modelData': {
                    'pendingStatusUpdates': False,
                },
                'type': 'entry',
                'updatedTimestamp': '2017-09-07T17:00:00Z',
                'viewOptions': {},
            })
        self.assertTrue(html.startswith('<div id="initial_status_updates"'))
        self.assertTrue(html.endswith('\n</div>'))

        metadata, html = updates[3]
        self.assertEqual(
            metadata,
            {
                'type': 'issue-summary-table',
                'updatedTimestamp': self.general_comment.timestamp.strftime(
                    '%Y-%m-%dT%H:%M:%SZ'),
            })
        self.assertRegex(
            html,
            r'^<div class="rb-c-review-request__field"'
            r'\s+id="issue-summary"')
        self.assertTrue(html.endswith('\n</div>'))
        self.assertIn('ĀĒĪŌ', html)

    def test_get_with_entries(self):
        """Testing ReviewRequestUpdatesView GET with ?entries=..."""
        updates = self._get_updates({
            'entries': 'review:2;initial_status_updates:0',
        })
        self.assertEqual(len(updates), 3)

        metadata, html = updates[0]
        self.assertEqual(
            metadata,
            {
                'addedTimestamp': '2017-09-27T17:00:00Z',
                'entryID': '2',
                'entryType': 'review',
                'etag': '',
                'modelData': {
                    'reviewData': {
                        'authorName': 'dopey',
                        'id': self.review2.pk,
                        'public': True,
                        'bodyTop': self.review2.body_top,
                        'bodyBottom': self.review2.body_bottom,
                        'shipIt': self.review2.ship_it,
                    },
                },
                'type': 'entry',
                'updatedTimestamp': '2017-09-27T17:00:00Z',
                'viewOptions': {},
            })
        self.assertTrue(html.startswith('<div id="review2"'))
        self.assertTrue(html.endswith('\n</div>'))

        metadata, html = updates[1]
        self.assertEqual(
            metadata,
            {
                'addedTimestamp': '2017-09-07T17:00:00Z',
                'entryID': '0',
                'entryType': 'initial_status_updates',
                'etag': '05a79f06cf3f67f726dae68d18a2290f6c9a50c9',
                'modelData': {
                    'pendingStatusUpdates': False,
                },
                'type': 'entry',
                'updatedTimestamp': '2017-09-07T17:00:00Z',
                'viewOptions': {},
            })
        self.assertTrue(html.startswith('<div id="initial_status_updates"'))
        self.assertTrue(html.endswith('\n</div>'))

        # The issue summary table is always added when reviews have updates.
        metadata, html = updates[2]
        self.assertEqual(
            metadata,
            {
                'type': 'issue-summary-table',
                'updatedTimestamp': self.general_comment.timestamp.strftime(
                    '%Y-%m-%dT%H:%M:%SZ'),
            })
        self.assertRegex(
            html,
            r'^<div class="rb-c-review-request__field"'
            r'\s+id="issue-summary"')
        self.assertTrue(html.endswith('\n</div>'))

    def test_get_with_review_entries_adds_issue_summary_table(self):
        """Testing ReviewRequestUpdatesView GET with ?entries=review:...
        always includes the issue summary table
        """
        updates = self._get_updates({
            'entries': 'review:2',
        })
        self.assertEqual(len(updates), 2)

        metadata, html = updates[0]
        self.assertEqual(
            metadata,
            {
                'addedTimestamp': '2017-09-27T17:00:00Z',
                'entryID': '2',
                'entryType': 'review',
                'etag': '',
                'modelData': {
                    'reviewData': {
                        'authorName': 'dopey',
                        'id': self.review2.pk,
                        'public': True,
                        'bodyTop': self.review2.body_top,
                        'bodyBottom': self.review2.body_bottom,
                        'shipIt': self.review2.ship_it,
                    },
                },
                'type': 'entry',
                'updatedTimestamp': '2017-09-27T17:00:00Z',
                'viewOptions': {},
            })
        self.assertTrue(html.startswith('<div id="review2"'))
        self.assertTrue(html.endswith('\n</div>'))

        metadata, html = updates[1]
        self.assertEqual(
            metadata,
            {
                'type': 'issue-summary-table',
                'updatedTimestamp': self.general_comment.timestamp.strftime(
                    '%Y-%m-%dT%H:%M:%SZ'),
            })
        self.assertRegex(
            html,
            r'^<div class="rb-c-review-request__field"'
            r'\s+id="issue-summary"')
        self.assertTrue(html.endswith('\n</div>'))

    def test_get_with_invalid_entries(self):
        """Testing ReviewRequestUpdatesView GET with invalid ?entries=...
        values
        """
        response = self.client.get(self._build_url(), {
            'entries': 'review2',
        })
        self.assertEqual(response.status_code, 400)

    def test_get_with_since(self) -> None:
        """Testing ReviewRequestUpdatesView GET with ?since=..."""
        timestamp = self.review1.timestamp + timedelta(days=1)
        updates = self._get_updates({
            'since': timestamp.isoformat(),
        })
        self.assertEqual(len(updates), 2)

        metadata, html = updates[0]
        self.assertEqual(
            metadata,
            {
                'addedTimestamp': '2017-09-27T17:00:00Z',
                'entryID': '2',
                'entryType': 'review',
                'etag': '',
                'modelData': {
                    'reviewData': {
                        'authorName': 'dopey',
                        'id': self.review2.pk,
                        'public': True,
                        'bodyTop': self.review2.body_top,
                        'bodyBottom': self.review2.body_bottom,
                        'shipIt': self.review2.ship_it,
                    },
                },
                'type': 'entry',
                'updatedTimestamp': '2017-09-27T17:00:00Z',
                'viewOptions': {},
            })
        self.assertTrue(html.startswith('<div id="review2"'))
        self.assertTrue(html.endswith('\n</div>'))

        metadata, html = updates[1]
        self.assertEqual(
            metadata,
            {
                'type': 'issue-summary-table',
                'updatedTimestamp': self.general_comment.timestamp.strftime(
                    '%Y-%m-%dT%H:%M:%SZ'),
            })
        self.assertRegex(
            html,
            r'^<div class="rb-c-review-request__field"'
            r'\s+id="issue-summary"')
        self.assertTrue(html.endswith('\n</div>'))

    def test_get_with_since_and_review_no_issues(self) -> None:
        """Testing ReviewRequestUpdatesView GET with ?since=... and review
        with updates but no issues
        """
        timestamp = self.review1.timestamp + timedelta(days=8)
        updates = self._get_updates({
            'since': timestamp.isoformat(),
        })
        self.assertEqual(len(updates), 1)

        metadata, html = updates[0]
        self.assertEqual(
            metadata,
            {
                'addedTimestamp': '2017-09-27T17:00:00Z',
                'entryID': '2',
                'entryType': 'review',
                'etag': '',
                'modelData': {
                    'reviewData': {
                        'authorName': 'dopey',
                        'id': self.review2.pk,
                        'public': True,
                        'bodyTop': self.review2.body_top,
                        'bodyBottom': self.review2.body_bottom,
                        'shipIt': self.review2.ship_it,
                    },
                },
                'type': 'entry',
                'updatedTimestamp': '2017-09-27T17:00:00Z',
                'viewOptions': {},
            })
        self.assertTrue(html.startswith('<div id="review2"'))
        self.assertTrue(html.endswith('\n</div>'))

    def test_get_with_since_and_no_entries(self) -> None:
        """Testing ReviewRequestUpdatesView GET with ?since=... and no entries
        """
        timestamp = self.review1.timestamp + timedelta(days=30)
        updates = self._get_updates({
            'since': timestamp.isoformat(),
        })
        self.assertEqual(len(updates), 0)

    def test_post(self):
        """Testing ReviewRequestUpdatesView POST not allowed"""
        # 1 SQL query for SiteConfiguration in the middleware.
        with self.assertNumQueries(1):
            response = self.client.post(self._build_url())

        self.assertEqual(response.status_code, 405)

    def test_put(self):
        """Testing ReviewRequestUpdatesView PUT not allowed"""
        # 1 SQL query for SiteConfiguration in the middleware.
        with self.assertNumQueries(1):
            response = self.client.put(self._build_url())

        self.assertEqual(response.status_code, 405)

    def test_delete(self):
        """Testing ReviewRequestUpdatesView DELETE not allowed"""
        # 1 SQL query for SiteConfiguration in the middleware.
        with self.assertNumQueries(1):
            response = self.client.delete(self._build_url())

        self.assertEqual(response.status_code, 405)

    def _build_url(self):
        return reverse('review-request-updates',
                       args=[self.review_request.display_id])

    def _get_updates(self, query={}):
        response = self.client.get(self._build_url(), query)
        self.assertEqual(response.status_code, 200)

        content = response.content
        self.assertIs(type(content), bytes)

        i = 0
        updates = []

        while i < len(content):
            # Read the length of the metadata.
            metadata_len = struct.unpack_from('<L', content, i)[0]
            i += 4

            # Read the metadata.
            metadata = json.loads(content[i:i + metadata_len].decode('utf-8'))
            i += metadata_len

            # Read the length of the HTML.
            html_len = struct.unpack_from('<L', content, i)[0]
            i += 4

            # Read the HTML.
            html = content[i:i + html_len].decode('utf-8')
            i += html_len

            updates.append((metadata, html))

        return updates
