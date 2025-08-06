"""Tests for the DiffFileAttachmentResource."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from djblets.webapi.errors import DUPLICATE_ITEM, PERMISSION_DENIED
from djblets.webapi.testing.decorators import webapi_test_template

from reviewboard.attachments.models import FileAttachment
from reviewboard.scmtools.core import PRE_CREATION
from reviewboard.webapi.errors import DIFF_TOO_BIG
from reviewboard.webapi.resources import resources
from reviewboard.webapi.tests.base import BaseWebAPITestCase
from reviewboard.webapi.tests.mimetypes import (
    diff_file_attachment_item_mimetype,
    diff_file_attachment_list_mimetype)
from reviewboard.webapi.tests.mixins import (BasicPostTestSetupState,
                                             BasicTestsMetaclass)
from reviewboard.webapi.tests.urls import (get_diff_file_attachment_item_url,
                                           get_diff_file_attachment_list_url)

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from djblets.util.typing import JSONDict

    from reviewboard.diffviewer.models import FileDiff
    from reviewboard.reviews.models import ReviewRequest


class ResourceListTests(BaseWebAPITestCase, metaclass=BasicTestsMetaclass):
    """Testing the DiffFileAttachmentResource list APIs."""

    fixtures = ['test_users', 'test_scmtools']
    sample_api_url = 'repositories/<id>/diff-file-attachments/'
    resource = resources.diff_file_attachment

    def compare_item(self, item_rsp, attachment):
        self.assertEqual(item_rsp['id'], attachment.pk)
        self.assertEqual(item_rsp['filename'], attachment.filename)
        self.assertEqual(item_rsp['caption'], attachment.caption)
        self.assertEqual(item_rsp['mimetype'], attachment.mimetype)

    def setup_http_not_allowed_item_test(self, user):
        repository = self.create_repository()

        return get_diff_file_attachment_list_url(repository)

    def setup_http_not_allowed_list_test(self, user):
        repository = self.create_repository()

        return get_diff_file_attachment_list_url(repository)

    #
    # HTTP GET tests
    #

    def setup_basic_get_test(self, user, with_local_site, local_site_name,
                             populate_items):
        repository = self.create_repository(with_local_site=with_local_site)
        review_request = self.create_review_request(repository=repository)

        if populate_items:
            diffset = self.create_diffset(review_request=review_request,
                                          repository=repository)
            filediff = self.create_filediff(diffset)
            items = [self.create_diff_file_attachment(filediff)]
        else:
            items = []

        return (get_diff_file_attachment_list_url(repository, local_site_name),
                diff_file_attachment_list_mimetype,
                items)

    def test_get_with_mimetype(self):
        """Testing the GET repositories/<id>/diff-file-attachments/ API
        with ?mimetype=
        """
        repository = self.create_repository()
        review_request = self.create_review_request(repository=repository)
        diffset = self.create_diffset(review_request=review_request,
                                      repository=repository)
        filediff = self.create_filediff(diffset)
        attachment = self.create_diff_file_attachment(
            filediff,
            caption='Image',
            orig_filename='image.png',
            mimetype='image/png')
        self.create_diff_file_attachment(
            filediff,
            caption='Text',
            orig_filename='text.txt',
            mimetype='text/plain')

        rsp = self.api_get(
            get_diff_file_attachment_list_url(repository) +
            '?mimetype=image/png',
            expected_mimetype=diff_file_attachment_list_mimetype)
        assert rsp is not None
        self.assertEqual(rsp['stat'], 'ok')
        self.assertIn('diff_file_attachments', rsp)

        attachments_rsp = rsp['diff_file_attachments']
        self.assertEqual(len(attachments_rsp), 1)
        attachment_rsp = attachments_rsp[0]
        self.assertEqual(attachment_rsp['id'], attachment.pk)
        self.assertEqual(attachment_rsp['filename'], 'image.png')
        self.assertEqual(attachment_rsp['caption'], 'Image')
        self.assertEqual(attachment_rsp['mimetype'], 'image/png')

    def test_get_with_repository_file_path(self):
        """Testing the GET repositories/<id>/diff-file-attachments/ API
        with ?repository-file-path=
        """
        repository = self.create_repository()
        review_request = self.create_review_request(repository=repository)
        diffset = self.create_diffset(review_request=review_request,
                                      repository=repository)
        filediff1 = self.create_filediff(diffset,
                                         source_file='/test-file-1.png',
                                         dest_file='/test-file-1.png')
        filediff2 = self.create_filediff(diffset,
                                         source_file='/test-file-2.png',
                                         dest_file='/test-file-2.png')
        attachment = self.create_diff_file_attachment(
            filediff1,
            caption='File 1',
            orig_filename='/test-file-1.png')
        self.create_diff_file_attachment(
            filediff2,
            caption='File 2',
            orig_filename='/test-file-2.png')

        rsp = self.api_get(
            get_diff_file_attachment_list_url(repository) +
            '?repository-file-path=/test-file-1.png',
            expected_mimetype=diff_file_attachment_list_mimetype)
        assert rsp is not None

        self.assertEqual(rsp['stat'], 'ok')
        self.assertIn('diff_file_attachments', rsp)

        attachments_rsp = rsp['diff_file_attachments']
        self.assertEqual(len(attachments_rsp), 1)
        attachment_rsp = attachments_rsp[0]
        self.assertEqual(attachment_rsp['id'], attachment.pk)
        self.assertEqual(attachment_rsp['filename'], '/test-file-1.png')
        self.assertEqual(attachment_rsp['caption'], 'File 1')
        self.assertEqual(attachment_rsp['mimetype'], 'image/png')

    def test_get_with_repository_revision(self):
        """Testing the GET repositories/<id>/diff-file-attachments/ API
        with ?repository-revision=
        """
        repository = self.create_repository()
        review_request = self.create_review_request(repository=repository)
        diffset = self.create_diffset(review_request=review_request,
                                      repository=repository)
        filediff1 = self.create_filediff(diffset,
                                         source_file='/test-file-1.png',
                                         dest_file='/test-file-1.png',
                                         source_revision='4',
                                         dest_detail='5')
        filediff2 = self.create_filediff(diffset,
                                         source_file='/test-file-2.png',
                                         dest_file='/test-file-2.png',
                                         source_revision='9',
                                         dest_detail='10')
        attachment = self.create_diff_file_attachment(
            filediff1,
            from_modified=False,
            caption='File 1',
            orig_filename='/test-file-1.png')
        self.create_diff_file_attachment(
            filediff2,
            from_modified=False,
            caption='File 2',
            orig_filename='/test-file-2.png')

        rsp = self.api_get(
            get_diff_file_attachment_list_url(repository) +
            '?repository-revision=4',
            expected_mimetype=diff_file_attachment_list_mimetype)
        assert rsp is not None

        self.assertEqual(rsp['stat'], 'ok')
        self.assertIn('diff_file_attachments', rsp)

        attachments_rsp = rsp['diff_file_attachments']
        self.assertEqual(len(attachments_rsp), 1)
        attachment_rsp = attachments_rsp[0]
        self.assertEqual(attachment_rsp['id'], attachment.pk)
        self.assertEqual(attachment_rsp['filename'], '/test-file-1.png')
        self.assertEqual(attachment_rsp['caption'], 'File 1')
        self.assertEqual(attachment_rsp['mimetype'], 'image/png')

    #
    # HTTP POST tests
    #

    def check_post_result(
        self,
        user: User,
        rsp: JSONDict,
        filediff: FileDiff,
        review_request: ReviewRequest,
        source_file: bool = None,
        *args,
        **kwargs,
    ) -> None:
        """Check the results of an HTTP POST.

        Args:
            user (django.contrib.auth.models.User):
                The user performing the request.

            rsp (dict):
                The POST response payload.

            *args (tuple):
                Positional arguments provided by
                :py:meth:`populate_post_test_objects`.

            **kwargs (dict):
                Keyword arguments provided by
                :py:meth:`populate_post_test_objects`.

        Raises:
            AssertionError:
                One of the checks failed.
        """
        self.assertIn('diff_file_attachment', rsp)
        item_rsp = rsp['diff_file_attachment']

        attachment = FileAttachment.objects.get(pk=item_rsp['id'])

        if source_file:
            self.assertEqual(attachment.repo_path, filediff.source_file)
            self.assertEqual(attachment.repo_revision,
                             filediff.source_revision)
        else:
            self.assertEqual(attachment.added_in_filediff, filediff)

        review_request.refresh_from_db()
        self.assertEqual(review_request.file_attachments_count, 1)

    def populate_post_test_objects(
        self,
        *,
        setup_state: BasicPostTestSetupState,
        create_valid_request_data: bool,
        new_file: bool = False,
        **kwargs,
    ) -> None:
        """Populate objects for a POST test.

        Args:
            setup_state (reviewboard.webapi.tests.mixins.
                         BasicPostTestSetupState):
                The setup state for the test.

            create_valid_request_data (bool):
                Whether ``request_data`` in ``setup_state`` should provide
                valid data for a POST test, given the populated objects.

            new_file (bool, optional):
                Whether to create a newly-added file.

            **kwargs (dict):
                Additional keyword arguments for future expansion.
        """
        repository = self.create_repository(
            local_site=setup_state['local_site'])
        review_request = self.create_review_request(
            local_site=setup_state['local_site'],
            submitter=setup_state['owner'],
            repository=repository,
            create_with_history=True)
        diffset = self.create_diffset(review_request)
        commit = self.create_diffcommit(diffset=diffset)

        self.assertEqual(review_request.file_attachments_count, 0)

        if new_file:
            source_revision = PRE_CREATION
        else:
            source_revision = '123'

        filediff = self.create_filediff(
            diffset=diffset,
            commit=commit,
            source_revision=source_revision,
            diff=b'',
            binary=True)

        if create_valid_request_data:
            setup_state['request_data'] = {
                'path': open(self.get_sample_image_filename(), 'rb'),
                'filediff': filediff.pk,
            }
        else:
            setup_state['request_data'] = {}

        setup_state['url'] = get_diff_file_attachment_list_url(
            repository, setup_state['local_site_name'])
        setup_state['mimetype'] = diff_file_attachment_item_mimetype
        setup_state['check_result_args'] = (filediff, review_request)

    @webapi_test_template
    def test_post_with_new_file(self) -> None:
        """Testing the POST <URL> API with a newly-added binary file"""
        resource = self.resource

        self.assertTrue(getattr(resource.create, 'login_required', False))
        self.assertTrue(getattr(resource.create, 'checks_local_site', False))

        self.load_fixtures(self.basic_post_fixtures)
        self._login_user(admin=self.basic_post_use_admin)

        setup_state = cast(
            BasicPostTestSetupState,
            self._build_common_setup_state(fixtures=self.basic_post_fixtures))
        self.populate_post_test_objects(
            setup_state=setup_state,
            create_valid_request_data=True,
            new_file=True)

        request_data = setup_state.get('request_data')

        rsp = self.api_post(setup_state['url'],
                            request_data,
                            expected_mimetype=setup_state['mimetype'],
                            expected_status=self.basic_post_success_status)

        assert rsp
        self.assertEqual(rsp['stat'], 'ok')
        self.check_post_result(setup_state['owner'],
                               rsp,
                               *setup_state.get('check_result_args', ()),
                               **setup_state.get('check_result_kwargs', {}))

    @webapi_test_template
    def test_post_source_file(self) -> None:
        """Testing the POST <URL> API with source_file=1"""
        resource = self.resource

        self.assertTrue(getattr(resource.create, 'login_required', False))
        self.assertTrue(getattr(resource.create, 'checks_local_site', False))

        self.load_fixtures(self.basic_post_fixtures)
        self._login_user(admin=self.basic_post_use_admin)

        setup_state = cast(
            BasicPostTestSetupState,
            self._build_common_setup_state(fixtures=self.basic_post_fixtures))
        self.populate_post_test_objects(
            setup_state=setup_state,
            create_valid_request_data=True)

        request_data = setup_state.get('request_data')
        request_data['source_file'] = '1'

        rsp = self.api_post(setup_state['url'],
                            request_data,
                            expected_mimetype=setup_state['mimetype'],
                            expected_status=self.basic_post_success_status)

        assert rsp
        self.assertEqual(rsp['stat'], 'ok')
        self.check_post_result(setup_state['owner'],
                               rsp,
                               source_file=True,
                               *setup_state.get('check_result_args', ()),
                               **setup_state.get('check_result_kwargs', {}))

    @webapi_test_template
    def test_post_duplicate_file(self) -> None:
        """Testing the POST <URL> API with a duplicate file"""
        resource = self.resource

        self.assertTrue(getattr(resource.create, 'login_required', False))
        self.assertTrue(getattr(resource.create, 'checks_local_site', False))

        self.load_fixtures(self.basic_post_fixtures)
        self._login_user(admin=self.basic_post_use_admin)

        setup_state = cast(
            BasicPostTestSetupState,
            self._build_common_setup_state(fixtures=self.basic_post_fixtures))
        self.populate_post_test_objects(
            setup_state=setup_state,
            create_valid_request_data=True)

        filediff = setup_state['check_result_args'][0]
        self.create_diff_file_attachment(filediff)

        request_data = setup_state.get('request_data')

        rsp = self.api_post(setup_state['url'],
                            request_data,
                            expected_status=409)

        assert rsp
        self.assertEqual(rsp['stat'], 'fail')
        self.assertEqual(rsp['err']['code'], DUPLICATE_ITEM.code)

    @webapi_test_template
    def test_post_file_too_big(self) -> None:
        """Testing the POST <URL> API with a file that exceeds configured size
        limits
        """
        resource = self.resource

        self.assertTrue(getattr(resource.create, 'login_required', False))
        self.assertTrue(getattr(resource.create, 'checks_local_site', False))

        self.load_fixtures(self.basic_post_fixtures)
        self._login_user(admin=self.basic_post_use_admin)

        setup_state = cast(
            BasicPostTestSetupState,
            self._build_common_setup_state(fixtures=self.basic_post_fixtures))
        self.populate_post_test_objects(
            setup_state=setup_state,
            create_valid_request_data=True,
            new_file=True)

        request_data = setup_state.get('request_data')

        with self.siteconfig_settings({'diffviewer_max_binary_size': 2},
                                      reload_settings=False):
            rsp = self.api_post(setup_state['url'],
                                request_data,
                                expected_status=400)

        assert rsp is not None
        self.assertEqual(rsp['stat'], 'fail')
        self.assertEqual(rsp['err']['code'], DIFF_TOO_BIG.code)
        self.assertIn('reason', rsp)
        self.assertIn('max_size', rsp)
        self.assertEqual(rsp['max_size'], 2)


class ResourceItemTests(BaseWebAPITestCase, metaclass=BasicTestsMetaclass):
    """Testing the DiffFileAttachmentResource item APIs."""

    fixtures = ['test_users', 'test_scmtools']
    sample_api_url = 'repositories/<id>/diff-file-attachments/<id>/'
    resource = resources.diff_file_attachment

    def compare_item(self, item_rsp, attachment):
        self.assertEqual(item_rsp['id'], attachment.pk)
        self.assertEqual(item_rsp['filename'], attachment.filename)
        self.assertEqual(item_rsp['caption'], attachment.caption)
        self.assertEqual(item_rsp['mimetype'], attachment.mimetype)

    def setup_http_not_allowed_item_test(self, user):
        repository = self.create_repository()
        review_request = self.create_review_request(repository=repository)
        diffset = self.create_diffset(review_request=review_request,
                                      repository=repository)
        filediff = self.create_filediff(diffset)
        attachment = self.create_diff_file_attachment(filediff)

        return get_diff_file_attachment_item_url(repository, attachment)

    def setup_http_not_allowed_list_test(self, user):
        assert self.user is not None

        repository = self.create_repository(public=False)
        repository.users.add(self.user)
        review_request = self.create_review_request(repository=repository)
        diffset = self.create_diffset(review_request=review_request,
                                      repository=repository)
        filediff = self.create_filediff(diffset)
        attachment = self.create_diff_file_attachment(filediff)

        return get_diff_file_attachment_item_url(attachment, repository)

    #
    # HTTP GET tests
    #

    def setup_basic_get_test(self, user, with_local_site, local_site_name):
        repository = self.create_repository(with_local_site=with_local_site)
        review_request = self.create_review_request(repository=repository)
        diffset = self.create_diffset(review_request=review_request,
                                      repository=repository)
        filediff = self.create_filediff(diffset)
        attachment = self.create_diff_file_attachment(filediff)

        return (get_diff_file_attachment_item_url(attachment, repository,
                                                  local_site_name),
                diff_file_attachment_item_mimetype,
                attachment)

    def test_get_with_invite_only_repo(self):
        """Testing the GET repositories/<id>/diff-file-attachments/<id>/ API
        with access to an invite-only repository
        """
        assert self.user is not None

        repository = self.create_repository(public=False)
        repository.users.add(self.user)
        review_request = self.create_review_request(repository=repository)
        diffset = self.create_diffset(review_request=review_request,
                                      repository=repository)
        filediff = self.create_filediff(diffset)
        attachment = self.create_diff_file_attachment(filediff)

        rsp = self.api_get(
            get_diff_file_attachment_item_url(attachment, repository),
            expected_mimetype=diff_file_attachment_item_mimetype)
        assert rsp is not None

        self.assertEqual(rsp['stat'], 'ok')
        self.assertIn('diff_file_attachment', rsp)

        attachment_rsp = rsp['diff_file_attachment']
        self.assertEqual(attachment_rsp['id'], attachment.pk)
        self.assertEqual(attachment_rsp['filename'], attachment.filename)
        self.assertEqual(attachment_rsp['caption'], attachment.caption)
        self.assertEqual(attachment_rsp['mimetype'], attachment.mimetype)

    def test_get_with_invite_only_repo_no_access(self):
        """Testing the GET repositories/<id>/diff-file-attachments/<id>/ API
        without access to an invite-only repository
        """
        repository = self.create_repository(public=False)
        review_request = self.create_review_request(repository=repository)
        diffset = self.create_diffset(review_request=review_request,
                                      repository=repository)
        filediff = self.create_filediff(diffset)
        attachment = self.create_diff_file_attachment(filediff)

        rsp = self.api_get(
            get_diff_file_attachment_item_url(attachment, repository),
            expected_status=403)
        assert rsp is not None

        self.assertEqual(rsp['stat'], 'fail')
        self.assertEqual(rsp['err']['code'], PERMISSION_DENIED.code)
