"""Unit tests for reviewboard.reviews.builtin_fields."""

from django.contrib.auth.models import AnonymousUser, User
from django.db.models import Q
from django.test.client import RequestFactory
from django.urls import resolve
from django.utils.safestring import SafeText

from reviewboard.attachments.models import FileAttachment
from reviewboard.reviews.builtin_fields import (CommitListField,
                                                FileAttachmentsField)
from reviewboard.reviews.detail import ReviewRequestPageData
from reviewboard.reviews.models import ReviewRequestDraft
from reviewboard.testing.testcase import TestCase


class FieldsTestCase(TestCase):
    """Base test case for built-in fields."""

    field_cls = None

    def make_field(self, review_request):
        """Return an instance of the field to test with.

        The field will be populated with all review request page state.

        Args:
            review_request (reviewboard.reviews.models.review_request.
                            ReviewRequest):
                The review request being tested.

        Returns:
            reviewboard.reviews.fields.BaseReviewRequestField:
            The resulting field instance.
        """
        request = self.build_review_request_get(review_request)

        data = ReviewRequestPageData(review_request, request)
        data.query_data_pre_etag()
        data.query_data_post_etag()

        return self.field_cls(review_request, request=request, data=data)

    def build_review_request_get(self, review_request):
        """Return an HTTP GET request for the review request.

        This will return a new HTTP request to a review request's page,
        containing a resolver match, without actually fetching the page.

        Args:
            review_request (reviewboard.reviews.models.review_request.
                            ReviewRequest):
                The review request being tested.

        Returns:
            django.http.HttpRequest:
            The request for the review request detail page.
        """
        url = review_request.get_absolute_url()
        request = RequestFactory().get(url)
        request.user = AnonymousUser()
        request.resolver_match = resolve(url)

        return request


class CommitListFieldTests(FieldsTestCase):
    """Unit tests for CommitListField."""

    field_cls = CommitListField
    fixtures = ['test_scmtools', 'test_users']

    def test_should_render_history_review_request(self):
        """Testing CommitListField.should_render with a review request created
        with history
        """
        review_request = self.create_review_request(create_repository=True,
                                                    create_with_history=True)
        request = self.build_review_request_get(review_request)
        self.create_diffset(review_request)
        field = CommitListField(review_request, request=request)

        self.assertTrue(field.should_render)

    def test_should_render_history_draft(self):
        """Testing CommitListField.should_render with a draft of a review
        request created with history
        """
        review_request = self.create_review_request(create_repository=True,
                                                    create_with_history=True)
        self.create_diffset(review_request, draft=True)
        request = self.build_review_request_get(review_request)
        field = CommitListField(review_request.get_draft(), request=request)

        self.assertTrue(field.should_render)

    def test_should_render_no_history_review_request(self):
        """Testing CommitListField.should_render with a review request created
        without history
        """
        review_request = self.create_review_request()
        request = self.build_review_request_get(review_request)
        field = CommitListField(review_request, request=request)

        self.assertFalse(field.should_render)

    def test_should_render_no_history_draft(self):
        """Testing CommitListField.should_render with a draft of a review
        request created without history
        """
        review_request = self.create_review_request()
        draft = ReviewRequestDraft.create(review_request)
        request = self.build_review_request_get(review_request)
        field = CommitListField(draft, request=request)

        self.assertFalse(field.should_render)

    def test_should_render_with_no_value(self):
        """Testing CommitListField.should_render with no value"""
        review_request = self.create_review_request(create_with_history=True)
        draft = ReviewRequestDraft.create(review_request)
        request = self.build_review_request_get(review_request)
        field = CommitListField(draft, request=request)

        self.assertFalse(field.should_render)

    def test_can_record_change_entry_history_review_request(self):
        """Testing CommitListField.can_record_change_entry with a review
        request created with history
        """
        review_request = self.create_review_request(create_with_history=True)
        field = CommitListField(review_request)

        self.assertTrue(field.can_record_change_entry)

    def test_can_record_change_entry_history_draft(self):
        """Testing CommitListField.can_record_change_entry with a draft of a
        review request created with history
        """
        review_request = self.create_review_request(create_with_history=True)
        draft = ReviewRequestDraft.create(review_request)
        field = CommitListField(draft)

        self.assertTrue(field.can_record_change_entry)

    def test_can_record_change_entry_no_history_review_request(self):
        """Testing CommitListField.can_record_change_entry with a review
        request created without history
        """
        review_request = self.create_review_request()
        field = CommitListField(review_request)

        self.assertFalse(field.can_record_change_entry)

    def test_can_record_change_entry_no_history_draft(self):
        """Testing CommitListField.can_record_change_entry with a draft of a
        review request created without history
        """
        review_request = self.create_review_request()
        draft = ReviewRequestDraft.create(review_request)
        field = CommitListField(draft)

        self.assertFalse(field.can_record_change_entry)

    def test_render_value(self):
        """Testing CommitListField.render_value"""
        repository = self.create_repository(tool_name='Git')
        review_request = self.create_review_request(repository=repository,
                                                    create_with_history=True)
        diffset = self.create_diffset(review_request)

        author_name = review_request.submitter.get_full_name()
        self.assertEqual(author_name, 'Doc Dwarf')

        self.create_diffcommit(diffset=diffset,
                               commit_id='r1',
                               parent_id='r0',
                               commit_message='Commit message 1',
                               author_name=author_name)
        self.create_diffcommit(diffset=diffset,
                               commit_id='r2',
                               parent_id='r1',
                               commit_message='Commit message 2',
                               author_name=author_name)

        field = self.make_field(review_request)
        result = field.render_value(field.load_value(review_request))

        self.assertHTMLEqual(
            result,
            """
            <div class="rb-c-review-request-field-tabular rb-c-commit-list">
             <table class="rb-c-review-request-field-tabular__data">
              <thead>
               <tr>
                <th class="rb-c-commit-list__column-summary">Summary</th>
                <th class="rb-c-commit-list__column-id">ID</th>
               </tr>
              </thead>
              <tbody>
               <tr class="rb-c-commit-list__commit">
                <td class="rb-c-commit-list__message">
                 <div class="rb-c-commit-list__message-summary">Commit
                  message 1</div>
                </td>
                <td class="rb-c-commit-list__id" title="r1">r1</td>
               </tr>

               <tr class="rb-c-commit-list__commit">
                <td class="rb-c-commit-list__message">
                 <div class="rb-c-commit-list__message-summary">Commit
                  message 2</div>
                </td>
                <td class="rb-c-commit-list__id" title="r2">r2</td>
               </tr>
              </tbody>
             </table>
            </div>
            """)

    def test_render_value_with_author(self):
        """Testing CommitListField.render_value with an author that differs
        from the review request submitter
        """
        repository = self.create_repository(tool_name='Git')
        review_request = self.create_review_request(repository=repository,
                                                    create_with_history=True)
        diffset = self.create_diffset(review_request)

        submitter_name = review_request.submitter.get_full_name()
        self.assertEqual(submitter_name, 'Doc Dwarf')

        self.create_diffcommit(diffset=diffset,
                               commit_id='r1',
                               parent_id='r0',
                               commit_message='Commit message 1',
                               author_name='Example Author')
        self.create_diffcommit(diffset=diffset,
                               commit_id='r2',
                               parent_id='r1',
                               commit_message='Commit message 2',
                               author_name=submitter_name)

        field = self.make_field(review_request)
        result = field.render_value(field.load_value(review_request))

        self.assertHTMLEqual(
            result,
            """
            <div class="rb-c-review-request-field-tabular rb-c-commit-list">
             <table class="rb-c-review-request-field-tabular__data">
              <thead>
               <tr>
                <th class="rb-c-commit-list__column-summary">Summary</th>
                <th class="rb-c-commit-list__column-id">ID</th>
                <th class="rb-c-commit-list__column-author">Author</th>
               </tr>
              </thead>
              <tbody>
               <tr class="rb-c-commit-list__commit">
                <td class="rb-c-commit-list__message">
                 <div class="rb-c-commit-list__message-summary">Commit
                  message 1</div>
                </td>
                <td class="rb-c-commit-list__id" title="r1">r1</td>
                <td class="rb-c-commit-list__author">Example Author</td>
               </tr>

               <tr class="rb-c-commit-list__commit">
                <td class="rb-c-commit-list__message">
                 <div class="rb-c-commit-list__message-summary">Commit
                  message 2</div>
                </td>
                <td class="rb-c-commit-list__id" title="r2">r2</td>
                <td class="rb-c-commit-list__author">Doc Dwarf</td>
               </tr>
              </tbody>
             </table>
            </div>
            """)

    def test_render_value_with_collapse(self):
        """Testing CommitListField.render_value with a multi-line commit
        message
        """
        repository = self.create_repository(tool_name='Git')
        review_request = self.create_review_request(repository=repository,
                                                    create_with_history=True)
        diffset = self.create_diffset(review_request)

        author_name = review_request.submitter.get_full_name()
        self.assertEqual(author_name, 'Doc Dwarf')

        self.create_diffcommit(diffset=diffset,
                               commit_id='r1',
                               parent_id='r0',
                               commit_message='Commit message 1',
                               author_name=author_name)
        self.create_diffcommit(diffset=diffset,
                               commit_id='r2',
                               parent_id='r1',
                               commit_message='Commit message 2\n'
                                              'Longer message\n',
                               author_name=author_name)

        field = self.make_field(review_request)
        result = field.render_value(field.load_value(review_request))

        self.assertHTMLEqual(
            result,
            """
            <div class="rb-c-review-request-field-tabular rb-c-commit-list">
             <table class="rb-c-review-request-field-tabular__data">
              <thead>
               <tr>
                <th class="rb-c-commit-list__column-summary">Summary</th>
                <th class="rb-c-commit-list__column-id">ID</th>
               </tr>
              </thead>
              <tbody>
               <tr class="rb-c-commit-list__commit">
                <td class="rb-c-commit-list__message">
                 <div class="rb-c-commit-list__message-summary">Commit
                  message 1</div>
                </td>
                <td class="rb-c-commit-list__id" title="r1">r1</td>
               </tr>

               <tr class="rb-c-commit-list__commit">
                <td class="rb-c-commit-list__message">
                 <details>
                  <summary class="rb-c-commit-list__message-summary">Commit
                   message 2</summary>
                  <div class="rb-c-commit-list__message-body">Longer
                   message</div>
                 </details>
                </td>
                <td class="rb-c-commit-list__id" title="r2">r2</td>
               </tr>
              </tbody>
             </table>
            </div>
            """)

    def test_render_value_with_collapse_and_author(self):
        """Testing CommitListField.render_value with an author that differs
        from the review request submitter and a multi-line commit message
        """
        repository = self.create_repository(tool_name='Git')
        review_request = self.create_review_request(repository=repository,
                                                    create_with_history=True)
        diffset = self.create_diffset(review_request)

        submitter_name = review_request.submitter.get_full_name()
        self.assertEqual(submitter_name, 'Doc Dwarf')

        self.create_diffcommit(diffset=diffset,
                               commit_id='r1',
                               parent_id='r0',
                               commit_message='Commit message 1',
                               author_name='Example Author')
        self.create_diffcommit(diffset=diffset,
                               commit_id='r2',
                               parent_id='r1',
                               commit_message='Commit message 2\n'
                                              'Longer message\n',
                               author_name=submitter_name)

        field = self.make_field(review_request)
        result = field.render_value(field.load_value(review_request))

        self.assertHTMLEqual(
            result,
            """
            <div class="rb-c-review-request-field-tabular rb-c-commit-list">
             <table class="rb-c-review-request-field-tabular__data">
              <thead>
               <tr>
                <th class="rb-c-commit-list__column-summary">Summary</th>
                <th class="rb-c-commit-list__column-id">ID</th>
                <th class="rb-c-commit-list__column-author">Author</th>
               </tr>
              </thead>
              <tbody>
               <tr class="rb-c-commit-list__commit">
                <td class="rb-c-commit-list__message">
                 <div class="rb-c-commit-list__message-summary">Commit
                  message 1</div>
                </td>
                <td class="rb-c-commit-list__id" title="r1">r1</td>
                <td class="rb-c-commit-list__author">Example Author</td>
               </tr>

               <tr class="rb-c-commit-list__commit">
                <td class="rb-c-commit-list__message">
                 <details>
                  <summary class="rb-c-commit-list__message-summary">Commit
                   message 2</summary>
                  <div class="rb-c-commit-list__message-body">Longer
                   message</div>
                 </details>
                </td>
                <td class="rb-c-commit-list__id" title="r2">r2</td>
                <td class="rb-c-commit-list__author">Doc Dwarf</td>
               </tr>
              </tbody>
             </table>
            </div>
            """)

    def test_render_change_entry_html(self):
        """Testing CommitListField.render_change_entry_html"""
        target = User.objects.get(username='doc')
        repository = self.create_repository(tool_name='Git')
        review_request = self.create_review_request(repository=repository,
                                                    target_people=[target],
                                                    public=True,
                                                    create_with_history=True)
        diffset = self.create_diffset(review_request)

        author_name = review_request.submitter.get_full_name()

        self.create_diffcommit(diffset=diffset,
                               commit_id='r1',
                               parent_id='r0',
                               commit_message='Commit message 1',
                               author_name=author_name)
        self.create_diffcommit(diffset=diffset,
                               commit_id='r2',
                               parent_id='r1',
                               commit_message='Commit message 2',
                               author_name=author_name)

        draft_diffset = self.create_diffset(review_request, draft=True)
        self.create_diffcommit(diffset=draft_diffset,
                               commit_id='r1',
                               parent_id='r0',
                               commit_message='New commit message 1',
                               author_name=author_name)

        self.create_diffcommit(diffset=draft_diffset,
                               commit_id='r2',
                               parent_id='r1',
                               commit_message='New commit message 2',
                               author_name=author_name)

        draft_diffset.finalize_commit_series(
            cumulative_diff=self.DEFAULT_GIT_FILEDIFF_DATA_DIFF,
            validation_info=None,
            validate=False,
            save=True)

        review_request.publish(user=review_request.submitter)
        changedesc = review_request.changedescs.latest()

        field = self.make_field(review_request)
        result = field.render_change_entry_html(
            changedesc.fields_changed[field.field_id])

        self.assertHTMLEqual(
            result,
            """
            <div class="commit-list-container">
             <div class="rb-c-review-request-field-tabular rb-c-commit-list">
              <table class="rb-c-review-request-field-tabular__data">
               <thead>
                <tr>
                 <th class="rb-c-commit-list__column-op"></th>
                 <th class="rb-c-commit-list__column-summary">Summary</th>
                 <th class="rb-c-commit-list__column-id">ID</th>
                </tr>
               </thead>
               <tbody>
                <tr class="rb-c-commit-list__commit -is-removed">
                 <td class="rb-c-commit-list__op"
                     aria-label="Removed commit"></td>
                 <td class="rb-c-commit-list__message">
                  <div class="rb-c-commit-list__message-summary">Commit
                   message 1</div>
                 </td>
                 <td class="rb-c-commit-list__id" title="r1">r1</td>
                </tr>

                <tr class="rb-c-commit-list__commit -is-removed">
                 <td class="rb-c-commit-list__op"
                     aria-label="Removed commit"></td>
                 <td class="rb-c-commit-list__message">
                  <div class="rb-c-commit-list__message-summary">Commit
                   message 2</div>
                 </td>
                 <td class="rb-c-commit-list__id" title="r2">r2</td>
                </tr>

                <tr class="rb-c-commit-list__commit -is-added">
                 <td class="rb-c-commit-list__op"
                     aria-label="Added commit"></td>
                 <td class="rb-c-commit-list__message">
                  <div class="rb-c-commit-list__message-summary">New
                   commit message 1</div>
                 </td>
                 <td class="rb-c-commit-list__id" title="r1">r1</td>
                </tr>

                <tr class="rb-c-commit-list__commit -is-added">
                 <td class="rb-c-commit-list__op"
                     aria-label="Added commit"></td>
                 <td class="rb-c-commit-list__message">
                  <div class="rb-c-commit-list__message-summary">New
                   commit message 2</div>
                 </td>
                 <td class="rb-c-commit-list__id" title="r2">r2</td>
                </tr>
               </tbody>
              </table>
             </div>
            """)

    def test_render_change_entry_html_expand(self):
        """Testing CommitListField.render_change_entry_html with a multi-line
        commit message
        """
        target = User.objects.get(username='doc')
        repository = self.create_repository(tool_name='Git')
        review_request = self.create_review_request(repository=repository,
                                                    target_people=[target],
                                                    public=True,
                                                    create_with_history=True)
        diffset = self.create_diffset(review_request)

        author_name = review_request.submitter.get_full_name()

        self.create_diffcommit(diffset=diffset,
                               commit_id='r1',
                               parent_id='r0',
                               commit_message='Commit message 1\n\n'
                                              'A long message.\n',
                               author_name=author_name)
        self.create_diffcommit(diffset=diffset,
                               commit_id='r2',
                               parent_id='r1',
                               commit_message='Commit message 2',
                               author_name=author_name)

        draft_diffset = self.create_diffset(review_request, draft=True)
        self.create_diffcommit(diffset=draft_diffset,
                               commit_id='r1',
                               parent_id='r0',
                               commit_message='New commit message 1',
                               author_name=author_name)

        self.create_diffcommit(diffset=draft_diffset,
                               commit_id='r2',
                               parent_id='r1',
                               commit_message='New commit message 2\n\n'
                                              'So very long of a message.\n',
                               author_name=author_name)

        draft_diffset.finalize_commit_series(
            cumulative_diff=self.DEFAULT_GIT_FILEDIFF_DATA_DIFF,
            validation_info=None,
            validate=False,
            save=True)

        review_request.publish(user=review_request.submitter)
        changedesc = review_request.changedescs.latest()

        field = self.make_field(review_request)
        result = field.render_change_entry_html(
            changedesc.fields_changed[field.field_id])

        self.assertHTMLEqual(
            result,
            """
            <div class="commit-list-container">
             <div class="rb-c-review-request-field-tabular rb-c-commit-list">
              <table class="rb-c-review-request-field-tabular__data">
               <thead>
                <tr>
                 <th class="rb-c-commit-list__column-op"></th>
                 <th class="rb-c-commit-list__column-summary">Summary</th>
                 <th class="rb-c-commit-list__column-id">ID</th>
                </tr>
               </thead>
               <tbody>
                <tr class="rb-c-commit-list__commit -is-removed">
                 <td class="rb-c-commit-list__op"
                     aria-label="Removed commit"></td>
                 <td class="rb-c-commit-list__message">
                  <details>
                   <summary class="rb-c-commit-list__message-summary">Commit
                    message 1</summary>
                   <div class="rb-c-commit-list__message-body">A long
                    message.</div>
                  </details>
                 </td>
                 <td class="rb-c-commit-list__id" title="r1">r1</td>
                </tr>

                <tr class="rb-c-commit-list__commit -is-removed">
                 <td class="rb-c-commit-list__op"
                     aria-label="Removed commit"></td>
                 <td class="rb-c-commit-list__message">
                  <div class="rb-c-commit-list__message-summary">Commit
                   message 2</div>
                 </td>
                 <td class="rb-c-commit-list__id" title="r2">r2</td>
                </tr>

                <tr class="rb-c-commit-list__commit -is-added">
                 <td class="rb-c-commit-list__op"
                     aria-label="Added commit"></td>
                 <td class="rb-c-commit-list__message">
                  <div class="rb-c-commit-list__message-summary">New commit
                   message 1</div>
                 </td>
                 <td class="rb-c-commit-list__id" title="r1">r1</td>
                </tr>

                <tr class="rb-c-commit-list__commit -is-added">
                 <td class="rb-c-commit-list__op"
                     aria-label="Added commit"></td>
                 <td class="rb-c-commit-list__message">
                  <details>
                   <summary class="rb-c-commit-list__message-summary">New
                    commit message 2</summary>
                   <div class="rb-c-commit-list__message-body">So very long
                    of a message.</div>
                  </details>
                 </td>
                 <td class="rb-c-commit-list__id" title="r2">r2</td>
                </tr>
               </tbody>
              </table>
             </div>
            </div>
            """)

    def test_render_change_entry_html_expand_with_author(self):
        """Testing CommitListField.render_change_entry_html with an author that
        differs from the review request submitter and a multi-line commit
        message
        """
        target = User.objects.get(username='doc')
        repository = self.create_repository(tool_name='Git')
        review_request = self.create_review_request(repository=repository,
                                                    target_people=[target],
                                                    public=True,
                                                    create_with_history=True)
        diffset = self.create_diffset(review_request)

        submitter_name = review_request.submitter.get_full_name()
        self.assertEqual(submitter_name, 'Doc Dwarf')

        self.create_diffcommit(diffset=diffset,
                               commit_id='r1',
                               parent_id='r0',
                               commit_message='Commit message 1\n\n'
                                              'A long message.\n',
                               author_name='Example Author')
        self.create_diffcommit(diffset=diffset,
                               commit_id='r2',
                               parent_id='r1',
                               commit_message='Commit message 2',
                               author_name=submitter_name)

        draft_diffset = self.create_diffset(review_request, draft=True)
        self.create_diffcommit(diffset=draft_diffset,
                               commit_id='r1',
                               parent_id='r0',
                               commit_message='New commit message 1',
                               author_name=submitter_name)

        self.create_diffcommit(diffset=draft_diffset,
                               commit_id='r2',
                               parent_id='r1',
                               commit_message='New commit message 2\n\n'
                                              'So very long of a message.\n',
                               author_name=submitter_name)

        draft_diffset.finalize_commit_series(
            cumulative_diff=self.DEFAULT_GIT_FILEDIFF_DATA_DIFF,
            validation_info=None,
            validate=False,
            save=True)

        review_request.publish(user=review_request.submitter)
        changedesc = review_request.changedescs.latest()

        field = self.make_field(review_request)
        result = field.render_change_entry_html(
            changedesc.fields_changed[field.field_id])

        self.assertHTMLEqual(
            result,
            """
            <div class="commit-list-container">
             <div class="rb-c-review-request-field-tabular rb-c-commit-list">
              <table class="rb-c-review-request-field-tabular__data">
               <thead>
                <tr>
                 <th class="rb-c-commit-list__column-op"></th>
                 <th class="rb-c-commit-list__column-summary">Summary</th>
                 <th class="rb-c-commit-list__column-id">ID</th>
                 <th class="rb-c-commit-list__column-author">Author</th>
                </tr>
               </thead>
               <tbody>
                <tr class="rb-c-commit-list__commit -is-removed">
                 <td class="rb-c-commit-list__op"
                     aria-label="Removed commit"></td>
                 <td class="rb-c-commit-list__message">
                  <details>
                   <summary class="rb-c-commit-list__message-summary">Commit
                    message 1</summary>
                   <div class="rb-c-commit-list__message-body">A long
                    message.</div>
                  </details>
                 </td>
                 <td class="rb-c-commit-list__id" title="r1">r1</td>
                 <td class="rb-c-commit-list__author">Example Author</td>
                </tr>

                <tr class="rb-c-commit-list__commit -is-removed">
                 <td class="rb-c-commit-list__op"
                     aria-label="Removed commit"></td>
                 <td class="rb-c-commit-list__message">
                  <div class="rb-c-commit-list__message-summary">Commit
                   message 2</div>
                 </td>
                 <td class="rb-c-commit-list__id" title="r2">r2</td>
                 <td class="rb-c-commit-list__author">Doc Dwarf</td>
                </tr>

                <tr class="rb-c-commit-list__commit -is-added">
                 <td class="rb-c-commit-list__op"
                     aria-label="Added commit"></td>
                 <td class="rb-c-commit-list__message">
                  <div class="rb-c-commit-list__message-summary">New commit
                   message 1</div>
                 </td>
                 <td class="rb-c-commit-list__id" title="r1">r1</td>
                 <td class="rb-c-commit-list__author">Doc Dwarf</td>
                </tr>

                <tr class="rb-c-commit-list__commit -is-added">
                 <td class="rb-c-commit-list__op"
                     aria-label="Added commit"></td>
                 <td class="rb-c-commit-list__message">
                  <details>
                   <summary class="rb-c-commit-list__message-summary">New
                    commit message 2</summary>
                   <div class="rb-c-commit-list__message-body">So very long
                    of a message.</div>
                  </details>
                 </td>
                 <td class="rb-c-commit-list__id" title="r2">r2</td>
                 <td class="rb-c-commit-list__author">Doc Dwarf</td>
                </tr>
               </tbody>
              </table>
             </div>
            </div>
            """)

    def test_render_change_entry_html_with_author_old(self):
        """Testing CommitListField.render_change_entry_html with an author that
        differs from the review request submitter in the old commits
        """
        target = User.objects.get(username='doc')
        repository = self.create_repository(tool_name='Git')
        review_request = self.create_review_request(repository=repository,
                                                    target_people=[target],
                                                    public=True,
                                                    create_with_history=True)
        diffset = self.create_diffset(review_request)

        submitter_name = review_request.submitter.get_full_name()
        self.assertEqual(submitter_name, 'Doc Dwarf')

        self.create_diffcommit(diffset=diffset,
                               commit_id='r1',
                               parent_id='r0',
                               commit_message='Commit message 1',
                               author_name='Example Author')
        self.create_diffcommit(diffset=diffset,
                               commit_id='r2',
                               parent_id='r1',
                               commit_message='Commit message 2',
                               author_name=submitter_name)

        draft_diffset = self.create_diffset(review_request, draft=True)
        self.create_diffcommit(diffset=draft_diffset,
                               commit_id='r1',
                               parent_id='r0',
                               commit_message='New commit message 1',
                               author_name=submitter_name)

        self.create_diffcommit(diffset=draft_diffset,
                               commit_id='r2',
                               parent_id='r1',
                               commit_message='New commit message 2',
                               author_name=submitter_name)

        draft_diffset.finalize_commit_series(
            cumulative_diff=self.DEFAULT_GIT_FILEDIFF_DATA_DIFF,
            validation_info=None,
            validate=False,
            save=True)

        review_request.publish(user=review_request.submitter)
        changedesc = review_request.changedescs.latest()

        field = self.make_field(review_request)
        result = field.render_change_entry_html(
            changedesc.fields_changed[field.field_id])

        self.assertHTMLEqual(
            result,
            """
            <div class="commit-list-container">
             <div class="rb-c-review-request-field-tabular rb-c-commit-list">
              <table class="rb-c-review-request-field-tabular__data">
               <thead>
                <tr>
                 <th class="rb-c-commit-list__column-op"></th>
                 <th class="rb-c-commit-list__column-summary">Summary</th>
                 <th class="rb-c-commit-list__column-id">ID</th>
                 <th class="rb-c-commit-list__column-author">Author</th>
                </tr>
               </thead>
               <tbody>
                <tr class="rb-c-commit-list__commit -is-removed">
                 <td class="rb-c-commit-list__op"
                     aria-label="Removed commit"></td>
                 <td class="rb-c-commit-list__message">
                  <div class="rb-c-commit-list__message-summary">Commit
                   message 1</div>
                 </td>
                 <td class="rb-c-commit-list__id" title="r1">r1</td>
                 <td class="rb-c-commit-list__author">Example Author</td>
                </tr>

                <tr class="rb-c-commit-list__commit -is-removed">
                 <td class="rb-c-commit-list__op"
                     aria-label="Removed commit"></td>
                 <td class="rb-c-commit-list__message">
                  <div class="rb-c-commit-list__message-summary">Commit
                   message 2</div>
                 </td>
                 <td class="rb-c-commit-list__id" title="r2">r2</td>
                 <td class="rb-c-commit-list__author">Doc Dwarf</td>
                </tr>

                <tr class="rb-c-commit-list__commit -is-added">
                 <td class="rb-c-commit-list__op"
                     aria-label="Added commit"></td>
                 <td class="rb-c-commit-list__message">
                  <div class="rb-c-commit-list__message-summary">New
                   commit message 1</div>
                 </td>
                 <td class="rb-c-commit-list__id" title="r1">r1</td>
                 <td class="rb-c-commit-list__author">Doc Dwarf</td>
                </tr>

                <tr class="rb-c-commit-list__commit -is-added">
                 <td class="rb-c-commit-list__op"
                     aria-label="Added commit"></td>
                 <td class="rb-c-commit-list__message">
                  <div class="rb-c-commit-list__message-summary">New
                   commit message 2</div>
                 </td>
                 <td class="rb-c-commit-list__id" title="r2">r2</td>
                 <td class="rb-c-commit-list__author">Doc Dwarf</td>
                </tr>
               </tbody>
              </table>
             </div>
            </div>
            """)

    def test_render_change_entry_html_with_author_new(self):
        """Testing CommitListField.render_change_entry_html with an author that
        differs from the review request submitter in the new commits
        """
        target = User.objects.get(username='doc')
        repository = self.create_repository(tool_name='Git')
        review_request = self.create_review_request(repository=repository,
                                                    target_people=[target],
                                                    public=True,
                                                    create_with_history=True)
        diffset = self.create_diffset(review_request)

        submitter_name = review_request.submitter.get_full_name()
        self.assertEqual(submitter_name, 'Doc Dwarf')

        self.create_diffcommit(diffset=diffset,
                               commit_id='r1',
                               parent_id='r0',
                               commit_message='Commit message 1',
                               author_name=submitter_name)
        self.create_diffcommit(diffset=diffset,
                               commit_id='r2',
                               parent_id='r1',
                               commit_message='Commit message 2',
                               author_name=submitter_name)

        draft_diffset = self.create_diffset(review_request, draft=True)
        self.create_diffcommit(diffset=draft_diffset,
                               commit_id='r1',
                               parent_id='r0',
                               commit_message='New commit message 1',
                               author_name=submitter_name)

        self.create_diffcommit(diffset=draft_diffset,
                               commit_id='r2',
                               parent_id='r1',
                               commit_message='New commit message 2',
                               author_name='Example Author')

        draft_diffset.finalize_commit_series(
            cumulative_diff=self.DEFAULT_GIT_FILEDIFF_DATA_DIFF,
            validation_info=None,
            validate=False,
            save=True)

        review_request.publish(user=review_request.submitter)
        changedesc = review_request.changedescs.latest()

        field = self.make_field(review_request)
        result = field.render_change_entry_html(
            changedesc.fields_changed[field.field_id])

        self.assertHTMLEqual(
            result,
            """
            <div class="commit-list-container">
             <div class="rb-c-review-request-field-tabular rb-c-commit-list">
              <table class="rb-c-review-request-field-tabular__data">
               <thead>
                <tr>
                 <th class="rb-c-commit-list__column-op"></th>
                 <th class="rb-c-commit-list__column-summary">Summary</th>
                 <th class="rb-c-commit-list__column-id">ID</th>
                 <th class="rb-c-commit-list__column-author">Author</th>
                </tr>
               </thead>
               <tbody>
                <tr class="rb-c-commit-list__commit -is-removed">
                 <td class="rb-c-commit-list__op"
                     aria-label="Removed commit"></td>
                 <td class="rb-c-commit-list__message">
                  <div class="rb-c-commit-list__message-summary">Commit
                   message 1</div>
                 </td>
                 <td class="rb-c-commit-list__id" title="r1">r1</td>
                 <td class="rb-c-commit-list__author">Doc Dwarf</td>
                </tr>

                <tr class="rb-c-commit-list__commit -is-removed">
                 <td class="rb-c-commit-list__op"
                     aria-label="Removed commit"></td>
                 <td class="rb-c-commit-list__message">
                  <div class="rb-c-commit-list__message-summary">Commit
                   message 2</div>
                 </td>
                 <td class="rb-c-commit-list__id" title="r2">r2</td>
                 <td class="rb-c-commit-list__author">Doc Dwarf</td>
                </tr>

                <tr class="rb-c-commit-list__commit -is-added">
                 <td class="rb-c-commit-list__op"
                     aria-label="Added commit"></td>
                 <td class="rb-c-commit-list__message">
                  <div class="rb-c-commit-list__message-summary">New
                   commit message 1</div>
                 </td>
                 <td class="rb-c-commit-list__id" title="r1">r1</td>
                 <td class="rb-c-commit-list__author">Doc Dwarf</td>
                </tr>

                <tr class="rb-c-commit-list__commit -is-added">
                 <td class="rb-c-commit-list__op"
                     aria-label="Added commit"></td>
                 <td class="rb-c-commit-list__message">
                  <div class="rb-c-commit-list__message-summary">New
                   commit message 2</div>
                 </td>
                 <td class="rb-c-commit-list__id" title="r2">r2</td>
                 <td class="rb-c-commit-list__author">Example Author</td>
                </tr>
               </tbody>
              </table>
             </div>
            </div>
            """)

    def test_render_change_entry_html_first_diffset(self):
        """Testing CommitListfield.render_change_entry_html with a change that
        adds the first diffset
        """
        target = User.objects.get(username='doc')
        repository = self.create_repository(tool_name='Git')
        review_request = self.create_review_request(repository=repository,
                                                    target_people=[target],
                                                    public=True,
                                                    create_with_history=True)
        author_name = review_request.submitter.get_full_name()
        self.assertEqual(author_name, 'Doc Dwarf')

        draft_diffset = self.create_diffset(review_request, draft=True)
        self.create_diffcommit(diffset=draft_diffset,
                               commit_id='r1',
                               parent_id='r0',
                               commit_message='New commit message 1',
                               author_name=author_name)

        self.create_diffcommit(diffset=draft_diffset,
                               commit_id='r2',
                               parent_id='r1',
                               commit_message='New commit message 2',
                               author_name=author_name)

        draft_diffset.finalize_commit_series(
            cumulative_diff=self.DEFAULT_GIT_FILEDIFF_DATA_DIFF,
            validation_info=None,
            validate=False,
            save=True)

        review_request.publish(user=review_request.submitter)
        changedesc = review_request.changedescs.latest()

        field = self.make_field(review_request)
        result = field.render_change_entry_html(
            changedesc.fields_changed[field.field_id])

        self.assertHTMLEqual(
            result,
            """
            <div class="commit-list-container">
             <div class="rb-c-review-request-field-tabular rb-c-commit-list">
              <table class="rb-c-review-request-field-tabular__data">
               <thead>
                <tr>
                 <th class="rb-c-commit-list__column-op"></th>
                 <th class="rb-c-commit-list__column-summary">Summary</th>
                 <th class="rb-c-commit-list__column-id">ID</th>
                </tr>
               </thead>
               <tbody>
                <tr class="rb-c-commit-list__commit -is-added">
                 <td class="rb-c-commit-list__op"
                     aria-label="Added commit"></td>
                 <td class="rb-c-commit-list__message">
                  <div class="rb-c-commit-list__message-summary">New
                   commit message 1</div>
                 </td>
                 <td class="rb-c-commit-list__id" title="r1">r1</td>
                </tr>

                <tr class="rb-c-commit-list__commit -is-added">
                 <td class="rb-c-commit-list__op"
                     aria-label="Added commit"></td>
                 <td class="rb-c-commit-list__message">
                  <div class="rb-c-commit-list__message-summary">New
                   commit message 2</div>
                 </td>
                 <td class="rb-c-commit-list__id" title="r2">r2</td>
                </tr>
               </tbody>
              </table>
             </div>
            </div>
            """)

    def test_serialize_change_entry(self):
        """Testing CommitListField.serialize_change_entry"""
        target = User.objects.get(username='doc')
        repository = self.create_repository(tool_name='Git')
        review_request = self.create_review_request(repository=repository,
                                                    target_people=[target],
                                                    public=True,
                                                    create_with_history=True)
        diffset = self.create_diffset(review_request)

        submitter_name = review_request.submitter.get_full_name()

        self.create_diffcommit(diffset=diffset,
                               commit_id='r1',
                               parent_id='r0',
                               commit_message='Commit message 1',
                               author_name=submitter_name)
        self.create_diffcommit(diffset=diffset,
                               commit_id='r2',
                               parent_id='r1',
                               commit_message='Commit message 2',
                               author_name=submitter_name)

        draft_diffset = self.create_diffset(review_request, draft=True)
        self.create_diffcommit(diffset=draft_diffset,
                               commit_id='r1',
                               parent_id='r0',
                               commit_message='New commit message 1',
                               author_name=submitter_name)

        self.create_diffcommit(diffset=draft_diffset,
                               commit_id='r2',
                               parent_id='r1',
                               commit_message='New commit message 2',
                               author_name='Example Author')

        draft_diffset.finalize_commit_series(
            cumulative_diff=self.DEFAULT_GIT_FILEDIFF_DATA_DIFF,
            validation_info=None,
            validate=False,
            save=True)

        review_request.publish(user=review_request.submitter)
        changedesc = review_request.changedescs.latest()
        field = self.make_field(review_request)

        self.assertEqual(
            {
                'old': [
                    {
                        'author': submitter_name,
                        'summary': 'Commit message 1',
                    },
                    {
                        'author': submitter_name,
                        'summary': 'Commit message 2',
                    },
                ],
                'new': [
                    {
                        'author': submitter_name,
                        'summary': 'New commit message 1',
                    },
                    {
                        'author': 'Example Author',
                        'summary': 'New commit message 2',
                    },
                ],
            },
            field.serialize_change_entry(changedesc))

    def serialize_change_entry_first_diffset(self):
        """Testing CommitListField.serialize_change_entry with a change that
        adds the first diffset
        """
        target = User.objects.get(username='doc')
        repository = self.create_repository(tool_name='Git')
        review_request = self.create_review_request(repository=repository,
                                                    target_people=[target],
                                                    public=True,
                                                    create_with_history=True)
        submitter_name = review_request.submitter.get_full_name()

        draft_diffset = self.create_diffset(review_request, draft=True)
        self.create_diffcommit(diffset=draft_diffset,
                               commit_id='r1',
                               parent_id='r0',
                               commit_message='New commit message 1',
                               author_name=submitter_name)

        self.create_diffcommit(diffset=draft_diffset,
                               commit_id='r2',
                               parent_id='r1',
                               commit_message='New commit message 2',
                               author_name='Example Author')

        draft_diffset.finalize_commit_series(
            cumulative_diff=self.DEFAULT_GIT_FILEDIFF_DATA_DIFF,
            validation_info=None,
            validate=False,
            save=True)

        review_request.publish(user=review_request.submitter)
        changedesc = review_request.changedescs.latest()
        field = self.make_field(review_request)

        self.assertEqual(
            {
                'old': None,
                'new': [
                    {
                        'author': submitter_name,
                        'summary': 'New commit message 1',
                    },
                    {
                        'author': 'Example Author',
                        'summary': 'New commit message 2',
                    },
                ],
            },
            field.serialize_change_entry(changedesc))


class FileAttachmentsFieldTests(FieldsTestCase):
    """Unit tests for FileAttachmentsField."""

    field_cls = FileAttachmentsField
    fixtures = ['test_users']

    def test_render_change_entry_html(self):
        """Testing FileAttachmentsField.render_change_entry_html"""
        target = User.objects.get(username='doc')
        review_request = self.create_review_request(public=True,
                                                    create_with_history=True,
                                                    target_people=[target])
        attachment1 = self.create_file_attachment(
            review_request,
            caption='Attachment 1',
            orig_filename='file1.png')

        attachment2 = self.create_file_attachment(
            review_request,
            draft=True,
            draft_caption='Attachment 2',
            orig_filename='file2.png')
        attachment3 = self.create_file_attachment(
            review_request,
            draft=True,
            draft_caption='Attachment 3',
            orig_filename='file3.png')

        draft = review_request.get_draft()
        draft.inactive_file_attachments.add(attachment1)
        draft.file_attachments.remove(attachment1)

        review_request.publish(user=review_request.submitter)
        changedesc = review_request.changedescs.latest()

        field = self.make_field(review_request)

        # 3 queries:
        #
        # 1. Fetch active file attachments
        # 2. Fetch inactive file attachments
        # 3. Fetch the review request draft
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
                    'reviews_reviewrequest_inactive_file_attachments':
                        'INNER JOIN',
                },
                'model': FileAttachment,
                'num_joins': 1,
                'tables': {
                    'attachments_fileattachment',
                    'reviews_reviewrequest_inactive_file_attachments',
                },
                'where': Q(inactive_review_request__id=review_request.pk),
            },
            {
                'model': ReviewRequestDraft,
                'where': Q(review_request=review_request),
            },
        ]

        # Check the added file attachments. Only file attachments 2 and 3
        # should be present.
        with self.assertQueries(queries):
            result = field.render_change_entry_html(
                changedesc.fields_changed[field.field_id]['added'])

        self.assertIsInstance(result, SafeText)

        self.assertNotIn('"id": %s,' % attachment1.pk, result)
        self.assertIn('"id": %s,' % attachment2.pk, result)
        self.assertIn('"id": %s,' % attachment3.pk, result)

        # Check the removed file attachments. Only file attachment 1
        # should be present.
        with self.assertNumQueries(0):
            result = field.render_change_entry_html(
                changedesc.fields_changed[field.field_id]['removed'])

        self.assertIsInstance(result, SafeText)

        self.assertIn('"id": %s,' % attachment1.pk, result)
        self.assertNotIn('"id": %s,' % attachment2.pk, result)
        self.assertNotIn('"id": %s,' % attachment3.pk, result)

    def test_get_change_entry_sections_html(self):
        """Testing FileAttachmentsField.get_change_entry_sections_html"""
        target = User.objects.get(username='doc')
        review_request = self.create_review_request(public=True,
                                                    create_with_history=True,
                                                    target_people=[target])
        attachment1 = self.create_file_attachment(
            review_request,
            caption='Attachment 1',
            orig_filename='file1.png')

        self.create_file_attachment(
            review_request,
            draft=True,
            draft_caption='Attachment 2',
            orig_filename='file2.png')
        self.create_file_attachment(
            review_request,
            draft=True,
            draft_caption='Attachment 3',
            orig_filename='file3.png')

        draft = review_request.get_draft()
        draft.inactive_file_attachments.add(attachment1)
        draft.file_attachments.remove(attachment1)

        review_request.publish(user=review_request.submitter)
        changedesc = review_request.changedescs.latest()

        field = self.make_field(review_request)

        # 3 queries:
        #
        # 1. Fetch active file attachments
        # 2. Fetch inactive file attachments
        # 3. Fetch the review request draft
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
                    'reviews_reviewrequest_inactive_file_attachments':
                        'INNER JOIN',
                },
                'model': FileAttachment,
                'num_joins': 1,
                'tables': {
                    'attachments_fileattachment',
                    'reviews_reviewrequest_inactive_file_attachments',
                },
                'where': Q(inactive_review_request__id=review_request.pk),
            },
            {
                'model': ReviewRequestDraft,
                'where': Q(review_request=review_request),
            },
        ]

        # Check that the queries are only run once and that the cached data
        # is used subsequently when fetching the state of all file attachments
        # in the changedesc.
        with self.assertQueries(queries):
            field.get_change_entry_sections_html(
                changedesc.fields_changed[field.field_id])
