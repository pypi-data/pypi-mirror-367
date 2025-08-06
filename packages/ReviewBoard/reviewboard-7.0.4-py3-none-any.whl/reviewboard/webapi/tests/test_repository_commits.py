import unittest

import kgb
from djblets.testing.decorators import add_fixtures
from djblets.webapi.testing.decorators import webapi_test_template

from reviewboard.webapi.resources import resources
from reviewboard.webapi.errors import REPO_INFO_ERROR, REPO_NOT_IMPLEMENTED
from reviewboard.webapi.tests.base import BaseWebAPITestCase
from reviewboard.webapi.tests.mimetypes import repository_commits_item_mimetype
from reviewboard.webapi.tests.mixins import BasicTestsMetaclass
from reviewboard.webapi.tests.mixins_ssl import SSLTestsMixin
from reviewboard.webapi.tests.urls import get_repository_commits_url


class ResourceTests(kgb.SpyAgency, SSLTestsMixin, BaseWebAPITestCase,
                    metaclass=BasicTestsMetaclass):
    """Testing the RepositoryCommitsResource APIs."""

    fixtures = ['test_users', 'test_scmtools']
    sample_api_url = 'repositories/<id>/commits/'
    resource = resources.repository_commits
    test_http_methods = ('DELETE', 'POST', 'PUT')

    def setup_http_not_allowed_list_test(self, user):
        repository = self.create_repository(tool_name='Test')

        return get_repository_commits_url(repository)

    def setup_http_not_allowed_item_test(self, user):
        repository = self.create_repository(tool_name='Test')

        return get_repository_commits_url(repository)

    #
    # HTTP GET tests
    #

    def test_get(self):
        """Testing the GET repositories/<id>/commits/ API"""
        repository = self.create_repository(tool_name='Test')

        rsp = self.api_get(get_repository_commits_url(repository),
                           data={'start': 5},
                           expected_mimetype=repository_commits_item_mimetype)
        self.assertEqual(rsp['stat'], 'ok')
        self.assertEqual(len(rsp['commits']), 5)
        self.assertEqual(rsp['commits'][0]['message'], 'Commit 5')
        self.assertEqual(rsp['commits'][3]['author_name'], 'user2')

    @add_fixtures(['test_site'])
    def test_get_with_site(self):
        """Testing the GET repositories/<id>/commits/ API with a local site"""
        self._login_user(local_site=True)
        repository = self.create_repository(with_local_site=True,
                                            tool_name='Test')

        rsp = self.api_get(
            get_repository_commits_url(repository, self.local_site_name),
            data={'start': 7},
            expected_mimetype=repository_commits_item_mimetype)
        self.assertEqual(len(rsp['commits']), 7)
        self.assertEqual(rsp['stat'], 'ok')
        self.assertEqual(rsp['commits'][0]['id'], '7')
        self.assertEqual(rsp['commits'][1]['message'], 'Commit 6')

    @add_fixtures(['test_site'])
    def test_get_with_site_no_access(self):
        """Testing the GET repositories/<id>/commits/ API
        with a local site and Permission Denied error
        """
        repository = self.create_repository(with_local_site=True)

        self.api_get(
            get_repository_commits_url(repository, self.local_site_name),
            expected_status=403)

    def test_get_with_no_support(self):
        """Testing the GET repositories/<id>/commits/ API
        with a repository that does not implement it
        """
        repository = self.create_repository(tool_name='CVS')

        try:
            rsp = self.api_get(
                get_repository_commits_url(repository),
                data={'start': ''},
                expected_status=501)
        except ImportError:
            raise unittest.SkipTest('cvs binary not found')

        self.assertEqual(rsp['stat'], 'fail')
        self.assertEqual(rsp['err']['code'], REPO_NOT_IMPLEMENTED.code)

    def test_get_with_hosting_service_error(self):
        """Testing the GET repositories/<id>/commits/ API with
        HostingServiceError
        """
        repository = self.create_repository(tool_name='Test')

        rsp = self.api_get(
            get_repository_commits_url(repository),
            data={
                'branch': 'bad:hosting-service-error',
            },
            expected_status=500)

        self.assertEqual(rsp['stat'], 'fail')
        self.assertEqual(rsp['err']['code'], REPO_INFO_ERROR.code)
        self.assertEqual(rsp['err']['msg'], 'This is a HostingServiceError')

    def test_get_with_scm_error(self):
        """Testing the GET repositories/<id>/commits/ API with SCMError"""
        repository = self.create_repository(tool_name='Test')

        rsp = self.api_get(
            get_repository_commits_url(repository),
            data={
                'branch': 'bad:scm-error',
            },
            expected_status=500)

        self.assertEqual(rsp['stat'], 'fail')
        self.assertEqual(rsp['err']['code'], REPO_INFO_ERROR.code)
        self.assertEqual(rsp['err']['msg'], 'This is a SCMError')

    @webapi_test_template
    def test_get_with_ssl_error(self) -> None:
        """Testing the GET <URL> API with CertificateVerificationError"""
        repository = self.create_repository(tool_name='Test')

        self.run_ssl_cert_test(
            spy_func=repository.scmtool_class.get_commits,
            spy_owner=repository.scmtool_class,
            url=get_repository_commits_url(repository),
            method='get')
