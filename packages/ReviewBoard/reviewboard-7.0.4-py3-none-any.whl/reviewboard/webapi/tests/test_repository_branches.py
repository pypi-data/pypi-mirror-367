import unittest

import kgb
from djblets.webapi.testing.decorators import webapi_test_template

from reviewboard.webapi.errors import REPO_NOT_IMPLEMENTED
from reviewboard.webapi.resources import resources
from reviewboard.webapi.tests.base import BaseWebAPITestCase
from reviewboard.webapi.tests.mimetypes import \
    repository_branches_item_mimetype
from reviewboard.webapi.tests.mixins import BasicTestsMetaclass
from reviewboard.webapi.tests.mixins_ssl import SSLTestsMixin
from reviewboard.webapi.tests.urls import get_repository_branches_url


class ResourceTests(kgb.SpyAgency, SSLTestsMixin, BaseWebAPITestCase,
                    metaclass=BasicTestsMetaclass):
    """Testing the RepositoryBranchesResource list APIs."""

    fixtures = ['test_users', 'test_scmtools']
    sample_api_url = 'repositories/<id>/branches/'
    resource = resources.repository_branches

    def setup_http_not_allowed_list_test(self, user):
        repository = self.create_repository(tool_name='Test')

        return get_repository_branches_url(repository)

    def setup_http_not_allowed_item_test(self, user):
        repository = self.create_repository(tool_name='Test')

        return get_repository_branches_url(repository)

    def compare_item(self, item_rsp, branch):
        self.assertEqual(item_rsp, branch)

    #
    # HTTP GET tests
    #

    def setup_basic_get_test(self, user, with_local_site, local_site_name):
        repository = self.create_repository(tool_name='Test',
                                            with_local_site=with_local_site)

        return (
            get_repository_branches_url(repository, local_site_name),
            repository_branches_item_mimetype,
            [
                {
                    'id': 'trunk',
                    'name': 'trunk',
                    'commit': '5',
                    'default': True
                },
                {
                    'id': 'branch1',
                    'name': 'branch1',
                    'commit': '7',
                    'default': False
                },
            ])

    def test_get_with_no_support(self):
        """Testing the GET repositories/<id>/branches/ API
        with a repository that does not implement it
        """
        repository = self.create_repository(tool_name='CVS')

        try:
            rsp = self.api_get(get_repository_branches_url(repository),
                               expected_status=501)
        except ImportError:
            raise unittest.SkipTest('cvs binary not found')

        self.assertEqual(rsp['stat'], 'fail')
        self.assertEqual(rsp['err']['code'], REPO_NOT_IMPLEMENTED.code)

    @webapi_test_template
    def test_get_with_ssl_error(self) -> None:
        """Testing the GET <URL> API with CertificateVerificationError"""
        repository = self.create_repository(tool_name='Test')

        self.run_ssl_cert_test(
            spy_func=repository.scmtool_class.get_branches,
            spy_owner=repository.scmtool_class,
            url=get_repository_branches_url(repository),
            method='get')
