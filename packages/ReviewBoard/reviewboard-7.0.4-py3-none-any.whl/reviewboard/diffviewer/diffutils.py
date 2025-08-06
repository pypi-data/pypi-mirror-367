"""Utilities for processing and generating diffs."""

from __future__ import annotations

import fnmatch
import logging
import os
import re
import shutil
import subprocess
import tempfile
from difflib import SequenceMatcher
from typing import (Any, AnyStr, Callable, Iterator, Optional, Sequence,
                    TYPE_CHECKING, TypeVar)

from django.core.files.base import ContentFile
from django.utils.encoding import force_str
from django.utils.translation import gettext as _
from djblets.log import log_timed
from djblets.siteconfig.models import SiteConfiguration
from djblets.util.contextmanagers import controlled_subprocess
from housekeeping.functions import deprecate_non_keyword_only_args
from typing_extensions import NotRequired, TypedDict

from reviewboard.attachments.mimetypes import guess_mimetype
from reviewboard.deprecation import (RemovedInReviewBoard80Warning,
                                     RemovedInReviewBoard90Warning)
from reviewboard.diffviewer.commit_utils import exclude_ancestor_filediffs
from reviewboard.diffviewer.errors import DiffTooBigError, PatchError
from reviewboard.diffviewer.filetypes import (HEADER_EXTENSIONS,
                                              IMPL_EXTENSIONS)
from reviewboard.diffviewer.settings import DiffSettings
from reviewboard.scmtools.core import FileLookupContext, PRE_CREATION, HEAD

if TYPE_CHECKING:
    from django.http import HttpRequest
    from reviewboard.diffviewer.models import (
        DiffCommit,
        DiffSet,
        FileDiff,
    )


logger = logging.getLogger(__name__)


#: A regex for matching a diff chunk header.
#:
#: Version Added:
#:     3.0.18
CHUNK_RANGE_RE = re.compile(
    br'^@@ -(?P<orig_start>\d+)(,(?P<orig_len>\d+))? '
    br'\+(?P<modified_start>\d+)(,(?P<modified_len>\d+))? @@',
    re.M)

NEWLINE_CONVERSION_BYTES_RE = re.compile(br'\r(\r?\n)?')
NEWLINE_CONVERSION_UNICODE_RE = re.compile(r'\r(\r?\n)?')
NEWLINE_BYTES_RE = re.compile(br'(?:\n|\r(?:\r?\n)?)')
NEWLINE_UNICODE_RE = re.compile(r'(?:\n|\r(?:\r?\n)?)')

_PATCH_GARBAGE_INPUT = 'patch: **** Only garbage was found in the patch input.'


_T = TypeVar('_T')


class DiffFileExtraContext(TypedDict):
    """Extra context for diff files.

    Version Added:
        7.0.4
    """

    #: The tabstop width for a given file.
    tab_size: NotRequired[int]


class SerializedDiffFile(TypedDict):
    """Serialized information on a diff file.

    Version Added:
        7.0
    """

    #: The FileDiff for the base of a commit range diff.
    base_filediff: Optional[FileDiff]

    #: Whether the file is binary.
    binary: bool

    #: Whether the diff chunks have been loaded.
    chunks_loaded: bool

    #: Whether the file was copied from another location.
    copied: bool

    #: Whether the file was deleted.
    deleted: bool

    #: Extra information about the diff file.
    #:
    #: Version Added:
    #:     7.0.4
    extra: DiffFileExtraContext

    #: The FileDiff for the file.
    filediff: FileDiff

    #: Whether to force rendering an interdiff.
    #:
    #: This is used to show correct interdiffs for files that were reverted
    #: in later versions.
    force_interdiff: bool

    #: The revision to use when forcing an interdiff.
    force_interdiff_revision: NotRequired[int]

    #: The index of the file within the change.
    index: int

    #: The interdiff FileDiff to use.
    interfilediff: Optional[FileDiff]

    #: Whether the file should be rendered as a new file.
    is_new_file: bool

    #: Whether the file is a symbolic link.
    is_symlink: bool

    #: The filename for the modified version of the file.
    modified_filename: str

    #: The revision for the modified version of the file.
    #:
    #: This may not always be a real revision, depending on the type of
    #: SCM in use.
    modified_revision: str

    #: Whether the file was moved from another location.
    moved: bool

    #: Whether the file was either moved or copied.
    moved_or_copied: bool

    #: Whether the file was a new file in the original diff.
    newfile: bool

    #: The filename for the original version of the file.
    orig_filename: str

    #: The revision for the original version of the file.
    orig_revision: str

    #: Whether this file is part of a published diff.
    public: bool


def convert_to_unicode(s, encoding_list):
    """Return the passed string as a unicode object.

    If conversion to unicode fails, we try the user-specified encoding, which
    defaults to ISO 8859-15. This can be overridden by users inside the
    repository configuration, which gives users repository-level control over
    file encodings.

    Ideally, we'd like to have per-file encodings, but this is hard. The best
    we can do now is a comma-separated list of things to try.

    Returns the encoding type which was used and the decoded unicode object.

    Args:
        s (bytes or bytearray or unicode):
            The string to convert to Unicode.

        encoding_list (list of unicode):
            The list of encodings to try.

    Returns:
        tuple:
        A tuple with the following information:

        1. A compatible encoding (:py:class:`unicode`).
        2. The Unicode data (:py:class:`unicode`).

    Raises:
        TypeError:
            The provided value was not a Unicode string, byte string, or
            a byte array.

        UnicodeDecodeError:
            None of the encoding types were valid for the provided string.
    """
    if isinstance(s, bytearray):
        # Some SCMTool backends return file data as a bytearray instead of
        # bytes.
        s = bytes(s)

    if isinstance(s, str):
        # Nothing to do
        return 'utf-8', s
    elif isinstance(s, bytes):
        try:
            # First try strict utf-8
            enc = 'utf-8'
            return enc, str(s, enc)
        except UnicodeError:
            # Now try any candidate encodings
            for e in encoding_list:
                try:
                    return e, str(s, e)
                except (UnicodeError, LookupError):
                    pass

            # Finally, try to convert to unicode and replace all unknown
            # characters.
            try:
                enc = 'utf-8'
                return enc, str(s, enc, errors='replace')
            except UnicodeError:
                raise UnicodeDecodeError(
                    _("Diff content couldn't be converted to unicode using "
                      "the following encodings: %s")
                    % (['utf-8'] + encoding_list))
    else:
        raise TypeError('Value to convert is unexpected type %s', type(s))


def convert_line_endings(data):
    r"""Convert line endings in a file.

    Some types of repositories provide files with a single trailing Carriage
    Return (``\r``), even if the rest of the file used a CRLF (``\r\n``)
    throughout. In these cases, GNU diff will add a ``\ No newline at end of
    file`` to the end of the diff, which GNU patch understands and will apply
    to files with just a trailing ``\r``.

    However, we normalize ``\r`` to ``\n``, which breaks GNU patch in these
    cases. This function works around this by removing the last ``\r`` and
    then converting standard types of newlines to a ``\n``.

    This is not meant for use in providing byte-compatible versions of files,
    but rather to help with comparing lines-for-lines in situations where
    two versions of a file may come from different platforms with different
    newlines.

    Args:
        data (bytes or unicode):
            A string to normalize. This supports either byte strings or
            Unicode strings.

    Returns:
        bytes or unicode:
        The data with newlines converted, in the original string type.

    Raises:
        TypeError:
            The ``data`` argument provided is not a byte string or Unicode
            string.
    """
    # See https://www.reviewboard.org/bugs/386/ and
    # https://reviews.reviewboard.org/r/286/ for the rationale behind the
    # normalization.
    if data:
        if isinstance(data, bytes):
            cr = b'\r'
            lf = b'\n'
            newline_re = NEWLINE_CONVERSION_BYTES_RE
        elif isinstance(data, str):
            cr = '\r'
            lf = '\n'
            newline_re = NEWLINE_CONVERSION_UNICODE_RE
        else:
            raise TypeError(
                _('%s is not a valid string type for convert_line_endings.')
                % type(data))

        if data.endswith(cr):
            data = data[:-1]

        data = newline_re.sub(lf, data)

    return data


def split_line_endings(
    data: AnyStr,
) -> list[AnyStr]:
    """Split a string into lines while preserving all non-CRLF characters.

    Unlike :py:meth:`str.splitlines`, this will only split on the following
    character sequences: ``\\n``, ``\\r``, ``\\r\\n``, and ``\\r\\r\\n``.

    This is needed to prevent the sort of issues encountered with
    Unicode strings when calling :py:meth:`str.splitlines``, which is that form
    feed characters would be split. :program:`patch` and :program:`diff` accept
    form feed characters as valid characters in diffs, and doesn't treat them
    as newlines, but :py:meth:`str.splitlines` will treat it as a newline
    anyway.

    Args:
        data (bytes or unicode):
            The data to split into lines.

    Returns:
        list of bytes or unicode:
        The list of lines.
    """
    if isinstance(data, bytes):
        lines = NEWLINE_BYTES_RE.split(data)
    elif isinstance(data, str):
        lines = NEWLINE_UNICODE_RE.split(data)
    else:
        raise TypeError('data must be a bytes or unicode string, not %s'
                        % type(data))

    # splitlines() would chop off the last entry, if the string ends with
    # a newline. split() doesn't do this. We need to retain that same
    # behavior by chopping it off ourselves.
    if not lines[-1]:
        lines = lines[:-1]

    return lines


def patch(
    diff: bytes,
    orig_file: bytes,
    filename: str,
    request: Optional[HttpRequest] = None,
    *,
    workaround_errors: bool = True,
) -> bytes:
    """Apply a diff to a file.

    This delegates out to ``patch`` because no one except Larry Wall knows how
    to patch.

    If patching fails, this may attempt to work around the patch error,
    depending on the nature of the error. The end result may be a viewable
    diff, but may not be a byte-for-byte copy of the expected final patched
    file.

    Currently, patch workarounds only support the case where a file being
    patched does not end in a newline and the diff is missing a
    ``\\ No newline at end of file`` marker.

    If patching fails and can't be worked around, the diff, reject file,
    original file, and patched file will be made available to the caller
    via the :py:class:`reviewboard.diffutils.errors.PatchError` exception.

    Version Changed:
        7.0.3:
        Added mitigation workarounds for certain types of bad diffs. This
        is controlled via the new ``workaround_errors``.

    Args:
        diff (bytes):
            The contents of the diff to apply.

        orig_file (bytes):
            The contents of the original file.

        filename (unicode):
            The name of the file being patched.

        request (django.http.HttpRequest, optional):
            The HTTP request, for use in logging.

        workaround_errors (bool, optional):
            Whether to attempt to work around errors encountered during
            patching.

            Version Added:
                7.0.3

    Returns:
        bytes:
        The contents of the patched file.

    Raises:
        reviewboard.diffutils.errors.PatchError:
            An error occurred when trying to apply the patch.
    """
    log_timer = log_timed('Patching file %s' % filename, request=request)

    if not diff.strip():
        # Someone uploaded an unchanged file. Return the one we're patching.
        return orig_file

    # Prepare the temporary directory if none is available
    tempdir = tempfile.mkdtemp(prefix='reviewboard.')

    try:
        orig_file = convert_line_endings(orig_file)
        diff = convert_line_endings(diff)

        (fd, oldfile) = tempfile.mkstemp(dir=tempdir)
        f = os.fdopen(fd, 'w+b')
        f.write(orig_file)
        f.close()

        newfile = '%s-new' % oldfile

        process = subprocess.Popen(['patch', '-o', newfile, oldfile],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   cwd=tempdir)

        with controlled_subprocess('patch', process) as p:
            stdout, stderr = p.communicate(diff)
            failure = p.returncode

        try:
            with open(newfile, 'rb') as f:
                new_file = f.read()
        except Exception:
            new_file = None

        if failure and workaround_errors:
            # Let's see if this is a diff error we can work around.
            if (not orig_file.endswith(b'\n') and
                not diff.rfind(br'\ No newline at end of file') != -1):
                # The file doesn't end with a newline, and this isn't
                # reflected in the diff. See if we can patch if we add a
                # trailing newline. This is not going to be a completely
                # accurate representation of the resulting file, but it's
                # suitable for viewing.
                try:
                    return patch(diff=diff,
                                 orig_file=orig_file + b'\n',
                                 filename=filename,
                                 request=request,
                                 workaround_errors=False)
                except Exception:
                    # Ignore this and fall back to the original error.
                    pass

        if failure:
            rejects_file = '%s.rej' % newfile

            try:
                with open(rejects_file, 'rb') as f:
                    rejects = f.read()
            except Exception:
                rejects = None

            error_output = force_str(stderr.strip() or stdout.strip())

            # Munge the output to show the filename instead of
            # randomly-generated tempdir locations.
            base_filename = os.path.basename(filename)

            error_output = (
                error_output
                .replace(rejects_file, '%s.rej' % base_filename)
                .replace(oldfile, base_filename)
            )

            raise PatchError(filename=filename,
                             error_output=error_output,
                             orig_file=orig_file,
                             new_file=new_file,
                             diff=diff,
                             rejects=rejects)

        return new_file
    finally:
        shutil.rmtree(tempdir)
        log_timer.done()


def get_original_file_from_repo(filediff, request=None):
    """Return the pre-patched file for the FileDiff from the repository.

    The parent diff will be applied if it exists.

    Version Added:
        4.0

    Version Changed:
        5.0:
        Removed the old ``encoding_list`` parameter.

    Args:
        filediff (reviewboard.diffviewer.models.filediff.FileDiff):
            The FileDiff to retrieve the pre-patch file for.

        request (django.http.HttpRequest, optional):
            The HTTP request from the client.

    Returns:
        bytes:
        The pre-patched file.

    Raises:
        UnicodeDecodeError:
            The source file was not compatible with any of the available
            encodings.

        reviewboard.diffutils.errors.PatchError:
            An error occurred when trying to apply the patch.

        reviewboard.scmtools.errors.SCMError:
            An error occurred while computing the pre-patch file.
    """
    data = b''
    extra_data = filediff.extra_data or {}

    # If the file has a parent source filename/revision recorded, we're
    # going to need to fetch that, since that'll be (potentially) the
    # latest commit in the repository.
    #
    # This information was added in Review Board 3.0.19. Prior versions
    # stored the parent source revision as filediff.source_revision
    # (rather than leaving that as identifying information for the actual
    # file being shown in the review). It did not store the parent
    # filename at all (which impacted diffs that contained a moved/renamed
    # file on any type of repository that required a filename for lookup,
    # such as Mercurial -- Git was not affected, since it only needs
    # blob SHAs).
    #
    # If we're not working with a parent diff, or this is a FileDiff
    # with legacy parent diff information, we just use the FileDiff
    # FileDiff filename/revision fields as normal.
    source_filename = extra_data.get('parent_source_filename',
                                     filediff.source_file)
    source_revision = extra_data.get('parent_source_revision',
                                     filediff.source_revision)

    if source_revision != PRE_CREATION:
        repository = filediff.get_repository()

        if filediff.commit_id is not None:
            commit_extra_data = filediff.commit.extra_data
        else:
            commit_extra_data = {}

        context = FileLookupContext(
            request=request,
            base_commit_id=filediff.diffset.base_commit_id,
            diff_extra_data=filediff.diffset.extra_data,
            commit_extra_data=commit_extra_data,
            file_extra_data=extra_data)

        data = repository.get_file(path=source_filename,
                                   revision=source_revision,
                                   context=context)

        # Convert to unicode before we do anything to manipulate the string.
        encoding_list = get_filediff_encodings(filediff)
        encoding, data = convert_to_unicode(data, encoding_list)

        # Repository.get_file doesn't know or care about how we need line
        # endings to work. So, we'll just transform every time.
        #
        # This is mostly only a problem if the diff chunks aren't in the
        # cache, though if several people are working off the same file,
        # we'll be doing extra work to convert those line endings for each
        # of those instead of once.
        #
        # Only other option is to cache the resulting file, but then we're
        # duplicating the cached contents.
        data = convert_line_endings(data)

        # Convert back to bytes using whichever encoding we used to decode.
        data = data.encode(encoding)

        if not filediff.encoding:
            # Now that we know an encoding that works, remember it for next
            # time.
            filediff.extra_data['encoding'] = encoding
            filediff.save(update_fields=('extra_data',))

    # If there's a parent diff set, apply it to the buffer.
    if (filediff.parent_diff and
        not filediff.is_parent_diff_empty(cache_only=True)):
        try:
            data = patch(diff=filediff.parent_diff,
                         orig_file=data,
                         filename=source_filename,
                         request=request)
        except PatchError as e:
            # patch(1) cannot process diff files that contain no diff sections.
            # We are going to check and see if the parent diff contains no diff
            # chunks.
            if (e.error_output == _PATCH_GARBAGE_INPUT and
                not filediff.is_parent_diff_empty()):
                raise

    return data


def get_original_file(filediff, request=None):
    """Return the pre-patch file of a FileDiff.

    Version Changed:
        4.0:
        The ``encoding_list`` parameter should no longer be provided by
        callers. Encoding lists are now calculated automatically. Passing a
        custom list with override the calculated one.

    Version Changed:
        5.0:
        The ``encoding_list`` parameter has been removed. Encoding lists are
        now calculated automatically.

    Args:
        filediff (reviewboard.diffviewer.models.filediff.FileDiff):
            The FileDiff to retrieve the pre-patch file for.

        request (django.http.HttpRequest, optional):
            The HTTP request from the client.

    Returns:
        bytes:
        The pre-patch file.

    Raises:
        UnicodeDecodeError:
            The source file was not compatible with any of the available
            encodings.

        reviewboard.diffutils.errors.PatchError:
            An error occurred when trying to apply the patch.

        reviewboard.scmtools.errors.SCMError:
            An error occurred while computing the pre-patch file.
    """
    data = b''

    # If the FileDiff has a parent diff, it must be the case that it has no
    # ancestor FileDiffs. We can fall back to the no history case here.
    if filediff.parent_diff:
        data = get_original_file_from_repo(filediff=filediff,
                                           request=request)
    else:
        # Otherwise, there may be one or more ancestors that we have to apply.
        ancestors = filediff.get_ancestors(minimal=True)

        if ancestors:
            oldest_ancestor = ancestors[0]

            # If the file was created outside this history, fetch it from the
            # repository and apply the parent diff if it exists.
            if not oldest_ancestor.is_new:
                data = get_original_file_from_repo(filediff=oldest_ancestor,
                                                   request=request)

            if not oldest_ancestor.is_diff_empty:
                data = patch(diff=oldest_ancestor.diff,
                             orig_file=data,
                             filename=oldest_ancestor.source_file,
                             request=request)

            for ancestor in ancestors[1:]:
                # TODO: Cache these results so that if this ``filediff`` is an
                # ancestor of another FileDiff, computing that FileDiff's
                # original file will be cheaper. This will also allow an
                # ancestor filediff's original file to be computed cheaper.
                data = patch(diff=ancestor.diff,
                             orig_file=data,
                             filename=ancestor.source_file,
                             request=request)
        elif not filediff.is_new:
            data = get_original_file_from_repo(filediff=filediff,
                                               request=request)

    return data


def get_patched_file(source_data, filediff, request=None):
    """Return the patched version of a file.

    This will normalize the patch, applying any changes needed for the
    repository, and then patch the provided data with the patch contents.

    Args:
        source_data (bytes):
            The file contents to patch.

        filediff (reviewboard.diffviewer.models.filediff.FileDiff):
            The FileDiff representing the patch.

        request (django.http.HttpClient, optional):
            The HTTP request from the client.

    Returns:
        bytes:
        The patched file contents.
    """
    repository = filediff.get_repository()
    diff = repository.normalize_patch(patch=filediff.diff,
                                      filename=filediff.source_file,
                                      revision=filediff.source_revision)

    return patch(diff=diff,
                 orig_file=source_data,
                 filename=filediff.dest_file,
                 request=request)


def get_original_and_patched_files(
    filediff: FileDiff,
    request: Optional[HttpRequest] = None,
    update_mimetypes: bool = True,
) -> tuple[Optional[bytes], Optional[bytes]]:
    """Return the original and patched version of a file.

    Args:
        filediff (reviewboard.diffviewer.models.filediff.FileDiff):
            The filediff to fetch versions for.

        request (django.http.HttpRequest, optional):
            The request object.

        update_mimetypes (bool, optional):
            Whether to store the detected mimetypes of the old and new
            versions in the filediff extra_data.

    Returns:
        tuple:
        A 2-tuple with the following items:

        Tuple:
            0 (bytes):
                The original version of the file.

            1 (bytes):
                The patched version of the file.
    """
    old = get_original_file(filediff=filediff,
                            request=request)
    new = get_patched_file(source_data=old,
                           filediff=filediff,
                           request=request)

    if update_mimetypes:
        needs_update = False

        if old and 'source_mimetype' not in filediff.extra_data:
            logger.debug('Detecting MIME type for old version of FileDiff %d',
                         filediff.pk,
                         extra={'request': request})

            with ContentFile(old) as f:
                mimetype = guess_mimetype(f)

            filediff.extra_data['source_mimetype'] = mimetype
            needs_update = True

        if new and 'dest_mimetype' not in filediff.extra_data:
            logger.debug('Detecting MIME type for new version of FileDiff %d',
                         filediff.pk,
                         extra={'request': request})

            with ContentFile(new) as f:
                mimetype = guess_mimetype(f)

            filediff.extra_data['dest_mimetype'] = mimetype
            needs_update = True

        if needs_update:
            filediff.save(update_fields=['extra_data'])

    return (old, new)


def get_revision_str(revision):
    if revision == HEAD:
        return "HEAD"
    elif revision == PRE_CREATION:
        return ""
    else:
        return _("Revision %s") % revision


def get_filenames_match_patterns(patterns, filenames):
    """Return whether any of the filenames match any of the patterns.

    This is used to compare a list of filenames to a list of
    :py:mod:`patterns <fnmatch>`. The patterns are case-sensitive.

    Args:
        patterns (list of unicode):
            The list of patterns to match against.

        filename (list of unicode):
            The list of filenames.

    Returns:
        bool:
        ``True`` if any filenames match any patterns. ``False`` if none match.
    """
    for pattern in patterns:
        for filename in filenames:
            if fnmatch.fnmatchcase(filename, pattern):
                return True

    return False


def get_filediff_encodings(filediff):
    """Return a list of encodings to try for a FileDiff's source text.

    If the FileDiff already has a known encoding stored, then it will take
    priority. The provided encoding list, or the repository's list of
    configured encodingfs, will be provided as fallbacks.

    Version Changed:
        5.0:
        The ``encoding_list`` parameter has been removed.

    Args:
        filediff (reviewboard.diffviewer.models.filediff.FileDiff):
            The FileDiff to return encodings for.

    Returns:
        list of unicode:
        The list of encodings to try for the source file.
    """
    filediff_encoding = filediff.encoding
    encodings = []

    encoding_list = filediff.get_repository().get_encoding_list()

    if filediff_encoding:
        encodings.append(filediff_encoding)
        encodings += [
            encoding
            for encoding in encoding_list
            if encoding != filediff_encoding
        ]
    else:
        encodings += encoding_list

    return encodings


def get_matched_interdiff_files(tool, filediffs, interfilediffs):
    """Generate pairs of matched files for display in interdiffs.

    This compares a list of filediffs and a list of interfilediffs, attempting
    to best match up the files in both for display in the diff viewer.

    This will prioritize matches that share a common source filename,
    destination filename, and new/deleted state. Failing that, matches that
    share a common source filename are paired off.

    Any entries in ``interfilediffs` that don't have any match in ``filediffs``
    are considered new changes in the interdiff, and any entries in
    ``filediffs`` that don't have entries in ``interfilediffs`` are considered
    reverted changes.

    Args:
        tool (reviewboard.scmtools.core.SCMTool)
            The tool used for all these diffs.

        filediffs (list of reviewboard.diffviewer.models.filediff.FileDiff):
            The list of filediffs on the left-hand side of the diff range.

        interfilediffs (list of reviewboard.diffviewer.models.filediff.
                        FileDiff):
            The list of filediffs on the right-hand side of the diff range.

    Yields:
        tuple:
        A paired off filediff match. This is a tuple containing two entries,
        each a :py:class:`~reviewboard.diffviewer.models.filediff.FileDiff` or
        ``None``.
    """
    parser = tool.get_parser(b'')
    _normfile = parser.normalize_diff_filename

    def _make_detail_key(filediff):
        return (_normfile(filediff.source_file),
                _normfile(filediff.dest_file),
                filediff.is_new,
                filediff.deleted)

    # In order to support interdiffs properly, we need to display diffs on
    # every file in the union of both diffsets. Iterating over one diffset
    # or the other doesn't suffice. We also need to be careful to handle
    # things like renamed/moved files, particularly when there are multiple
    # of them with the same source filename.
    #
    # This is done in four stages:
    #
    # 1. Build up maps and a set for keeping track of possible
    #    interfilediff candidates for future stages.
    #
    # 2. Look for any files that are common between the two diff revisions
    #    that have the same source filename, same destination filename, and
    #    the same new/deleted states.
    #
    #    Unless a diff is hand-crafted, there should never be more than one
    #    match here.
    #
    # 3. Look for any files that are common between the two diff revisions
    #    that have the same source filename and new/deleted state. These will
    #    ignore the destination filename, helping to match cases where diff 1
    #    modifies a file and diff 2 modifies + renames/moves it.
    #
    # 4. Add any remaining files from diff 2 that weren't found in diff 1.
    #
    # We don't have to worry about things like the order of matched diffs.
    # That will be taken care of at the end of the function.
    detail_interdiff_map = {}
    simple_interdiff_map = {}
    remaining_interfilediffs = set()

    # Stage 1: Build up the maps/set of interfilediffs.
    for interfilediff in interfilediffs:
        source_file = _normfile(interfilediff.source_file)
        detail_key = _make_detail_key(interfilediff)

        # We'll store this interfilediff in three spots: The set of
        # all interfilediffs, the detail map (for source + dest +
        # is_new file comparisons), and the simple map (for direct
        # source_file comparisons). These will be used for the
        # different matching stages.
        remaining_interfilediffs.add(interfilediff)
        detail_interdiff_map[detail_key] = interfilediff
        simple_interdiff_map.setdefault(source_file, set()).add(interfilediff)

    # Stage 2: Look for common files with the same source/destination
    #          filenames and new/deleted states.
    #
    # There will only be one match per filediff, at most. Any filediff or
    # interfilediff that we find will be excluded from future stages.
    remaining_filediffs = []

    for filediff in filediffs:
        source_file = _normfile(filediff.source_file)

        try:
            interfilediff = detail_interdiff_map.pop(
                _make_detail_key(filediff))
        except KeyError:
            remaining_filediffs.append(filediff)
            continue

        yield filediff, interfilediff

        if interfilediff:
            remaining_interfilediffs.discard(interfilediff)

            try:
                simple_interdiff_map.get(source_file, []).remove(interfilediff)
            except ValueError:
                pass

    # Stage 3: Look for common files with the same source/destination
    #          filenames (when they differ).
    #
    # Any filediff from diff 1 not already processed in stage 2 will be
    # processed here. We'll look for any filediffs from diff 2 that were
    # moved/copied from the same source to the same destination. This is one
    # half of the detailed file state we checked in stage 2.
    new_remaining_filediffs = []

    for filediff in remaining_filediffs:
        source_file = _normfile(filediff.source_file)
        found_interfilediffs = [
            temp_interfilediff
            for temp_interfilediff in simple_interdiff_map.get(source_file, [])
            if (temp_interfilediff.dest_file == filediff.dest_file and
                filediff.source_file != filediff.dest_file)
        ]

        if found_interfilediffs:
            remaining_interfilediffs.difference_update(found_interfilediffs)

            for interfilediff in found_interfilediffs:
                simple_interdiff_map[source_file].remove(interfilediff)
                yield filediff, interfilediff
        else:
            new_remaining_filediffs.append(filediff)

    remaining_filediffs = new_remaining_filediffs

    # Stage 4: Look for common files with the same source filenames and
    #          new/deleted states.
    #
    # Any filediff from diff 1 not already processed in stage 3 will be
    # processed here. We'll look for any filediffs from diff 2 that match
    # the source filename and the new/deleted state. Any that we find will
    # be matched up.
    new_remaining_filediffs = []

    for filediff in remaining_filediffs:
        source_file = _normfile(filediff.source_file)
        found_interfilediffs = [
            temp_interfilediff
            for temp_interfilediff in simple_interdiff_map.get(source_file, [])
            if (temp_interfilediff.is_new == filediff.is_new and
                temp_interfilediff.deleted == filediff.deleted)
        ]

        if found_interfilediffs:
            remaining_interfilediffs.difference_update(found_interfilediffs)

            for interfilediff in found_interfilediffs:
                simple_interdiff_map[source_file].remove(interfilediff)
                yield filediff, interfilediff
        else:
            new_remaining_filediffs.append(filediff)

    remaining_filediffs = new_remaining_filediffs

    # Stage 5: Look for common files with the same source filenames and
    #          compatible new/deleted states.
    #
    # This will help catch files that were marked as new in diff 1 but not in
    # diff 2, or deleted in diff 2 but not in diff 1. (The inverse for either
    # is NOT matched!). This is important because if a file is introduced in a
    # parent diff, the file can end up showing up as new itself (which is a
    # separate bug).
    #
    # Even if that bug did not exist, it's still possible for a file to be new
    # in one revision but committed separately (by that user or another), so we
    # need these matched.
    #
    # Any files not found with a matching interdiff will simply be yielded.
    # This is the last stage dealing with the filediffs in the first revision.
    for filediff in remaining_filediffs:
        source_file = _normfile(filediff.source_file)
        found_interfilediffs = [
            temp_interfilediff
            for temp_interfilediff in simple_interdiff_map.get(source_file, [])
            if (((filediff.is_new or not temp_interfilediff.is_new) or
                 (not filediff.is_new and temp_interfilediff.is_new and
                  filediff.dest_detail == temp_interfilediff.dest_detail)) and
                (not filediff.deleted or temp_interfilediff.deleted))
        ]

        if found_interfilediffs:
            remaining_interfilediffs.difference_update(found_interfilediffs)

            for interfilediff in found_interfilediffs:
                # NOTE: If more stages are ever added that deal with
                #       simple_interdiff_map, then we'll need to remove
                #       interfilediff from that map here.
                yield filediff, interfilediff
        else:
            yield filediff, None

    # Stage 6: Add any remaining files from the interdiff.
    #
    # We've removed everything that we've already found.  What's left are
    # interdiff files that are new. They have no file to diff against.
    #
    # The end result is going to be a view that's the same as when you're
    # viewing a standard diff. As such, we can pretend the interdiff is
    # the source filediff and not specify an interdiff. Keeps things
    # simple, code-wise, since we really have no need to special-case
    # this.
    for interfilediff in remaining_interfilediffs:
        yield None, interfilediff


def get_filediffs_match(filediff1, filediff2):
    """Return whether two FileDiffs effectively match.

    This is primarily checking that the patched version of two files are going
    to be basically the same.

    This will first check that we even have both FileDiffs. Assuming we have
    both, this will check the diff for equality. If not equal, we at least
    check that both files were deleted (which is equivalent to being equal).

    The patched SHAs are then checked. These would be generated as part of the
    diff viewing process, so may not be available. We prioritize the SHA256
    hashes (introduced in Review Board 4.0), and fall back on SHA1 hashes if
    not present.

    Args:
        filediff1 (reviewboard.diffviewer.models.filediff.FileDiff):
            The first FileDiff to compare.

        filediff2 (reviewboard.diffviewer.models.filediff.FileDiff):
            The second FileDiff to compare.

    Returns:
        bool:
        ``True`` if both FileDiffs effectively match. ``False`` if they do
        not.

    Raises:
        ValueError:
            ``None`` was provided for both ``filediff1`` and ``filediff2``.
    """
    if filediff1 is None and filediff2 is None:
        raise ValueError('filediff1 and filediff2 cannot both be None')

    # For the hash comparisons, there's a chance we won't have any SHA1 (RB
    # 2.0+) or SHA256 (RB 4.0+) hashes, so we have to check for them. We want
    # to prioritize SHA256 hashes, but if the filediff or interfilediff lacks
    # a SHA256 hash, we want to fall back to SHA1.
    return (filediff1 is not None and filediff2 is not None and
            (filediff1.diff == filediff2.diff or
             (filediff1.deleted and filediff2.deleted) or
             (filediff1.patched_sha256 is not None and
              filediff1.patched_sha256 == filediff2.patched_sha256) or
             ((filediff1.patched_sha256 is None or
               filediff2.patched_sha256 is None) and
              filediff1.patched_sha1 is not None and
              filediff1.patched_sha1 == filediff2.patched_sha1)))


@deprecate_non_keyword_only_args(RemovedInReviewBoard90Warning)
def get_diff_files(
    *,
    diffset: DiffSet,
    filediff: Optional[FileDiff] = None,
    interdiffset: Optional[DiffSet] = None,
    interfilediff: Optional[FileDiff] = None,
    base_filediff: Optional[FileDiff] = None,
    request: Optional[HttpRequest] = None,
    filename_patterns: Optional[list[str]] = None,
    base_commit: Optional[DiffCommit] = None,
    tip_commit: Optional[DiffCommit] = None,
    diff_settings: Optional[DiffSettings] = None,
) -> list[SerializedDiffFile]:
    """Return a list of files that will be displayed in a diff.

    This will go through the given diffset/interdiffset, or a given filediff
    within that diffset, and generate the list of files that will be
    displayed. This file list will contain a bunch of metadata on the files,
    such as the index, original/modified names, revisions, associated
    filediffs/diffsets, and so on.

    This can be used along with :py:func:`populate_diff_chunks` to build a full
    list containing all diff chunks used for rendering a side-by-side diff.

    Version Changed:
        7.0.4:
        * Made arguments keyword-only.
        * Added the ``diff_settings`` argument.

    Args:
        diffset (reviewboard.diffviewer.models.diffset.DiffSet):
            The diffset containing the files to return.

        filediff (reviewboard.diffviewer.models.filediff.FileDiff, optional):
            A specific file in the diff to return information for.

        interdiffset (reviewboard.diffviewer.models.diffset.DiffSet, optional):
            A second diffset used for an interdiff range.

        interfilediff (reviewboard.diffviewer.models.filediff.FileDiff,
                       optional):
            A second specific file in ``interdiffset`` used to return
            information for. This should be provided if ``filediff`` and
            ``interdiffset`` are both provided. If it's ``None`` in this
            case, then the diff will be shown as reverted for this file.

            This may not be provided if ``base_filediff`` is provided.

        base_filediff (reviewbaord.diffviewer.models.filediff.FileDiff,
                       optional):
            The base FileDiff to use.

            This may only be provided if ``filediff`` is provided and
            ``interfilediff`` is not.

        filename_patterns (list of str, optional):
            A list of filenames or :py:mod:`patterns <fnmatch>` used to
            limit the results. Each of these will be matched against the
            original and modified file of diffs and interdiffs.

        base_commit (reviewboard.diffviewer.models.diffcommit.DiffCommit,
                     optional):
            An optional base commit. No :py:class:`FileDiffs
            <reviewboard.diffviewer.models.filediff.FileDiff>` from commits
            before that commit will be included in the results.

            This argument only applies to :py:class:`DiffSets
            <reviewboard.diffviewer.models.diffset.DiffSet>` with
            :py:class:`DiffCommits <reviewboard.diffviewer.models.diffcommit
            .DiffCommit>`.

        tip_commit (reviewboard.diffviewer.models.diffcommit.DiffSet,
                    optional):
            An optional tip commit. No :py:class:`FileDiffs
            <reviewboard.diffviewer.models.filediff.FileDiff>` from commits
            after that commit will be included in the results.

            This argument only applies to :py:class:`DiffSets
            <reviewboard.diffviewer.models.diffset.DiffSet>` with
            :py:class:`DiffCommits <reviewboard.diffviewer.models.diffcommit
            .DiffCommit>`.

        diff_settings (reviewboard.diffviewer.settings.DiffSettings, optional):
            The diff settings object. This will become mandatory in Review
            Board 9.0.

            Version Added:
                7.0.4

    Returns:
        list of dict:
        A list of dictionaries containing information on the files to show
        in the diff, in the order in which they would be shown.
    """
    # It is presently not supported to do an interdiff with commit spans. It
    # would require base/tip commits for the interdiffset as well.
    assert not interdiffset or (base_commit is None and tip_commit is None)
    assert base_filediff is None or interfilediff is None

    if diff_settings is None:
        RemovedInReviewBoard90Warning.warn(
            'get_diff_files was called without a diff_settings argument. '
            'This argument will become mandatory in Review Board 9.0')
        diff_settings = DiffSettings.create(request=request)

    if (diffset.commit_count > 0 and
        base_commit and
        tip_commit and
        base_commit.pk > tip_commit.pk):
        # If the base commit is more recent than the tip commit the interval
        # **must** be empty.
        return []

    per_commit_filediffs = None
    requested_base_filediff = base_filediff

    if filediff:
        filediffs = [filediff]

        if interdiffset:
            log_timer = log_timed(
                f'Generating diff file info for interdiffset ids '
                f'{diffset.pk}-{interdiffset.pk}, filediff {filediff.pk}',
                request=request)
        else:
            log_timer = log_timed(
                f'Generating diff file info for diffset id {diffset.pk}, '
                f'filediff {filediff.pk}',
                request=request)

            if (diffset.commit_count > 0 and
                ((base_commit and filediff.commit_id <= base_commit.pk) or
                 (tip_commit and filediff.commit_id > tip_commit.pk))):
                # The requested FileDiff is outside the requested commit range.
                return []
    else:
        if (diffset.commit_count > 0 and
            (base_commit is not None or tip_commit is not None)):
            # Even if we have base_commit, we need to query for all FileDiffs
            # so that we can do ancestor computations.
            filediffs = per_commit_filediffs = diffset.per_commit_files

            if base_commit:
                base_commit_id = base_commit.pk
            else:
                base_commit_id = 0

            if tip_commit:
                tip_commit_id = tip_commit.pk
            else:
                tip_commit_id = None

            filediffs = [
                f
                for f in filediffs
                if (f.commit_id > base_commit_id and
                    (not tip_commit_id or
                     f.commit_id <= tip_commit_id))
            ]

            filediffs = exclude_ancestor_filediffs(filediffs,
                                                   per_commit_filediffs)
        else:
            filediffs = diffset.cumulative_files

        if interdiffset:
            log_timer = log_timed("Generating diff file info for "
                                  "interdiffset ids %s-%s" %
                                  (diffset.id, interdiffset.id),
                                  request=request)
        else:
            log_timer = log_timed("Generating diff file info for "
                                  "diffset id %s" % diffset.id,
                                  request=request)

    # Filediffs that were created with leading slashes stripped won't match
    # those created with them present, so we need to compare them without in
    # order for the filenames to match up properly.
    tool = diffset.repository.get_scmtool()

    if interdiffset:
        if not filediff:
            if interdiffset.commit_count > 0:
                # Currently, only interdiffing between cumulative diffs is
                # supported.
                interfilediffs = interdiffset.cumulative_files
            else:
                interfilediffs = list(interdiffset.files.all())

        elif interfilediff:
            interfilediffs = [interfilediff]
        else:
            interfilediffs = []

        filediff_parts = []
        matched_filediffs = get_matched_interdiff_files(
            tool=tool,
            filediffs=filediffs,
            interfilediffs=interfilediffs)

        for temp_filediff, temp_interfilediff in matched_filediffs:
            if temp_filediff:
                filediff_parts.append((temp_filediff, temp_interfilediff,
                                       True))
            elif temp_interfilediff:
                filediff_parts.append((temp_interfilediff, None, False))
            else:
                logger.error(
                    'get_matched_interdiff_files returned an entry with an '
                    'empty filediff and interfilediff for diffset=%r, '
                    'interdiffset=%r, filediffs=%r, interfilediffs=%r',
                    diffset, interdiffset, filediffs, interfilediffs)

                raise ValueError(
                    'Internal error: get_matched_interdiff_files returned an '
                    'entry with an empty filediff and interfilediff! Please '
                    'report this along with information from the server '
                    'error log.')
    else:
        # We're not working with interdiffs. We can easily create the
        # filediff_parts directly.
        filediff_parts = [
            (temp_filediff, None, False)
            for temp_filediff in filediffs
        ]

    # Now that we have all the bits and pieces we care about for the filediffs,
    # we can start building information about each entry on the diff viewer.
    files: list[SerializedDiffFile] = []

    for parts in filediff_parts:
        filediff, interfilediff, force_interdiff = parts

        newfile = filediff.is_new

        if interdiffset:
            # First, find out if we want to even process this one.
            # If the diffs are identical, or the patched files are identical,
            # or if the files were deleted in both cases, then we can be
            # absolutely sure that there's nothing interesting to show to
            # the user.
            if get_filediffs_match(filediff, interfilediff):
                continue

            orig_revision = _('Diff Revision %s') % diffset.revision
        else:
            orig_revision = get_revision_str(filediff.source_revision)

        if interfilediff:
            assert interdiffset is not None
            modified_revision = _('Diff Revision %s') % interdiffset.revision
        elif force_interdiff and interdiffset:
            modified_revision = (_('Diff Revision %s - File Reverted') %
                                 interdiffset.revision)
        elif newfile:
            modified_revision = _('New File')
        else:
            modified_revision = _('New Change')

        orig_extra_data = filediff.extra_data

        if interfilediff:
            raw_orig_filename = filediff.dest_file
            raw_modified_filename = interfilediff.dest_file
            modified_extra_data = interfilediff.extra_data
        else:
            raw_orig_filename = filediff.source_file
            raw_modified_filename = filediff.dest_file
            modified_extra_data = filediff.extra_data

        orig_filename = tool.normalize_path_for_display(
            raw_orig_filename,
            extra_data=orig_extra_data)
        modified_filename = tool.normalize_path_for_display(
            raw_modified_filename,
            extra_data=modified_extra_data)

        if filename_patterns:
            if modified_filename == orig_filename:
                filenames = [modified_filename]
            else:
                filenames = [modified_filename, orig_filename]

            if not get_filenames_match_patterns(patterns=filename_patterns,
                                                filenames=filenames):
                continue

        base_filediff = None

        if filediff.commit_id:
            # If we pre-computed this above (or before) and we have all
            # FileDiffs, this will cost no additional queries.
            #
            # Otherwise this will cost up to
            # ``1 + len(diffset.per_commit_files.count())`` queries.
            ancestors = filediff.get_ancestors(minimal=False,
                                               filediffs=per_commit_filediffs)

            if ancestors:
                if requested_base_filediff:
                    assert len(filediffs) == 1

                    if requested_base_filediff in ancestors:
                        base_filediff = requested_base_filediff
                    else:
                        raise ValueError(
                            f'Invalid base_filediff (ID '
                            f'{requested_base_filediff.pk}) for filediff (ID '
                            f'{filediff.pk})')
                elif base_commit:
                    base_filediff = filediff.get_base_filediff(
                        base_commit=base_commit,
                        ancestors=ancestors)
                else:
                    # If the file was newly-added in the ancestors, we need to
                    # propagate that state forward.
                    newfile = ancestors[0].is_new
                    orig_revision = get_revision_str(PRE_CREATION)

        extra: DiffFileExtraContext = {}

        if diff_settings.tab_size:
            extra['tab_size'] = diff_settings.tab_size

        f: SerializedDiffFile = {
            'base_filediff': base_filediff,
            'binary': filediff.binary,
            'chunks_loaded': False,
            'copied': filediff.copied,
            'deleted': filediff.deleted,
            'extra': extra,
            'filediff': filediff,
            'force_interdiff': force_interdiff,
            'index': len(files),
            'interfilediff': interfilediff,
            'is_new_file': (
                newfile and
                base_filediff is None and
                interfilediff is None and
                not filediff.parent_diff
            ),
            'is_symlink': filediff.extra_data.get('is_symlink', False),
            'modified_filename': modified_filename or orig_filename,
            'modified_revision': modified_revision,
            'moved': filediff.moved,
            'moved_or_copied': filediff.moved or filediff.copied,
            'newfile': newfile,
            'orig_filename': orig_filename,
            'orig_revision': orig_revision,
            'public': (diffset.history is not None and
                       (interdiffset is None or
                        interdiffset.history is not None)),
        }

        # When displaying an interdiff, we do not want to display the
        # revision of the base filediff. Instead, we will display the diff
        # revision as computed above.
        if base_filediff and not interdiffset:
            f['orig_revision'] = \
                get_revision_str(base_filediff.source_revision)
            f['orig_filename'] = tool.normalize_path_for_display(
                base_filediff.source_file)

        if force_interdiff and interdiffset:
            f['force_interdiff_revision'] = interdiffset.revision

        files.append(f)

    log_timer.done()

    if len(files) == 1:
        return files
    else:
        return get_sorted_filediffs(
            files,
            key=lambda f: f['interfilediff'] or f['filediff'])


@deprecate_non_keyword_only_args(RemovedInReviewBoard80Warning)
def populate_diff_chunks(
    files,
    *,
    request=None,
    diff_settings: DiffSettings):
    """Populate a list of diff files with chunk data.

    This accepts a list of files (generated by :py:func:`get_diff_files`) and
    generates diff chunk data for each file in the list. The chunk data is
    stored in memory in the file state.

    Version Changed:
        6.0:
        * Made all arguments other than ``files`` keyword-only.
        * Made the ``diff_settings`` argument mandatory.

    Args:
        files (list of dict):
            The list of diff files to generate chunks for.

        request (django.http.HttpRequest, optional):
            The HTTP request from the client.

        diff_settings (reviewboard.diffviewer.settings.DiffSettings):
            The settings used to control the display of diffs.

            Version Added:
                5.0.2
    """
    from reviewboard.diffviewer.chunk_generator import get_diff_chunk_generator

    for diff_file in files:
        chunk_generator = get_diff_chunk_generator(
            request=request,
            filediff=diff_file['filediff'],
            interfilediff=diff_file['interfilediff'],
            force_interdiff=diff_file['force_interdiff'],
            base_filediff=diff_file.get('base_filediff'),
            diff_settings=diff_settings)
        chunks = list(chunk_generator.get_chunks())

        diff_file.update({
            'chunks': chunks,
            'num_chunks': len(chunks),
            'changed_chunk_indexes': [],
            'whitespace_only': len(chunks) > 0,
        })

        if chunk_generator.all_code_safety_results:
            diff_file['code_safety_results'] = \
                chunk_generator.all_code_safety_results

        for j, chunk in enumerate(chunks):
            chunk['index'] = j

            if chunk['change'] != 'equal':
                diff_file['changed_chunk_indexes'].append(j)
                meta = chunk.get('meta', {})

                if not meta.get('whitespace_chunk', False):
                    diff_file['whitespace_only'] = False

        diff_file.update({
            'num_changes': len(diff_file['changed_chunk_indexes']),
            'chunks_loaded': True,
        })


def get_file_from_filediff(
    context: dict[str, Any],
    filediff: FileDiff,
    interfilediff: Optional[FileDiff],
    *,
    diff_settings: DiffSettings,
    base_filediff: Optional[FileDiff] = None,
    base_commit: Optional[DiffCommit] = None,
    tip_commit: Optional[DiffCommit] = None,
) -> Optional[dict[str, Any]]:
    """Return the files that corresponds to the filediff/interfilediff.

    This is primarily intended for use with templates. It takes a template
    context for looking up the user and for caching file lists, in order to
    improve performance and reduce lookup times for files that have already
    been fetched.

    This function returns either exactly one file or ``None``.

    Version Changed:
        7.0:
        * Added ``base_filediff`, ``base_commit`` and ``tip_commit``
          arguments.

    Version Changed:
        6.0:
        * Made ``diff_settings`` mandatory.

    Version Changed:
        5.0.2:
        * Added the optional ``diff_settings`` argument.

    Args:
        context (dict):
            Template context being used to render the diff.

        filediff (reviewboard.diffviewer.models.filediff.FileDiff):
            The filediff being rendered.

        interfilediff (reviewboard.diffviewer.models.filediff.FileDiff,
                       optional):
            The optional filediff being used to render an interdiff.

        diff_settings (reviewboard.diffviewer.settings.DiffSettings):
            The settings used to control the display of diffs.

            Version Added:
                5.0.2

        base_filediff (reviewbaord.diffviewer.models.filediff.FileDiff,
                       optional):
            The base FileDiff to use.

            This may only be provided if ``filediff`` is provided and
            ``interfilediff`` is not.

            Version Added:
                7.0

        base_commit (reviewboard.diffviewer.models.diffcommit.DiffCommit,
                     optional):
            An optional base commit. No :py:class:`FileDiffs
            <reviewboard.diffviewer.models.filediff.FileDiff>` from commits
            before that commit will be included in the results.

            This argument only applies to :py:class:`DiffSets
            <reviewboard.diffviewer.models.diffset.DiffSet>` with
            :py:class:`DiffCommits <reviewboard.diffviewer.models.diffcommit
            .DiffCommit>`.

            Version Added:
                7.0

        tip_commit (reviewboard.diffviewer.models.diffcommit.DiffCommit,
                    optional):
            An optional tip commit. No :py:class:`FileDiffs
            <reviewboard.diffviewer.models.filediff.FileDiff>` from commits
            after that commit will be included in the results.

            This argument only applies to :py:class:`DiffSets
            <reviewboard.diffviewer.models.diffset.DiffSet>` with
            :py:class:`DiffCommits <reviewboard.diffviewer.models.diffcommit
            .DiffCommit>`.

            Version Added:
                7.0

    Returns:
        dict:
        The diff file information. If not found, this will return ``None``.
    """
    interdiffset = None

    key = f'_diff_files_{filediff.diffset.pk}_{filediff.pk}'

    if base_filediff:
        key += f'_base{base_filediff.pk}'

    if interfilediff:
        key += f'_{interfilediff.pk}'
        interdiffset = interfilediff.diffset

    if key in context:
        files = context[key]
    else:
        assert 'user' in context

        request = context.get('request')
        files = get_diff_files(
            diffset=filediff.diffset,
            filediff=filediff,
            interdiffset=interdiffset,
            interfilediff=interfilediff,
            base_filediff=base_filediff,
            request=request,
            base_commit=base_commit,
            tip_commit=tip_commit,
            diff_settings=diff_settings)

        populate_diff_chunks(files=files,
                             request=request,
                             diff_settings=diff_settings)
        context[key] = files

    if files:
        assert len(files) == 1
        return files[0]

    return None


def get_last_line_number_in_diff(
    context: dict[str, Any],
    filediff: FileDiff,
    interfilediff: Optional[FileDiff],
    *,
    diff_settings: DiffSettings,
    base_filediff: Optional[FileDiff] = None,
    base_commit: Optional[DiffCommit] = None,
    tip_commit: Optional[DiffCommit] = None,
) -> int:
    """Return the last virtual line number in the filediff/interfilediff.

    This returns the virtual line number to be used in expandable diff
    fragments.

    Version Changed:
        7.0:
        * Added ``base_filediff`, ``base_commit`` and ``tip_commit``
          arguments.

    Version Changed:
        5.0.2:
        * Added the optional ``diff_settings`` argument.

    Args:
        context (dict):
            Template context being used to render the diff.

        filediff (reviewboard.diffviewer.models.filediff.FileDiff):
            The filediff being rendered.

        interfilediff (reviewboard.diffviewer.models.filediff.FileDiff,
                       optional):
            The optional filediff being used to render an interdiff.

        diff_settings (reviewboard.diffviewer.settings.DiffSettings):
            The settings used to control the display of diffs.

            Version Added:
                5.0.2

        base_filediff (reviewbaord.diffviewer.models.filediff.FileDiff,
                       optional):
            The base FileDiff to use.

            This may only be provided if ``filediff`` is provided and
            ``interfilediff`` is not.

            Version Added:
                7.0

        base_commit (reviewboard.diffviewer.models.diffcommit.DiffCommit,
                     optional):
            An optional base commit. No :py:class:`FileDiffs
            <reviewboard.diffviewer.models.filediff.FileDiff>` from commits
            before that commit will be included in the results.

            This argument only applies to :py:class:`DiffSets
            <reviewboard.diffviewer.models.diffset.DiffSet>` with
            :py:class:`DiffCommits <reviewboard.diffviewer.models.diffcommit
            .DiffCommit>`.

            Version Added:
                7.0

        tip_commit (reviewboard.diffviewer.models.diffcommit.DiffCommit,
                    optional):
            An optional tip commit. No :py:class:`FileDiffs
            <reviewboard.diffviewer.models.filediff.FileDiff>` from commits
            after that commit will be included in the results.

            This argument only applies to :py:class:`DiffSets
            <reviewboard.diffviewer.models.diffset.DiffSet>` with
            :py:class:`DiffCommits <reviewboard.diffviewer.models.diffcommit
            .DiffCommit>`.

            Version Added:
                7.0

    Returns:
        int:
        The last virtual line number.
    """
    diff_file = get_file_from_filediff(context=context,
                                       filediff=filediff,
                                       interfilediff=interfilediff,
                                       diff_settings=diff_settings,
                                       base_commit=base_commit,
                                       tip_commit=tip_commit)
    assert diff_file is not None

    last_chunk = diff_file['chunks'][-1]
    last_line = last_chunk['lines'][-1]

    return last_line[0]


def _get_last_header_in_chunks_before_line(chunks, target_line):
    """Find the last header in the list of chunks before the target line."""
    def find_last_line_numbers(lines):
        """Return a tuple of the last line numbers in the given list of lines.

        The last line numbers are not always contained in the last element of
        the ``lines`` list. This is the case when dealing with interdiffs that
        have filtered out opcodes.

        See :py:func:`get_chunks_in_range` for a description of what is
        contained in each element of ``lines``.
        """
        last_left = None
        last_right = None

        for line in reversed(lines):
            if not last_right and line[4]:
                last_right = line[4]

            if not last_left and line[1]:
                last_left = line[1]

            if last_left and last_right:
                break

        return last_left, last_right

    def find_header(headers, offset, last_line):
        """Return the last header that occurs before a line.

        The offset parameter is the difference between the virtual number and
        and actual line number in the chunk. This is required because the
        header line numbers are original or patched line numbers, not virtual
        line numbers.
        """
        # In the case of interdiffs, it is possible that there will be headers
        # in the chunk that don't belong to it, but were put there due to
        # chunks being merged together. We must therefore ensure that the
        # header we're looking at is actually in the chunk.
        end_line = min(last_line, target_line)

        for header in reversed(headers):
            virtual_line = header[0] + offset

            if virtual_line < end_line:
                return {
                    'line': virtual_line,
                    'text': header[1]
                }

    # The most up-to-date header information
    header = {
        'left': None,
        'right': None
    }

    for chunk in chunks:
        lines = chunk['lines']
        virtual_first_line = lines[0][0]

        if virtual_first_line <= target_line:
            if virtual_first_line == target_line:
                # The given line number is the first line of a new chunk so
                # there can't be any relevant header information here.
                break

            last_left, last_right = find_last_line_numbers(lines)

            if 'left_headers' in chunk['meta'] and lines[0][1]:
                offset = virtual_first_line - lines[0][1]

                left_header = find_header(chunk['meta']['left_headers'],
                                          offset, last_left + offset)

                header['left'] = left_header or header['left']

            if 'right_headers' in chunk['meta'] and lines[0][4]:
                offset = virtual_first_line - lines[0][4]

                right_header = find_header(chunk['meta']['right_headers'],
                                           offset, last_right + offset)

                header['right'] = right_header or header['right']
        else:
            # We've gone past the given line number.
            break

    return header


def get_last_header_before_line(
    context: dict[str, Any],
    filediff: FileDiff,
    interfilediff: Optional[FileDiff],
    target_line: int,
    *,
    diff_settings: DiffSettings,
    base_filediff: Optional[FileDiff] = None,
    base_commit: Optional[DiffCommit] = None,
    tip_commit: Optional[DiffCommit] = None,
) -> dict:
    """Return the last header that occurs before the given line.

    Version Changed:
        7.0:
        * Added the ``base_filediff``, ``base_commit``, and ``tip_commit``
          arguments.

    Version Changed:
        5.0.2:
        * Added the optional ``diff_settings`` argument.

    Args:
        context (dict):
            Template context being used to render the diff.

        filediff (reviewboard.diffviewer.models.filediff.FileDiff):
            The filediff being rendered.

        interfilediff (reviewboard.diffviewer.models.filediff.FileDiff),
            The optional filediff being used to render an interdiff.

        target_line (int):
            The virtual line number that the header must be before.

        diff_settings (reviewboard.diffviewer.settings.DiffSettings):
            The settings used to control the display of diffs.

            Version Added:
                5.0.2

        base_filediff (reviewbaord.diffviewer.models.filediff.FileDiff,
                       optional):
            The base FileDiff to use.

            This may only be provided if ``filediff`` is provided and
            ``interfilediff`` is not.

            Version Added:
                7.0

        base_commit (reviewboard.diffviewer.models.diffcommit.DiffCommit,
                     optional):
            An optional base commit. No :py:class:`FileDiffs
            <reviewboard.diffviewer.models.filediff.FileDiff>` from commits
            before that commit will be included in the results.

            This argument only applies to :py:class:`DiffSets
            <reviewboard.diffviewer.models.diffset.DiffSet>` with
            :py:class:`DiffCommits <reviewboard.diffviewer.models.diffcommit
            .DiffCommit>`.

            Version Added:
                7.0

        tip_commit (reviewboard.diffviewer.models.diffcommit.DiffCommit,
                    optional):
            An optional tip commit. No :py:class:`FileDiffs
            <reviewboard.diffviewer.models.filediff.FileDiff>` from commits
            after that commit will be included in the results.

            This argument only applies to :py:class:`DiffSets
            <reviewboard.diffviewer.models.diffset.DiffSet>` with
            :py:class:`DiffCommits <reviewboard.diffviewer.models.diffcommit
            .DiffCommit>`.

            Version Added:
                7.0

    Returns:
        dict:
        Information on any headers found. See
        :py:class:`DiffSideBySideHeadersInfo` for details.
    """
    diff_file = get_file_from_filediff(
        context=context,
        filediff=filediff,
        interfilediff=interfilediff,
        diff_settings=diff_settings,
        base_filediff=base_filediff,
        base_commit=base_commit,
        tip_commit=tip_commit)
    assert diff_file is not None

    return _get_last_header_in_chunks_before_line(chunks=diff_file['chunks'],
                                                  target_line=target_line)


def get_file_chunks_in_range(
    context: dict[str, Any],
    filediff: FileDiff,
    interfilediff: Optional[FileDiff],
    first_line: int,
    num_lines: int,
    *,
    diff_settings: DiffSettings,
    base_filediff: Optional[FileDiff] = None,
    base_commit: Optional[DiffCommit] = None,
    tip_commit: Optional[DiffCommit] = None,
) -> Iterator[dict[str, Any]]:
    """Generate the chunks within a range of lines in the specified filediff.

    This is primarily intended for use with templates. It takes a template
    request context for looking up the user and for caching file lists, in
    order to improve performance and reduce lookup times for files that have
    already been fetched.

    See :py:func:`get_chunks_in_range` for information on the returned state
    of the chunks.

    Version Changed:
        7.0:
        * Added ``base_filediff``, ``base_commit`` and ``tip_commit``
          arguments.

    Version Changed:
        5.0.2:
        * Added the optional ``diff_settings`` argument.

    Args:
        context (dict):
            Template context being used to render the diff.

        filediff (reviewboard.diffviewer.models.filediff.FileDiff):
            The filediff being rendered.

        interfilediff (reviewboard.diffviewer.models.filediff.FileDiff),
            The optional filediff being used to render an interdiff.

        first_line (int):
            The first line number in the range.

        num_lines (int):
            The number of lines in the range.

        diff_settings (reviewboard.diffviewer.settings.DiffSettings):
            The settings used to control the display of diffs.

            Version Added:
                5.0.2

        base_filediff (reviewbaord.diffviewer.models.filediff.FileDiff,
                       optional):
            The base FileDiff to use.

            This may only be provided if ``filediff`` is provided and
            ``interfilediff`` is not.

            Version Added:
                7.0

        base_commit (reviewboard.diffviewer.models.diffcommit.DiffCommit,
                     optional):
            An optional base commit. No :py:class:`FileDiffs
            <reviewboard.diffviewer.models.filediff.FileDiff>` from commits
            before that commit will be included in the results.

            This argument only applies to :py:class:`DiffSets
            <reviewboard.diffviewer.models.diffset.DiffSet>` with
            :py:class:`DiffCommits <reviewboard.diffviewer.models.diffcommit
            .DiffCommit>`.

            Version Added:
                7.0

        tip_commit (reviewboard.diffviewer.models.diffcommit.DiffCommit,
                    optional):
            An optional tip commit. No :py:class:`FileDiffs
            <reviewboard.diffviewer.models.filediff.FileDiff>` from commits
            after that commit will be included in the results.

            This argument only applies to :py:class:`DiffSets
            <reviewboard.diffviewer.models.diffset.DiffSet>` with
            :py:class:`DiffCommits <reviewboard.diffviewer.models.diffcommit
            .DiffCommit>`.

            Version Added:
                7.0

    Yields:
        DiffChunk:
        Each chunk in the range.
    """
    diff_file = get_file_from_filediff(context=context,
                                       filediff=filediff,
                                       interfilediff=interfilediff,
                                       diff_settings=diff_settings,
                                       base_filediff=base_filediff,
                                       base_commit=base_commit,
                                       tip_commit=tip_commit)

    if diff_file:
        yield from get_chunks_in_range(chunks=diff_file['chunks'],
                                       first_line=first_line,
                                       num_lines=num_lines)


def get_chunks_in_range(chunks, first_line, num_lines):
    """Generate the chunks within a range of lines of a larger list of chunks.

    This takes a list of chunks, computes a subset of those chunks from the
    line ranges provided, and generates a new set of those chunks.

    Each returned chunk is a dictionary with the following fields:

    ============= ========================================================
    Variable      Description
    ============= ========================================================
    ``change``    The change type ("equal", "replace", "insert", "delete")
    ``numlines``  The number of lines in the chunk.
    ``lines``     The list of lines in the chunk.
    ``meta``      A dictionary containing metadata on the chunk
    ============= ========================================================


    Each line in the list of lines is an array with the following data:

    ======== =============================================================
    Index    Description
    ======== =============================================================
    0        Virtual line number (union of the original and patched files)
    1        Real line number in the original file
    2        HTML markup of the original file
    3        Changed regions of the original line (for "replace" chunks)
    4        Real line number in the patched file
    5        HTML markup of the patched file
    6        Changed regions of the patched line (for "replace" chunks)
    7        True if line consists of only whitespace changes
    ======== =============================================================
    """
    for i, chunk in enumerate(chunks):
        lines = chunk['lines']

        if lines[-1][0] >= first_line >= lines[0][0]:
            start_index = first_line - lines[0][0]

            if first_line + num_lines <= lines[-1][0]:
                last_index = start_index + num_lines
            else:
                last_index = len(lines)

            new_chunk = {
                'index': i,
                'lines': chunk['lines'][start_index:last_index],
                'numlines': last_index - start_index,
                'change': chunk['change'],
                'meta': chunk.get('meta', {}),
            }

            yield new_chunk

            first_line += new_chunk['numlines']
            num_lines -= new_chunk['numlines']

            assert num_lines >= 0
            if num_lines == 0:
                break


def get_line_changed_regions(oldline, newline):
    """Returns regions of changes between two similar lines."""
    if oldline is None or newline is None:
        return None, None

    # Use the SequenceMatcher directly. It seems to give us better results
    # for this. We should investigate steps to move to the new differ.
    differ = SequenceMatcher(None, oldline, newline)

    # This thresholds our results -- we don't want to show inter-line diffs
    # if most of the line has changed, unless those lines are very short.

    # FIXME: just a plain, linear threshold is pretty crummy here.  Short
    # changes in a short line get lost.  I haven't yet thought of a fancy
    # nonlinear test.
    if differ.ratio() < 0.6:
        return None, None

    oldchanges = []
    newchanges = []
    back = (0, 0)

    for tag, i1, i2, j1, j2 in differ.get_opcodes():
        if tag == 'equal':
            if (i2 - i1 < 3) or (j2 - j1 < 3):
                back = (j2 - j1, i2 - i1)

            continue

        oldstart, oldend = i1 - back[0], i2
        newstart, newend = j1 - back[1], j2

        if oldchanges and oldstart <= oldchanges[-1][1] < oldend:
            oldchanges[-1] = (oldchanges[-1][0], oldend)
        elif not oldline[oldstart:oldend].isspace():
            oldchanges.append((oldstart, oldend))

        if newchanges and newstart <= newchanges[-1][1] < newend:
            newchanges[-1] = (newchanges[-1][0], newend)
        elif not newline[newstart:newend].isspace():
            newchanges.append((newstart, newend))

        back = (0, 0)

    return oldchanges, newchanges


def get_sorted_filediffs(
    filediffs: Sequence[_T],
    key: Optional[Callable[[_T], FileDiff]] = None,
) -> Sequence[_T]:
    """Sorts a list of filediffs or filediff-wrapping objects.

    The list of filediffs will be sorted first by their base paths in
    ascending order.

    Within a base path, they'll be sorted by base name (minus the extension)
    in ascending order.

    If two files have the same base path and base name, we'll sort by the
    extension in descending order. This will make :file:`*.h` sort ahead of
    :file:`*.c`/:file:`*.cpp`, for example.

    If the list being passed in is actually not a list of FileDiffs, it
    must provide a callable ``key`` parameter that will return a FileDiff
    for the given entry in the list. This will only be called once per
    item.

    Args:
        filediffs (list of object):
            The list of FileDiffs (or objects to convert to FileDiffs) to
            sort.

        key (callable, optional):
            The optional function used to transform sequences of items to
            FileDiffs.

    Returns:
        list of reviewboard.diffviewer.models.FileDiff:
        The sorted list of filediffs.
    """
    from reviewboard.diffviewer.models import FileDiff

    def make_key(
        item: _T,
    ) -> tuple[str, str, int, str]:
        filediff: FileDiff

        if key:
            filediff = key(item)
        else:
            assert isinstance(item, FileDiff)

            filediff = item

        filename = filediff.dest_file
        i = filename.rfind('/')

        if i == -1:
            base_path = ''
        else:
            base_path = filename[:i]
            filename = filename[i + 1:]

        base_name, ext = os.path.splitext(filename)
        ext = ext[1:]

        if ext in HEADER_EXTENSIONS:
            order_flag = 1
        elif ext in IMPL_EXTENSIONS:
            order_flag = 2
        else:
            order_flag = 0

        return base_path, base_name, order_flag, ext

    return sorted(filediffs, key=make_key)


def get_displayed_diff_line_ranges(chunks, first_vlinenum, last_vlinenum):
    """Return the displayed line ranges based on virtual line numbers.

    This takes the virtual line numbers (the index in the side-by-side diff
    lines) and returns the human-readable line numbers, the chunks they're in,
    and mapped virtual line numbers.

    A virtual line range may start or end in a chunk not containing displayed
    line numbers (such as an "original" range starting/ending in an "insert"
    chunk). The resulting displayed line ranges will exclude these chunks.

    Args:
        chunks (list of dict):
            The list of chunks for the diff.

        first_vlinenum (int):
            The first virtual line number. This uses 1-based indexes.

        last_vlinenum (int):
            The last virtual line number. This uses 1-based indexes.

    Returns:
        tuple:
        A tuple of displayed line range information, containing 2 items.

        Each item will either be a dictionary of information, or ``None``
        if there aren't any displayed lines to show.

        The dictionary contains the following keys:

        ``display_range``:
            A tuple containing the displayed line range.

        ``virtual_range``:
            A tuple containing the virtual line range that ``display_range``
            maps to.

        ``chunk_range``:
            A tuple containing the beginning/ending chunks that
            ``display_range`` maps to.

    Raises:
        ValueError:
            The range provided was invalid.
    """
    if first_vlinenum < 0:
        raise ValueError('first_vlinenum must be >= 0')

    if last_vlinenum < first_vlinenum:
        raise ValueError('last_vlinenum must be >= first_vlinenum')

    orig_start_linenum = None
    orig_end_linenum = None
    orig_start_chunk = None
    orig_last_valid_chunk = None
    patched_start_linenum = None
    patched_end_linenum = None
    patched_start_chunk = None
    patched_last_valid_chunk = None

    for chunk in chunks:
        lines = chunk['lines']

        if not lines:
            logger.warning('get_displayed_diff_line_ranges: Encountered '
                           'empty chunk %r',
                           chunk)
            continue

        first_line = lines[0]
        last_line = lines[-1]
        chunk_first_vlinenum = first_line[0]
        chunk_last_vlinenum = last_line[0]

        if first_vlinenum > chunk_last_vlinenum:
            # We're too early. There won't be anything of interest here.
            continue

        if last_vlinenum < chunk_first_vlinenum:
            # We're not going to find anything useful at this point, so bail.
            break

        change = chunk['change']
        valid_for_orig = (change != 'insert' and first_line[1])
        valid_for_patched = (change != 'delete' and first_line[4])

        if valid_for_orig:
            orig_last_valid_chunk = chunk

            if not orig_start_chunk:
                orig_start_chunk = chunk

        if valid_for_patched:
            patched_last_valid_chunk = chunk

            if not patched_start_chunk:
                patched_start_chunk = chunk

        if chunk_first_vlinenum <= first_vlinenum <= chunk_last_vlinenum:
            # This chunk contains the first line that can possibly be used for
            # the comment range. We know the start and end virtual line numbers
            # in the range, so we can compute the proper offset.
            offset = first_vlinenum - chunk_first_vlinenum

            if valid_for_orig:
                orig_start_linenum = first_line[1] + offset
                orig_start_vlinenum = first_line[0] + offset

            if valid_for_patched:
                patched_start_linenum = first_line[4] + offset
                patched_start_vlinenum = first_line[0] + offset
        elif first_vlinenum < chunk_first_vlinenum:
            # One side of the the comment range may not have started in a valid
            # chunk (this would happen if a comment began in an insert or
            # delete chunk). If that happened, we may not have been able to set
            # the beginning of the range in the condition above. Check for this
            # and try setting it now.
            if orig_start_linenum is None and valid_for_orig:
                orig_start_linenum = first_line[1]
                orig_start_vlinenum = first_line[0]

            if patched_start_linenum is None and valid_for_patched:
                patched_start_linenum = first_line[4]
                patched_start_vlinenum = first_line[0]

    # Figure out the end ranges, now that we know the valid ending chunks of
    # each. We're going to try to get the line within the chunk that represents
    # the end, if within the chunk, capping it to the last line in the chunk.
    #
    # If a particular range did not have a valid chunk anywhere in that range,
    # we're going to invalidate the entire range.
    if orig_last_valid_chunk:
        lines = orig_last_valid_chunk['lines']
        first_line = lines[0]
        last_line = lines[-1]
        offset = last_vlinenum - first_line[0]

        orig_end_linenum = min(last_line[1], first_line[1] + offset)
        orig_end_vlinenum = min(last_line[0], first_line[0] + offset)

        assert orig_end_linenum >= orig_start_linenum
        assert orig_end_vlinenum >= orig_start_vlinenum

        orig_range_info = {
            'display_range': (orig_start_linenum, orig_end_linenum),
            'virtual_range': (orig_start_vlinenum, orig_end_vlinenum),
            'chunk_range': (orig_start_chunk, orig_last_valid_chunk),
        }
    else:
        orig_range_info = None

    if patched_last_valid_chunk:
        lines = patched_last_valid_chunk['lines']
        first_line = lines[0]
        last_line = lines[-1]
        offset = last_vlinenum - first_line[0]

        patched_end_linenum = min(last_line[4], first_line[4] + offset)
        patched_end_vlinenum = min(last_line[0], first_line[0] + offset)

        assert patched_end_linenum >= patched_start_linenum
        assert patched_end_vlinenum >= patched_start_vlinenum

        patched_range_info = {
            'display_range': (patched_start_linenum, patched_end_linenum),
            'virtual_range': (patched_start_vlinenum, patched_end_vlinenum),
            'chunk_range': (patched_start_chunk, patched_last_valid_chunk),
        }
    else:
        patched_range_info = None

    return orig_range_info, patched_range_info


def get_diff_data_chunks_info(diff):
    """Return information on each chunk in a diff.

    This will scan through a unified diff file, looking for each chunk in the
    diff and returning information on their ranges and lines of context. This
    can be used to generate statistics on diffs and help map changed regions
    in diffs to lines of source files.

    Version Added:
        3.0.18

    Args:
        diff (bytes):
            The diff data to scan.

    Returns:
        list of dict:
        A list of chunk information dictionaries. Each entry has an ``orig``
        and ``modified`` dictionary containing the following keys:

        ``chunk_start`` (``int``):
            The starting line number of the chunk shown in the diff, including
            any lines of context. This is 0-based.

        ``chunk_len`` (``int``):
            The length of the chunk shown in the diff, including any lines of
            context.

        ``changes_start`` (``int``):
            The starting line number of a range of changes shown in a chunk in
            the diff.
            This is after any lines of context and is 0-based.

        ``changes_len`` (``int``):
            The length of the changes shown in a chunk in the diff, excluding
            any lines of context.

        ``pre_lines_of_context`` (``int``):
            The number of lines of context before any changes in a chunk. If
            the chunk doesn't have any changes, this will contain all lines of
            context otherwise shown around changes in the other region in this
            entry.

        ``post_lines_of_context`` (``int``):
            The number of lines of context after any changes in a chunk. If
            the chunk doesn't have any changes, this will be 0.
    """
    def _finalize_result():
        if not cur_result:
            return

        for result_dict, unchanged_lines in ((cur_result_orig,
                                              orig_unchanged_lines),
                                             (cur_result_modified,
                                              modified_unchanged_lines)):
            result_dict['changes_len'] -= unchanged_lines

            if result_dict['changes_len'] == 0:
                assert result_dict['pre_lines_of_context'] == 0
                result_dict['pre_lines_of_context'] = unchanged_lines
            else:
                result_dict['post_lines_of_context'] = unchanged_lines

    process_orig_changes = False
    process_modified_changes = False

    results = []
    cur_result = None
    cur_result_orig = None
    cur_result_modified = None

    orig_unchanged_lines = 0
    modified_unchanged_lines = 0

    # Look through the chunks of the diff, trying to find the amount
    # of context shown at the beginning of each chunk. Though this
    # will usually be 3 lines, it may be fewer or more, depending
    # on file length and diff generation settings.
    for i, line in enumerate(split_line_endings(diff.strip())):
        if line.startswith(b'-'):
            if process_orig_changes:
                # We've found the first change in the original side of the
                # chunk. We now know how many lines of context we have here.
                #
                # We reduce the indexes by 1 because the chunk ranges
                # in diffs start at 1, and we want a 0-based index.
                cur_result_orig['pre_lines_of_context'] = orig_unchanged_lines
                cur_result_orig['changes_start'] += orig_unchanged_lines
                cur_result_orig['changes_len'] -= orig_unchanged_lines
                process_orig_changes = False

            orig_unchanged_lines = 0
        elif line.startswith(b'+'):
            if process_modified_changes:
                # We've found the first change in the modified side of the
                # chunk. We now know how many lines of context we have here.
                #
                # We reduce the indexes by 1 because the chunk ranges
                # in diffs start at 1, and we want a 0-based index.
                cur_result_modified['pre_lines_of_context'] = \
                    modified_unchanged_lines
                cur_result_modified['changes_start'] += \
                    modified_unchanged_lines
                cur_result_modified['changes_len'] -= modified_unchanged_lines
                process_modified_changes = False

            modified_unchanged_lines = 0
        elif line.startswith(b' '):
            # We might be before a group of changes, inside a group of changes,
            # or after a group of changes. Either way, we want to track these
            # values.
            orig_unchanged_lines += 1
            modified_unchanged_lines += 1
        else:
            # This was not a change within a chunk, or we weren't processing,
            # so check to see if this is a chunk header instead.
            m = CHUNK_RANGE_RE.match(line)

            if m:
                # It is a chunk header. Start by updating the previous range
                # to factor in the lines of trailing context.
                _finalize_result()

                # Next, reset the state for the next range, and pull the line
                # numbers and lengths from the header. We'll also normalize
                # the starting locations to be 0-based.
                orig_start = int(m.group('orig_start')) - 1
                orig_len = int(m.group('orig_len') or '1')
                modified_start = int(m.group('modified_start')) - 1
                modified_len = int(m.group('modified_len') or '1')

                cur_result_orig = {
                    'pre_lines_of_context': 0,
                    'post_lines_of_context': 0,
                    'chunk_start': orig_start,
                    'chunk_len': orig_len,
                    'changes_start': orig_start,
                    'changes_len': orig_len,
                }
                cur_result_modified = {
                    'pre_lines_of_context': 0,
                    'post_lines_of_context': 0,
                    'chunk_start': modified_start,
                    'chunk_len': modified_len,
                    'changes_start': modified_start,
                    'changes_len': modified_len,
                }
                cur_result = {
                    'orig': cur_result_orig,
                    'modified': cur_result_modified,
                }
                results.append(cur_result)

                process_orig_changes = True
                process_modified_changes = True
                orig_unchanged_lines = 0
                modified_unchanged_lines = 0

    # We need to adjust the last range, if we're still processing
    # trailing context.
    _finalize_result()

    return results


def check_diff_size(diff_file, parent_diff_file=None):
    """Check the size of the given diffs against the maximum allowed size.

    If either of the provided diffs are too large, an exception will be raised.

    Args:
        diff_file (django.core.files.uploadedfile.UploadedFile):
            The diff file.

        parent_diff_file (django.core.files.uploadedfile.UploadedFile,
                          optional):
            The parent diff file, if any.

    Raises:
        reviewboard.diffviewer.errors.DiffTooBigError:
            The supplied files are too big.
    """
    siteconfig = SiteConfiguration.objects.get_current()
    max_diff_size = siteconfig.get('diffviewer_max_diff_size')

    if max_diff_size > 0:
        if diff_file.size > max_diff_size:
            raise DiffTooBigError(
                _('The supplied diff file is too large.'),
                max_diff_size=max_diff_size)

        if parent_diff_file and parent_diff_file.size > max_diff_size:
            raise DiffTooBigError(
                _('The supplied parent diff file is too large.'),
                max_diff_size=max_diff_size)


def get_total_line_counts(files_qs):
    """Return the total line counts of all given FileDiffs.

    Args:
        files_qs (django.db.models.query.QuerySet):
            The queryset descripting the :py:class:`FileDiffs
            <reviewboard.diffviewer.models.filediff.FileDiff>`.

    Returns:
        dict:
        A dictionary with the following keys:

        * ``raw_insert_count``
        * ``raw_delete_count``
        * ``insert_count``
        * ``delete_count``
        * ``replace_count``
        * ``equal_count``
        * ``total_line_count``

        Each entry maps to the sum of that line count type for all
        :py:class:`FileDiffs
        <reviewboard.diffviewer.models.filediff.FileDiff>`.
    """
    counts = {
        'raw_insert_count': 0,
        'raw_delete_count': 0,
        'insert_count': 0,
        'delete_count': 0,
        'replace_count': None,
        'equal_count': None,
        'total_line_count': None,
    }

    for filediff in files_qs:
        for key, value in filediff.get_line_counts().items():
            if value is not None:
                if counts[key] is None:
                    counts[key] = value
                else:
                    counts[key] += value

    return counts
