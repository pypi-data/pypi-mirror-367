# coding: utf-8
"""Unit tests for reviewboard.reviews.views.CommentDiffFragmentsView."""

import struct

from django.contrib.auth.models import User
from djblets.testing.decorators import add_fixtures

from reviewboard.site.urlresolvers import local_site_reverse
from reviewboard.testing.testcase import BaseFileDiffAncestorTests


class CommentDiffFragmentsViewTests(BaseFileDiffAncestorTests):
    """Unit tests for reviewboard.reviews.views.CommentDiffFragmentsView."""

    fixtures = ['test_users', 'test_scmtools']

    def setUp(self):
        super(CommentDiffFragmentsViewTests, self).setUp()

        self.repository = self.create_repository(tool_name='Test')

    def test_get_with_unpublished_review_request_not_owner(self):
        """Testing CommentDiffFragmentsView with unpublished review request and
        user is not the owner
        """
        user = User.objects.create_user(username='reviewer',
                                        password='reviewer',
                                        email='reviewer@example.com')

        review_request = self.create_review_request(repository=self.repository)
        diffset = self.create_diffset(review_request)
        filediff = self.create_filediff(diffset)

        review = self.create_review(review_request, user=user)
        comment1 = self.create_diff_comment(review, filediff)
        comment2 = self.create_diff_comment(review, filediff)

        self.assertTrue(self.client.login(username='reviewer',
                                          password='reviewer'))

        self._get_fragments(review_request,
                            [comment1.pk, comment2.pk],
                            expected_status=403)

    def test_get_with_unpublished_review_request_owner(self):
        """Testing CommentDiffFragmentsView with unpublished review request and
        user is the owner
        """
        user = User.objects.create_user(username='test-user',
                                        password='test-user',
                                        email='user@example.com')

        review_request = self.create_review_request(
            repository=self.repository,
            submitter=user)
        diffset = self.create_diffset(review_request)
        filediff = self.create_filediff(diffset)
        review_request.publish(user)

        review = self.create_review(review_request, user=user)
        comment1 = self.create_diff_comment(review, filediff)
        comment2 = self.create_diff_comment(review, filediff)
        review.publish()

        self.assertTrue(self.client.login(username='test-user',
                                          password='test-user'))

        fragments = self._get_fragments(review_request,
                                        [comment1.pk, comment2.pk])
        self.assertEqual(len(fragments), 2)
        self.assertEqual(fragments[0][0], comment1.pk)
        self.assertEqual(fragments[1][0], comment2.pk)

    @add_fixtures(['test_site'])
    def test_get_with_published_review_request_local_site_access(self):
        """Testing CommentDiffFragmentsView with published review request on
        a Local Site the user has access to
        """
        user = User.objects.create_user(username='test-user',
                                        password='test-user',
                                        email='user@example.com')

        review_request = self.create_review_request(
            repository=self.repository,
            with_local_site=True,
            publish=True)
        diffset = self.create_diffset(review_request)
        filediff = self.create_filediff(diffset)

        review = self.create_review(review_request)
        comment1 = self.create_diff_comment(review, filediff)
        comment2 = self.create_diff_comment(review, filediff)
        review.publish()

        review_request.local_site.users.add(user)

        self.assertTrue(self.client.login(username='test-user',
                                          password='test-user'))

        fragments = self._get_fragments(review_request,
                                        [comment1.pk, comment2.pk],
                                        local_site_name='local-site-1')
        self.assertEqual(len(fragments), 2)
        self.assertEqual(fragments[0][0], comment1.pk)
        self.assertEqual(fragments[1][0], comment2.pk)

    @add_fixtures(['test_site'])
    def test_get_with_published_review_request_local_site_no_access(self):
        """Testing CommentDiffFragmentsView with published review request on
        a Local Site the user does not have access to
        """
        User.objects.create_user(username='test-user',
                                 password='test-user',
                                 email='user@example.com')

        review_request = self.create_review_request(
            repository=self.repository,
            with_local_site=True,
            publish=True)
        diffset = self.create_diffset(review_request)
        filediff = self.create_filediff(diffset)

        review = self.create_review(review_request)
        comment1 = self.create_diff_comment(review, filediff)
        comment2 = self.create_diff_comment(review, filediff)
        review.publish()

        self.assertTrue(self.client.login(username='test-user',
                                          password='test-user'))

        self._get_fragments(review_request,
                            [comment1.pk, comment2.pk],
                            local_site_name='local-site-1',
                            expected_status=403)

    def test_get_with_unicode(self):
        """Testing CommentDiffFragmentsView with Unicode content"""
        user = User.objects.create(username='reviewer')

        review_request = self.create_review_request(
            repository=self.repository,
            publish=True)
        diffset = self.create_diffset(review_request)
        filediff = self.create_filediff(
            diffset,
            source_file='/data:áéíóú🔥',
            dest_file='/data:ÄËÏÖÜŸ',
            diff=(
                'diff --git a/data b/data\n'
                'index abcd123..abcd124 100644\n'
                '--- a/data\n'
                '+++ b/data\n'
                '@@ -1,1 +1,1 @@\n'
                '-áéíóú🔥\n'
                '+ÄËÏÖÜŸ\n'
            ).encode('utf-8'))

        review = self.create_review(review_request, user=user)
        comment1 = self.create_diff_comment(review, filediff)
        comment2 = self.create_diff_comment(review, filediff)
        review.publish()

        fragments = self._get_fragments(review_request,
                                        [comment1.pk, comment2.pk])
        self.assertEqual(len(fragments), 2)

        comment_id, html = fragments[0]
        self.assertEqual(comment_id, comment1.pk)
        self.assertTrue(html.startswith('<table class="sidebyside'))
        self.assertTrue(html.endswith('</table>'))
        self.assertIn('áéíóú🔥', html)

        comment_id, html = fragments[1]
        self.assertEqual(comment_id, comment2.pk)
        self.assertTrue(html.startswith('<table class="sidebyside'))
        self.assertTrue(html.endswith('</table>'))
        self.assertIn('ÄËÏÖÜŸ', html)

    def test_get_with_valid_comment_ids(self):
        """Testing CommentDiffFragmentsView with valid comment ID"""
        user = User.objects.create_user(username='reviewer',
                                        email='reviewer@example.com')

        review_request = self.create_review_request(
            repository=self.repository,
            publish=True)
        diffset = self.create_diffset(review_request)
        filediff = self.create_filediff(diffset)

        review = self.create_review(review_request, user=user)
        comment1 = self.create_diff_comment(review, filediff)
        comment2 = self.create_diff_comment(review, filediff)
        review.publish()

        fragments = self._get_fragments(review_request,
                                        [comment1.pk, comment2.pk])
        self.assertEqual(len(fragments), 2)
        self.assertEqual(fragments[0][0], comment1.pk)
        self.assertEqual(fragments[1][0], comment2.pk)

    def test_get_with_valid_and_invalid_comment_ids(self):
        """Testing CommentDiffFragmentsView with mix of valid comment IDs and
        comment IDs not found in database
        """
        user = User.objects.create_user(username='reviewer',
                                        email='reviewer@example.com')

        review_request = self.create_review_request(
            repository=self.repository,
            publish=True)
        diffset = self.create_diffset(review_request)
        filediff = self.create_filediff(diffset)

        review = self.create_review(review_request, user=user)
        comment = self.create_diff_comment(review, filediff)
        review.publish()

        fragments = self._get_fragments(review_request, [999, comment.pk])
        self.assertEqual(len(fragments), 1)
        self.assertEqual(fragments[0][0], comment.pk)

    def test_get_with_no_valid_comment_ids(self):
        """Testing CommentDiffFragmentsView with no valid comment IDs"""
        review_request = self.create_review_request(
            repository=self.repository,
            publish=True)

        self._get_fragments(review_request,
                            [100, 200, 300],
                            expected_status=404)

    def test_get_with_comment_ids_from_other_review_request(self):
        """Testing CommentDiffFragmentsView with comment ID from another review
        request
        """
        user = User.objects.create_user(username='reviewer',
                                        email='reviewer@example.com')

        # Create the first review request and review.
        review_request1 = self.create_review_request(
            repository=self.repository,
            publish=True)
        diffset = self.create_diffset(review_request1)
        filediff = self.create_filediff(diffset)

        review = self.create_review(review_request1, user=user)
        comment1 = self.create_diff_comment(review, filediff)
        review.publish()

        # Create the second review request and review.
        review_request2 = self.create_review_request(
            repository=self.repository,
            publish=True)
        diffset = self.create_diffset(review_request2)
        filediff = self.create_filediff(diffset)

        review = self.create_review(review_request2, user=user)
        comment2 = self.create_diff_comment(review, filediff)
        review.publish()

        fragments = self._get_fragments(review_request1,
                                        [comment1.pk, comment2.pk])
        self.assertEqual(len(fragments), 1)
        self.assertEqual(fragments[0][0], comment1.pk)

    def test_get_with_comment_ids_from_draft_review_owner(self):
        """Testing CommentDiffFragmentsView with comment ID from draft review,
        accessed by the review's owner
        """
        user = User.objects.create_user(username='reviewer',
                                        password='reviewer',
                                        email='reviewer@example.com')

        review_request1 = self.create_review_request(
            repository=self.repository,
            publish=True)
        diffset = self.create_diffset(review_request1)
        filediff = self.create_filediff(diffset)

        review = self.create_review(review_request1, user=user)
        comment = self.create_diff_comment(review, filediff)

        self.assertTrue(self.client.login(username='reviewer',
                                          password='reviewer'))

        fragments = self._get_fragments(review_request1, [comment.pk])
        self.assertEqual(len(fragments), 1)
        self.assertEqual(fragments[0][0], comment.pk)

    def test_get_with_comment_ids_from_draft_review_not_owner(self):
        """Testing CommentDiffFragmentsView with comment ID from draft review,
        accessed by someone other than the review's owner
        """
        user = User.objects.create_user(username='reviewer',
                                        email='reviewer@example.com')

        review_request1 = self.create_review_request(
            repository=self.repository,
            publish=True)
        diffset = self.create_diffset(review_request1)
        filediff = self.create_filediff(diffset)

        review = self.create_review(review_request1, user=user)
        comment = self.create_diff_comment(review, filediff)

        self._get_fragments(review_request1,
                            [comment.pk],
                            expected_status=404)

    def test_get_with_file_not_found_error(self):
        """Testing CommentDiffFragmentsView with FileNotFoundError"""
        user = User.objects.create_user(username='reviewer',
                                        email='reviewer@example.com')

        review_request = self.create_review_request(
            repository=self.repository,
            publish=True)
        diffset = self.create_diffset(review_request)
        filediff = self.create_filediff(diffset,
                                        source_file='bad:file-not-found',
                                        dest_file='bad:file-not-found')

        review = self.create_review(review_request, user=user)
        comment = self.create_diff_comment(review, filediff)
        review.publish()

        self._get_fragments(review_request,
                            [comment.pk],
                            expect_cacheable=False)

    def test_get_with_scmerror(self):
        """Testing CommentDiffFragmentsView with SCMError"""
        user = User.objects.create_user(username='reviewer',
                                        email='reviewer@example.com')

        review_request = self.create_review_request(
            repository=self.repository,
            publish=True)
        diffset = self.create_diffset(review_request)
        filediff = self.create_filediff(diffset,
                                        source_file='bad:scm-error',
                                        dest_file='bad:scm-error')

        review = self.create_review(review_request, user=user)
        comment = self.create_diff_comment(review, filediff)
        review.publish()

        self._get_fragments(review_request,
                            [comment.pk],
                            expect_cacheable=False)

    def _get_fragments(self, review_request, comment_ids,
                       local_site_name=None, expected_status=200,
                       expect_cacheable=True):
        """Load and return fragments from the server.

        Args:
            review_request (reviewboard.reviews.models.review_request.
                            ReviewRequest):
                The review request the comments were made on.

            comment_ids (list of int):
                The list of comment IDs to load.

            local_site_name (unicode, optional):
                The name of the Local Site for the URL.

            expected_status (int, optional):
                The expected HTTP status code. By default, this is a
                successful 200.

            expect_cacheable (bool, optional):
                Expect that the fragment is allowed to be cached by the
                browser. This will check the :mailheader:`Cache-Control`
                headers on the response.

        Returns:
            list of tuple:
            A list of ``(comment_id, html)`` from the parsed payload, if
            the status code was 200.
        """
        response = self.client.get(
            local_site_reverse(
                'diff-comment-fragments',
                kwargs={
                    'review_request_id': review_request.display_id,
                    'comment_ids': ','.join(
                        str(comment_id)
                        for comment_id in comment_ids
                    ),
                },
                local_site_name=local_site_name))
        self.assertEqual(response.status_code, expected_status)

        if expect_cacheable:
            self.assertFalse(response.has_header('Cache-Control'))
        else:
            self.assertTrue(response.has_header('Cache-Control'))
            self.assertEqual(
                set(response['Cache-Control'].split(', ')),
                {
                    'max-age=0',
                    'must-revalidate',
                    'no-cache',
                    'no-store',
                })

        if expected_status != 200:
            return None

        self.assertEqual(response['Content-type'], 'text/plain; charset=utf-8')

        content = response.content
        self.assertIs(type(content), bytes)

        i = 0
        results = []

        while i < len(content):
            # Read the comment ID.
            comment_id = struct.unpack_from('<L', content, i)[0]
            i += 4

            # Read the length of the HTML.
            html_len = struct.unpack_from('<L', content, i)[0]
            i += 4

            # Read the HTML.
            html = content[i:i + html_len].decode('utf-8')
            i += html_len

            results.append((comment_id, html))

        return results

    def test_comment_fragment_on_commit_range1(self) -> None:
        """Testing CommentDiffFragmentsView with a comment made on a commit
        range starting from the base commit
        """
        self._create_commit_comment_data()

        comment_id, html = self._get_fragments(
            self.review_request,
            [self.commit_comment1.pk])[0]

        # We don't have a great way of actually looking at diff content,
        # especially because these diffs are totally fake, but this is a good
        # proxy to ensure that we're rendering with the correct commit
        # information.
        self.assertIn(
            '<a href="/r/1/diff/1/?tip-commit-id=3#file7line1">bar</a>',
            html)

    def test_comment_fragment_on_commit_range2(self) -> None:
        """Testing CommentDiffFragmentsView with a comment made on a commit
        range starting from the base commit
        """
        self._create_commit_comment_data()

        comment_id, html = self._get_fragments(
            self.review_request,
            [self.commit_comment2.pk],
            expect_cacheable=False)[0]

        # We don't have a great way of actually looking at diff content,
        # especially because these diffs are totally fake, but this is a good
        # proxy to ensure that we're rendering with the correct commit
        # information.
        self.assertIn(
            '<a href="/r/1/diff/1/?base-commit-id=2&amp;'
            'tip-commit-id=3#file7line1">bar</a>',
            html)

    def test_diff_comment_links_with_commits(self) -> None:
        """Testing Comment.get_absolute_url with commit ranges"""
        self._create_commit_comment_data()

        self.assertEqual(
            self.cumulative_comment.get_absolute_url(),
            '/r/1/diff/1/?#file10line1')

        self.assertEqual(
            self.commit_comment1.get_absolute_url(),
            '/r/1/diff/1/?tip-commit-id=3#file7line1')

        self.assertEqual(
            self.commit_comment2.get_absolute_url(),
            '/r/1/diff/1/?base-commit-id=2&tip-commit-id=3#file7line1')

    def _create_commit_comment_data(self) -> None:
        """Create the test data for commit comments."""
        self.set_up_filediffs()

        review = self.create_review(review_request=self.review_request,
                                    publish=True)
        self.cumulative_comment = self.create_diff_comment(
            review=review,
            filediff=self.diffset.cumulative_files[0])

        commit1 = self.diff_commits[1]
        commit2 = self.diff_commits[2]

        # Comment from the base commit to a tip
        self.commit_comment1 = self.create_diff_comment(
            review=review,
            filediff=commit2.files.get(dest_file='bar'))

        # Comment from one commit to another
        self.commit_comment2 = self.create_diff_comment(
            review=review,
            filediff=commit2.files.get(dest_file='bar'))
        self.commit_comment2.base_filediff_id = \
            commit1.files.get(dest_file='bar').pk
        self.commit_comment2.save(update_fields=['extra_data'])
