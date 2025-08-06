# coding=utf-8

import os
import unittest
from hashlib import md5

import kgb
from django.conf import settings
from djblets.testing.decorators import add_fixtures

from reviewboard.diffviewer.diffutils import patch
from reviewboard.diffviewer.testing.mixins import DiffParserTestingMixin
from reviewboard.scmtools.core import (Branch, Commit, Revision, HEAD,
                                       PRE_CREATION)
from reviewboard.scmtools.errors import SCMError, FileNotFoundError
from reviewboard.scmtools.svn import (
    SVNTool,
    recompute_svn_backend,
    _IDEA_EMPTY,
)
from reviewboard.scmtools.svn.utils import (collapse_svn_keywords,
                                            has_expanded_svn_keywords)
from reviewboard.scmtools.tests.testcases import SCMTestCase
from reviewboard.testing.testcase import TestCase


class _CommonSVNTestCase(DiffParserTestingMixin, kgb.SpyAgency, SCMTestCase):
    """Common unit tests for Subversion.

    This is meant to be subclassed for each backend that wants to run
    the common set of tests.
    """

    backend = None
    backend_name = None
    fixtures = ['test_scmtools']

    ssh_required_system_exes = ['svn', 'svnserve']

    __test__ = False

    @classmethod
    def setUpClass(cls):
        super(_CommonSVNTestCase, cls).setUpClass()

        cls._old_backend_setting = settings.SVNTOOL_BACKENDS
        settings.SVNTOOL_BACKENDS = [cls.backend]
        recompute_svn_backend()

    @classmethod
    def tearDownClass(cls):
        super(_CommonSVNTestCase, cls).tearDownClass()

        settings.SVNTOOL_BACKENDS = cls._old_backend_setting
        recompute_svn_backend()

    def setUp(self):
        super(_CommonSVNTestCase, self).setUp()

        self.svn_repo_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__),
                         '..', 'testdata', 'svn_repo'))
        self.svn_ssh_path = ('svn+ssh://localhost%s'
                             % self.svn_repo_path.replace('\\', '/'))
        self.repository = self.create_repository(
            name='Subversion SVN',
            path='file://%s' % self.svn_repo_path,
            tool_name='Subversion')

        try:
            self.tool = self.repository.get_scmtool()
        except ImportError:
            raise unittest.SkipTest('The %s backend could not be used. A '
                                    'dependency may be missing.'
                                    % self.backend)

        assert self.tool.client.__class__.__module__ == self.backend

    def shortDescription(self):
        desc = super(_CommonSVNTestCase, self).shortDescription()
        desc = desc.replace('<backend>', self.backend_name)

        return desc

    def test_get_repository_info(self):
        """Testing SVN (<backend>) get_repository_info"""
        info = self.tool.get_repository_info()

        self.assertIn('uuid', info)
        self.assertIsInstance(info['uuid'], str)
        self.assertEqual(info['uuid'], '41215d38-f5a5-421f-ba17-e0be11e6c705')

        self.assertIn('root_url', info)
        self.assertIsInstance(info['root_url'], str)
        self.assertEqual(info['root_url'], self.repository.path)

        self.assertIn('url', info)
        self.assertIsInstance(info['url'], str)
        self.assertEqual(info['url'], self.repository.path)

    def test_ssh(self):
        """Testing SVN (<backend>) with a SSH-backed Subversion repository"""
        self._test_ssh(self.svn_ssh_path, 'trunk/doc/misc-docs/Makefile')

    def test_ssh_with_site(self):
        """Testing SVN (<backend>) with a SSH-backed Subversion repository
        with a LocalSite
        """
        self._test_ssh_with_site(self.svn_ssh_path,
                                 'trunk/doc/misc-docs/Makefile')

    def test_get_file(self):
        """Testing SVN (<backend>) get_file"""
        tool = self.tool

        expected = (b'include ../tools/Makefile.base-vars\n'
                    b'NAME = misc-docs\n'
                    b'OUTNAME = svn-misc-docs\n'
                    b'INSTALL_DIR = $(DESTDIR)/usr/share/doc/subversion\n'
                    b'include ../tools/Makefile.base-rules\n')

        # There are 3 versions of this test in order to get 100% coverage of
        # the svn module.
        rev = Revision('2')
        filename = 'trunk/doc/misc-docs/Makefile'

        value = tool.get_file(filename, rev)
        self.assertIsInstance(value, bytes)
        self.assertEqual(value, expected)

        value = tool.get_file('/%s' % filename, rev)
        self.assertIsInstance(value, bytes)
        self.assertEqual(value, expected)

        value = tool.get_file('%s/%s' % (self.repository.path, filename), rev)
        self.assertIsInstance(value, bytes)
        self.assertEqual(value, expected)

        with self.assertRaises(FileNotFoundError):
            tool.get_file('')

    def test_file_exists(self):
        """Testing SVN (<backend>) file_exists"""
        tool = self.tool

        self.assertTrue(tool.file_exists('trunk/doc/misc-docs/Makefile'))
        self.assertFalse(tool.file_exists('trunk/doc/misc-docs/Makefile2'))

        with self.assertRaises(FileNotFoundError):
            tool.get_file('hello', PRE_CREATION)

    def test_get_file_with_special_url_chars(self):
        """Testing SVN (<backend>) get_file with filename containing
        characters that are special in URLs and repository path as a URI
        """
        value = self.tool.get_file('trunk/crazy& ?#.txt', Revision('12'))
        self.assertTrue(isinstance(value, bytes))
        self.assertEqual(value, b'Lots of characters in this one.\n')

    def test_file_exists_with_special_url_chars(self):
        """Testing SVN (<backend>) file_exists with filename containing
        characters that are special in URLs
        """
        self.assertTrue(self.tool.file_exists('trunk/crazy& ?#.txt',
                                              Revision('12')))

        # These should not crash. We'll be testing both file:// URLs
        # (which fail for anything lower than ASCII code 32) and for actual
        # URLs (which support all characters).
        self.assertFalse(self.tool.file_exists('trunk/%s.txt' % ''.join(
            chr(c)
            for c in range(32, 128)
        )))

        self.tool.client.repopath = 'svn+ssh://localhost:0/svn'

        try:
            self.assertFalse(self.tool.file_exists('trunk/%s.txt' % ''.join(
                chr(c)
                for c in range(128)
            )))
        except SCMError:
            # Couldn't connect. Valid result.
            pass

    def test_normalize_path_with_special_chars_and_remote_url(self):
        """Testing SVN (<backend>) normalize_path with special characters
        and remote URL
        """
        client = self.tool.client

        client.repopath = 'svn+ssh://example.com/svn'
        path = client.normalize_path(''.join(
            chr(c)
            for c in range(128)
        ))

        # This URL was generated based on modified code that directly used
        # Subversion's lookup take explicitly, ensuring we're getting the
        # results we want from urllib.quote() and our list of safe characters.
        self.assertEqual(
            path,
            "svn+ssh://example.com/svn/%00%01%02%03%04%05%06%07%08%09%0A"
            "%0B%0C%0D%0E%0F%10%11%12%13%14%15%16%17%18%19%1A%1B%1C%1D%1E"
            "%1F%20!%22%23$%25&'()*+,-./0123456789:%3B%3C=%3E%3F@ABCDEFGH"
            "IJKLMNOPQRSTUVWXYZ%5B%5C%5D%5E_%60abcdefghijklmnopqrstuvwxyz"
            "%7B%7C%7D~%7F")

    def test_normalize_path_with_special_chars_and_file_url(self):
        """Testing SVN (<backend>) normalize_path with special characters
        and local file:// URL
        """
        client = self.tool.client

        client.repopath = 'file:///tmp/svn'
        path = client.normalize_path(''.join(
            chr(c)
            for c in range(32, 128)
        ))

        # This URL was generated based on modified code that directly used
        # Subversion's lookup take explicitly, ensuring we're getting the
        # results we want from urllib.quote() and our list of safe characters.
        self.assertEqual(
            path,
            "file:///tmp/svn/%20!%22%23$%25&'()*+,-./0123456789:%3B%3C=%3E"
            "%3F@ABCDEFGHIJKLMNOPQRSTUVWXYZ%5B%5C%5D%5E_%60abcdefghijklmno"
            "pqrstuvwxyz%7B%7C%7D~%7F")

        # This should provide a reasonable error for each code in 0..32.
        for i in range(32):
            c = chr(i)

            message = (
                'Invalid character code %s found in path %r.'
                % (i, c)
            )

            with self.assertRaisesMessage(SCMError, message):
                client.normalize_path(c)

    def test_normalize_path_with_absolute_repo_path(self):
        """Testing SVN (<backend>) normalize_path with absolute path"""
        client = self.tool.client

        client.repopath = '/var/lib/svn'
        path = '/var/lib/svn/foo/bar'
        self.assertEqual(client.normalize_path(path), path)

        client.repopath = 'svn+ssh://example.com/svn/'
        path = 'svn+ssh://example.com/svn/foo/bar'
        self.assertEqual(client.normalize_path(path), path)

    def test_normalize_path_with_rel_path(self):
        """Testing SVN (<backend>) normalize_path with relative path"""
        client = self.tool.client
        client.repopath = 'svn+ssh://example.com/svn'

        self.assertEqual(client.normalize_path('foo/bar'),
                         'svn+ssh://example.com/svn/foo/bar')
        self.assertEqual(client.normalize_path('/foo/bar'),
                         'svn+ssh://example.com/svn/foo/bar')
        self.assertEqual(client.normalize_path('//foo/bar'),
                         'svn+ssh://example.com/svn/foo/bar')
        self.assertEqual(client.normalize_path('foo&/b ar?/#file#.txt'),
                         'svn+ssh://example.com/svn/foo&/b%20ar%3F/'
                         '%23file%23.txt')

    def test_revision_parsing(self):
        """Testing SVN (<backend>) revision number parsing"""
        parser = self.tool.get_parser(b'')

        self.assertEqual(
            parser.parse_diff_revision(filename=b'',
                                       revision=b'(working copy)'),
            (b'', HEAD))
        self.assertEqual(
            parser.parse_diff_revision(filename=b'',
                                       revision=b'   (revision 0)'),
            (b'', PRE_CREATION))

        self.assertEqual(
            parser.parse_diff_revision(filename=b'',
                                       revision=b'(revision 1)'),
            (b'', b'1'))
        self.assertEqual(
            parser.parse_diff_revision(filename=b'',
                                       revision=b'(revision 23)'),
            (b'', b'23'))

        # Fix for bug 2176
        self.assertEqual(
            parser.parse_diff_revision(filename=b'',
                                       revision=b'\t(revision 4)'),
            (b'', b'4'))

        self.assertEqual(
            parser.parse_diff_revision(
                filename=b'',
                revision=b'2007-06-06 15:32:23 UTC (rev 10958)'),
            (b'', b'10958'))

        # Fix for bug 2632
        self.assertEqual(
            parser.parse_diff_revision(filename=b'',
                                       revision=b'(revision )'),
            (b'', _IDEA_EMPTY))

        with self.assertRaises(SCMError):
            parser.parse_diff_revision(filename=b'',
                                       revision=b'hello')

        # Verify that 'svn diff' localized revision strings parse correctly.
        self.assertEqual(
            parser.parse_diff_revision(
                filename=b'',
                revision='(revisión: 5)'.encode('utf-8')),
            (b'', b'5'))
        self.assertEqual(
            parser.parse_diff_revision(
                filename=b'',
                revision='(リビジョン 6)'.encode('utf-8')),
            (b'', b'6'))
        self.assertEqual(
            parser.parse_diff_revision(
                filename=b'',
                revision='(版本 7)'.encode('utf-8')),
            (b'', b'7'))

    def test_revision_parsing_with_nonexistent(self):
        """Testing SVN (<backend>) revision parsing with "(nonexistent)"
        revision indicator
        """
        parser = self.tool.get_parser(b'')

        # English
        self.assertEqual(
            parser.parse_diff_revision(filename=b'',
                                       revision=b'(nonexistent)'),
            (b'', PRE_CREATION))

        # German
        self.assertEqual(
            parser.parse_diff_revision(filename=b'',
                                       revision=b'(nicht existent)'),
            (b'', PRE_CREATION))

        # Simplified Chinese
        self.assertEqual(
            parser.parse_diff_revision(
                filename=b'',
                revision='(不存在的)'.encode('utf-8')),
            (b'', PRE_CREATION))

    def test_revision_parsing_with_nonexistent_and_branches(self):
        """Testing SVN (<backend>) revision parsing with relocation
        information and nonexistent revision specifier
        """
        parser = self.tool.get_parser(b'')

        self.assertEqual(
            parser.parse_diff_revision(
                filename=b'',
                revision=b'(.../trunk) (nonexistent)'),
            (b'trunk/', PRE_CREATION))

        self.assertEqual(
            parser.parse_diff_revision(
                filename=b'',
                revision=b'(.../branches/branch-1.0)     (nicht existent)'),
            (b'branches/branch-1.0/', PRE_CREATION))

        self.assertEqual(
            parser.parse_diff_revision(
                filename=b'',
                revision='        (.../trunk)     (不存在的)'.encode('utf-8')),
            (b'trunk/', PRE_CREATION))

    def test_interface(self):
        """Testing SVN (<backend>) with basic SVNTool API"""
        self.assertFalse(self.tool.diffs_use_absolute_paths)

        self.assertRaises(NotImplementedError,
                          lambda: self.tool.get_changeset(1))

    def test_binary_diff(self):
        """Testing SVN (<backend>) parsing SVN diff with binary file"""
        diff = (
            b'Index: binfile\n'
            b'============================================================'
            b'=======\n'
            b'Cannot display: file marked as a binary type.\n'
            b'svn:mime-type = application/octet-stream\n'
        )

        parsed_files = self.tool.get_parser(diff).parse()
        self.assertEqual(len(parsed_files), 1)

        self.assert_parsed_diff_file(
            parsed_files[0],
            orig_filename=b'binfile',
            orig_file_details=b'(unknown)',
            modified_filename=b'binfile',
            modified_file_details=b'(working copy)',
            index_header_value=b'binfile',
            binary=True,
            data=diff)

    def test_binary_diff_with_property_change(self):
        """Testing SVN (<backend>) parsing SVN diff with binary file with
        property change
        """
        diff = (
            b'Index: binfile\n'
            b'============================================================'
            b'=======\n'
            b'Cannot display: file marked as a binary type.\n'
            b'svn:mime-type = application/octet-stream\n'
            b'\n'
            b'Property changes on: binfile\n'
            b'____________________________________________________________'
            b'_______\n'
            b'Added: svn:mime-type\n'
            b'## -0,0 +1 ##\n'
            b'+application/octet-stream\n'
            b'\\ No newline at end of property\n'
        )

        parsed_files = self.tool.get_parser(diff).parse()
        self.assertEqual(len(parsed_files), 1)

        self.assert_parsed_diff_file(
            parsed_files[0],
            orig_filename=b'binfile',
            orig_file_details=b'(unknown)',
            modified_filename=b'binfile',
            modified_file_details=b'(working copy)',
            index_header_value=b'binfile',
            binary=True,
            insert_count=1,
            data=diff)

    def test_binary_diff_with_revision(self) -> None:
        """Testing SVN (<backend>) parsing diff with binary file that has
        revision information, generated with --force
        """
        diff = (
            b'Index: binfile\n'
            b'============================================================'
            b'=======\n'
            b'Binary files binfile (revision 3) and binfile (working copy) '
            b'differ\n'
            b'Cannot display: file marked as a binary type.\n'
        )

        parsed_files = self.tool.get_parser(diff).parse()
        self.assertEqual(len(parsed_files), 1)

        self.assert_parsed_diff_file(
            parsed_files[0],
            orig_filename=b'binfile',
            orig_file_details=b'3',
            modified_filename=b'binfile',
            modified_file_details=HEAD,
            index_header_value=b'binfile',
            binary=True,
            insert_count=0,
            data=diff)

    def test_keyword_diff(self):
        """Testing SVN (<backend>) parsing diff with keywords"""
        # 'svn cat' will expand special variables in svn:keywords,
        # but 'svn diff' doesn't expand anything.  This causes the
        # patch to fail if those variables appear in the patch context.
        diff = (b'Index: Makefile\n'
                b'==========================================================='
                b'========\n'
                b'--- Makefile    (revision 4)\n'
                b'+++ Makefile    (working copy)\n'
                b'@@ -1,6 +1,7 @@\n'
                b' # $Id$\n'
                b' # $Rev$\n'
                b' # $Revision::     $\n'
                b'+# foo\n'
                b' include ../tools/Makefile.base-vars\n'
                b' NAME = misc-docs\n'
                b' OUTNAME = svn-misc-docs\n')

        filename = 'trunk/doc/misc-docs/Makefile'
        rev = Revision('4')
        file = self.tool.get_file(filename, rev)
        patch(diff, file, filename)

    def test_unterminated_keyword_diff(self):
        """Testing SVN (<backend>) parsing diff with unterminated keywords"""
        diff = (b'Index: Makefile\n'
                b'==========================================================='
                b'========\n'
                b'--- Makefile    (revision 4)\n'
                b'+++ Makefile    (working copy)\n'
                b'@@ -1,6 +1,7 @@\n'
                b' # $Id$\n'
                b' # $Id:\n'
                b' # $Rev$\n'
                b' # $Revision::     $\n'
                b'+# foo\n'
                b' include ../tools/Makefile.base-vars\n'
                b' NAME = misc-docs\n'
                b' OUTNAME = svn-misc-docs\n')

        filename = 'trunk/doc/misc-docs/Makefile'
        rev = Revision('5')
        file = self.tool.get_file(filename, rev)
        patch(diff, file, filename)

    def test_svn16_property_diff(self):
        """Testing SVN (<backend>) parsing SVN 1.6 diff with property changes
        """
        diff = (
            b'Index:\n'
            b'======================================================'
            b'=============\n'
            b'--- (revision 123)\n'
            b'+++ (working copy)\n'
            b'Property changes on: .\n'
            b'______________________________________________________'
            b'_____________\n'
            b'Modified: reviewboard:url\n'
            b'## -1 +1 ##\n'
            b'-http://reviews.reviewboard.org\n'
            b'+http://reviews.reviewboard.org\n'
            b'Index: binfile\n'
            b'======================================================='
            b'============\nCannot display: file marked as a '
            b'binary type.\nsvn:mime-type = application/octet-stream\n'
        )

        parsed_files = self.tool.get_parser(diff).parse()
        self.assertEqual(len(parsed_files), 1)

        self.assert_parsed_diff_file(
            parsed_files[0],
            orig_filename=b'binfile',
            orig_file_details=b'(unknown)',
            modified_filename=b'binfile',
            modified_file_details=b'(working copy)',
            index_header_value=b'binfile',
            binary=True,
            data=diff)

    def test_svn17_property_diff(self):
        """Testing SVN (<backend>) parsing SVN 1.7+ diff with property changes
        """
        diff = (
            b'Index .:\n'
            b'======================================================'
            b'=============\n'
            b'--- .  (revision 123)\n'
            b'+++ .  (working copy)\n'
            b'\n'
            b'Property changes on: .\n'
            b'______________________________________________________'
            b'_____________\n'
            b'Modified: reviewboard:url\n'
            b'## -0,0 +1,3 ##\n'
            b'-http://reviews.reviewboard.org\n'
            b'+http://reviews.reviewboard.org\n'
            b'Added: myprop\n'
            b'## -0,0 +1 ##\n'
            b'+Property test.\n'
            b'Index: binfile\n'
            b'======================================================='
            b'============\nCannot display: file marked as a '
            b'binary type.\nsvn:mime-type = application/octet-stream\n'
        )

        parsed_files = self.tool.get_parser(diff).parse()
        self.assertEqual(len(parsed_files), 1)

        self.assert_parsed_diff_file(
            parsed_files[0],
            orig_filename=b'binfile',
            orig_file_details=b'(unknown)',
            modified_filename=b'binfile',
            modified_file_details=b'(working copy)',
            index_header_value=b'binfile',
            binary=True,
            data=diff)

    def test_unicode_diff(self):
        """Testing SVN (<backend>) parsing diff with unicode characters"""
        diff = (
            'Index: Filé\n'
            '==========================================================='
            '========\n'
            '--- Filé    (revision 4)\n'
            '+++ Filé    (working copy)\n'
            '@@ -1,6 +1,7 @@\n'
            '+# foó\n'
            ' include ../tools/Makefile.base-vars\n'
            ' NAME = misc-docs\n'
            ' OUTNAME = svn-misc-docs\n'
        ).encode('utf-8')

        parsed_files = self.tool.get_parser(diff).parse()
        self.assertEqual(len(parsed_files), 1)

        self.assert_parsed_diff_file(
            parsed_files[0],
            orig_filename='Filé'.encode('utf-8'),
            orig_file_details=b'4',
            modified_filename='Filé'.encode('utf-8'),
            modified_file_details=HEAD,
            index_header_value='Filé'.encode('utf-8'),
            insert_count=1,
            data=diff)

    def test_diff_with_spaces_in_filenames(self):
        """Testing SVN (<backend>) parsing diff with spaces in filenames"""
        diff = (
            b'Index: File with spaces\n'
            b'==========================================================='
            b'========\n'
            b'--- File with spaces    (revision 4)\n'
            b'+++ File with spaces    (working copy)\n'
            b'@@ -1,6 +1,7 @@\n'
            b'+# foo\n'
            b' include ../tools/Makefile.base-vars\n'
            b' NAME = misc-docs\n'
            b' OUTNAME = svn-misc-docs\n'
        )

        parsed_files = self.tool.get_parser(diff).parse()
        self.assertEqual(len(parsed_files), 1)

        self.assert_parsed_diff_file(
            parsed_files[0],
            orig_filename=b'File with spaces',
            orig_file_details=b'4',
            modified_filename=b'File with spaces',
            modified_file_details=HEAD,
            index_header_value=b'File with spaces',
            insert_count=1,
            data=diff)

    def test_diff_with_added_empty_file(self):
        """Testing parsing SVN diff with added empty file"""
        diff = (
            b'Index: empty-file\t(added)\n'
            b'==========================================================='
            b'========\n'
            b'--- empty-file\t(revision 0)\n'
            b'+++ empty-file\t(revision 0)\n'
        )

        parsed_files = self.tool.get_parser(diff).parse()
        self.assertEqual(len(parsed_files), 1)

        self.assert_parsed_diff_file(
            parsed_files[0],
            orig_filename=b'empty-file',
            orig_file_details=PRE_CREATION,
            modified_filename=b'empty-file',
            modified_file_details=PRE_CREATION,
            index_header_value=b'empty-file\t(added)',
            data=diff)

    def test_diff_with_deleted_empty_file(self):
        """Testing parsing SVN diff with deleted empty file"""
        diff = (
            b'Index: empty-file\t(deleted)\n'
            b'==========================================================='
            b'========\n'
            b'--- empty-file\t(revision 4)\n'
            b'+++ empty-file\t(working copy)\n'
        )

        parsed_files = self.tool.get_parser(diff).parse()
        self.assertEqual(len(parsed_files), 1)

        self.assert_parsed_diff_file(
            parsed_files[0],
            orig_filename=b'empty-file',
            orig_file_details=b'4',
            modified_filename=b'empty-file',
            modified_file_details=HEAD,
            index_header_value=b'empty-file\t(deleted)',
            deleted=True,
            data=diff)

    def test_diff_with_nonexistent_revision_for_dest_file(self):
        """Testing parsing SVN diff with deleted file using "nonexistent"
        destination revision
        """
        diff = (
            b'Index: deleted-file\n'
            b'==========================================================='
            b'========\n'
            b'--- deleted-file\t(revision 4)\n'
            b'+++ deleted-file\t(nonexistent)\n'
            b'@@ -1,2 +0,0 @@\n'
            b'-line 1\n'
            b'-line 2\n'
        )

        parsed_files = self.tool.get_parser(diff).parse()
        self.assertEqual(len(parsed_files), 1)

        self.assert_parsed_diff_file(
            parsed_files[0],
            orig_filename=b'deleted-file',
            orig_file_details=b'4',
            modified_filename=b'deleted-file',
            modified_file_details=PRE_CREATION,
            index_header_value=b'deleted-file',
            deleted=True,
            delete_count=2,
            data=diff)

    def test_idea_diff(self):
        """Testing parsing SVN diff with multi-file diff generated by IDEA
        IDEs
        """
        diff1 = (
            b'Index: path/to/README\n'
            b'IDEA additional info:\n'
            b'Subsystem: org.reviewboard.org.test\n'
            b'<+>ISO-8859-1\n'
            b'=============================================================='
            b'=====\n'
            b'--- path/to/README\t(revision 4)\n'
            b'+++ path/to/README\t(revision )\n'
            b'@@ -1,6 +1,7 @@\n'
            b' #\n'
            b' #\n'
            b' #\n'
            b'+# test\n'
            b' #\n'
            b' #\n'
            b' #\n'
        )
        diff2 = (
            b'Index: path/to/README2\n'
            b'IDEA additional info:\n'
            b'Subsystem: org.reviewboard.org.test\n'
            b'<+>ISO-8859-1\n'
            b'=============================================================='
            b'=====\n'
            b'--- path/to/README2\t(revision 4)\n'
            b'+++ path/to/README2\t(revision )\n'
            b'@@ -1,6 +1,7 @@\n'
            b' #\n'
            b' #\n'
            b' #\n'
            b'+# test\n'
            b' #\n'
            b' #\n'
            b' #\n'
        )
        diff = diff1 + diff2

        parsed_files = self.tool.get_parser(diff).parse()
        self.assertEqual(len(parsed_files), 2)

        self.assert_parsed_diff_file(
            parsed_files[0],
            orig_filename=b'path/to/README',
            orig_file_details=b'4',
            modified_filename=b'path/to/README',
            modified_file_details=HEAD,
            index_header_value=b'path/to/README',
            insert_count=1,
            data=diff1)

        self.assert_parsed_diff_file(
            parsed_files[1],
            orig_filename=b'path/to/README2',
            orig_file_details=b'4',
            modified_filename=b'path/to/README2',
            modified_file_details=HEAD,
            index_header_value=b'path/to/README2',
            insert_count=1,
            data=diff2)

    def test_get_branches(self):
        """Testing SVN (<backend>) get_branches"""
        branches = self.tool.get_branches()

        self.assertEqual(len(branches), 3)
        self.assertEqual(branches[0], Branch(id='trunk', name='trunk',
                                             commit='12', default=True))
        self.assertEqual(branches[1], Branch(id='branches/branch1',
                                             name='branch1',
                                             commit='7', default=False))
        self.assertEqual(branches[2], Branch(id='top-level-branch',
                                             name='top-level-branch',
                                             commit='10', default=False))

    def test_get_commits(self):
        """Testing SVN (<backend>) get_commits"""
        commits = self.tool.get_commits(start='5')

        self.assertEqual(len(commits), 5)
        self.assertEqual(
            commits[0],
            Commit('chipx86',
                   '5',
                   '2010-05-21T09:33:40.893946',
                   'Add an unterminated keyword for testing bug #1523\n',
                   '4'))

        commits = self.tool.get_commits(start='7')
        self.assertEqual(len(commits), 7)
        self.assertEqual(
            commits[1],
            Commit('david',
                   '6',
                   '2013-06-13T07:43:04.725088',
                   'Add a branches directory',
                   '5'))

    def test_get_commits_with_branch(self):
        """Testing SVN (<backend>) get_commits with branch"""
        commits = self.tool.get_commits(branch='/branches/branch1', start='5')

        self.assertEqual(len(commits), 5)
        self.assertEqual(
            commits[0],
            Commit('chipx86',
                   '5',
                   '2010-05-21T09:33:40.893946',
                   'Add an unterminated keyword for testing bug #1523\n',
                   '4'))

        commits = self.tool.get_commits(branch='/branches/branch1', start='7')
        self.assertEqual(len(commits), 6)
        self.assertEqual(
            commits[0],
            Commit('david',
                   '7',
                   '2013-06-13T07:43:27.259554',
                   'Add a branch',
                   '5'))
        self.assertEqual(
            commits[1],
            Commit('chipx86',
                   '5',
                   '2010-05-21T09:33:40.893946',
                   'Add an unterminated keyword for testing bug #1523\n',
                   '4'))

    def test_get_commits_with_no_date(self):
        """Testing SVN (<backend>) get_commits with no date in commit"""
        self.spy_on(self.tool.client.get_log, op=kgb.SpyOpReturn([
            {
                'author': 'chipx86',
                'message': 'Commit 1',
                'revision': '5',
            },
        ]))

        commits = self.tool.get_commits(start='5')

        self.assertEqual(len(commits), 1)
        self.assertEqual(
            commits[0],
            Commit('chipx86',
                   '5',
                   '',
                   'Commit 1'))

    def test_get_commits_with_exception(self):
        """Testing SVN (<backend>) get_commits with exception"""
        self.spy_on(self.tool.client.communicate_hook,
                    op=kgb.SpyOpRaise(Exception('Bad things happened')))

        with self.assertRaisesMessage(SCMError, 'Bad things happened'):
            self.tool.get_commits(start='5')

    def test_get_change(self):
        """Testing SVN (<backend>) get_change"""
        commit = self.tool.get_change('5')

        self.assertEqual(md5(commit.message.encode('utf-8')).hexdigest(),
                         '928336c082dd756e3f7af4cde4724ebf')
        self.assertEqual(md5(commit.diff).hexdigest(),
                         '56e50374056931c03a333f234fa63375')

    def test_utf8_keywords(self):
        """Testing SVN (<backend>) with UTF-8 files with keywords"""
        self.repository.get_file(path='trunk/utf8-file.txt',
                                 revision='9')

    def test_normalize_patch_with_svn_and_expanded_keywords(self):
        """Testing SVN (<backend>) normalize_patch with expanded keywords"""
        diff = (
            b'Index: Makefile\n'
            b'==========================================================='
            b'========\n'
            b'--- Makefile    (revision 4)\n'
            b'+++ Makefile    (working copy)\n'
            b'@@ -1,6 +1,7 @@\n'
            b' # $Id$\n'
            b' # $Rev: 123$\n'
            b' # $Revision:: 123   $\n'
            b'+# foo\n'
            b' include ../tools/Makefile.base-vars\n'
            b' NAME = misc-docs\n'
            b' OUTNAME = svn-misc-docs\n'
        )

        normalized = self.tool.normalize_patch(
            patch=diff,
            filename='trunk/doc/misc-docs/Makefile',
            revision='4')

        self.assertEqual(
            normalized,
            b'Index: Makefile\n'
            b'==========================================================='
            b'========\n'
            b'--- Makefile    (revision 4)\n'
            b'+++ Makefile    (working copy)\n'
            b'@@ -1,6 +1,7 @@\n'
            b' # $Id$\n'
            b' # $Rev$\n'
            b' # $Revision::       $\n'
            b'+# foo\n'
            b' include ../tools/Makefile.base-vars\n'
            b' NAME = misc-docs\n'
            b' OUTNAME = svn-misc-docs\n')

    def test_normalize_patch_with_svn_and_no_expanded_keywords(self):
        """Testing SVN (<backend>) normalize_patch with no expanded keywords"""
        diff = (
            b'Index: Makefile\n'
            b'==========================================================='
            b'========\n'
            b'--- Makefile    (revision 4)\n'
            b'+++ Makefile    (working copy)\n'
            b'@@ -1,6 +1,7 @@\n'
            b' # $Id$\n'
            b' # $Rev$\n'
            b' # $Revision::    $\n'
            b'+# foo\n'
            b' include ../tools/Makefile.base-vars\n'
            b' NAME = misc-docs\n'
            b' OUTNAME = svn-misc-docs\n'
        )

        normalized = self.tool.normalize_patch(
            patch=diff,
            filename='trunk/doc/misc-docs/Makefile',
            revision='4')

        self.assertEqual(
            normalized,
            b'Index: Makefile\n'
            b'==========================================================='
            b'========\n'
            b'--- Makefile    (revision 4)\n'
            b'+++ Makefile    (working copy)\n'
            b'@@ -1,6 +1,7 @@\n'
            b' # $Id$\n'
            b' # $Rev$\n'
            b' # $Revision::    $\n'
            b'+# foo\n'
            b' include ../tools/Makefile.base-vars\n'
            b' NAME = misc-docs\n'
            b' OUTNAME = svn-misc-docs\n')


class PySVNTests(_CommonSVNTestCase):
    backend = 'reviewboard.scmtools.svn.pysvn'
    backend_name = 'pysvn'

    __test__ = True


class UtilsTests(SCMTestCase):
    """Unit tests for reviewboard.scmtools.svn.utils."""

    def test_collapse_svn_keywords(self):
        """Testing collapse_svn_keywords"""
        keyword_test_data = [
            (b'Id',
             b'/* $Id: test2.c 3 2014-08-04 22:55:09Z david $ */',
             b'/* $Id$ */'),
            (b'id',
             b'/* $Id: test2.c 3 2014-08-04 22:55:09Z david $ */',
             b'/* $Id$ */'),
            (b'id',
             b'/* $id: test2.c 3 2014-08-04 22:55:09Z david $ */',
             b'/* $id$ */'),
            (b'Id',
             b'/* $id: test2.c 3 2014-08-04 22:55:09Z david $ */',
             b'/* $id$ */')
        ]

        for keyword, data, result in keyword_test_data:
            self.assertEqual(collapse_svn_keywords(data, keyword),
                             result)

    def test_has_expanded_svn_keywords(self):
        """Testing has_expanded_svn_keywords"""
        self.assertTrue(has_expanded_svn_keywords(b'.. $ID: 123$ ..'))
        self.assertTrue(has_expanded_svn_keywords(b'.. $id::  123$ ..'))

        self.assertFalse(has_expanded_svn_keywords(b'.. $Id::   $ ..'))
        self.assertFalse(has_expanded_svn_keywords(b'.. $Id$ ..'))
        self.assertFalse(has_expanded_svn_keywords(b'.. $Id ..'))
        self.assertFalse(has_expanded_svn_keywords(b'.. $Id Here$ ..'))


class SVNAuthFormTests(TestCase):
    """Unit tests for SVNTool's authentication form."""

    def test_fields(self):
        """Testing SVNTool authentication form fields"""
        form = SVNTool.create_auth_form()

        self.assertEqual(list(form.fields), ['username', 'password'])
        self.assertEqual(form['username'].help_text, '')
        self.assertEqual(form['username'].label, 'Username')
        self.assertEqual(form['password'].help_text, '')
        self.assertEqual(form['password'].label, 'Password')

    @add_fixtures(['test_scmtools'])
    def test_load(self):
        """Tetting SVNTool authentication form load"""
        repository = self.create_repository(
            tool_name='Subversion',
            username='test-user',
            password='test-pass')

        form = SVNTool.create_auth_form(repository=repository)
        form.load()

        self.assertEqual(form['username'].value(), 'test-user')
        self.assertEqual(form['password'].value(), 'test-pass')

    @add_fixtures(['test_scmtools'])
    def test_save(self):
        """Tetting SVNTool authentication form save"""
        repository = self.create_repository(tool_name='Subversion')

        form = SVNTool.create_auth_form(
            repository=repository,
            data={
                'username': 'test-user',
                'password': 'test-pass',
            })
        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(repository.username, 'test-user')
        self.assertEqual(repository.password, 'test-pass')


class SVNRepositoryFormTests(TestCase):
    """Unit tests for SVNTool's repository form."""

    def test_fields(self) -> None:
        """Testing SVNTool repository form fields"""
        form = SVNTool.create_repository_form()

        self.assertEqual(list(form.fields), ['path', 'mirror_path'])
        self.assertEqual(form['path'].help_text,
                         'The path to the repository. This will generally be '
                         'the URL you would use to check out the repository.')
        self.assertEqual(form['path'].label, 'Path')
        self.assertEqual(form['mirror_path'].help_text, '')
        self.assertEqual(form['mirror_path'].label, 'Mirror Path')

    @add_fixtures(['test_scmtools'])
    def test_load(self) -> None:
        """Tetting SVNTool repository form load"""
        repository = self.create_repository(
            tool_name='Subversion',
            path='https://svn.example.com/',
            mirror_path='https://svn.mirror.example.com')

        form = SVNTool.create_repository_form(repository=repository)
        form.load()

        self.assertEqual(form['path'].value(), 'https://svn.example.com/')
        self.assertEqual(form['mirror_path'].value(),
                         'https://svn.mirror.example.com')

    @add_fixtures(['test_scmtools'])
    def test_save(self) -> None:
        """Tetting SVNTool repository form save"""
        repository = self.create_repository(tool_name='Subversion')

        form = SVNTool.create_repository_form(
            repository=repository,
            data={
                'path': 'https://svn.example.com/',
                'mirror_path': 'https://svn.mirror.example.com',
            })
        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(repository.path, 'https://svn.example.com/')
        self.assertEqual(repository.mirror_path,
                         'https://svn.mirror.example.com')

    @add_fixtures(['test_scmtools'])
    def test_save_with_file_url(self) -> None:
        """Tetting SVNTool repository form save with file:// URL"""
        repository = self.create_repository(tool_name='Subversion')

        form = SVNTool.create_repository_form(
            repository=repository,
            data={
                'path': 'file:///opt/svnrepo/',
            })
        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(repository.path, 'file:///opt/svnrepo/')

    @add_fixtures(['test_scmtools'])
    def test_save_with_bare_file_path(self) -> None:
        """Testing SVNTool repository form save with raw path instead of
        URL
        """
        repository = self.create_repository(tool_name='Subversion')

        form = SVNTool.create_repository_form(
            repository=repository,
            data={
                'path': '/opt/svnrepo/',
            })
        self.assertFalse(form.is_valid())
        form.full_clean()

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['path'], [
            'The path to the SVN repository must be a URL. To specify a local '
            'repository, use a file:// URL.',
        ])
