"""Unit tests for the Gitorious hosting service."""

from reviewboard.hostingsvcs.testing import HostingServiceTestCase


class GitoriousTests(HostingServiceTestCase):
    """Unit tests for the Gitorious hosting service."""

    service_name = 'gitorious'

    def test_service_support(self):
        """Testing Gitorious service support capabilities"""
        self.assertFalse(self.service_class.supports_bug_trackers)
        self.assertTrue(self.service_class.supports_repositories)
        self.assertTrue(self.service_class.self_hosted)

    def test_get_repository_fields(self):
        """Testing Gitorious.get_repository_fields"""
        self.assertEqual(
            self.get_repository_fields(
                'Git',
                fields={
                    'gitorious_project_name': 'myproj',
                    'gitorious_repo_name': 'myrepo',
                }
            ),
            {
                'path': 'git://example.com/myproj/myrepo.git',
                'mirror_path': 'https://example.com/myproj/myrepo.git',
                'raw_file_url': ('https://example.com/myproj/myrepo/blobs/raw/'
                                 '<revision>'),
            })
