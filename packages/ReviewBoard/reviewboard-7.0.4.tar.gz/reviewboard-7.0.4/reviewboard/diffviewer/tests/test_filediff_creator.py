"""Tests for reviewboard.diffviewer.filediff_creator."""

from __future__ import annotations

from typing import TYPE_CHECKING, Union

import kgb
from django.utils.timezone import now

from reviewboard.diffviewer.filediff_creator import create_filediffs
from reviewboard.diffviewer.models import DiffCommit, DiffSet
from reviewboard.scmtools.core import Revision
from reviewboard.scmtools.git import GitTool
from reviewboard.testing import TestCase

if TYPE_CHECKING:
    from reviewboard.scmtools.core import FileLookupContext


class FileDiffCreatorTests(kgb.SpyAgency, TestCase):
    """Tests for reviewboard.diffviewer.filediff_creator."""

    fixtures = ['test_scmtools']

    def test_create_filediffs_file_count(self):
        """Testing create_filediffs() with a DiffSet"""
        repository = self.create_repository()
        diffset = self.create_diffset(repository=repository)

        self.assertEqual(diffset.files.count(), 0)

        create_filediffs(
            diff_file_contents=self.DEFAULT_GIT_FILEDIFF_DATA_DIFF,
            parent_diff_file_contents=None,
            repository=repository,
            basedir='/',
            base_commit_id='0' * 40,
            diffset=diffset,
            check_existence=False)

        diffset = DiffSet.objects.get(pk=diffset.pk)

        self.assertEqual(diffset.files.count(), 1)

    def test_create_filediffs_commit_file_count(self):
        """Testing create_filediffs() with a DiffSet and a DiffCommit"""
        repository = self.create_repository()
        diffset = DiffSet.objects.create_empty(repository=repository)
        commits = [
            DiffCommit.objects.create(
                diffset=diffset,
                filename='diff',
                author_name='Author Name',
                author_email='author@example.com',
                commit_message='Message',
                author_date=now(),
                commit_id='a' * 40,
                parent_id='0' * 40),
            DiffCommit.objects.create(
                diffset=diffset,
                filename='diff',
                author_name='Author Name',
                author_email='author@example.com',
                commit_message='Message',
                author_date=now(),
                commit_id='b' * 40,
                parent_id='a' * 40),
        ]

        self.assertEqual(diffset.files.count(), 0)
        self.assertEqual(commits[0].files.count(), 0)

        create_filediffs(
            diff_file_contents=self.DEFAULT_GIT_FILEDIFF_DATA_DIFF,
            parent_diff_file_contents=None,
            repository=repository,
            basedir='/',
            base_commit_id='0' * 40,
            diffset=diffset,
            diffcommit=commits[0],
            check_existence=False)

        diffset = DiffSet.objects.get(pk=diffset.pk)
        commits[0] = DiffCommit.objects.get(pk=commits[0].pk)

        self.assertEqual(diffset.files.count(), 1)
        self.assertEqual(commits[0].files.count(), 1)

        create_filediffs(
            diff_file_contents=self.DEFAULT_GIT_FILEDIFF_DATA_DIFF,
            parent_diff_file_contents=None,
            repository=repository,
            basedir='/',
            base_commit_id='0' * 40,
            diffset=diffset,
            diffcommit=commits[1],
            check_existence=False)

        diffset = DiffSet.objects.get(pk=diffset.pk)
        commits[1] = DiffCommit.objects.get(pk=commits[1].pk)

        self.assertEqual(diffset.files.count(), 2)
        self.assertEqual(commits[1].files.count(), 1)

    def test_create_filediffs_with_symlinks(self):
        """Testing create_filediffs() with symlinks"""
        repository = self.create_repository(tool_name='TestToolDiffX')
        diffset = self.create_diffset(repository=repository)

        self.assertEqual(diffset.files.count(), 0)

        create_filediffs(
            diff_file_contents=(
                b'#diffx: encoding=utf-8, version=1.0\n'
                b'#.change:\n'
                b'#..file:\n'
                b'#...meta: format=json, length=140\n'
                b'{\n'
                b'    "op": "modify",\n'
                b'    "path": "name",\n'
                b'    "revision": {\n'
                b'        "old": "abc123",\n'
                b'        "new": "def456"\n'
                b'    },\n'
                b'    "type": "symlink"\n'
                b'}\n'
            ),
            parent_diff_file_contents=None,
            repository=repository,
            basedir='/',
            base_commit_id='0' * 40,
            diffset=diffset,
            check_existence=False)

        diffset = DiffSet.objects.get(pk=diffset.pk)

        self.assertEqual(diffset.files.count(), 1)
        filediff = diffset.files.get()

        self.assertTrue(filediff.is_symlink)
        self.assertIsNone(filediff.old_symlink_target)
        self.assertIsNone(filediff.new_symlink_target)

    def test_create_filediffs_with_symlinks_and_targets(self):
        """Testing create_filediffs() with symlinks and symlink targets"""
        repository = self.create_repository(tool_name='TestToolDiffX')
        diffset = self.create_diffset(repository=repository)

        self.assertEqual(diffset.files.count(), 0)

        create_filediffs(
            diff_file_contents=(
                b'#diffx: encoding=utf-8, version=1.0\n'
                b'#.change:\n'
                b'#..file:\n'
                b'#...meta: format=json, length=230\n'
                b'{\n'
                b'    "op": "modify",\n'
                b'    "path": "name",\n'
                b'    "revision": {\n'
                b'        "old": "abc123",\n'
                b'        "new": "def456"\n'
                b'    },\n'
                b'    "symlink target": {\n'
                b'        "old": "old/target/",\n'
                b'        "new": "new/target/"\n'
                b'    },\n'
                b'    "type": "symlink"\n'
                b'}\n'
            ),
            parent_diff_file_contents=None,
            repository=repository,
            basedir='/',
            base_commit_id='0' * 40,
            diffset=diffset,
            check_existence=False)

        diffset = DiffSet.objects.get(pk=diffset.pk)

        self.assertEqual(diffset.files.count(), 1)
        filediff = diffset.files.get()

        self.assertTrue(filediff.is_symlink)
        self.assertEqual(filediff.old_symlink_target, 'old/target/')
        self.assertEqual(filediff.new_symlink_target, 'new/target/')

    def test_create_filediffs_with_unix_mode(self):
        """Testing create_filediffs() with UNIX file modes"""
        repository = self.create_repository(tool_name='TestToolDiffX')
        diffset = self.create_diffset(repository=repository)

        self.assertEqual(diffset.files.count(), 0)

        create_filediffs(
            diff_file_contents=(
                b'#diffx: encoding=utf-8, version=1.0\n'
                b'#.change:\n'
                b'#..file:\n'
                b'#...meta: format=json, length=199\n'
                b'{\n'
                b'    "op": "modify",\n'
                b'    "path": "name",\n'
                b'    "revision": {\n'
                b'        "old": "abc123",\n'
                b'        "new": "def456"\n'
                b'    },\n'
                b'    "unix file mode": {\n'
                b'        "old": "0100644",\n'
                b'        "new": "0100755"\n'
                b'    }\n'
                b'}\n'
            ),
            parent_diff_file_contents=None,
            repository=repository,
            basedir='/',
            base_commit_id='0' * 40,
            diffset=diffset,
            check_existence=False)

        diffset = DiffSet.objects.get(pk=diffset.pk)

        self.assertEqual(diffset.files.count(), 1)
        filediff = diffset.files.get()

        self.assertEqual(filediff.old_unix_mode, '0100644')
        self.assertEqual(filediff.new_unix_mode, '0100755')

    def test_create_filediffs_with_parent_and_revision_instance(self) -> None:
        """Testing create_filediffs() with parent diff and revisions as
        Revision
        """
        repository = self.create_repository(tool_name='Git')
        diffset = self.create_diffset(repository=repository)

        self.assertEqual(diffset.files.count(), 0)

        def _parse_diff_revision(
            self: object,
            filename: bytes,
            revision: bytes,
            *args,
            **kwargs,
        ) -> tuple[bytes, Union[Revision, bytes]]:
            return (filename, Revision(revision.decode('utf-8')))

        # Make sure we run this test with a Revision as a result.
        self.spy_on(GitTool.parse_diff_revision,
                    owner=GitTool,
                    call_fake=_parse_diff_revision)

        # We'll use the same diff for both tests. It doesn't really matter.
        # We're just looking for the end result of the parsed filenames and
        # revisions here.
        create_filediffs(
            diff_file_contents=(
                b'diff --git a/readme b/readme\n'
                b'index 1234567..7654321\n'
                b'--- a/readme\n'
                b'+++ b/readme\n'
                b'@@ -1 +1 @@\n'
                b'Test 1\n'
                b'Test 2\n'
            ),
            parent_diff_file_contents=(
                b'diff --git /dev/null b/readme\n'
                b'index 1234567..7654321\n'
                b'--- a/readme\n'
                b'+++ b/readme\n'
                b'@@ -1 +1 @@\n'
                b'Test 1\n'
                b'Test 2\n'
            ),
            repository=repository,
            basedir='/',
            base_commit_id='0' * 40,
            diffset=diffset,
            check_existence=False)

        diffset = DiffSet.objects.get(pk=diffset.pk)

        self.assertEqual(diffset.files.count(), 1)
        filediff = diffset.files.get()

        self.assertEqual(filediff.source_revision, '1234567')
        self.assertEqual(filediff.dest_detail, '7654321')
        self.assertEqual(filediff.extra_data.get('parent_source_filename'),
                         '/readme')
        self.assertEqual(filediff.extra_data.get('parent_source_revision'),
                         '1234567')

    def test_create_filediffs_without_per_file_revisions(self) -> None:
        """Testing create_filediffs() without per-file revisions and
        validated parent ID
        """
        repository = self.create_repository(tool_name='Mercurial')
        diffset = self.create_diffset(repository=repository)

        self.assertEqual(diffset.files.count(), 0)

        def get_file_exists(
            *args,
            context: FileLookupContext,
            **kwargs,
        ) -> bool:
            context.file_extra_data['__validated_parent_id'] = 'zzzzzzzzzzzz'

            return True

        create_filediffs(
            diff_file_contents=(
                b'# HG changeset patch\n'
                b'# Node ID aaaaaaaaaaaa\n'
                b'# Parent  bbbbbbbbbbbb\n'
                b'diff --git a/readme b/readme\n'
                b'--- a/readme\n'
                b'+++ b/readme\n'
                b'@@ -1 +1 @@\n'
                b'Test 1\n'
                b'Test 2\n'
            ),
            parent_diff_file_contents=None,
            repository=repository,
            basedir='/',
            base_commit_id='0' * 40,
            diffset=diffset,
            get_file_exists=get_file_exists)

        diffset = DiffSet.objects.get(pk=diffset.pk)

        self.assertEqual(diffset.files.count(), 1)
        filediff = diffset.files.get()

        self.assertEqual(filediff.source_revision, 'zzzzzzzzzzzz')
        self.assertEqual(filediff.dest_detail, 'aaaaaaaaaaaa')
        self.assertEqual(filediff.extra_data, {
            'is_symlink': False,
            'raw_delete_count': 0,
            'raw_insert_count': 0,
        })
