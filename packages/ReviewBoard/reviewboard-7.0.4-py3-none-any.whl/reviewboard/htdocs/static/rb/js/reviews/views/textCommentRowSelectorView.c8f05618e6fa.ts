/**
 * Provides multi-line commenting capabilities for a diff.
 */

import {
    type EventsHash,
    BaseView,
    spina,
} from '@beanbag/spina';

import { type AbstractReviewableView } from './abstractReviewableView';


/**
 * Options for the TextCommentRowSelector view.
 *
 * Version Added:
 *     7.0
 */
export interface TextCommentRowSelectorOptions {
    /** The view for the reviewable object. */
    reviewableView: AbstractReviewableView;
}


/**
 * Provides multi-line commenting capabilities for a diff.
 *
 * This tacks on commenting capabilities onto a DiffReviewableView's
 * element. It listens for mouse events that begin/end the creation of
 * a new comment.
 */
@spina
export class TextCommentRowSelector extends BaseView<
    undefined,
    HTMLTableElement,
    TextCommentRowSelectorOptions
> {
    static ghostCommentFlagTemplate = dedent`
        <span class="commentflag ghost-commentflag">
         <span class="commentflag-shadow"></span>
         <span class="commentflag-inner"></span>
        </span>
    `;

    static events: EventsHash = {
        'copy': '_onCopy',
        'mousedown': '_onMouseDown',
        'mouseout': '_onMouseOut',
        'mouseover': '_onMouseOver',
        'mouseup': '_onMouseUp',
        'touchcancel': '_onTouchCancel',
        'touchend': '_onTouchEnd',
        'touchmove': '_onTouchMove',
        'touchstart': '_onTouchStart',
    };

    /**********************
     * Instance variables *
     **********************/

    /** Options for the view. */
    options: TextCommentRowSelectorOptions;

    /**
     * The row element of the beginning of the selection.
     *
     * This is public for consumption in unit tests.
     */
    _$begin: JQuery<HTMLTableRowElement> = null;

    /**
     * The row element of the end of the selection.
     *
     * This is public for consumption in unit tests.
     */
    _$end: JQuery<HTMLTableRowElement> = null;

    /**
     * The row index of the row last moused over/touched.
     *
     * This is public for consumption in unit tests.
     */
    _lastSeenIndex = 0;

    /**
     * The temporary comment flag.
     *
     * This is public for consumption in unit tests.
     */
    _$ghostCommentFlag: JQuery = null;

    /**
     * The line number of the beginning of the selection.
     *
     * This is public for consumption in unit tests.
     */
    _beginLineNum = 0;

    /**
     * The line number of the end of the selection.
     *
     * This is public for consumption in unit tests.
     */
    _endLineNum = 0;

    /** The table cell that the ghost flag is on. */
    #$ghostCommentFlagCell: JQuery = null;

    /** The type of newline character or sequence used in the file. */
    #newlineChar: string = null;

    /** The index of the currently selected cell. */
    #selectedCellIndex: number = null;

    /**
     * The class applied to elements while selecting text.
     *
     * This is used to keep the selection within one column.
     */
    #selectionClass: string = null;

    /** Whether the browser supports setting the clipboard contents. */
    #supportsSetClipboard: boolean;

    /**
     * Initialize the commenting selector.
     *
     * Args:
     *     options (TextCommentRowSelectorOptions):
     *         Options for initializing the view.
     */
    initialize(
        options: TextCommentRowSelectorOptions,
    ) {
        this.options = options;

        /*
         * Support setting the clipboard only if we have the necessary
         * functions. This may still be turned off later if we can't
         * actually set the data.
         */
        this.#supportsSetClipboard = (
            window.getSelection !== undefined &&
            window.Range !== undefined &&
            window.Range.prototype.cloneContents !== undefined);
    }

    /**
     * Remove the selector from the DOM.
     *
     * Returns:
     *     TextCommentRowSelector:
     *     This object, for chaining.
     */
    remove(): this {
        this._$ghostCommentFlag.remove();

        return super.remove();
    }

    /**
     * Render the selector.
     */
    protected onInitialRender() {
        this._$ghostCommentFlag =
            $(TextCommentRowSelector.ghostCommentFlagTemplate)
            .on({
                mousedown: this._onMouseDown.bind(this),
                mouseout: this._onMouseOut.bind(this),
                mouseover: this._onMouseOver.bind(this),
                mouseup: this._onMouseUp.bind(this),
            })
            .hide()
            .appendTo('body');
    }

    /**
     * Create a comment for a chunk of a diff.
     *
     * Args:
     *     beginLineNum (number):
     *         The first line number of the range being commented upon.
     *
     *     endLineNum (number):
     *         The last line number of the range being commented upon.
     *
     *     beginNode (Element):
     *         The element for the first row of the range being commented on.
     *
     *     endNode (Element):
     *         The element of the last row of the range being commented on.
     */
    createComment(
        beginLineNum: number,
        endLineNum: number,
        beginNode: HTMLElement,
        endNode: HTMLElement,
    ) {
        this._beginLineNum = beginLineNum;
        this._endLineNum = endLineNum;

        let $node = this._getActualLineNumCell($(beginNode)).parent();
        this._$begin = $node as JQuery<HTMLTableRowElement>;

        $node = this._getActualLineNumCell($(endNode)).parent();
        this._$end = $node as JQuery<HTMLTableRowElement>;

        if (this._isLineNumCell(endNode)) {
            this._end(this._$end);
        }

        this._reset();
    }

    /**
     * Return the beginning and end rows for a given line number range.
     *
     * Args:
     *      beginLineNum (number):
     *         The first line number of the range.
     *
     *      endLineNum (number):
     *         The last line number of the range.
     *
     *      minRowIndex (number):
     *         A minimum row index to constrain the search to.
     *
     *         No rows with indices less than this will be searched.
     *
     * Returns:
     *     array of Element:
     *     If the row corresponding to ``beginLineNum`` cannot be found, the
     *     return value with be ``null``.
     *
     *     Otherwise, this will be a 2 element array containing:
     *
     *     * The :js:class:`Element` for the row corresponding to
     *       ``beginLineNum``.
     *     * The :js:class:`Element` for the row corresponding to
     *       ``endLineNum``, or ``null`` if it cannot be found.
     */
    getRowsForRange(
        beginLineNum: number,
        endLineNum?: number,
        minRowIndex?: number,
    ): [Element, Element] {
        const beginRowEl = this.findLineNumRow(beginLineNum, minRowIndex);

        if (beginRowEl) {
            const rowIndex = beginRowEl.rowIndex;
            const endRowEl = (
                endLineNum === beginLineNum
                ? beginRowEl
                : this.findLineNumRow(
                    endLineNum,
                    rowIndex,
                    rowIndex + endLineNum - beginLineNum)
            );

            return [beginRowEl, endRowEl];
        } else {
            return null;
        }
    }

    /**
     * Find the row in a table matching the specified line number.
     *
     * This will perform a binary search of the lines trying to find
     * the matching line number. It will then return the row element,
     * if found.
     *
     * Args:
     *     lineNum (number):
     *         The line number to find.
     *
     *     startRow (number):
     *         The index of the row to start the search at.
     *
     *     endRow (number):
     *         The index of the row to end the sarch at.
     */
    findLineNumRow(
        lineNum: number,
        startRow?: number,
        endRow?: number,
    ): HTMLTableRowElement {
        const table = this.el;
        const rowOffset = 1; // Get past the headers.
        let row = null;

        if (table.rows.length - rowOffset > lineNum) {
            row = table.rows[rowOffset + lineNum];

            // Account for the "x lines hidden" row.
            if (row && this.getLineNum(row) === lineNum) {
                return row;
            }
        }

        if (startRow) {
            // startRow already includes the offset, so we need to remove it.
            startRow -= rowOffset;
        }

        let low = startRow || 0;
        let high = Math.min(endRow || table.rows.length, table.rows.length);

        if (endRow !== undefined && endRow < table.rows.length) {
            // See if we got lucky and found it in the last row.
            if (this.getLineNum(table.rows[endRow]) === lineNum) {
                return table.rows[endRow];
            }
        } else if (row !== null) {
            /*
             * We collapsed the rows (unless someone mucked with the DB),
             * so the desired row is less than the row number retrieved.
             */
            high = Math.min(high, rowOffset + lineNum);
        }

        // Binary search for this cell.
        for (let i = Math.round((low + high) / 2); low < high - 1;) {
            row = table.rows[rowOffset + i];

            if (!row) {
                // This should not happen, unless we miscomputed high.
                high--;

                /*
                 * This won't do much if low + high is odd, but we'll catch
                 * up on the next iteration.
                 */
                i = Math.round((low + high) / 2);
                continue;
            }

            let value = this.getLineNum(row);

            if (!value) {
                /*
                 * Bad luck, let's look around.
                 *
                 * We'd expect to find a value on the first try, but the
                 * following makes sure we explore all rows.
                 */
                let found = false;

                for (let j = 1; j <= (high - low) / 2; j++) {
                    row = table.rows[rowOffset + i + j];

                    if (row && this.getLineNum(row)) {
                        i = i + j;
                        found = true;
                        break;
                    } else {
                        row = table.rows[rowOffset + i - j];

                        if (row && this.getLineNum(row)) {
                            i = i - j;
                            found = true;
                            break;
                        }
                    }
                }

                if (found) {
                    value = this.getLineNum(row);
                } else {
                    return null;
                }
            }

            // See if we can use simple math to find the row quickly.
            const guessRowNum = lineNum - value + rowOffset + i;

            if (guessRowNum >= 0 && guessRowNum < table.rows.length) {
                const guessRow = table.rows[guessRowNum];

                if (guessRow && this.getLineNum(guessRow) === lineNum) {
                    // We found it using maths!
                    return guessRow;
                }
            }

            const oldHigh = high;
            const oldLow = low;

            if (value > lineNum) {
                high = i;
            } else if (value < lineNum) {
                low = i;
            } else {
                return row;
            }

            /*
             * Make sure we don't get stuck in an infinite loop. This can
             * happen when a comment is placed in a line that isn't being
             * shown.
             */
            if (oldHigh === high && oldLow === low) {
                break;
            }

            i = Math.round((low + high) / 2);
        }

        // Well.. damn. Ignore this then.
        return null;
    }

    /**
     * Begin the selection of line numbers.
     *
     * Args:
     *     $row (jQuery):
     *         The selected row.
     */
    _begin($row: JQuery<HTMLTableRowElement>) {
        const lineNum = this.getLineNum($row[0]);

        this._$begin = $row;
        this._$end = $row;
        this._beginLineNum = lineNum;
        this._endLineNum = lineNum;
        this._lastSeenIndex = $row[0].rowIndex;

        $row.addClass('selected');
        this.$el.disableSelection();
    }

    /**
     * Finalize the selection and pop up a comment dialog.
     *
     * Args:
     *     $row (jQuery):
     *         The selected row.
     */
    _end($row: JQuery<HTMLTableRowElement>) {
        if (this._beginLineNum === this._endLineNum) {
            /* See if we have a comment flag on the selected row. */
            const $commentFlag = $row.find('.commentflag');

            if ($commentFlag.length === 1) {
                $commentFlag.click();

                return;
            }
        }

        /*
         * Selection was finalized. Create the comment block
         * and show the comment dialog.
         */
        this.options.reviewableView.createAndEditCommentBlock({
            $beginRow: this._$begin,
            $endRow: this._$end,
            beginLineNum: this._beginLineNum,
            endLineNum: this._endLineNum,
        });
    }

    /**
     * Add a row to the selection.
     *
     * This will update the selection range and mark the rows as selected.
     *
     * This row is assumed to be the most recently selected row, and
     * will mark the new beginning or end of the selection.
     *
     * Args:
     *     $row (jQuery):
     *         The row to add to the selection.
     */
    _addRow($row: JQuery<HTMLTableRowElement>) {
        /* We have an active selection. */
        const lineNum = this.getLineNum($row[0]);

        if (lineNum < this._beginLineNum) {
            this._$begin = $row;
            this._beginLineNum = lineNum;
        } else if (lineNum > this._beginLineNum) {
            this._$end = $row;
            this._endLineNum = lineNum;
        }

        const min = Math.min(this._lastSeenIndex, $row[0].rowIndex);
        const max = Math.max(this._lastSeenIndex, $row[0].rowIndex);

        for (let i = min; i <= max; i++) {
            $(this.el.rows[i]).addClass('selected');
        }

        this._lastSeenIndex = $row[0].rowIndex;
    }

    /**
     * Highlight a row.
     *
     * This will highlight a row and show a ghost comment flag. This is done
     * when the mouse hovers over the row.
     *
     * Args:
     *     $row (jQuery):
     *         The row to highlight.
     */
    _highlightRow($row: JQuery<HTMLTableRowElement>) {
        const $lineNumCell = $($row[0].cells[0]);

        /* See if we have a comment flag in here. */
        if ($lineNumCell.find('.commentflag').length === 0) {
            this._$ghostCommentFlag
                .css('top', $row.offset().top - 1)
                .show()
                .parent()
                    .removeClass('selected');
            this.#$ghostCommentFlagCell = $lineNumCell;
        }

        $row.addClass('selected');
    }

    /**
     * Remove old rows from the selection based on the most recent selection.
     *
     * Args:
     *     $row (jQuery):
     *         The most recent row selection.
     */
    _removeOldRows($row: JQuery<HTMLTableRowElement>) {
        const destRowIndex = $row[0].rowIndex;

        if (destRowIndex >= this._$begin[0].rowIndex) {
            if (this._lastSeenIndex !== this._$end[0].rowIndex &&
                this._lastSeenIndex < destRowIndex) {
                /*
                 * We're removing from the top of the range. The beginning
                 * location will need to be moved.
                 */
                this._removeSelectionClasses(this._lastSeenIndex,
                                             destRowIndex);
                this._$begin = $row;
                this._beginLineNum = this.getLineNum($row[0]);
            } else {
                /*
                 * We're removing from the bottom of the selection. The end
                 * location will need to be moved.
                 */
                this._removeSelectionClasses(destRowIndex,
                                             this._lastSeenIndex);

                this._$end = $row;
                this._endLineNum = this.getLineNum($row[0]);
            }

            this._lastSeenIndex = destRowIndex;
        }
    }

    /**
     * Reset the selection information.
     */
    _reset() {
        if (this._$begin) {
            /* Reset the selection. */
            this._removeSelectionClasses(this._$begin[0].rowIndex,
                                         this._$end[0].rowIndex);

            this._$begin = null;
            this._$end = null;
            this._beginLineNum = 0;
            this._endLineNum = 0;
            this._lastSeenIndex = 0;
        }

        this.#$ghostCommentFlagCell = null;

        /* Re-enable text selection on IE */
        this.$el.enableSelection();
    }

    /**
     * Remove the selection classes on a range of rows.
     *
     * Args:
     *     startRowIndex (number):
     *         The row index to start removing selection classes at.
     *
     *     endRowIndex (number):
     *         The row index to stop removing selection classes at.
     */
    _removeSelectionClasses(
        startRowIndex: number,
        endRowIndex: number,
    ) {
        for (let i = startRowIndex; i <= endRowIndex; i++) {
            $(this.el.rows[i]).removeClass('selected');
        }
    }

    /**
     * Return whether a particular cell is a line number cell.
     *
     * Args:
     *     cell (Element):
     *         The cell to inspect.
     */
    _isLineNumCell(cell: HTMLElement) {
        return cell.tagName === 'TH' &&
               (cell.parentNode as HTMLElement).getAttribute('line');
    }

    /**
     * Return the actual cell node in the table.
     *
     * If the node specified is the ghost flag, this will return the
     * cell the ghost flag represents.
     *
     * If this is a comment flag inside a cell, this will return the
     * comment flag's parent cell.
     *
     * If this is a code warning indicator, this will return its parent cell.
     *
     * Args:
     *     $node (jQuery):
     *         A node in the table.
     *
     * Returns:
     *     jQuery:
     *     The row.
     */
    _getActualLineNumCell(
        $node: JQuery,
    ): JQuery {
        if ($node.hasClass('commentflag')) {
            if ($node[0] === this._$ghostCommentFlag[0]) {
                return this.#$ghostCommentFlagCell;
            } else {
                return $node.parent();
            }
        } else if ($node.hasClass('fa-warning')) {
            return $node.parent();
        }

        return $node;
    }

    /**
     * Handler for when the user copies text in a column.
     *
     * This will begin the process of capturing any selected text in
     * a column to the clipboard in a cross-browser way.
     *
     * Args:
     *     e (JQuery.TriggeredEvent):
     *         The clipboard event.
     */
    _onCopy(e: JQuery.TriggeredEvent) {
        const clipboardEvent = e.originalEvent as ClipboardEvent;
        const clipboardData = clipboardEvent.clipboardData;

        if (clipboardData && this.#supportsSetClipboard &&
            this._copySelectionToClipboard(clipboardData)) {
            /*
             * Prevent the default copy action from occurring.
             */
            e.preventDefault();
            e.stopPropagation();
        }
    }

    /**
     * Find the pre tags and push them into the result array.
     *
     * Args:
     *     result (array):
     *         The array for which all matching ``<pre>`` elements will be
     *         pushed into.
     *
     *     parentEl (Element):
     *         The parent element to search under.
     *
     *     tdClass (string):
     *         The class of ``<td>`` elements to search.
     *
     *     excludeTBodyClass (string):
     *         The class of the ``<tbody>`` to exclude.
     */
    _findPreTags(
        result: Element[],
        parentEl: Element | DocumentFragment,
        tdClass: string,
        excludeTBodyClass: string,
    ) {
        for (let i = 0; i < parentEl.children.length; i++) {
            const node = parentEl.children[i];

            if (node.nodeType === Node.ELEMENT_NODE) {
                if (node.tagName === 'PRE') {
                    result.push(node);
                } else if ((node.tagName !== 'TD' ||
                            $(node).hasClass(tdClass)) &&
                           (node.tagName !== 'TBODY' ||
                            !$(node).hasClass(excludeTBodyClass))) {
                    this._findPreTags(result, node, tdClass,
                                      excludeTBodyClass);
                }
            }
        }
    }

    /**
     * Copy the current selection to the clipboard.
     *
     * This will locate the desired text to copy, based on the selection
     * range within the column where selection started. It will then
     * extract the code from the ``<pre>`` tags and build a string to set in
     * the clipboard.
     *
     * This requires support in the browser for setting clipboard contents
     * on copy. If the browser does not support this, the default behavior
     * will be used.
     *
     * Args:
     *     clipboardData (DataTransfer):
     *         The clipboard data from the copy event.
     *
     * Returns:
     *     boolean:
     *     Whether or not we successfully set the clipboard data.
     */
    _copySelectionToClipboard(
        clipboardData: DataTransfer,
    ): boolean {
        let excludeTBodyClass;
        let tdClass;

        if (this.#newlineChar === null) {
            /*
             * Figure out what newline character should be used on this
             * platform. Ideally, we'd determine this from some browser
             * behavior, but it doesn't seem that can be consistently
             * determined.
             */
            if (navigator.appVersion.includes('Win')) {
                this.#newlineChar = '\r\n';
            } else {
                this.#newlineChar = '\n';
            }
        }

        if (this.#selectedCellIndex === 3 || this.$el.hasClass('newfile')) {
            tdClass = 'r';
            excludeTBodyClass = 'delete';
        } else {
            tdClass = 'l';
            excludeTBodyClass = 'insert';
        }

        const sel = window.getSelection();
        const textParts = [];

        for (let i = 0; i < sel.rangeCount; i++) {
            const range = sel.getRangeAt(i);

            if (range.collapsed) {
                continue;
            }

            const nodes = [];
            const doc = range.cloneContents();
            this._findPreTags(nodes, doc, tdClass, excludeTBodyClass);

            if (nodes.length > 0) {
                /*
                 * The selection spans multiple rows. Find the blocks of text
                 * in the column we want, and copy those to the clipboard.
                 */
                for (let j = 0; j < nodes.length; j++) {
                    textParts.push(nodes[j].textContent);
                }
            } else {
                /*
                 * If we're here, then we selected a subset of a single
                 * cell. There was only one Range, and no <pre> tags as
                 * part of it. We can just grab the text of the document.
                 *
                 * (We don't really need to break here, but we're going to
                 * in order to be clear that we're completely done.)
                 */
                textParts.push($(doc).text());
                break;
            }
        }

        try {
            clipboardData.setData('text', textParts.join(this.#newlineChar));
        } catch (e) {
            /* Let the native behavior take over. */
            this.#supportsSetClipboard = false;

            return false;
        }

        return true;
    }

    /**
     * Handle the mouse down event, which begins selection for comments.
     *
     * Args:
     *     e (jQuery.Event):
     *         The ``mousedown`` event.
     */
    _onMouseDown(e: Event) {
        if (this.#selectionClass) {
            this.$el.removeClass(this.#selectionClass);
        }

        const node = this.#$ghostCommentFlagCell
                   ? this.#$ghostCommentFlagCell[0]
                   : e.target as HTMLElement;

        if (this._isLineNumCell(node)) {
            this._begin($(node.parentNode) as JQuery<HTMLTableRowElement>);
        } else {
            const $node =
                (node.tagName === 'TD'
                    ? $(node)
                    : $(node).parentsUntil('tr', 'td')
                ) as JQuery<HTMLTableDataCellElement>;

            if ($node.length > 0) {
                this.#selectionClass = 'selecting-col-' + $node[0].cellIndex;
                this.#selectedCellIndex = $node[0].cellIndex;
                this.$el.addClass(this.#selectionClass);
            }
        }
    }

    /**
     * Handle the mouse up event.
     *
     * This will finalize the selection of a range of lines, creating a new
     * comment block and displaying the dialog.
     *
     * Args:
     *     e (jQuery.Event):
     *         The ``mouseup`` event.
     */
    _onMouseUp(e: Event) {
        const node = this.#$ghostCommentFlagCell
                   ? this.#$ghostCommentFlagCell[0]
                   : e.target as HTMLElement;

        if (this._isLineNumCell(node)) {
            const $node = this._getActualLineNumCell(
                $(node).parent() as JQuery<HTMLElement>);

            this._end($node as JQuery<HTMLTableRowElement>);

            e.stopImmediatePropagation();
        }

        this._reset();
    }

    /**
     * Handle the mouse over event.
     *
     * This will update the selection, if there is one, to include this row
     * in the range, and set the "selected" class on the new row.
     *
     * Args:
     *     e (jQuery.Event):
     *         The ``mouseover`` event.
     */
    _onMouseOver(e: Event) {
        const $node = this._getActualLineNumCell(
            $(e.target) as JQuery<HTMLElement>);
        const $row = $node.parent() as JQuery<HTMLTableRowElement>;

        if (this._isLineNumCell($node[0])) {
            if (this._$begin) {
                this._addRow($row);
            } else {
                this._highlightRow($row);
            }
        } else if (this.#$ghostCommentFlagCell &&
                   $node[0] !== this.#$ghostCommentFlagCell[0]) {
            $row.removeClass('selected');
        }
    }

    /**
     * Handle the mouse out event.
     *
     * This will remove any lines outside the new range from the selection.
     *
     * Args:
     *     e (jQuery.Event):
     *         The ``mouseout`` event.
     */
    _onMouseOut(e: MouseEvent) {
        const relTarget = e.relatedTarget as HTMLElement;

        if (relTarget !== this._$ghostCommentFlag[0]) {
            this._$ghostCommentFlag.hide();
            this.#$ghostCommentFlagCell = null;
        }

        const $node = this._getActualLineNumCell(
            $(e.target) as JQuery<HTMLElement>);

        if (this._$begin) {
            if (relTarget && this._isLineNumCell(relTarget)) {
                this._removeOldRows(
                    $(relTarget.parentNode) as JQuery<HTMLTableRowElement>);
            }
        } else if ($node && this._isLineNumCell($node[0])) {
            /*
             * Opera seems to generate lots of spurious mouse-out
             * events, which would cause us to get all sorts of
             * errors in here unless we check the target above.
             */
            $node.parent().removeClass('selected');
        }
    }

    /**
     * Handle the beginning of a touch event.
     *
     * If the user is touching a line number, then this will begin tracking
     * a new comment selection state, allowing them to either open an existing
     * comment or create a new one.
     *
     * Args:
     *     e (jQuery.Event):
     *         The ``touchstart`` event.
     */
    _onTouchStart(e: JQuery.TriggeredEvent) {
        const touchEvent = e.originalEvent as TouchEvent;
        const firstTouch = touchEvent.targetTouches[0];

        const $node = this._getActualLineNumCell(
            $(firstTouch.target) as JQuery<HTMLElement>);

        if ($node !== null && this._isLineNumCell($node[0])) {
            e.preventDefault();
            this._begin($node.parent() as JQuery<HTMLTableRowElement>);
        }
    }

    /**
     * Handle the end of a touch event.
     *
     * If the user ended on a line number, then this will either open an
     * existing comment (if the result was a single-line selection on the
     * line of an existing comment) or create a new comment spanning all
     * selected lines.
     *
     * If they ended outside of the line numbers column, then this will
     * simply reset the selection.
     *
     * Args:
     *     e (jQuery.Event):
     *         The ``touchend`` event.
     */
    _onTouchEnd(e: JQuery.TriggeredEvent) {
        const touchEvent = e.originalEvent as TouchEvent;
        const firstTouch = touchEvent.changedTouches[0];
        const target = document.elementFromPoint(firstTouch.clientX,
                                                 firstTouch.clientY);
        const $node = this._getActualLineNumCell(
            $(target) as JQuery<HTMLElement>);

        if ($node !== null && this._isLineNumCell($node[0])) {
            e.preventDefault();
            this._end($node.parent() as JQuery<HTMLTableRowElement>);
        }

        this._reset();
    }

    /**
     * Handle touch movement events.
     *
     * If selecting up or down line numbers, this will update the selection
     * to span all rows from the original line number first touched and the
     * line number currently being touched.
     *
     * Args:
     *     e (jQuery.Event):
     *         The ``touchmove`` event.
     */
    _onTouchMove(e: JQuery.TriggeredEvent) {
        const touchEvent = e.originalEvent as TouchEvent;
        const firstTouch = touchEvent.targetTouches[0];
        const target = document.elementFromPoint(firstTouch.clientX,
                                                 firstTouch.clientY);
        const $node = this._getActualLineNumCell(
            $(target) as JQuery<HTMLElement>);

        if ($node !== null) {
            const $row = $node.parent() as JQuery<HTMLTableRowElement>;

            if (this._lastSeenIndex !== $row[0].rowIndex &&
                this._isLineNumCell($node[0])) {
                e.preventDefault();

                this._removeOldRows($row);
                this._addRow($row);
            }
        }
    }

    /**
     * Handle touch cancellation events.
     *
     * This resets the line number selection. The user will need to begin the
     * selection again.
     */
    _onTouchCancel() {
        this._reset();
    }

    /**
     * Return the line number for a row.
     *
     * Args:
     *     row (Element):
     *         The element to get the line number for.
     *
     * Returns:
     *     number:
     *     The line number.
     */
    getLineNum(
        row: Element,
    ): number {
        return parseInt(row.getAttribute('line'), 10);
    }
}
