"""Diff chunk generator implementations."""

from __future__ import annotations

import fnmatch
import hashlib
import logging
import re
from itertools import zip_longest
from typing import Optional, Sequence, TYPE_CHECKING, Union

import pygments.util
from django.utils.encoding import force_str
from django.utils.html import escape
from django.utils.translation import get_language, gettext as _
from djblets.log import log_timed
from djblets.cache.backend import cache_memoize
from djblets.siteconfig.models import SiteConfiguration
from housekeeping.functions import deprecate_non_keyword_only_args
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import (find_lexer_class,
                             guess_lexer_for_filename)

from reviewboard.codesafety import code_safety_checker_registry
from reviewboard.deprecation import RemovedInReviewBoard80Warning
from reviewboard.diffviewer.differ import DiffCompatVersion, get_differ
from reviewboard.diffviewer.diffutils import (get_filediff_encodings,
                                              get_line_changed_regions,
                                              get_original_file,
                                              get_original_and_patched_files,
                                              get_patched_file,
                                              convert_to_unicode,
                                              split_line_endings)
from reviewboard.diffviewer.opcode_generator import get_diff_opcode_generator
from reviewboard.diffviewer.settings import DiffSettings

if TYPE_CHECKING:
    from django.http import HttpRequest

    from reviewboard.diffviewer.models.filediff import FileDiff


logger = logging.getLogger(__name__)


class NoWrapperHtmlFormatter(HtmlFormatter):
    """An HTML Formatter for Pygments that doesn't wrap items in a div."""
    def __init__(self, *args, **kwargs):
        super(NoWrapperHtmlFormatter, self).__init__(*args, **kwargs)

    def _wrap_div(self, inner):
        """Removes the div wrapper from formatted code.

        This is called by the formatter to wrap the contents of inner.
        Inner is a list of tuples containing formatted code. If the first item
        in the tuple is zero, then it's the div wrapper, so we should ignore
        it.
        """
        for tup in inner:
            if tup[0]:
                yield tup


class RawDiffChunkGenerator(object):
    """A generator for chunks for a diff that can be used for rendering.

    Each chunk represents an insert, delete, replace, or equal section. It
    contains all the data needed to render the portion of the diff.

    This is general-purpose and meant to operate on strings each consisting of
    at least one line of text, or lists of lines of text.

    If the caller passes lists of lines instead of strings, then the
    caller will also be responsible for applying any syntax highlighting and
    dealing with newline differences.

    Chunk generator instances must be recreated for each new file being
    parsed.

    Version Changed:
        5.0:
        Added :py:attr:`all_code_safety_results`.

    Attributes:
        all_code_safety_results (dict):
            Code safety warnings were found while processing the diff.

            This is in the form of::

                {
                    '<checker_id>': {
                        'warnings': {'<result_id>', ...},
                        'errors': {'<result_id>', ...},
                    },
                    ...
                }

            All keys are optional.

            Version Added:
                5.0
    """

    NEWLINES_RE = re.compile(r'\r?\n')

    # The maximum size a line can be before we start shutting off styling.
    STYLED_MAX_LINE_LEN = 1000
    STYLED_MAX_LIMIT_BYTES = 200000  # 200KB

    # A list of filename extensions that won't be styled.
    STYLED_EXT_BLACKLIST = (
        '.txt',  # ResourceLexer is used as a default.
    )

    #: The default width for a tabstop.
    TAB_SIZE = DiffSettings.DEFAULT_TAB_SIZE

    ######################
    # Instance variables #
    ######################

    #: Settings used for the generation of the diff.
    #:
    #: Version Added:
    #:     5.0.2
    #:
    #: Type:
    #:     reviewboard.diffviewer.settings.DiffSettings
    diff_settings: DiffSettings

    def __init__(
        self,
        old: Optional[Union[bytes, Sequence[bytes]]],
        new: Optional[Union[bytes, Sequence[bytes]]],
        orig_filename: str,
        modified_filename: str,
        encoding_list: Optional[Sequence[str]] = None,
        diff_compat: int = DiffCompatVersion.DEFAULT,
        *,
        diff_settings: DiffSettings,
    ) -> None:
        """Initialize the chunk generator.

        Version Changed:
            6.0:
            * Removed ``enable_syntax_highlighting``.
            * Made ``diff_settings`` mandatory.

        Version Changed:
            5.0.2:
            * Added ``diff_settings``, which will be required starting in
              Review Board 6.
            * Deprecated ``enable_syntax_highlighting`` in favor of
              ``diff_settings``.

        Args:
            old (bytes or list of bytes):
                The old data being modified.

            new (bytes or list of bytes):
                The new data.

            orig_filename (unicode):
                The filename corresponding to the old data.

            modified_filename (unicode):
                The filename corresponding to the new data.

            encoding_list (list of unicode, optional):
                A list of encodings to try for the ``old`` and ``new`` data,
                when converting to Unicode. If not specified, this defaults
                to ``iso-8859-15``.

            diff_compat (int, optional):
                A specific diff compatibility version to use for any diffing
                logic.

            diff_settings (reviewboard.diffviewer.settings.DiffSettings):
                The settings used to control the display of diffs.

                Version Added:
                    5.0.2
        """
        # Check that the data coming in is in the formats we accept.
        for param, param_name in ((old, 'old'), (new, 'new')):
            if param is not None:
                if isinstance(param, list):
                    if param and not isinstance(param[0], bytes):
                        raise TypeError(
                            _('%s expects None, list of bytes, or bytes '
                              'value for "%s", not list of %s')
                            % (type(self).__name__, param_name,
                               type(param[0])))
                elif not isinstance(param, bytes):
                    raise TypeError(
                        _('%s expects None, list of bytes, or bytes value '
                          'for "%s", not %s')
                        % (type(self).__name__, param_name, type(param)))

        if not isinstance(orig_filename, str):
            raise TypeError(
                _('%s expects a Unicode value for "orig_filename"')
                % type(self).__name__)

        if not isinstance(modified_filename, str):
            raise TypeError(
                _('%s expects a Unicode value for "modified_filename"')
                % type(self).__name__)

        assert diff_settings.tab_size
        self.diff_settings = diff_settings

        self.old = old
        self.new = new
        self.orig_filename = orig_filename
        self.modified_filename = modified_filename
        self.diff_settings = diff_settings
        self.enable_syntax_highlighting = diff_settings.syntax_highlighting
        self.encoding_list = encoding_list or ['iso-8859-15']
        self.diff_compat = diff_compat
        self.differ = None

        self.all_code_safety_results = {}

        # Chunk processing state.
        self._last_header = [None, None]
        self._last_header_index = [0, 0]
        self._chunk_index = 0

    def get_opcode_generator(self):
        """Return the DiffOpcodeGenerator used to generate diff opcodes."""
        return get_diff_opcode_generator(self.differ)

    def get_chunks(self, cache_key=None):
        """Return the chunks for the given diff information.

        If a cache key is provided and there are chunks already computed in the
        cache, they will be yielded. Otherwise, new chunks will be generated,
        stored in cache (given a cache key), and yielded.
        """
        if cache_key:
            chunks = cache_memoize(cache_key,
                                   lambda: list(self.get_chunks_uncached()),
                                   large_data=True)
        else:
            chunks = self.get_chunks_uncached()

        for chunk in chunks:
            yield chunk

    def get_chunks_uncached(self):
        """Yield the list of chunks, bypassing the cache."""
        for chunk in self.generate_chunks(self.old, self.new):
            yield chunk

    def generate_chunks(self, old, new, old_encoding_list=None,
                        new_encoding_list=None):
        """Generate chunks for the difference between two strings.

        The strings will be normalized, ensuring they're of the proper
        encoding and ensuring they have consistent newlines. They're then
        syntax-highlighted (if requested).

        Once the strings are ready, chunks are built from the strings and
        yielded to the caller. Each chunk represents information on an
        equal, inserted, deleted, or replaced set of lines.

        The number of lines of each chunk type are stored in the
        :py:attr:`counts` dictionary, which can then be accessed after
        yielding all chunks.

        Args:
            old (bytes or list of bytes):
                The old data being modified.

            new (bytes or list of bytes):
                The new data.

            old_encoding_list (list of unicode, optional):
                An optional list of encodings that ``old`` may be encoded in.
                If not provided, :py:attr:`encoding_list` is used.

            new_encoding_list (list of unicode, optional):
                An optional list of encodings that ``new`` may be encoded in.
                If not provided, :py:attr:`encoding_list` is used.

        Yields:
            dict:
            A rendered chunk containing the following keys:

            ``index`` (int)
                The 0-based index of the chunk.

            ``lines`` (list of unicode):
                The rendered list of lines.

            ``numlines`` (int):
                The number of lines in the chunk.

            ``change`` (unicode):
                The type of change (``delete``, ``equal``, ``insert`` or
                ``replace``).

            ``collapsable`` (bool):
                Whether the chunk can be collapsed.

            ``meta`` (dict):
                Metadata on the chunk.
        """
        is_lists = isinstance(old, list)
        assert is_lists == isinstance(new, list)

        if old_encoding_list is None:
            old_encoding_list = self.encoding_list

        if new_encoding_list is None:
            new_encoding_list = self.encoding_list

        if is_lists:
            if self.encoding_list:
                old = self.normalize_source_list(old, old_encoding_list)
                new = self.normalize_source_list(new, new_encoding_list)

            a = old
            b = new
        else:
            old, a = self.normalize_source_string(old, old_encoding_list)
            new, b = self.normalize_source_string(new, new_encoding_list)

        a_num_lines = len(a)
        b_num_lines = len(b)

        if is_lists:
            markup_a = a
            markup_b = b
        else:
            markup_a = None
            markup_b = None

            if self._get_enable_syntax_highlighting(old, new, a, b):
                # TODO: Try to figure out the right lexer for these files
                #       once instead of twice.
                markup_a = self._apply_pygments(
                    old or '',
                    self.normalize_path_for_display(self.orig_filename))
                markup_b = self._apply_pygments(
                    new or '',
                    self.normalize_path_for_display(self.modified_filename))

            if not markup_a:
                markup_a = self.NEWLINES_RE.split(escape(old))

            if not markup_b:
                markup_b = self.NEWLINES_RE.split(escape(new))

        siteconfig = SiteConfiguration.objects.get_current()
        ignore_space = True

        for pattern in siteconfig.get('diffviewer_include_space_patterns'):
            if fnmatch.fnmatch(self.orig_filename, pattern):
                ignore_space = False
                break

        self.differ = get_differ(a, b, ignore_space=ignore_space,
                                 compat_version=self.diff_compat)
        self.differ.add_interesting_lines_for_headers(self.orig_filename)

        context_num_lines = siteconfig.get("diffviewer_context_num_lines")
        collapse_threshold = 2 * context_num_lines + 3

        line_num = 1
        opcodes_generator = self.get_opcode_generator()

        counts = {
            'equal': 0,
            'replace': 0,
            'insert': 0,
            'delete': 0,
        }

        for tag, i1, i2, j1, j2, meta in opcodes_generator:
            old_lines = markup_a[i1:i2]
            new_lines = markup_b[j1:j2]
            num_lines = max(len(old_lines), len(new_lines))

            lines = [
                self._diff_line(tag, meta, *diff_args)
                for diff_args in zip_longest(
                    range(line_num, line_num + num_lines),
                    range(i1 + 1, i2 + 1),
                    range(j1 + 1, j2 + 1),
                    a[i1:i2],
                    b[j1:j2],
                    old_lines,
                    new_lines)
            ]

            counts[tag] += num_lines

            if tag == 'equal' and num_lines > collapse_threshold:
                last_range_start = num_lines - context_num_lines

                if line_num == 1:
                    yield self._new_chunk(lines, 0, last_range_start, True)
                    yield self._new_chunk(lines, last_range_start, num_lines)
                else:
                    yield self._new_chunk(lines, 0, context_num_lines)

                    if i2 == a_num_lines and j2 == b_num_lines:
                        yield self._new_chunk(lines, context_num_lines,
                                              num_lines, True)
                    else:
                        yield self._new_chunk(lines, context_num_lines,
                                              last_range_start, True)
                        yield self._new_chunk(lines, last_range_start,
                                              num_lines)
            else:
                yield self._new_chunk(lines, 0, num_lines, False, tag, meta)

            line_num += num_lines

        self.counts = counts

    def check_line_code_safety(self, orig_line, modified_line,
                               extra_state={}, **kwargs):
        """Check the safety of a line of code.

        This will run the original and modified line through all registered
        code safety checkers. If any checker produces warnings or errors,
        those will be associated with the line.

        Version Added:
            5.0

        Args:
            orig_line (str):
                The original line to check.

            modified_line (str):
                The modiifed line to check.

            extra_state (dict, optional):
                Extra state to pass to the checker for the original or
                modified line content item. Used by subclasses to produce
                additional information that may be useful for some code safety
                checkers.

            **kwargs (dict, optional):
                Unused keyword arguments, for future expansion.

        Returns:
            list of tuple:
            A list of code safety results containing warnings or errors. Each
            item is a tuple containing:

            1. The registered checker ID.
            2. A dictionary with ``errors`` and/or ``warnings`` keys.
        """
        # Check for any unsafe/suspicious content on this line by passing
        # the raw source through any registered code safety checkers.
        results = []
        to_check = []

        if orig_line:
            to_check.append(dict({
                'path': self.orig_filename,
                'lines': [orig_line],
            }, **extra_state))

        if modified_line:
            to_check.append(dict({
                'path': self.modified_filename,
                'lines': [modified_line],
            }, **extra_state))

        if to_check:
            code_safety_configs = self.diff_settings.code_safety_configs

            # We have code to check. Let's go through each code checker
            # and see if we have any warnings or errors to display.
            for checker in code_safety_checker_registry:
                checker_config = code_safety_configs.get(checker.checker_id,
                                                         {})
                checker_results = checker.check_content(content_items=to_check,
                                                        **checker_config)

                if checker_results:
                    # Normalize the code checker results. We're going to
                    # extract only "errors" and "warnings" keys and set them
                    # only if they have a truthy value (present in the
                    # dictionary, non-None, and not an empty list).
                    norm_checker_results = {}

                    for key in ('errors', 'warnings'):
                        checker_result_ids = checker_results.get(key)

                        if checker_result_ids:
                            norm_checker_results[key] = checker_result_ids

                    if norm_checker_results:
                        # We have normalized checker results, so add them to
                        # the final list of results as documented in "Returns".
                        results.append((checker.checker_id,
                                        norm_checker_results))

        return results

    def normalize_source_string(self, s, encoding_list, **kwargs):
        """Normalize a source string of text to use for the diff.

        This will normalize the encoding of the string and the newlines,
        returning a tuple containing the normalized string and a list of
        lines split from the source.

        Both the original and modified strings used for the diff will be
        normalized independently.

        This is only used if the caller passes a string instead of a list for
        the original or new values.

        Subclasses can override this to provide custom behavior.

        Args:
            s (bytes):
                The string to normalize.

            encoding_list (list of unicode):
                The list of encodings to try when converting the string to
                Unicode.

            **kwargs (dict):
                Additional keyword arguments, for future expansion.

        Returns:
            tuple:
            A tuple containing:

            1. The full normalized string
            2. The list of lines from the string

        Raises:
            UnicodeDecodeError:
                The string could not be converted to Unicode.
        """
        s = convert_to_unicode(s, encoding_list)[1]

        # Normalize the input so that if there isn't a trailing newline, we
        # add it.
        if s and not s.endswith('\n'):
            s += '\n'

        lines = self.NEWLINES_RE.split(s or '')

        # Remove the trailing newline, now that we've split this. This will
        # prevent a duplicate line number at the end of the diff.
        del lines[-1]

        return s, lines

    def normalize_source_list(self, lines, encoding_list, **kwargs):
        """Normalize a list of source lines to use for the diff.

        This will normalize the encoding of the lines.

        Both the original and modified lists of lines used for the diff will be
        normalized independently.

        This is only used if the caller passes a list instead of a string for
        the original or new values.

        Subclasses can override this to provide custom behavior.

        Args:
            lines (list of bytes):
                The list of lines to normalize.

            encoding_list (list of unicode):
                The list of encodings to try when converting the lines to
                Unicode.

            **kwargs (dict):
                Additional keyword arguments, for future expansion.

        Returns:
            list of unicode:
            The resulting list of normalized lines.

        Raises:
            UnicodeDecodeError:
                One or more lines could not be converted to Unicode.
        """
        if encoding_list:
            lines = [
                convert_to_unicode(s, encoding_list)[1]
                for s in lines
            ]

        return lines

    def normalize_path_for_display(self, filename):
        """Normalize a file path for display to the user.

        By default, this returns the filename as-is. Subclasses can override
        the behavior to return a variant of the filename.

        Args:
            filename (unicode):
                The filename to normalize.

        Returns:
            unicode:
            The normalized filename.
        """
        return filename

    def get_line_changed_regions(self, old_line_num, old_line,
                                 new_line_num, new_line):
        """Return information on changes between two lines.

        This returns a tuple containing a list of tuples of ranges in the
        old line, and a list of tuples of ranges in the new line, that
        should be highlighted.

        This defaults to simply wrapping get_line_changed_regions() from
        diffutils. Subclasses can override to provide custom behavior.
        """
        return get_line_changed_regions(old_line, new_line)

    def _get_enable_syntax_highlighting(self, old, new, a, b):
        """Returns whether or not we'll be enabling syntax highlighting.

        This is based first on the value received when constructing the
        generator, and then based on heuristics to determine if it's fast
        enough to render with syntax highlighting on.

        The heuristics take into account the size of the files in bytes and
        the number of lines.
        """
        if not self.enable_syntax_highlighting:
            return False

        threshold = self.diff_settings.syntax_highlighting_threshold

        if threshold and (len(a) > threshold or len(b) > threshold):
            return False

        # Very long files, especially XML files, can take a long time to
        # highlight. For files over a certain size, don't highlight them.
        if (len(old) > self.STYLED_MAX_LIMIT_BYTES or
                len(new) > self.STYLED_MAX_LIMIT_BYTES):
            return False

        # Don't style the file if we have any *really* long lines.
        # It's likely a minified file or data or something that doesn't
        # need styling, and it will just grind Review Board to a halt.
        for lines in (a, b):
            for line in lines:
                if len(line) > self.STYLED_MAX_LINE_LEN:
                    return False

        return True

    def _diff_line(self, tag, meta, v_line_num, old_line_num, new_line_num,
                   old_line, new_line, old_markup, new_markup):
        """Creates a single line in the diff viewer.

        Information on the line will be returned, and later will be used
        for rendering the line. The line represents a single row of a
        side-by-side diff. It contains a row number, real line numbers,
        region information, syntax-highlighted HTML for the text,
        and other metadata.
        """
        if (tag == 'replace' and
            old_line and new_line and
            len(old_line) <= self.STYLED_MAX_LINE_LEN and
            len(new_line) <= self.STYLED_MAX_LINE_LEN and
            old_line != new_line):
            # Generate information on the regions that changed between the
            # two lines.
            old_region, new_region = \
                self.get_line_changed_regions(old_line_num, old_line,
                                              new_line_num, new_line)
        else:
            old_region = new_region = []

        old_markup = old_markup or ''
        new_markup = new_markup or ''

        line_pair = (old_line_num, new_line_num)

        indentation_changes = meta.get('indentation_changes', {})

        if line_pair[0] is not None and line_pair[1] is not None:
            indentation_change = indentation_changes.get('%d-%d' % line_pair)

            # We check the ranges against (0, 0) for compatibility with a bug
            # present in Review Board 4.0.6 and older, where bad indentation
            # calculation logic could incorrectly determine that two
            # "filtered-equal" lines in interdiffs had a 0-length indentation
            # change. This broke our serialization logic.
            #
            # Review Board 4.0.7 and higher address this problem, but we could
            # be showing something that's still in cache. Note however that
            # the "indentation" lines will still be broken up into their own
            # chunks in the diff viewer, but at least they'll render.
            if indentation_change and indentation_change[1:] != (0, 0):
                old_markup, new_markup = self._highlight_indentation(
                    old_markup, new_markup, *indentation_change)

        result = [
            v_line_num,
            old_line_num or '', old_markup, old_region,
            new_line_num or '', new_markup, new_region,
            line_pair in meta['whitespace_lines']
        ]

        # NOTE: Prior to Review Board 5, this only contained moved info
        #       ("to"/"from" keys), and was not used for general line-level
        #       metadata. To avoid changing the structure of the line format
        #       too much (given that this can be consumed by third-parties),
        #       we have updated this to be a general-purpose metadata storage.
        line_meta = {}

        # Record all the moved line numbers, carefully making note of the
        # start of each range. Ranges start when the previous line number is
        # either not in a move range or does not immediately precede this
        # line.
        for direction, moved_line_num in (('to', old_line_num),
                                          ('from', new_line_num)):
            moved_meta = meta.get(f'moved-{direction}', {})
            direction_move_info = self._get_move_info(moved_line_num,
                                                      moved_meta)

            if direction_move_info is not None:
                line_meta[direction] = direction_move_info

        # Check for any unsafe/suspicious content on this line by passing
        # the raw source through any registered code safety checkers.
        code_safety_results = self.check_line_code_safety(
            orig_line=old_line,
            modified_line=new_line)

        if code_safety_results:
            # Store the code safety information for this line and in the
            # diff-wide all_code_safety_results.
            line_meta['code_safety'] = code_safety_results
            all_code_safety_results = self.all_code_safety_results

            for checker_id, checker_results in code_safety_results:
                all_code_checker_results = \
                    all_code_safety_results.setdefault(checker_id, {})

                for key, checker_result_ids in checker_results.items():
                    all_code_checker_results.setdefault(key, set()).update(
                        checker_result_ids)

        # Only include the meta information for the line if it has content.
        # Otherwise, save the space in cache.
        if line_meta:
            result.append(line_meta)

        return result

    def _get_move_info(self, line_num, moved_meta):
        """Return information for a moved line.

        This will return a tuple containing the line number on the other end
        of the move for a line, and whether this is the beginning of a move
        range.

        Args:
            line_num (int):
                The line number that was part of a move.

            moved_meta (dict):
                Information on the move.

        Returns:
            tuple:
            A tuple of ``(other_line, is_first_in_range)``.
        """
        if not line_num or line_num not in moved_meta:
            return None

        other_line_num = moved_meta[line_num]

        return (
            other_line_num,
            (line_num - 1 not in moved_meta or
             other_line_num != moved_meta[line_num - 1] + 1)
        )

    def _highlight_indentation(self, old_markup, new_markup, is_indent,
                               raw_indent_len, norm_indent_len_diff):
        """Highlights indentation in an HTML-formatted line.

        This will wrap the indentation in <span> tags, and format it in
        a way that makes it clear how many spaces or tabs were used.
        """
        if is_indent:
            new_markup = self._wrap_indentation_chars(
                'indent',
                new_markup,
                raw_indent_len,
                norm_indent_len_diff,
                self._serialize_indentation)
        else:
            old_markup = self._wrap_indentation_chars(
                'unindent',
                old_markup,
                raw_indent_len,
                norm_indent_len_diff,
                self._serialize_unindentation)

        return old_markup, new_markup

    def _wrap_indentation_chars(self, class_name, markup, raw_indent_len,
                                norm_indent_len_diff, serializer):
        """Wraps characters in a string with indentation markers.

        This will insert the indentation markers and its wrapper in the
        markup string. It's careful not to interfere with any tags that
        may be used to highlight that line.
        """
        start_pos = 0

        # There may be a tag wrapping this whitespace. If so, we need to
        # find where the actual whitespace chars begin.
        while markup[start_pos] == '<':
            end_tag_pos = markup.find('>', start_pos + 1)

            # We'll only reach this if some corrupted HTML was generated.
            # We want to know about that.
            assert end_tag_pos != -1

            start_pos = end_tag_pos + 1

        end_pos = start_pos + raw_indent_len

        indentation = markup[start_pos:end_pos]

        if indentation.strip() != '':
            # There may be other things in here we didn't expect. It's not
            # a straight sequence of characters. Give up on highlighting it.
            return markup

        serialized, remainder = serializer(indentation, norm_indent_len_diff)

        return '%s<span class="%s">%s</span>%s' % (
            markup[:start_pos],
            class_name,
            serialized,
            remainder + markup[end_pos:])

    def _serialize_indentation(self, chars, norm_indent_len_diff):
        """Serializes an indentation string into an HTML representation.

        This will show every space as ``>``, and every tab as ``------>|``.
        In the case of tabs, we display as much of it as possible (anchoring
        to the right-hand side) given the space we have within the tab
        boundary.

        Args:
            chars (unicode):
                The indentation characters to serialize.

            norm_indent_len_diff (int):
                The difference in indentation between the old and new lines.

        Returns:
            tuple:
            A 2-tuple containing:

            1. The serialized indentation string.
            2. The remaining indentation characters not serialized.
        """
        assert chars

        s = ''
        i = 0
        j = 0

        tab_size = self.diff_settings.tab_size
        assert tab_size

        for j, c in enumerate(chars):
            if c == ' ':
                s += '&gt;'
                i += 1
            elif c == '\t':
                # Build "------>|" with the room we have available.
                in_tab_pos = i % tab_size

                if in_tab_pos < tab_size - 1:
                    if in_tab_pos < tab_size - 2:
                        num_dashes = (tab_size - 2 - in_tab_pos)
                        s += '&mdash;' * num_dashes
                        i += num_dashes

                    s += '&gt;'
                    i += 1

                s += '|'
                i += 1

            if i >= norm_indent_len_diff:
                break

        return s, chars[j + 1:]

    def _serialize_unindentation(self, chars, norm_indent_len_diff):
        """Serialize an unindentation string into an HTML representation.

        This will show every space as ``<``, and every tab as ``|<------``.
        In the case of tabs, we display as much of it as possible (anchoring
        to the left-hand side) given the space we have within the tab
        boundary.

        Args:
            chars (unicode):
                The unindentation characters to serialize.

            norm_indent_len_diff (int):
                The difference in indentation between the old and new lines.

        Returns:
            tuple:
            A 2-tuple containing:

            1. The serialized unindentation string.
            2. The remaining unindentation characters not serialized.
        """
        assert chars

        s = ''
        i = 0
        j = 0

        tab_size = self.diff_settings.tab_size
        assert tab_size

        for j, c in enumerate(chars):
            if c == ' ':
                s += '&lt;'
                i += 1
            elif c == '\t':
                # Build "|<------" with the room we have available.
                in_tab_pos = i % tab_size

                s += '|'
                i += 1

                if in_tab_pos < tab_size - 1:
                    s += '&lt;'
                    i += 1

                    if in_tab_pos < tab_size - 2:
                        num_dashes = (tab_size - 2 - in_tab_pos)
                        s += '&mdash;' * num_dashes
                        i += num_dashes

            if i >= norm_indent_len_diff:
                break

        return s, chars[j + 1:]

    def _new_chunk(self, all_lines, start, end, collapsable=False,
                   tag='equal', meta=None):
        """Creates a chunk.

        A chunk represents an insert, delete, or equal region. The chunk
        contains a bunch of metadata for things like whether or not it's
        collapsable and any header information.

        This is what ends up being returned to the caller of this class.
        """
        if not meta:
            meta = {}

        left_headers = list(self._get_interesting_headers(
            all_lines, start, end - 1, False))
        right_headers = list(self._get_interesting_headers(
            all_lines, start, end - 1, True))

        meta['left_headers'] = left_headers
        meta['right_headers'] = right_headers

        lines = all_lines[start:end]
        num_lines = len(lines)

        compute_chunk_last_header(lines, num_lines, meta, self._last_header)

        if (collapsable and end < len(all_lines) and
                (self._last_header[0] or self._last_header[1])):
            meta['headers'] = list(self._last_header)

        chunk = {
            'index': self._chunk_index,
            'lines': lines,
            'numlines': num_lines,
            'change': tag,
            'collapsable': collapsable,
            'meta': meta,
        }

        self._chunk_index += 1

        return chunk

    def _get_interesting_headers(self, lines, start, end, is_modified_file):
        """Returns all headers for a region of a diff.

        This scans for all headers that fall within the specified range
        of the specified lines on both the original and modified files.
        """
        possible_functions = \
            self.differ.get_interesting_lines('header', is_modified_file)

        if not possible_functions:
            return

        try:
            if is_modified_file:
                last_index = self._last_header_index[1]
                i1 = lines[start][4]
                i2 = lines[end - 1][4]
            else:
                last_index = self._last_header_index[0]
                i1 = lines[start][1]
                i2 = lines[end - 1][1]
        except IndexError:
            return

        for i in range(last_index, len(possible_functions)):
            linenum, line = possible_functions[i]
            linenum += 1

            if i2 != '' and linenum > i2:
                break
            elif i1 != '' and linenum >= i1:
                last_index = i
                yield linenum, line

        if is_modified_file:
            self._last_header_index[1] = last_index
        else:
            self._last_header_index[0] = last_index

    def _apply_pygments(self, data, filename):
        """Apply Pygments syntax-highlighting to a file's contents.

        This will only apply syntax highlighting if a lexer is available and
        the file extension is not blacklisted.

        Args:
            data (unicode):
                The data to syntax highlight.

            filename (unicode):
                The name of the file. This is used to help determine a
                suitable lexer.

        Returns:
            list of unicode:
            A list of lines, all syntax-highlighted, if a lexer is found.
            If no lexer is available, this will return ``None``.
        """
        if filename.endswith(self.STYLED_EXT_BLACKLIST):
            return None

        custom_pygments_lexers = self.diff_settings.custom_pygments_lexers
        lexer = None

        for ext, lexer_name in custom_pygments_lexers.items():
            if ext and filename.endswith(ext):
                lexer_class = find_lexer_class(lexer_name)

                if lexer_class:
                    lexer = lexer_class(stripnl=False,
                                        encoding='utf-8')
                    break
                else:
                    logger.error(
                        'Pygments lexer "%s" for "%s" files in '
                        'Diff Viewer Settings was not found.',
                        lexer_name, ext)
        else:
            try:
                lexer = guess_lexer_for_filename(filename,
                                                 data,
                                                 stripnl=False,
                                                 encoding='utf-8')
            except pygments.util.ClassNotFound:
                return None

        lexer.add_filter('codetagify')

        return split_line_endings(
            highlight(data, lexer, NoWrapperHtmlFormatter()))


class DiffChunkGenerator(RawDiffChunkGenerator):
    """A generator for chunks for a FileDiff that can be used for rendering.

    Each chunk represents an insert, delete, replace, or equal section. It
    contains all the data needed to render the portion of the diff.

    There are three ways this can operate, based on provided parameters.

    1) filediff, no interfilediff -
       Returns chunks for a single filediff. This is the usual way
       people look at diffs in the diff viewer.

       In this mode, we get the original file based on the filediff
       and then patch it to get the resulting file.

       This is also used for interdiffs where the source revision
       has no equivalent modified file but the interdiff revision
       does. It's no different than a standard diff.

    2) filediff, interfilediff -
       Returns chunks showing the changes between a source filediff
       and the interdiff.

       This is the typical mode used when showing the changes
       between two diffs. It requires that the file is included in
       both revisions of a diffset.

    3) filediff, no interfilediff, force_interdiff -
       Returns chunks showing the changes between a source
       diff and an unmodified version of the diff.

       This is used when the source revision in the diffset contains
       modifications to a file which have then been reverted in the
       interdiff revision. We don't actually have an interfilediff
       in this case, so we have to indicate that we are indeed in
       interdiff mode so that we can special-case this and not
       grab a patched file for the interdiff version.
    """

    @deprecate_non_keyword_only_args(RemovedInReviewBoard80Warning)
    def __init__(
        self,
        request: HttpRequest,
        filediff: FileDiff,
        interfilediff: Optional[FileDiff] = None,
        force_interdiff: bool = False,
        base_filediff: Optional[FileDiff] = None,
        *,
        diff_settings: DiffSettings,
    ) -> None:
        """Initialize the DiffChunkGenerator.

        Version Changed:
            6.0:
            * Removed the old ``enable_syntax_highlighting`` argument.
            * Made ``diff_settings`` mandatory.

        Args:
            request (django.http.HttpRequest):
                The HTTP request from the client.

            filediff (reviewboard.diffviewer.models.filediff.FileDiff):
                The FileDiff to generate chunks for.

            interfilediff (reviewboard.diffviewer.models.filediff.FileDiff,
                           optional):
                If provided, the chunks will be generated for the differences
                between the result of applying ``filediff`` and the result of
                applying ``interfilediff``.

            force_interdiff (bool, optional):
                Whether or not to force an interdiff.

            base_filediff (reviewboard.diffviewer.models.filediff.FileDiff,
                           optional):
                An ancestor of ``filediff`` that we want to use as the base.
                Using this argument will result in the history between
                ``base_filediff`` and ``filediff`` being applied.

            diff_settings (reviewboard.diffviewer.settings.DiffSettings):
                The settings used to control the display of diffs.
        """
        assert filediff

        self.request = request
        self.diffset = filediff.diffset
        self.filediff = filediff
        self.interfilediff = interfilediff
        self.force_interdiff = force_interdiff
        self.repository = filediff.get_repository()
        self.tool = self.repository.get_scmtool()
        self.base_filediff = base_filediff

        if base_filediff:
            orig_filename = base_filediff.source_file
        else:
            orig_filename = filediff.source_file

        super().__init__(
            old=None,
            new=None,
            orig_filename=orig_filename,
            modified_filename=filediff.dest_file,
            encoding_list=self.repository.get_encoding_list(),
            diff_compat=filediff.diffset.diffcompat,
            diff_settings=diff_settings)

    def make_cache_key(self) -> str:
        """Return a new cache key for any generated chunks.

        Returns:
            str:
            The new cache key.
        """
        key: list[str] = []

        key.append('diff-sidebyside')

        if self.base_filediff is not None:
            key.append('base-%s' % self.base_filediff.pk)

        if not self.force_interdiff:
            key.append(str(self.filediff.pk))
        elif self.interfilediff:
            key.append('interdiff-%s-%s' % (self.filediff.pk,
                                            self.interfilediff.pk))
        else:
            key.append('interdiff-%s-none' % self.filediff.pk)

        key += [
            self.diff_settings.state_hash,
            get_language(),
        ]

        return '-'.join(key)

    def get_opcode_generator(self):
        """Return the DiffOpcodeGenerator used to generate diff opcodes."""
        diff = self.filediff.diff

        if self.interfilediff:
            interdiff = self.interfilediff.diff
        else:
            interdiff = None

        return get_diff_opcode_generator(self.differ, diff, interdiff,
                                         request=self.request,
                                         diff_settings=self.diff_settings)

    def get_chunks(self):
        """Return the chunks for the given diff information.

        If the file is binary or is an added or deleted 0-length file, or if
        the file has moved with no additional changes, then an empty list of
        chunks will be returned.

        If there are chunks already computed in the cache, they will be
        yielded. Otherwise, new chunks will be generated, stored in cache,
        and yielded.
        """
        counts = self.filediff.get_line_counts()

        if (self.filediff.binary or
            self.filediff.source_revision == '' or
            ((self.filediff.is_new or self.filediff.deleted or
              self.filediff.moved or self.filediff.copied) and
             counts['raw_insert_count'] == 0 and
             counts['raw_delete_count'] == 0)):
            return

        cache_key = self.make_cache_key()

        for chunk in super(DiffChunkGenerator, self).get_chunks(cache_key):
            yield chunk

    def get_chunks_uncached(self):
        """Yield the list of chunks, bypassing the cache."""
        base_filediff = self.base_filediff
        filediff = self.filediff
        interfilediff = self.interfilediff
        request = self.request

        old, new = get_original_and_patched_files(
            filediff=filediff,
            request=request)

        old_encoding_list = get_filediff_encodings(filediff)
        new_encoding_list = old_encoding_list

        if base_filediff is not None:
            # The diff is against a commit that:
            #
            # 1. Follows the first commit in a series (the first won't have
            #    a base_commit/base_filediff that can be looked up)
            #
            # 2. Follows a commit that modifies this file, or is the base
            #    commit that modifies this file.
            #
            # We'll be diffing against the patched version of this commit's
            # version of the file.
            old = get_original_file(filediff=base_filediff,
                                    request=request)
            old = get_patched_file(source_data=old,
                                   filediff=base_filediff,
                                   request=request)
            old_encoding_list = get_filediff_encodings(base_filediff)
        elif filediff.commit_id:
            # This diff is against a commit, but no previous FileDiff
            # modifying this file could be found. As per the above comment,
            # this could end up being the very first commit in a series, or
            # it might not have been modified in the base commit or any
            # previous commit.
            #
            # We'll need to fetch the first ancestor of this file in the
            # commit history, if we can find one. We'll base the "old" version
            # of the file on the original version of this commit, meaning that
            # this commit and all modifications since will be shown as "new".
            # Basically, viewing the upstream of the file, before any commits.
            #
            # This should be safe because, without a base_filediff, there
            # should be no older commit containing modifications that we want
            # to diff against. This would be the first one, and we're using
            # its upstream changes.
            ancestors = filediff.get_ancestors(minimal=True)

            if ancestors:
                ancestor_filediff = ancestors[0]
                old = get_original_file(filediff=ancestor_filediff,
                                        request=request)
                old_encoding_list = get_filediff_encodings(ancestor_filediff)

        # Check whether we have a SHA256 checksum first. They were introduced
        # in Review Board 4.0, long after SHA1 checksums. If we already have
        # a SHA256 checksum, then we'll also have a SHA1 checksum, but the
        # inverse is not true.
        if filediff.orig_sha256 is None:
            if filediff.orig_sha1 is None:
                filediff.extra_data.update({
                    'orig_sha1': self._get_sha1(old),
                    'patched_sha1': self._get_sha1(new),
                })

            filediff.extra_data.update({
                'orig_sha256': self._get_sha256(old),
                'patched_sha256': self._get_sha256(new),
            })
            filediff.save(update_fields=['extra_data'])

        if interfilediff:
            old = new
            old_encoding_list = new_encoding_list

            interdiff_orig = get_original_file(filediff=interfilediff,
                                               request=request)
            new = get_patched_file(source_data=interdiff_orig,
                                   filediff=interfilediff,
                                   request=request)
            new_encoding_list = get_filediff_encodings(interfilediff)

            # Check whether we have a SHA256 checksum first. They were
            # introduced in Review Board 4.0, long after SHA1 checksums. If we
            # already have a SHA256 checksum, then we'll also have a SHA1
            # checksum, but the inverse is not true.
            if interfilediff.orig_sha256 is None:
                if interfilediff.orig_sha1 is None:
                    interfilediff.extra_data.update({
                        'orig_sha1': self._get_sha1(interdiff_orig),
                        'patched_sha1': self._get_sha1(new),
                    })

                interfilediff.extra_data.update({
                    'orig_sha256': self._get_sha256(interdiff_orig),
                    'patched_sha256': self._get_sha256(new),
                })
                interfilediff.save(update_fields=['extra_data'])
        elif self.force_interdiff:
            # Basically, revert the change.
            old, new = new, old
            old_encoding_list, new_encoding_list = \
                new_encoding_list, old_encoding_list

        if interfilediff:
            log_timer = log_timed(
                "Generating diff chunks for interdiff ids %s-%s (%s)" %
                (filediff.id, interfilediff.id,
                 filediff.source_file),
                request=request)
        else:
            log_timer = log_timed(
                "Generating diff chunks for filediff id %s (%s)" %
                (filediff.id, filediff.source_file),
                request=request)

        for chunk in self.generate_chunks(old=old,
                                          new=new,
                                          old_encoding_list=old_encoding_list,
                                          new_encoding_list=new_encoding_list):
            yield chunk

        log_timer.done()

        if (not interfilediff and
            not self.base_filediff and
            not self.force_interdiff):
            insert_count = self.counts['insert']
            delete_count = self.counts['delete']
            replace_count = self.counts['replace']
            equal_count = self.counts['equal']

            filediff.set_line_counts(
                insert_count=insert_count,
                delete_count=delete_count,
                replace_count=replace_count,
                equal_count=equal_count,
                total_line_count=(insert_count + delete_count +
                                  replace_count + equal_count))

    def check_line_code_safety(self, orig_line, modified_line,
                               extra_state={}, **kwargs):
        """Check the safety of a line of code.

        This will run the original and modified line through all registered
        code safety checkers. If any checker produces warnings or errors,
        those will be associated with the line.

        This is a specialization of
        :py:meth:`RawDiffChunkGenerator.check_line_code_safety` that provides
        a ``repository`` key for each item to check, for use in the code
        safety checker.

        Version Added:
            5.0

        Args:
            orig_line (str):
                The original line to check.

            modified_line (str):
                The modiifed line to check.

            extra_state (dict, optional):
                Extra state to pass to the checker for the original or
                modified line content item. Used by subclasses to produce
                additional information that may be useful for some code safety
                checkers.

            **kwargs (dict, optional):
                Unused keyword arguments, for future expansion.

        Returns:
            list of tuple:
            A list of code safety results containing warnings or errors. Each
            item is a tuple containing:

            1. The registered checker ID.
            2. A dictionary with ``errors`` and/or ``warnings`` keys.
        """
        return super(DiffChunkGenerator, self).check_line_code_safety(
            orig_line=orig_line,
            modified_line=modified_line,
            extra_state=dict({
                'repository': self.repository,
            }, **extra_state),
            **kwargs)

    def normalize_path_for_display(self, filename):
        """Normalize a file path for display to the user.

        This uses the associated :py:class:`~reviewboard.scmtools.core.SCMTool`
        to normalize the filename.

        Args:
            filename (unicode):
                The filename to normalize.

        Returns:
            unicode:
            The normalized filename.
        """
        return self.tool.normalize_path_for_display(
            filename,
            extra_data=self.filediff.extra_data)

    def _get_sha1(self, content):
        """Return a SHA1 hash for the provided content.

        Args:
            content (bytes):
                The content to generate the hash for.

        Returns:
            unicode:
            The resulting hash.
        """
        return force_str(hashlib.sha1(content).hexdigest())

    def _get_sha256(self, content):
        """Return a SHA256 hash for the provided content.

        Args:
            content (bytes):
                The content to generate the hash for.

        Returns:
            unicode:
            The resulting hash.
        """
        return force_str(hashlib.sha256(content).hexdigest())


def compute_chunk_last_header(lines, numlines, meta, last_header=None):
    """Computes information for the displayed function/class headers.

    This will record the displayed headers, their line numbers, and expansion
    offsets relative to the header's collapsed line range.

    The last_header variable, if provided, will be modified, which is
    important when processing several chunks at once. It will also be
    returned as a convenience.
    """
    if last_header is None:
        last_header = [None, None]

    line = lines[0]

    for i, (linenum, header_key) in enumerate([(line[1], 'left_headers'),
                                               (line[4], 'right_headers')]):
        headers = meta[header_key]

        if headers:
            header = headers[-1]
            last_header[i] = {
                'line': header[0],
                'text': header[1].strip(),
            }

    return last_header


_generator: type[DiffChunkGenerator] = DiffChunkGenerator


def get_diff_chunk_generator_class() -> type[DiffChunkGenerator]:
    """Return the DiffChunkGenerator class used for generating chunks.

    Returns:
        type:
        The class for the DiffChunkGenerator to use.
    """
    return _generator


def set_diff_chunk_generator_class(
    renderer: type[DiffChunkGenerator],
) -> None:
    """Set the DiffChunkGenerator class used for generating chunks.

    Args:
        renderer (type):
            The class for the DiffChunkGenerator to use.
    """
    assert renderer

    globals()['_generator'] = renderer


def get_diff_chunk_generator(*args, **kwargs) -> DiffChunkGenerator:
    """Return a DiffChunkGenerator instance used for generating chunks.

    Args:
        *args (tuple):
            Positional arguments to pass to the DiffChunkGenerator.

        **kwargs (dict):
            Keyword arguments to pass to the DiffChunkGenerator.

    Returns:
        DiffChunkGenerator:
        The chunk generator instance.
    """
    return _generator(*args, **kwargs)
