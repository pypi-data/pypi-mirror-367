"""Unit tests for mercurial."""

from __future__ import annotations

import json
import os
import unittest
from typing import Optional, TYPE_CHECKING

import kgb
from djblets.testing.decorators import add_fixtures

from reviewboard.diffviewer.testing.mixins import DiffParserTestingMixin
from reviewboard.scmtools.core import (
    FileLookupContext,
    HEAD,
    PRE_CREATION,
    Revision,
)
from reviewboard.scmtools.errors import SCMError, FileNotFoundError
from reviewboard.scmtools.hg import (HgDiffParser,
                                     HgGitDiffParser,
                                     HgTool,
                                     HgWebClient)
from reviewboard.scmtools.tests.testcases import SCMTestCase
from reviewboard.testing import online_only
from reviewboard.testing.testcase import TestCase

if TYPE_CHECKING:
    from djblets.util.typing import SerializableJSONDict

    from reviewboard.scmtools.core import RevisionID, SCMClient


class MercurialTests(DiffParserTestingMixin, SCMTestCase):
    """Unit tests for mercurial."""

    fixtures = ['test_scmtools']

    def setUp(self) -> None:
        """Set up the test."""
        super().setUp()

        hg_repo_path = os.path.join(os.path.dirname(__file__),
                                    '..', 'testdata', 'hg_repo')
        self.repository = self.create_repository(
            name='Test HG',
            path=hg_repo_path,
            tool_name='Mercurial')

        try:
            self.tool = self.repository.get_scmtool()
        except ImportError:
            raise unittest.SkipTest('Hg is not installed')

    def test_ssh_disallowed(self) -> None:
        """Testing HgTool does not allow SSH URLs"""
        with self.assertRaises(SCMError):
            self.tool.check_repository('ssh://foo')

    def test_git_parser_selection_with_header(self) -> None:
        """Testing HgTool returns the git parser when a header is present"""
        diffContents = (b'# HG changeset patch\n'
                        b'# Node ID 6187592a72d7\n'
                        b'# Parent  9d3f4147f294\n'
                        b'diff --git a/emptyfile b/emptyfile\n'
                        b'new file mode 100644\n')

        parser = self.tool.get_parser(diffContents)
        self.assertEqual(type(parser), HgGitDiffParser)

    def test_hg_parser_selection_with_header(self) -> None:
        """Testing HgTool returns the hg parser when a header is present"""
        diffContents = (b'# HG changeset patch'
                        b'# Node ID 6187592a72d7\n'
                        b'# Parent  9d3f4147f294\n'
                        b'diff -r 9d3f4147f294 -r 6187592a72d7 new.py\n'
                        b'--- /dev/null   Thu Jan 01 00:00:00 1970 +0000\n'
                        b'+++ b/new.py  Tue Apr 21 12:20:05 2015 -0400\n')

        parser = self.tool.get_parser(diffContents)
        self.assertEqual(type(parser), HgDiffParser)

    def test_git_parser_sets_commit_ids(self) -> None:
        """Testing HgGitDiffParser sets the parser commit ids"""
        diffContents = (b'# HG changeset patch\n'
                        b'# Node ID 6187592a72d7\n'
                        b'# Parent  9d3f4147f294\n'
                        b'diff --git a/emptyfile b/emptyfile\n'
                        b'new file mode 100644\n')

        parser = self.tool.get_parser(diffContents)
        parser.parse()
        self.assertEqual(parser.new_commit_id, b'6187592a72d7')
        self.assertEqual(parser.base_commit_id, b'9d3f4147f294')

    def test_patch_creates_new_file(self) -> None:
        """Testing HgTool with a patch that creates a new file"""
        self.assertEqual(
            self.tool.parse_diff_revision(filename=b'/dev/null',
                                          revision=b'bf544ea505f8')[1],
            PRE_CREATION)

    def test_diff_parser_new_file(self) -> None:
        """Testing HgDiffParser with a diff that creates a new file"""
        diff = (
            b'diff -r bf544ea505f8 readme\n'
            b'--- /dev/null\n'
            b'+++ b/readme\n'
        )

        parsed_files = self.tool.get_parser(diff).parse()
        self.assertEqual(len(parsed_files), 1)

        self.assert_parsed_diff_file(
            parsed_files[0],
            orig_filename=b'readme',
            orig_file_details=PRE_CREATION,
            modified_filename=b'readme',
            modified_file_details=b'Uncommitted',
            data=diff)

    def test_diff_parser_with_added_empty_file(self) -> None:
        """Testing HgDiffParser with a diff with an added empty file"""
        diff = (
            b'diff -r 356a6127ef19 -r 4960455a8e88 empty\n'
            b'--- /dev/null\n'
            b'+++ b/empty\n'
        )

        parsed_files = self.tool.get_parser(diff).parse()
        self.assertEqual(len(parsed_files), 1)

        self.assert_parsed_diff_file(
            parsed_files[0],
            orig_filename=b'empty',
            orig_file_details=PRE_CREATION,
            modified_filename=b'empty',
            modified_file_details=b'4960455a8e88',
            data=diff)

    def test_diff_parser_with_deleted_empty_file(self) -> None:
        """Testing HgDiffParser with a diff with a deleted empty file"""
        diff = (
            b'diff -r 356a6127ef19 -r 4960455a8e88 empty\n'
            b'--- a/empty\n'
            b'+++ /dev/null\n'
        )

        parsed_files = self.tool.get_parser(diff).parse()
        self.assertEqual(len(parsed_files), 1)

        self.assert_parsed_diff_file(
            parsed_files[0],
            orig_filename=b'empty',
            orig_file_details=b'356a6127ef19',
            modified_filename=b'empty',
            modified_file_details=b'4960455a8e88',
            deleted=True,
            data=diff)

    def test_diff_parser_uncommitted(self) -> None:
        """Testing HgDiffParser with a diff with an uncommitted change"""
        diff = (
            b'diff -r bf544ea505f8 readme\n'
            b'--- a/readme\n'
            b'+++ b/readme\n'
        )

        parsed_files = self.tool.get_parser(diff).parse()
        self.assertEqual(len(parsed_files), 1)

        self.assert_parsed_diff_file(
            parsed_files[0],
            orig_filename=b'readme',
            orig_file_details=b'bf544ea505f8',
            modified_filename=b'readme',
            modified_file_details=b'Uncommitted',
            data=diff)

    def test_diff_parser_committed(self) -> None:
        """Testing HgDiffParser with a diff between committed revisions"""
        diff = (
            b'diff -r 356a6127ef19 -r 4960455a8e88 readme\n'
            b'--- a/readme\n'
            b'+++ b/readme\n'
        )

        parsed_files = self.tool.get_parser(diff).parse()
        self.assertEqual(len(parsed_files), 1)

        self.assert_parsed_diff_file(
            parsed_files[0],
            orig_filename=b'readme',
            orig_file_details=b'356a6127ef19',
            modified_filename=b'readme',
            modified_file_details=b'4960455a8e88',
            data=diff)

    def test_diff_parser_with_preamble_junk(self) -> None:
        """Testing HgDiffParser with a diff that contains non-diff junk text
        as a preamble
        """
        diff = (
            b'changeset:   60:3613c58ad1d5\n'
            b'user:        Michael Rowe <mrowe@mojain.com>\n'
            b'date:        Fri Jul 27 11:44:37 2007 +1000\n'
            b'files:       readme\n'
            b'description:\n'
            b'Update the readme file\n'
            b'\n'
            b'\n'
            b'diff -r 356a6127ef19 -r 4960455a8e88 readme\n'
            b'--- a/readme\n'
            b'+++ b/readme\n'
        )

        parsed_files = self.tool.get_parser(diff).parse()
        self.assertEqual(len(parsed_files), 1)

        self.assert_parsed_diff_file(
            parsed_files[0],
            orig_filename=b'readme',
            orig_file_details=b'356a6127ef19',
            modified_filename=b'readme',
            modified_file_details=b'4960455a8e88',
            data=diff)

    def test_git_diff_parsing(self) -> None:
        """Testing HgDiffParser git diff support"""
        diff = (
            b'# Node ID 4960455a8e88\n'
            b'# Parent bf544ea505f8\n'
            b'diff --git a/path/to file/readme.txt '
            b'b/new/path to/readme.txt\n'
            b'rename from path/to file/readme.txt\n'
            b'rename to new/path to/readme.txt\n'
            b'--- a/path/to file/readme.txt\n'
            b'+++ b/new/path to/readme.txt\n'
        )

        parsed_files = self.tool.get_parser(diff).parse()
        self.assertEqual(len(parsed_files), 1)

        self.assert_parsed_diff_file(
            parsed_files[0],
            orig_filename=b'path/to file/readme.txt',
            orig_file_details=b'bf544ea505f8',
            modified_filename=b'new/path to/readme.txt',
            modified_file_details=b'4960455a8e88',
            moved=True,
            data=diff)

    def test_git_diff_parser_with_new_binary_file(self) -> None:
        """Testing HgDiffParser diff with new binary file"""
        diff = (
            b'# Node ID 4960455a8e88\n'
            b'# Parent bf544ea505f8\n'
            b'diff --git a/test.png b/test.png\n'
            b'new file mode 100644\n'
            b'index 0000000000000000000000000000000000000000..'
            b'696eefb5e69b23fc2575f2eaf2863515f6937438\n'
            b'GIT binary patch\n'
            b'literal 12\n'
            b'zc$}1Zbx>SS@\n'
        )

        parsed_files = self.tool.get_parser(diff).parse()
        self.assertEqual(len(parsed_files), 1)

        self.assert_parsed_diff_file(
            parsed_files[0],
            orig_filename=b'test.png',
            orig_file_details=PRE_CREATION,
            modified_filename=b'test.png',
            modified_file_details=b'4960455a8e88',
            binary=True,
            new_unix_mode='100644',
            data=diff)

    def test_diff_parser_unicode(self) -> None:
        """Testing HgDiffParser with unicode characters"""
        diff = (
            'diff -r bf544ea505f8 réadme\n'
            '--- a/réadme\n'
            '+++ b/réadme\n'
        ).encode('utf-8')

        parsed_files = self.tool.get_parser(diff).parse()
        self.assertEqual(len(parsed_files), 1)

        self.assert_parsed_diff_file(
            parsed_files[0],
            orig_filename='réadme'.encode('utf-8'),
            orig_file_details=b'bf544ea505f8',
            modified_filename='réadme'.encode('utf-8'),
            modified_file_details=b'Uncommitted',
            data=diff)

    def test_git_diff_parsing_unicode(self) -> None:
        """Testing HgDiffParser git diff with unicode characters"""
        diff = (
            '# Node ID 4960455a8e88\n'
            '# Parent bf544ea505f8\n'
            'diff --git a/path/to file/réadme.txt '
            'b/new/path to/réadme.txt\n'
            'rename from path/to file/réadme.txt\n'
            'rename to new/path to/réadme.txt\n'
            '--- a/path/to file/réadme.txt\n'
            '+++ b/new/path to/réadme.txt\n'
        ).encode('utf-8')

        parsed_files = self.tool.get_parser(diff).parse()
        self.assertEqual(len(parsed_files), 1)

        self.assert_parsed_diff_file(
            parsed_files[0],
            orig_filename='path/to file/réadme.txt'.encode('utf-8'),
            orig_file_details=b'bf544ea505f8',
            modified_filename='new/path to/réadme.txt'.encode('utf-8'),
            modified_file_details=b'4960455a8e88',
            moved=True,
            data=diff)

    def test_revision_parsing(self) -> None:
        """Testing HgDiffParser revision number parsing"""
        self.assertEqual(
            self.tool.parse_diff_revision(filename=b'doc/readme',
                                          revision=b'bf544ea505f8'),
            (b'doc/readme', b'bf544ea505f8'))

        self.assertEqual(
            self.tool.parse_diff_revision(filename=b'/dev/null',
                                          revision=b'bf544ea505f8'),
            (b'/dev/null', PRE_CREATION))

    def test_get_branches(self) -> None:
        """Testing list of branches in HgClient.get_change"""
        value = self.tool.get_branches()
        self.assertTrue(isinstance(value, list))
        self.assertEqual(len(value), 1)

        self.assertEqual(value[0].id, 'default')
        self.assertEqual(value[0].commit,
                         '661e5dd3c4938ecbe8f77e2fdfa905d70485f94c')
        self.assertEqual(value[0].default, True)

    def test_get_change(self) -> None:
        """Testing raw diff of HgClient.get_change"""
        self.assertRaises(SCMError, lambda: self.tool.get_change('dummy'))

        value = self.tool.get_change('0')
        self.assertNotIn(b'goodbye', value.diff)
        self.assertEqual(value.id, 'f814b6e226d2ba6d26d02ca8edbff91f57ab2786')
        value = self.tool.get_change('1')
        self.assertIn(b'goodbye', value.diff)
        self.assertEqual(value.id, '661e5dd3c4938ecbe8f77e2fdfa905d70485f94c')

    def test_get_commits(self) -> None:
        """Testing commit objects in HgClient.get_commits"""
        value = self.tool.get_commits()
        self.assertTrue(isinstance(value, list))
        self.assertEqual(len(value), 2)

        self.assertEqual(value[0].id,
                         '661e5dd3c4938ecbe8f77e2fdfa905d70485f94c')
        self.assertEqual(value[0].message, 'second')
        self.assertEqual(value[0].author_name,
                         'Michael Rowe <mike.rowe@nab.com.au>')
        self.assertEqual(value[0].date, '2007-08-07T17:12:23')
        self.assertEqual(value[0].parent,
                         'f814b6e226d2ba6d26d02ca8edbff91f57ab2786')

        self.assertEqual(value[1].id,
                         'f814b6e226d2ba6d26d02ca8edbff91f57ab2786')
        self.assertEqual(value[1].message, 'first')
        self.assertEqual(value[1].author_name,
                         'Michael Rowe <mike.rowe@nab.com.au>')
        self.assertEqual(value[1].date, '2007-08-07T17:11:57')
        self.assertEqual(value[1].parent, '')

        self.assertRaisesRegex(SCMError, 'Cannot load commits: ',
                               lambda: self.tool.get_commits(branch='x'))

        rev = 'f814b6e226d2ba6d26d02ca8edbff91f57ab2786'
        value = self.tool.get_commits(start=rev)
        self.assertTrue(isinstance(value, list))
        self.assertEqual(len(value), 1)

    def test_get_commits_with_non_utc_server_timezone(self) -> None:
        """Testing commit objects in HgClient.get_commits with
        settings.TIME_ZONE != UTC
        """
        old_tz = os.environ['TZ']
        os.environ['TZ'] = 'US/Pacific'

        try:
            value = self.tool.get_commits()
        finally:
            os.environ['TZ'] = old_tz

        self.assertTrue(isinstance(value, list))
        self.assertEqual(len(value), 2)

        self.assertEqual(value[0].id,
                         '661e5dd3c4938ecbe8f77e2fdfa905d70485f94c')
        self.assertEqual(value[0].message, 'second')
        self.assertEqual(value[0].author_name,
                         'Michael Rowe <mike.rowe@nab.com.au>')
        self.assertEqual(value[0].date, '2007-08-07T17:12:23')
        self.assertEqual(value[0].parent,
                         'f814b6e226d2ba6d26d02ca8edbff91f57ab2786')

        self.assertEqual(value[1].id,
                         'f814b6e226d2ba6d26d02ca8edbff91f57ab2786')
        self.assertEqual(value[1].message, 'first')
        self.assertEqual(value[1].author_name,
                         'Michael Rowe <mike.rowe@nab.com.au>')
        self.assertEqual(value[1].date, '2007-08-07T17:11:57')
        self.assertEqual(value[1].parent, '')

        self.assertRaisesRegex(SCMError, 'Cannot load commits: ',
                               lambda: self.tool.get_commits(branch='x'))

        rev = 'f814b6e226d2ba6d26d02ca8edbff91f57ab2786'
        value = self.tool.get_commits(start=rev)
        self.assertTrue(isinstance(value, list))
        self.assertEqual(len(value), 1)

    def test_get_file(self) -> None:
        """Testing HgTool.get_file"""
        tool = self.tool

        value = tool.get_file('doc/readme', Revision('661e5dd3c493'))
        self.assertIsInstance(value, bytes)
        self.assertEqual(value, b'Hello\n\ngoodbye\n')

        with self.assertRaises(FileNotFoundError):
            tool.get_file('')

        with self.assertRaises(FileNotFoundError):
            tool.get_file('hello', PRE_CREATION)

    def test_file_exists(self) -> None:
        """Testing HgTool.file_exists"""
        rev = Revision('661e5dd3c493')

        self.assertTrue(self.tool.file_exists('doc/readme', rev))
        self.assertFalse(self.tool.file_exists('doc/readme2', rev))

    def test_get_file_base_commit_id_override(self) -> None:
        """Testing base_commit_id overrides revision in HgTool.get_file"""
        base_commit_id = '661e5dd3c493'
        bogus_rev = Revision('bogusrevision')
        file = 'doc/readme'

        context = FileLookupContext()
        context.base_commit_id = base_commit_id

        value = self.tool.get_file(file, bogus_rev, context=context)
        self.assertTrue(isinstance(value, bytes))
        self.assertEqual(value, b'Hello\n\ngoodbye\n')

        self.assertTrue(self.tool.file_exists(
            'doc/readme',
            bogus_rev,
            context=context))
        self.assertTrue(not self.tool.file_exists(
            'doc/readme2',
            bogus_rev,
            context=context))

    def test_interface(self) -> None:
        """Testing basic HgTool API"""
        self.assertTrue(self.tool.diffs_use_absolute_paths)

        self.assertRaises(NotImplementedError,
                          lambda: self.tool.get_changeset(1))

    @online_only
    def test_https_repo(self) -> None:
        """Testing HgTool.file_exists with an HTTPS-based repository"""
        repo = self.create_repository(
            name='Test HG2',
            path='https://www.mercurial-scm.org/repo/hg',
            tool_name='Mercurial')
        tool = repo.get_scmtool()

        self.assertTrue(tool.file_exists('mercurial/hgweb/common.py',
                                         Revision('f0735f2ce542')))
        self.assertFalse(tool.file_exists('mercurial/hgweb/common.py',
                                          Revision('abcdef123456')))

    def test_normalize_patch_with_git_diff_new_symlink(self) -> None:
        """Testing HgTool.normalize_patch with Git-style diff and new symlink
        """
        self.assertEqual(
            self.tool.normalize_patch(
                patch=(
                    b'diff --git /dev/null b/test\n'
                    b'new file mode 120000\n'
                    b'--- /dev/null\n'
                    b'+++ b/test\n'
                    b'@@ -0,0 +1,1 @@\n'
                    b'+target_file\n'
                    b'\\ No newline at end of file'
                ),
                filename='test',
                revision=PRE_CREATION),
            (
                b'diff --git /dev/null b/test\n'
                b'new file mode 100000\n'
                b'--- /dev/null\n'
                b'+++ b/test\n'
                b'@@ -0,0 +1,1 @@\n'
                b'+target_file\n'
                b'\\ No newline at end of file'
            ))

    def test_normalize_patch_with_git_diff_modified_symlink(self) -> None:
        """Testing HgTool.normalize_patch with Git-style diff and modified
        symlink
        """
        self.assertEqual(
            self.tool.normalize_patch(
                patch=(
                    b'diff --git a/test b/test\n'
                    b'index abc1234..def4567 120000\n'
                    b'--- a/test\n'
                    b'+++ b/test\n'
                    b'@@ -1,1 +1,1 @@\n'
                    b'-old_target\n'
                    b'\\ No newline at end of file'
                    b'+new_target\n'
                    b'\\ No newline at end of file'
                ),
                filename='test',
                revision='abc1234'),
            (
                b'diff --git a/test b/test\n'
                b'index abc1234..def4567 100000\n'
                b'--- a/test\n'
                b'+++ b/test\n'
                b'@@ -1,1 +1,1 @@\n'
                b'-old_target\n'
                b'\\ No newline at end of file'
                b'+new_target\n'
                b'\\ No newline at end of file'
            ))

    def test_normalize_patch_with_git_diff_deleted_symlink(self) -> None:
        """Testing HgTool.normalize_patch with Git-style diff and deleted
        symlink
        """
        self.assertEqual(
            self.tool.normalize_patch(
                patch=(
                    b'diff --git a/test b/test\n'
                    b'deleted file mode 120000\n'
                    b'index abc1234..0000000\n'
                    b'--- a/test\n'
                    b'+++ /dev/null\n'
                    b'@@ -1,1 +0,0 @@\n'
                    b'-old_target\n'
                    b'\\ No newline at end of file'
                ),
                filename='test',
                revision='abc1234'),
            (
                b'diff --git a/test b/test\n'
                b'deleted file mode 100000\n'
                b'index abc1234..0000000\n'
                b'--- a/test\n'
                b'+++ /dev/null\n'
                b'@@ -1,1 +0,0 @@\n'
                b'-old_target\n'
                b'\\ No newline at end of file'
            ))

    def test_normalize_patch_with_hg_diff(self) -> None:
        """Testing HgTool.normalize_patch with Git-style diff and deleted
        symlink
        """
        self.assertEqual(
            self.tool.normalize_patch(
                patch=(
                    b'diff -r 123456789abc -r 123456789def test\n'
                    b'--- a/test\n'
                    b'+++ b/test\n'
                    b'@@ -1,1 +1,1 @@\n'
                    b'-a\n'
                    b'-b\n'
                ),
                filename='test',
                revision='123456789abc'),
            (
                b'diff -r 123456789abc -r 123456789def test\n'
                b'--- a/test\n'
                b'+++ b/test\n'
                b'@@ -1,1 +1,1 @@\n'
                b'-a\n'
                b'-b\n'
            ))

    def test_get_diff_parser_cls_with_git_diff(self) -> None:
        """Testing HgTool._get_diff_parser_cls with Git diff"""
        self.assertIs(
            self.tool._get_diff_parser_cls(
                b'diff --git a/test b/test\n'
                b'--- a/test\n'
                b'+++ b/test\n'
                b'@@ -1,1 +1,1 @@\n'
                b'-a\n'
                b'-b\n'),
            HgGitDiffParser)

    def test_get_diff_parser_cls_with_git_diff_and_header(self) -> None:
        """Testing HgTool._get_diff_parser_cls with Git diff and header"""
        self.assertIs(
            self.tool._get_diff_parser_cls(
                b'# HG changeset patch\n'
                b'# Node ID 123456789abc\n'
                b'# Parent cba987654321\n'
                b'diff --git a/test b/test\n'
                b'--- a/test\n'
                b'+++ b/test\n'
                b'@@ -1,1 +1,1 @@\n'
                b'-a\n'
                b'-b\n'),
            HgGitDiffParser)

    def test_get_diff_parser_cls_with_hg_diff(self) -> None:
        """Testing HgTool._get_diff_parser_cls with Mercurial diff"""
        self.assertIs(
            self.tool._get_diff_parser_cls(
                b'diff -r 123456789abc -r 123456789def test\n'
                b'--- a/test   Thu Feb 17 12:36:00 2022 -0700\n'
                b'+++ b/test   Thu Feb 17 12:36:15 2022 -0700\n'
                b'@@ -1,1 +1,1 @@\n'
                b'-a\n'
                b'-b\n'),
            HgDiffParser)

    def test_get_diff_parser_cls_with_hg_diff_and_header(self) -> None:
        """Testing HgTool._get_diff_parser_cls with Mercurial diff and header
        """
        self.assertIs(
            self.tool._get_diff_parser_cls(
                b'# HG changeset patch\n'
                b'# Node ID 123456789abc\n'
                b'# Parent cba987654321\n'
                b'diff -r 123456789abc -r 123456789def test\n'
                b'--- a/test   Thu Feb 17 12:36:00 2022 -0700\n'
                b'+++ b/test   Thu Feb 17 12:36:15 2022 -0700\n'
                b'@@ -1,1 +1,1 @@\n'
                b'-a\n'
                b'-b\n'),
            HgDiffParser)

    def test_get_diff_parser_cls_with_git_before_hg(self) -> None:
        """Testing HgTool._get_diff_parser_cls with diff --git before diff -r
        """
        self.assertIs(
            self.tool._get_diff_parser_cls(
                b'diff --git a/test b/test\n'
                b'diff -r 123456789abc -r 123456789def test\n'),
            HgGitDiffParser)

    def test_get_diff_parser_cls_with_hg_before_git(self) -> None:
        """Testing HgTool._get_diff_parser_cls with diff -r before diff --git
        """
        self.assertIs(
            self.tool._get_diff_parser_cls(
                b'diff -r 123456789abc -r 123456789def test\n'
                b'diff --git a/test b/test\n'),
            HgDiffParser)


class HgWebClientTests(kgb.SpyAgency, TestCase):
    """Unit tests for reviewboard.scmtools.hg.HgWebClient."""

    def setUp(self) -> None:
        """Set up the test."""
        super().setUp()

        self.hgweb_client = HgWebClient(path='http://hg.example.com/',
                                        username='test-user',
                                        password='test-password')

    def test_cat_file_with_raw_file(self) -> None:
        """Testing HgWebClient.cat_file with URL using raw-file"""
        def _get_file_http(
            client: SCMClient,
            url: str,
            path: str,
            revision: RevisionID,
            mime_type: Optional[str],
            *args,
            **kwargs,
        ) -> Optional[bytes]:
            if url.startswith('http://hg.example.com/raw-file/'):
                return b'result payload'

            raise FileNotFoundError(path=path,
                                    revision=revision)

        spy = self.spy_on(self.hgweb_client.get_file_http,
                          call_fake=_get_file_http)

        rsp = self.hgweb_client.cat_file(path='foo/bar.txt',
                                         rev=HEAD)
        self.assertIsInstance(rsp, bytes)
        self.assertEqual(rsp, b'result payload')

        spy = self.hgweb_client.get_file_http.spy
        self.assertEqual(len(spy.calls), 1)
        self.assertTrue(spy.last_called_with(
            url='http://hg.example.com/raw-file/tip/foo/bar.txt',
            path='foo/bar.txt',
            revision='tip'))

    def test_cat_file_with_raw(self) -> None:
        """Testing HgWebClient.cat_file with URL using raw"""
        def _get_file_http(
            client: SCMClient,
            url: str,
            path: str,
            revision: RevisionID,
            mime_type: Optional[str],
            *args,
            **kwargs,
        ) -> Optional[bytes]:
            if url.startswith('http://hg.example.com/raw/'):
                return b'result payload'

            raise FileNotFoundError(path=path,
                                    revision=revision)

        spy = self.spy_on(self.hgweb_client.get_file_http,
                          call_fake=_get_file_http)

        rsp = self.hgweb_client.cat_file(path='foo/bar.txt',
                                         rev=HEAD)
        self.assertIsInstance(rsp, bytes)
        self.assertEqual(rsp, b'result payload')

        spy = self.hgweb_client.get_file_http.spy
        self.assertEqual(len(spy.calls), 2)
        self.assertTrue(spy.last_called_with(
            url='http://hg.example.com/raw/tip/foo/bar.txt',
            path='foo/bar.txt',
            revision='tip'))

    def test_cat_file_with_hg_history(self) -> None:
        """Testing HgWebClient.cat_file with URL using hg-history"""
        def _get_file_http(
            client: SCMClient,
            url: str,
            path: str,
            revision: RevisionID,
            mime_type: Optional[str],
            *args,
            **kwargs,
        ) -> Optional[bytes]:
            if url.startswith('http://hg.example.com/hg-history/'):
                return b'result payload'

            raise FileNotFoundError(path=path,
                                    revision=revision)

        self.spy_on(self.hgweb_client.get_file_http,
                    call_fake=_get_file_http)

        rsp = self.hgweb_client.cat_file(path='foo/bar.txt',
                                         rev=HEAD)
        self.assertIsInstance(rsp, bytes)
        self.assertEqual(rsp, b'result payload')

        spy = self.hgweb_client.get_file_http.spy
        self.assertEqual(len(spy.calls), 3)
        self.assertTrue(spy.last_called_with(
            url='http://hg.example.com/hg-history/tip/foo/bar.txt',
            path='foo/bar.txt',
            revision='tip'))

    def test_cat_file_with_base_commit_id(self) -> None:
        """Testing HgWebClient.cat_file with base_commit_id"""
        spy = self.spy_on(self.hgweb_client.get_file_http,
                          op=kgb.SpyOpReturn(b'result payload'))

        rsp = self.hgweb_client.cat_file(
            path='foo/bar.txt',
            base_commit_id='1ca5879492b8fd606df1964ea3c1e2f4520f076f')
        self.assertIsInstance(rsp, bytes)
        self.assertEqual(rsp, b'result payload')

        self.assertEqual(len(spy.calls), 1)
        self.assertTrue(spy.last_called_with(
            url='http://hg.example.com/raw-file/'
                '1ca5879492b8fd606df1964ea3c1e2f4520f076f/foo/bar.txt',
            path='foo/bar.txt',
            revision='1ca5879492b8fd606df1964ea3c1e2f4520f076f'))

    def test_cat_file_with_not_found(self) -> None:
        """Testing HgWebClient.cat_file with file not found"""
        spy = self.spy_on(
            self.hgweb_client.get_file_http,
            op=kgb.SpyOpRaise(FileNotFoundError('foo/bar.txt')))

        with self.assertRaises(FileNotFoundError):
            self.hgweb_client.cat_file(path='foo/bar.txt')

        self.assertEqual(len(spy.calls), 3)

    def test_get_branches(self) -> None:
        """Testing HgWebClient.get_branches"""
        def _get_file_http(
            client: SCMClient,
            url: str,
            path: str,
            revision: RevisionID,
            mime_type: Optional[str],
            *args,
            **kwargs,
        ) -> Optional[bytes]:
            self.assertEqual(url, 'http://hg.example.com/json-branches')
            self.assertEqual(mime_type, 'application/json')
            self.assertEqual(path, '')
            self.assertEqual(revision, '')

            return self._dump_json({
                'branches': [
                    {
                        'branch': 'default',
                        'node': '1ca5879492b8fd606df1964ea3c1e2f4520f076f',
                        'status': 'open',
                    },
                    {
                        'branch': 'closed-branch',
                        'node': 'b9af6489f6f2004ad11b82c6057f7007e3c35372',
                        'status': 'closed',
                    },
                    {
                        'branch': 'release-branch',
                        'node': '8210c0d945ef893d40a903c9dc14cd072eee5bb7',
                        'status': 'open',
                    },
                ],
            })

        self.spy_on(self.hgweb_client.get_file_http,
                    call_fake=_get_file_http)

        branches = self.hgweb_client.get_branches()
        self.assertIsInstance(branches, list)
        self.assertEqual(len(branches), 2)

        branch = branches[0]
        self.assertEqual(branch.id, 'default')
        self.assertEqual(branch.commit,
                         '1ca5879492b8fd606df1964ea3c1e2f4520f076f')
        self.assertTrue(branch.default)

        branch = branches[1]
        self.assertEqual(branch.id, 'release-branch')
        self.assertEqual(branch.commit,
                         '8210c0d945ef893d40a903c9dc14cd072eee5bb7')
        self.assertFalse(branch.default)

    def test_get_branches_with_error(self) -> None:
        """Testing HgWebClient.get_branches with error fetching result"""
        def _get_file_http(
            client: SCMClient,
            url: str,
            path: str,
            revision: RevisionID,
            mime_type: Optional[str],
            *args,
            **kwargs,
        ) -> Optional[bytes]:
            raise FileNotFoundError(path, revision)

        self.spy_on(self.hgweb_client.get_file_http,
                    call_fake=_get_file_http)

        branches = self.hgweb_client.get_branches()
        self.assertEqual(branches, [])

    def test_get_change(self) -> None:
        """Testing HgWebClient.get_change"""
        def _get_file_http(
            client: SCMClient,
            url: str,
            path: str,
            revision: RevisionID,
            mime_type: Optional[str],
            *args,
            **kwargs,
        ) -> Optional[bytes]:
            if url.startswith('http://hg.example.com/raw-rev/'):
                self.assertEqual(
                    url,
                    'http://hg.example.com/raw-rev/'
                    '1ca5879492b8fd606df1964ea3c1e2f4520f076f')
                self.assertEqual(path, '')
                self.assertEqual(revision, '')
                self.assertIsNone(mime_type)

                return b'diff payload'
            elif url.startswith('http://hg.example.com/json-rev/'):
                self.assertEqual(
                    url,
                    'http://hg.example.com/json-rev/'
                    '1ca5879492b8fd606df1964ea3c1e2f4520f076f')
                self.assertEqual(mime_type, 'application/json')
                self.assertEqual(path, '')
                self.assertEqual(revision, '')

                return self._dump_json({
                    'node': '1ca5879492b8fd606df1964ea3c1e2f4520f076f',
                    'desc': 'This is the change description',
                    'user': 'Test User',
                    'date': [1583149219, 28800],
                    'parents': [
                        'b9af6489f6f2004ad11b82c6057f7007e3c35372',
                    ],
                })
            else:
                raise FileNotFoundError(path=path,
                                        revision=revision)

        self.spy_on(self.hgweb_client.get_file_http,
                    call_fake=_get_file_http)

        commit = self.hgweb_client.get_change(
            '1ca5879492b8fd606df1964ea3c1e2f4520f076f')
        self.assertEqual(commit.id, '1ca5879492b8fd606df1964ea3c1e2f4520f076f')
        self.assertEqual(commit.message, 'This is the change description')
        self.assertEqual(commit.author_name, 'Test User')
        self.assertEqual(commit.date, '2020-03-02T03:40:19')
        self.assertEqual(commit.parent,
                         'b9af6489f6f2004ad11b82c6057f7007e3c35372')

    def test_get_commits(self) -> None:
        """Testing HgWebClient.get_commits"""
        def _get_file_http(
            client: SCMClient,
            url: str,
            path: str,
            revision: RevisionID,
            mime_type: Optional[str],
            *args,
            **kwargs,
        ) -> Optional[bytes]:
            self.assertEqual(
                url,
                'http://hg.example.com/json-log/?rev=branch(.)')
            self.assertEqual(mime_type, 'application/json')
            self.assertEqual(path, '')
            self.assertEqual(revision, '')

            return self._dump_json({
                'entries': [
                    {
                        'node': '1ca5879492b8fd606df1964ea3c1e2f4520f076f',
                        'desc': 'This is the change description',
                        'user': 'Test User',
                        'date': [1583149219, 28800],
                        'parents': [
                            'b9af6489f6f2004ad11b82c6057f7007e3c35372',
                        ],
                    },
                    {
                        'node': 'b9af6489f6f2004ad11b82c6057f7007e3c35372',
                        'desc': 'This is another description',
                        'user': 'Another User',
                        'date': [1581897120, 28800],
                        'parents': [
                            '8210c0d945ef893d40a903c9dc14cd072eee5bb7',
                        ],
                    },
                ],
            })

        self.spy_on(self.hgweb_client.get_file_http,
                    call_fake=_get_file_http)

        commits = self.hgweb_client.get_commits()
        self.assertEqual(len(commits), 2)

        commit = commits[0]
        self.assertEqual(commit.id, '1ca5879492b8fd606df1964ea3c1e2f4520f076f')
        self.assertEqual(commit.message, 'This is the change description')
        self.assertEqual(commit.author_name, 'Test User')
        self.assertEqual(commit.date, '2020-03-02T03:40:19')
        self.assertEqual(commit.parent,
                         'b9af6489f6f2004ad11b82c6057f7007e3c35372')

        commit = commits[1]
        self.assertEqual(commit.id, 'b9af6489f6f2004ad11b82c6057f7007e3c35372')
        self.assertEqual(commit.message, 'This is another description')
        self.assertEqual(commit.author_name, 'Another User')
        self.assertEqual(commit.date, '2020-02-16T15:52:00')
        self.assertEqual(commit.parent,
                         '8210c0d945ef893d40a903c9dc14cd072eee5bb7')

    def test_get_commits_with_branch(self) -> None:
        """Testing HgWebClient.get_commits with branch"""
        def _get_file_http(
            client: SCMClient,
            url: str,
            path: str,
            revision: RevisionID,
            mime_type: Optional[str],
            *args,
            **kwargs,
        ) -> Optional[bytes]:
            self.assertEqual(
                url,
                'http://hg.example.com/json-log/?rev=branch(my-branch)')
            self.assertEqual(mime_type, 'application/json')
            self.assertEqual(path, '')
            self.assertEqual(revision, '')

            return self._dump_json({
                'entries': [
                    {
                        'node': '1ca5879492b8fd606df1964ea3c1e2f4520f076f',
                        'desc': 'This is the change description',
                        'user': 'Test User',
                        'date': [1583149219, 28800],
                        'parents': [
                            'b9af6489f6f2004ad11b82c6057f7007e3c35372',
                        ],
                    },
                    {
                        'node': 'b9af6489f6f2004ad11b82c6057f7007e3c35372',
                        'desc': 'This is another description',
                        'user': 'Another User',
                        'date': [1581897120, 28800],
                        'parents': [
                            '8210c0d945ef893d40a903c9dc14cd072eee5bb7',
                        ],
                    },
                ],
            })

        self.spy_on(self.hgweb_client.get_file_http,
                    call_fake=_get_file_http)

        commits = self.hgweb_client.get_commits(branch='my-branch')
        self.assertEqual(len(commits), 2)

        commit = commits[0]
        self.assertEqual(commit.id, '1ca5879492b8fd606df1964ea3c1e2f4520f076f')
        self.assertEqual(commit.message, 'This is the change description')
        self.assertEqual(commit.author_name, 'Test User')
        self.assertEqual(commit.date, '2020-03-02T03:40:19')
        self.assertEqual(commit.parent,
                         'b9af6489f6f2004ad11b82c6057f7007e3c35372')

        commit = commits[1]
        self.assertEqual(commit.id, 'b9af6489f6f2004ad11b82c6057f7007e3c35372')
        self.assertEqual(commit.message, 'This is another description')
        self.assertEqual(commit.author_name, 'Another User')
        self.assertEqual(commit.date, '2020-02-16T15:52:00')
        self.assertEqual(commit.parent,
                         '8210c0d945ef893d40a903c9dc14cd072eee5bb7')

    def test_get_commits_with_start(self) -> None:
        """Testing HgWebClient.get_commits with start"""
        def _get_file_http(
            client: SCMClient,
            url: str,
            path: str,
            revision: RevisionID,
            mime_type: Optional[str],
            *args,
            **kwargs,
        ) -> Optional[bytes]:
            self.assertEqual(
                url,
                'http://hg.example.com/json-log/'
                '?rev=ancestors(1ca5879492b8fd606df1964ea3c1e2f4520f076f)'
                '+and+branch(.)')
            self.assertEqual(mime_type, 'application/json')
            self.assertEqual(path, '')
            self.assertEqual(revision, '')

            return self._dump_json({
                'entries': [
                    {
                        'node': '1ca5879492b8fd606df1964ea3c1e2f4520f076f',
                        'desc': 'This is the change description',
                        'user': 'Test User',
                        'date': [1583149219, 28800],
                        'parents': [
                            'b9af6489f6f2004ad11b82c6057f7007e3c35372',
                        ],
                    },
                    {
                        'node': 'b9af6489f6f2004ad11b82c6057f7007e3c35372',
                        'desc': 'This is another description',
                        'user': 'Another User',
                        'date': [1581897120, 28800],
                        'parents': [
                            '8210c0d945ef893d40a903c9dc14cd072eee5bb7',
                        ],
                    },
                ],
            })

        self.spy_on(self.hgweb_client.get_file_http,
                    call_fake=_get_file_http)

        commits = self.hgweb_client.get_commits(
            start='1ca5879492b8fd606df1964ea3c1e2f4520f076f')
        self.assertEqual(len(commits), 2)

        commit = commits[0]
        self.assertEqual(commit.id, '1ca5879492b8fd606df1964ea3c1e2f4520f076f')
        self.assertEqual(commit.message, 'This is the change description')
        self.assertEqual(commit.author_name, 'Test User')
        self.assertEqual(commit.date, '2020-03-02T03:40:19')
        self.assertEqual(commit.parent,
                         'b9af6489f6f2004ad11b82c6057f7007e3c35372')

        commit = commits[1]
        self.assertEqual(commit.id, 'b9af6489f6f2004ad11b82c6057f7007e3c35372')
        self.assertEqual(commit.message, 'This is another description')
        self.assertEqual(commit.author_name, 'Another User')
        self.assertEqual(commit.date, '2020-02-16T15:52:00')
        self.assertEqual(commit.parent,
                         '8210c0d945ef893d40a903c9dc14cd072eee5bb7')

    def test_get_commits_with_not_implemented(self) -> None:
        """Testing HgWebClient.get_commits with server response of "not yet
        implemented"
        """
        def _get_file_http(
            client: SCMClient,
            url: str,
            path: str,
            revision: RevisionID,
            mime_type: Optional[str],
            *args,
            **kwargs,
        ) -> Optional[bytes]:
            self.assertEqual(url,
                             'http://hg.example.com/json-log/?rev=branch(.)')
            self.assertEqual(mime_type, 'application/json')
            self.assertEqual(path, '')
            self.assertEqual(revision, '')

            return b'not yet implemented'

        self.spy_on(self.hgweb_client.get_file_http,
                    call_fake=_get_file_http)

        commits = self.hgweb_client.get_commits()
        self.assertEqual(commits, [])

    def _dump_json(
        self,
        obj: SerializableJSONDict,
    ) -> bytes:
        """Dump an object to a JSON byte string.

        Args:
            obj (object):
                The object to dump.

        Returns:
            bytes;
            The JSON-serialized byte string.
        """
        return json.dumps(obj).encode('utf-8')


class HgAuthFormTests(TestCase):
    """Unit tests for HgTool's authentication form."""

    def test_fields(self) -> None:
        """Testing HgTool authentication form fields"""
        form = HgTool.create_auth_form()

        self.assertEqual(list(form.fields), ['username', 'password'])
        self.assertEqual(form['username'].help_text, '')
        self.assertEqual(form['username'].label, 'Username')
        self.assertEqual(form['password'].help_text, '')
        self.assertEqual(form['password'].label, 'Password')

    @add_fixtures(['test_scmtools'])
    def test_load(self) -> None:
        """Tetting HgTool authentication form load"""
        repository = self.create_repository(
            tool_name='Mercurial',
            username='test-user',
            password='test-pass')

        form = HgTool.create_auth_form(repository=repository)
        form.load()

        self.assertEqual(form['username'].value(), 'test-user')
        self.assertEqual(form['password'].value(), 'test-pass')

    @add_fixtures(['test_scmtools'])
    def test_save(self) -> None:
        """Tetting HgTool authentication form save"""
        repository = self.create_repository(tool_name='Mercurial')

        form = HgTool.create_auth_form(
            repository=repository,
            data={
                'username': 'test-user',
                'password': 'test-pass',
            })
        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(repository.username, 'test-user')
        self.assertEqual(repository.password, 'test-pass')


class HgRepositoryFormTests(TestCase):
    """Unit tests for HgTool's repository form."""

    def test_fields(self) -> None:
        """Testing HgTool repository form fields"""
        form = HgTool.create_repository_form()

        self.assertEqual(list(form.fields), ['path', 'mirror_path'])
        self.assertEqual(form['path'].help_text,
                         'The path to the repository. This will generally be '
                         'the URL you would use to check out the repository.')
        self.assertEqual(form['path'].label, 'Path')
        self.assertEqual(form['mirror_path'].help_text, '')
        self.assertEqual(form['mirror_path'].label, 'Mirror Path')

    @add_fixtures(['test_scmtools'])
    def test_load(self) -> None:
        """Tetting HgTool repository form load"""
        repository = self.create_repository(
            tool_name='Mercurial',
            path='https://hg.example.com/repo',
            mirror_path='https://hg.mirror.example.com/repo')

        form = HgTool.create_repository_form(repository=repository)
        form.load()

        self.assertEqual(form['path'].value(), 'https://hg.example.com/repo')
        self.assertEqual(form['mirror_path'].value(),
                         'https://hg.mirror.example.com/repo')

    @add_fixtures(['test_scmtools'])
    def test_save(self) -> None:
        """Tetting HgTool repository form save"""
        repository = self.create_repository(tool_name='Mercurial')

        form = HgTool.create_repository_form(
            repository=repository,
            data={
                'path': 'https://hg.example.com/repo',
                'mirror_path': 'https://hg.mirror.example.com/repo',
            })
        self.assertTrue(form.is_valid())
        form.save()

        self.assertEqual(repository.path, 'https://hg.example.com/repo')
        self.assertEqual(repository.mirror_path,
                         'https://hg.mirror.example.com/repo')
