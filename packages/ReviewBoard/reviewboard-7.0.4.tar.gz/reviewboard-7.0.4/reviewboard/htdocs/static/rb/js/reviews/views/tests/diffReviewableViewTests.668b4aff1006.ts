import { suite } from '@beanbag/jasmine-suites';
import {
    afterEach,
    beforeEach,
    describe,
    expect,
    it,
    jasmine,
    spyOn,
    xit,
} from 'jasmine-core';

import { ReviewRequest } from 'reviewboard/common';
import {
    DiffFile,
    DiffReviewable,
    DiffReviewableView,
} from 'reviewboard/reviews';


suite('rb/diffviewer/views/DiffReviewableView', function() {
    const diffTableTemplate = _.template(dedent`
        <table class="sidebyside">
         <thead>
          <tr>
           <th colspan="2">
            <a name="1" class="file-anchor"></a> my-file.txt
           </th>
          </tr>
          <tr>
           <th class="rev">Revision 1</th>
           <th class="rev">Revision 2</th>
          </tr>
         </thead>
         <% _.each(chunks, function(chunk, index) { %>
          <% if (chunk.type === "collapsed") { %>
           <tbody class="diff-header">
            <tr>
             <th>
              <a href="#" class="diff-expand-btn tests-expand-above"
                 data-chunk-index="<%= index %>"
                 data-lines-of-context="20,0"><img></a>
             </th>
             <th colspan="3">
              <a href="#" class="diff-expand-btn tests-expand-chunk"
                 data-chunk-index="<%= index %>"><img> Expand</a>
             </th>
            </tr>
            <tr>
             <th>
              <a href="#" class="diff-expand-btn tests-expand-below"
                 data-chunk-index="<%= index %>"
                 data-lines-of-context="0,20"><img></a>
             </th>
             <th colspan="3">
              <a href="#" class="diff-expand-btn tests-expand-header"
                 data-chunk-index="<%= index %>"
                 data-lines-of-context="0,<%= chunk.expandHeaderLines %>">
               <img> <code>Some Function</code>
              </a>
             </th>
            </tr>
           </tbody>
          <% } else { %>
           <tbody class="<%= chunk.type %>
                         <% if (chunk.expanded) { %>loaded<% } %>
                         <%= chunk.extraClass || "" %>"
                  id="chunk0.<%= index %>">
            <% for (var i = 0; i < chunk.numRows; i++) { %>
             <tr line="<%= i + chunk.startRow %>">
              <th></th>
              <td>
               <% if (chunk.expanded && i === 0) { %>
                <div class="collapse-floater">
                 <div class="rb-c-diff-collapse-button"
                      data-chunk-index="<%= index %>"
                      data-lines-of-context="0"></div>
                </div>
               <% } %>
              </td>
              <th></th>
              <td></td>
             </tr>
            <% } %>
           </tbody>
          <% } %>
         <% }); %>
        </table>
    `);

    const fileAlertHTMLTemplate = _.template(dedent`
        <tbody class="rb-c-diff-file-notice">
         <tr>
          <td colspan="4">
           <div class="rb-c-alert -is-warning">
            <div class="rb-c-alert__content">
             <%= contentHTML %>
            </div>
           </div>
          </td>
         </tr>
        </tbody>
    `);

    let reviewRequest;
    let $container;
    let view;

    beforeEach(function() {
        $container = $('<div>').appendTo($testsScratch);

        reviewRequest = new ReviewRequest();
    });

    afterEach(function() {
        view.remove();
    });

    describe('CommentRowSelector', function() {
        let selector;
        let $rows;

        beforeEach(function() {
            view = new DiffReviewableView({
                el: $(diffTableTemplate({
                    chunks: [
                        {
                            numRows: 5,
                            startRow: 1,
                            type: 'equal',
                        },
                        {
                            numRows: 10,
                            startRow: 6,
                            type: 'delete',
                        },
                    ],
                })),
                model: new DiffReviewable({
                    reviewRequest: reviewRequest,
                }),
            });
            view.render().$el.appendTo($container);

            selector = view._selector;
            $rows = view.$el.find('tbody tr');
        });

        describe('Selecting range', function() {
            let $startRow;
            let startCell;

            beforeEach(function() {
                $startRow = $rows.eq(4);
                startCell = $startRow[0].cells[0];
            });

            it('Beginning selection', function() {
                selector._onMouseOver({
                    target: startCell,
                });

                selector._onMouseDown({
                    target: startCell,
                });

                expect($startRow.hasClass('selected')).toBe(true);
                expect(selector._$begin[0]).toBe($startRow[0]);
                expect(selector._$end[0]).toBe($startRow[0]);
                expect(selector._beginLineNum).toBe(5);
                expect(selector._endLineNum).toBe(5);
                expect(selector._lastSeenIndex).toBe($startRow[0].rowIndex);
            });

            describe('Adding rows to selection', function() {
                it('Above', function() {
                    const $prevRow = $rows.eq(3);

                    selector._onMouseOver({
                        target: startCell,
                    });

                    selector._onMouseDown({
                        target: startCell,
                    });

                    selector._onMouseOver({
                        target: $prevRow[0].cells[0],
                    });

                    expect($startRow.hasClass('selected')).toBe(true);
                    expect($prevRow.hasClass('selected')).toBe(true);
                    expect(selector._$begin[0]).toBe($prevRow[0]);
                    expect(selector._$end[0]).toBe($startRow[0]);
                    expect(selector._beginLineNum).toBe(4);
                    expect(selector._endLineNum).toBe(5);
                    expect(selector._lastSeenIndex).toBe($prevRow[0].rowIndex);
                });

                it('Below', function() {
                    const $nextRow = $rows.eq(5);

                    selector._onMouseOver({
                        target: startCell,
                    });

                    selector._onMouseDown({
                        target: startCell,
                    });

                    selector._onMouseOver({
                        target: $nextRow[0].cells[0],
                    });

                    expect($startRow.hasClass('selected')).toBe(true);
                    expect($nextRow.hasClass('selected')).toBe(true);
                    expect(selector._$begin[0]).toBe($startRow[0]);
                    expect(selector._$end[0]).toBe($nextRow[0]);
                    expect(selector._beginLineNum).toBe(5);
                    expect(selector._endLineNum).toBe(6);
                    expect(selector._lastSeenIndex).toBe($nextRow[0].rowIndex);
                });

                it('Rows inbetween two events', function() {
                    const $laterRow = $rows.eq(7);

                    selector._onMouseOver({
                        target: startCell,
                    });

                    selector._onMouseDown({
                        target: startCell,
                    });

                    selector._onMouseOver({
                        target: $laterRow[0].cells[0],
                    });

                    expect($($rows[4]).hasClass('selected')).toBe(true);
                    expect($($rows[5]).hasClass('selected')).toBe(true);
                    expect($($rows[6]).hasClass('selected')).toBe(true);
                    expect($($rows[7]).hasClass('selected')).toBe(true);
                    expect(selector._$begin[0]).toBe($startRow[0]);
                    expect(selector._$end[0]).toBe($laterRow[0]);
                    expect(selector._beginLineNum).toBe(5);
                    expect(selector._endLineNum).toBe(8);
                    expect(selector._lastSeenIndex)
                        .toBe($laterRow[0].rowIndex);
                });
            });

            describe('Removing rows from selection', function() {
                it('Above', function() {
                    const $prevRow = $rows.eq(3);
                    const prevCell = $prevRow[0].cells[0];

                    selector._onMouseOver({
                        target: startCell,
                    });

                    selector._onMouseDown({
                        target: startCell,
                    });

                    selector._onMouseOver({
                        target: prevCell,
                    });

                    selector._onMouseOut({
                        relatedTarget: startCell,
                        target: prevCell,
                    });

                    selector._onMouseOver({
                        target: startCell,
                    });

                    expect($startRow.hasClass('selected')).toBe(true);
                    expect($prevRow.hasClass('selected')).toBe(false);
                    expect(selector._$begin[0]).toBe($startRow[0]);
                    expect(selector._$end[0]).toBe($startRow[0]);
                    expect(selector._beginLineNum).toBe(5);
                    expect(selector._endLineNum).toBe(5);
                    expect(selector._lastSeenIndex)
                        .toBe($startRow[0].rowIndex);
                });

                it('Below', function() {
                    const $nextRow = $rows.eq(5);
                    const nextCell = $nextRow[0].cells[0];

                    selector._onMouseOver({
                        target: startCell,
                    });

                    selector._onMouseDown({
                        target: startCell,
                    });

                    selector._onMouseOver({
                        target: nextCell,
                    });

                    selector._onMouseOut({
                        relatedTarget: startCell,
                        target: nextCell,
                    });

                    selector._onMouseOver({
                        target: startCell,
                    });

                    expect($startRow.hasClass('selected')).toBe(true);
                    expect($nextRow.hasClass('selected')).toBe(false);
                    expect(selector._$begin[0]).toBe($startRow[0]);
                    expect(selector._$end[0]).toBe($startRow[0]);
                    expect(selector._beginLineNum).toBe(5);
                    expect(selector._endLineNum).toBe(5);
                    expect(selector._lastSeenIndex)
                        .toBe($startRow[0].rowIndex);
                });
            });

            describe('Finishing selection', function() {
                beforeEach(function() {
                    spyOn(view, 'createAndEditCommentBlock');
                });

                describe('With single line', function() {
                    let $row;
                    let cell;

                    beforeEach(function() {
                        $row = $($rows[4]);
                        cell = $row[0].cells[0];
                    });

                    it('And existing comment', function() {
                        const onClick = jasmine.createSpy('onClick');

                        $('<a class="commentflag">')
                            .click(onClick)
                            .appendTo(cell);

                        selector._onMouseOver({
                            target: cell,
                        });

                        selector._onMouseDown({
                            target: cell,
                        });

                        selector._onMouseUp({
                            preventDefault: function() {},
                            stopImmediatePropagation: function() {},
                            target: cell,
                        });

                        expect(view.createAndEditCommentBlock)
                            .not.toHaveBeenCalled();
                        expect(onClick).toHaveBeenCalled();

                        expect($row.hasClass('selected')).toBe(false);
                        expect(selector._$begin).toBe(null);
                        expect(selector._$end).toBe(null);
                        expect(selector._beginLineNum).toBe(0);
                        expect(selector._endLineNum).toBe(0);
                        expect(selector._lastSeenIndex).toBe(0);
                    });

                    it('And no existing comment', function() {
                        selector._onMouseOver({
                            target: cell,
                        });

                        selector._onMouseDown({
                            target: cell,
                        });

                        selector._onMouseUp({
                            target: cell,
                            preventDefault: function() {},
                            stopImmediatePropagation: function() {},
                        });

                        expect(view.createAndEditCommentBlock)
                            .toHaveBeenCalledWith({
                                $beginRow: $row,
                                $endRow: $row,
                                beginLineNum: 5,
                                endLineNum: 5,
                            });

                        expect($row.hasClass('selected')).toBe(false);
                        expect(selector._$begin).toBe(null);
                        expect(selector._$end).toBe(null);
                        expect(selector._beginLineNum).toBe(0);
                        expect(selector._endLineNum).toBe(0);
                        expect(selector._lastSeenIndex).toBe(0);
                    });
                });

                describe('With multiple lines', function() {
                    let $startRow;
                    let $endRow;
                    let startCell;
                    let endCell;

                    beforeEach(function() {
                        $startRow = $rows.eq(4);
                        $endRow = $rows.eq(5);
                        startCell = $startRow[0].cells[0];
                        endCell = $endRow[0].cells[0];
                    });

                    xit('And existing comment', function() {
                        const onClick = jasmine.createSpy('onClick');

                        $('<a class="commentflag">')
                            .click(onClick)
                            .appendTo(startCell);

                        selector._onMouseOver({
                            target: startCell,
                        });

                        selector._onMouseDown({
                            target: startCell,
                        });

                        selector._onMouseOver({
                            target: endCell,
                        });

                        expect(selector._$begin[0]).toBe($startRow[0]);
                        expect(selector._$end[0]).toBe($endRow[0]);

                        /* Copy these so we can directly compare. */
                        $startRow = selector._$begin;
                        $endRow = selector._$end;

                        selector._onMouseUp({
                            target: endCell,
                            preventDefault: function() {},
                            stopImmediatePropagation: function() {},
                        });

                        expect(view.createAndEditCommentBlock)
                            .toHaveBeenCalledWith({
                                $beginRow: $startRow,
                                $endRow: $endRow,
                                beginLineNum: 5,
                                endLineNum: 6,
                            });

                        expect(onClick).not.toHaveBeenCalled();
                        expect($startRow.hasClass('selected')).toBe(false);
                        expect($endRow.hasClass('selected')).toBe(false);
                        expect(selector._$begin).toBe(null);
                        expect(selector._$end).toBe(null);
                        expect(selector._beginLineNum).toBe(0);
                        expect(selector._endLineNum).toBe(0);
                        expect(selector._lastSeenIndex).toBe(0);
                    });

                    it('And no existing comment', function() {
                        selector._onMouseOver({
                            target: startCell,
                        });

                        selector._onMouseDown({
                            target: startCell,
                        });

                        selector._onMouseOver({
                            target: endCell,
                        });

                        expect(selector._$begin[0]).toBe($startRow[0]);
                        expect(selector._$end[0]).toBe($endRow[0]);

                        /* Copy these so we can directly compare. */
                        $startRow = selector._$begin;
                        $endRow = selector._$end;

                        selector._onMouseUp({
                            target: endCell,
                            preventDefault: function() {},
                            stopImmediatePropagation: function() {},
                        });

                        expect(view.createAndEditCommentBlock)
                            .toHaveBeenCalledWith({
                                $beginRow: $startRow,
                                $endRow: $endRow,
                                beginLineNum: 5,
                                endLineNum: 6,
                            });

                        expect($startRow.hasClass('selected')).toBe(false);
                        expect($endRow.hasClass('selected')).toBe(false);
                        expect(selector._$begin).toBe(null);
                        expect(selector._$end).toBe(null);
                        expect(selector._beginLineNum).toBe(0);
                        expect(selector._endLineNum).toBe(0);
                        expect(selector._lastSeenIndex).toBe(0);
                    });
                });
            });
        });

        describe('Hovering', function() {
            describe('Over line', function() {
                let $row;
                let cell;

                beforeEach(function() {
                    $row = $rows.eq(4);
                });

                it('Contents cell', function() {
                    cell = $row[0].cells[1];

                    selector._onMouseOver({
                        target: cell,
                    });

                    expect($row.hasClass('selected')).toBe(false);
                    expect(selector._$ghostCommentFlag.css('display'))
                        .toBe('none');
                });

                describe('Line number cell', function() {
                    beforeEach(function() {
                        cell = $row[0].cells[0];
                    });

                    it('With existing comment on row', function() {
                        $(cell).append('<a class="commentflag">');
                        selector._onMouseOver({
                            target: cell,
                        });

                        expect($row.hasClass('selected')).toBe(true);
                        expect(selector._$ghostCommentFlag.css('display'))
                            .toBe('none');
                    });

                    it('With no column flag', function() {
                        selector._onMouseOver({
                            target: cell,
                        });

                        expect($row.hasClass('selected')).toBe(true);
                        expect(selector._$ghostCommentFlag.css('display'))
                            .not.toBe('none');
                    });
                });
            });

            describe('Out of line', function() {
                it('Contents cell', function() {
                    const $row = $rows.eq(0);

                    selector._onMouseOver({
                        target: $row[0].cells[0],
                    });

                    expect(selector._$ghostCommentFlag.css('display'))
                        .not.toBe('none');

                    selector._onMouseOut({
                        target: $row[0].cells[0],
                    });

                    expect(selector._$ghostCommentFlag.css('display'))
                        .toBe('none');
                });

                it('Line number cell', function() {
                    const $row = $rows.eq(0);

                    selector._onMouseOver({
                        target: $row[0].cells[0],
                    });

                    expect(selector._$ghostCommentFlag.css('display'))
                        .not.toBe('none');
                    expect($row.hasClass('selected')).toBe(true);

                    selector._onMouseOut({
                        target: $row[0].cells[0],
                    });

                    expect(selector._$ghostCommentFlag.css('display'))
                        .toBe('none');
                    expect($row.hasClass('selected')).toBe(false);
                });
            });
        });
    });

    describe('Incremental expansion', function() {
        let model;

        beforeEach(function() {
            model = new DiffReviewable({
                file: new DiffFile({
                    index: 1
                }),
                fileDiffID: 10,
                reviewRequest: reviewRequest,
                revision: 1,
            });
        });

        describe('Expanding', function() {
            beforeEach(function() {
                view = new DiffReviewableView({
                    el: $(diffTableTemplate({
                        chunks: [
                            {
                                numRows: 5,
                                startRow: 1,
                                type: 'equal',
                            },
                            {
                                expandHeaderLines: 7,
                                type: 'collapsed',
                            },
                            {
                                numRows: 5,
                                startRow: 10,
                                type: 'delete',
                            },
                        ],
                    })),
                    model: model,
                });
                view.render().$el.appendTo($container);
            });

            describe('Fetching fragment', function() {
                beforeEach(function() {
                    spyOn(model, 'getRenderedDiffFragment')
                        .and.resolveTo('abc');
                });

                it('Full chunk', function() {
                    view.$('.tests-expand-chunk').click();

                    expect(model.getRenderedDiffFragment).toHaveBeenCalled();

                    const options = model
                        .getRenderedDiffFragment
                        .calls
                        .argsFor(0)[0];
                    expect(options.chunkIndex).toBe(1);
                    expect(options.linesOfContext).toBe(undefined);
                });

                it('+20 above', function() {
                    view.$('.tests-expand-above').click();

                    expect(model.getRenderedDiffFragment).toHaveBeenCalled();

                    const options = model
                        .getRenderedDiffFragment
                        .calls
                        .argsFor(0)[0];
                    expect(options.chunkIndex).toBe(1);
                    expect(options.linesOfContext).toBe('20,0');
                });

                it('+20 below', function() {
                    view.$('.tests-expand-below').click();

                    expect(model.getRenderedDiffFragment).toHaveBeenCalled();

                    const options = model
                        .getRenderedDiffFragment
                        .calls
                        .argsFor(0)[0];
                    expect(options.chunkIndex).toBe(1);
                    expect(options.linesOfContext).toBe('0,20');
                });

                it('Function/class', function() {
                    view.$('.tests-expand-header').click();

                    expect(model.getRenderedDiffFragment).toHaveBeenCalled();

                    const options = model
                        .getRenderedDiffFragment
                        .calls
                        .argsFor(0)[0];
                    expect(options.chunkIndex).toBe(1);
                    expect(options.linesOfContext).toBe('0,7');
                });
            });

            describe('Injecting HTML', function() {
                it('Whole chunk', function(done) {
                    spyOn(model, 'getRenderedDiffFragment')
                        .and.resolveTo(dedent`
                            <tbody class="equal tests-new-chunk">
                             <tr line="6">
                              <th></th>
                              <td>
                               <div class="collapse-floater">
                                <div class="rb-c-diff-collapse-button"
                                     data-chunk-index="1"
                                     data-lines-of-context="0"></div>
                               </div>
                              </td>
                              <th></th>
                              <td></td>
                             </tr>
                            </tbody>
                        `);
                    view.on('chunkExpansionChanged', () => {
                        expect(model.getRenderedDiffFragment)
                            .toHaveBeenCalled();

                        const $tbodies = view.$('tbody');
                        expect($tbodies.length).toBe(3);
                        expect($($tbodies[0]).hasClass('equal')).toBe(true);
                        expect($($tbodies[1]).hasClass('equal')).toBe(true);
                        expect($($tbodies[1]).hasClass('tests-new-chunk'))
                            .toBe(true);
                        expect($($tbodies[2]).hasClass('delete')).toBe(true);
                        expect(view._centered._elements.size).toBe(1);

                        done();
                    });

                    view.$('.tests-expand-chunk').click();
                });

                it('Merging adjacent expanded chunks', function(done) {
                    spyOn(model, 'getRenderedDiffFragment')
                        .and.resolveTo(dedent`
                            <tbody class="equal tests-new-chunk">
                             <tr line="6">
                              <th></th>
                              <td>
                               <div class="collapse-floater">
                                <div class="rb-c-diff-collapse-button"
                                     data-chunk-index="1"
                                     data-lines-of-context="0"></div>
                               </div>
                              </td>
                              <th></th>
                              <td></td>
                             </tr>
                            </tbody>
                        `);
                    view.on('chunkExpansionChanged', () => {
                        expect(model.getRenderedDiffFragment)
                            .toHaveBeenCalled();

                        const $tbodies = view.$('tbody');
                        expect($tbodies.length).toBe(3);
                        expect($($tbodies[0]).hasClass('equal')).toBe(true);
                        expect($($tbodies[1]).hasClass('equal')).toBe(true);
                        expect($($tbodies[1]).hasClass('tests-new-chunk'))
                            .toBe(true);
                        expect($($tbodies[2]).hasClass('delete')).toBe(true);
                        expect(view._centered._elements.size).toBe(1);

                        done();
                    });

                    /*
                     * Simulate having a couple nearby partially expanded
                     * chunks. These should end up being removed when
                     * expanding the chunk.
                     */
                    $('<tbody class="equal loaded">')
                        .append($('<div class="rb-c-diff-collapse-button">'))
                        .insertAfter(view.$('tbody')[1])
                        .clone().insertBefore(view.$('tbody')[1]);

                    expect(view.$('tbody').length).toBe(5);

                    view.$('.tests-expand-chunk').click();
                });
            });
        });

        describe('Collapsing', function() {
            let $collapseButton;

            beforeEach(function() {
                view = new DiffReviewableView({
                    el: $(diffTableTemplate({
                        chunks: [
                            {
                                numRows: 5,
                                startRow: 1,
                                type: 'equal',
                            },
                            {
                                expanded: true,
                                numRows: 2,
                                startRow: 6,
                                type: 'equal',
                            },
                            {
                                numRows: 5,
                                startRow: 10,
                                type: 'delete',
                            },
                        ],
                    })),
                    model: model,
                });
                view.render().$el.appendTo($container);

                $collapseButton = view.$('.rb-c-diff-collapse-button');
            });

            it('Fetching fragment', function(done) {
                spyOn(model, 'getRenderedDiffFragment')
                    .and.resolveTo('abc');

                view.on('chunkExpansionChanged', () => {
                    expect(model.getRenderedDiffFragment).toHaveBeenCalled();

                    const options = model
                        .getRenderedDiffFragment
                        .calls
                        .argsFor(0)[0];
                    expect(options.chunkIndex).toBe(1);
                    expect(options.linesOfContext).toBe(0);

                    done();
                });

                $collapseButton.click();
            });

            describe('Injecting HTML', function() {
                it('Single expanded chunk', function(done) {
                    spyOn(model, 'getRenderedDiffFragment')
                        .and.resolveTo(dedent`
                            <tbody class="equal tests-new-chunk">
                             <tr line="6">
                              <th></th>
                              <td></td>
                              <th></th>
                              <td></td>
                             </tr>
                            </tbody>
                        `);
                    view.on('chunkExpansionChanged', () => {
                        expect(model.getRenderedDiffFragment)
                            .toHaveBeenCalled();

                        const $tbodies = view.$('tbody');
                        expect($tbodies.length).toBe(3);
                        expect($($tbodies[0]).hasClass('equal')).toBe(true);
                        expect($($tbodies[1]).hasClass('equal')).toBe(true);
                        expect($($tbodies[1]).hasClass('tests-new-chunk'))
                            .toBe(true);
                        expect($($tbodies[2]).hasClass('delete')).toBe(true);
                        expect(view._centered._elements.size).toBe(0);

                        done();
                    });

                    $collapseButton.click();
                });

                it('Merging adjacent expanded chunks', function(done) {
                    let $tbodies;

                    spyOn(model, 'getRenderedDiffFragment')
                        .and.resolveTo(dedent`
                            <tbody class="equal tests-new-chunk">
                             <tr line="6">
                              <th></th>
                              <td></td>
                              <th></th>
                              <td></td>
                             </tr>
                            </tbody>
                        `);
                    view.on('chunkExpansionChanged', () => {
                        expect(model.getRenderedDiffFragment)
                            .toHaveBeenCalled();

                        $tbodies = view.$('tbody');
                        expect($tbodies.length).toBe(3);
                        expect($($tbodies[0]).hasClass('equal')).toBe(true);
                        expect($($tbodies[1]).hasClass('equal')).toBe(true);
                        expect($($tbodies[1]).hasClass('tests-new-chunk'))
                            .toBe(true);
                        expect($($tbodies[2]).hasClass('delete')).toBe(true);
                        expect(view._centered._elements.size).toBe(0);

                        done();
                    });

                    /*
                     * Simulate having a couple nearby partially expanded
                     * chunks. These should end up being removed when
                     * expanding the chunk.
                     */
                    $('<tbody class="equal loaded">')
                        .append($('<div class="rb-c-diff-collapse-button">'))
                        .insertAfter(view.$('tbody')[1])
                        .clone().insertBefore(view.$('tbody')[1]);

                    $collapseButton.click();
                });
            });
        });
    });

    describe('Comment flags', function() {
        describe('Placing visible comments', function() {
            const expandedDiffFragmentHTML = dedent`
                <tbody class="equal tests-new-chunk">
                 <tr line="11">
                  <th></th>
                  <td>
                   <div class="collapse-floater">
                    <div class="rb-c-diff-collapse-button"
                         data-chunk-index="1"
                         data-lines-of-context="0"></div>
                   </div>
                  </td>
                  <th></th>
                  <td></td>
                 </tr>
                </tbody>
                `;
            let $commentFlag;
            let $commentFlags;
            let $rows;
            let diffFragmentHTML;

            beforeEach(function() {
                view = new DiffReviewableView({
                    el: $(diffTableTemplate({
                        chunks: [
                            {
                                numRows: 10,
                                startRow: 1,
                                type: 'insert',
                            },
                            {
                                expandHeaderLines: 7,
                                type: 'collapsed',
                            },
                        ],
                    })),
                    model: new DiffReviewable({
                        reviewRequest: reviewRequest,
                        serializedCommentBlocks: {
                            '11-1': [
                                {
                                    comment_id: 1,
                                    issue_opened: false,
                                    line: 11,
                                    localdraft: false,
                                    num_lines: 1,
                                    review_id: 1,
                                    text: 'Comment 4',
                                    user: {
                                        name: 'testuser',
                                        username: 'testuser',
                                    },
                                },
                            ],
                            '2-2': [
                                {
                                    comment_id: 1,
                                    issue_opened: false,
                                    line: 2,
                                    localdraft: false,
                                    num_lines: 2,
                                    review_id: 1,
                                    text: 'Comment 1',
                                    user: {
                                        name: 'testuser',
                                        username: 'testuser',
                                    },
                                },
                            ],
                            '4-1': [
                                {
                                    comment_id: 1,
                                    issue_opened: false,
                                    line: 4,
                                    localdraft: false,
                                    num_lines: 1,
                                    review_id: 1,
                                    text: 'Comment 2',
                                    user: { name: 'testuser' },
                                },
                                {
                                    comment_id: 1,
                                    issue_opened: false,
                                    line: 4,
                                    localdraft: false,
                                    num_lines: 1,
                                    review_id: 1,
                                    text: 'Comment 3',
                                    user: {
                                        name: 'testuser',
                                        username: 'testuser',
                                    },
                                },
                            ],
                        },
                    }),
                });
                view.render().$el.appendTo($container);

                diffFragmentHTML = expandedDiffFragmentHTML;

                spyOn(view.model, 'getRenderedDiffFragment')
                    .and.callFake(() => {
                        return Promise.resolve(diffFragmentHTML);
                    });

                $commentFlags = view.$('.commentflag');
                $rows = view.$el.find('tbody tr');
            });

            it('On initial render', function() {
                expect($commentFlags.length).toBe(2);
                expect($($commentFlags[0]).find('.commentflag-count').text())
                    .toBe('1');
                expect($($commentFlags[1]).find('.commentflag-count').text())
                    .toBe('2');

                $commentFlag = $($rows[1]).find('.commentflag');
                expect($commentFlag.length).toBe(1);
                expect($commentFlag[0]).toBe($commentFlags[0]);
                expect($commentFlag.parents('tr').attr('line')).toBe('2');

                $commentFlag = $($rows[3]).find('.commentflag');
                expect($commentFlag.length).toBe(1);
                expect($commentFlag[0]).toBe($commentFlags[1]);
                expect($commentFlag.parents('tr').attr('line')).toBe('4');
            });

            it('On chunk expand', function(done) {
                expect($commentFlags.length).toBe(2);

                view.on('chunkExpansionChanged', () => {
                    $commentFlags = view.$('.commentflag');
                    $rows = view.$el.find('tbody tr');

                    expect($commentFlags.length).toBe(3);
                    expect(
                        $($commentFlags[2]).find('.commentflag-count').text())
                        .toBe('1');

                    $commentFlag = $($rows[10]).find('.commentflag');
                    expect($commentFlag.length).toBe(1);
                    expect($commentFlag[0]).toBe($commentFlags[2]);
                    expect($commentFlag.parents('tr').attr('line')).toBe('11');

                    done();
                });

                view.$('.tests-expand-chunk').click();
            });

            it('On chunk re-expand (after collapsing)', function(done) {
                const collapsedDiffFragmentHTML = [
                    '<tbody class="diff-header">',
                    $(view.$('tbody')[1]).html(),
                    '</tbody>',
                ].join('');

                expect($commentFlags.length).toBe(2);

                let n = 0;

                view.on('chunkExpansionChanged', () => {
                    n++;

                    if (n === 1) {
                        expect(view.$('.commentflag').length).toBe(3);

                        diffFragmentHTML = collapsedDiffFragmentHTML;

                        view.$('.rb-c-diff-collapse-button').click();
                    } else if (n === 2) {
                        expect(view.$('.commentflag').length).toBe(2);
                        diffFragmentHTML = expandedDiffFragmentHTML;

                        view.$('.tests-expand-chunk').click();
                    } else if (n === 3) {
                        expect(view.$('.commentflag').length).toBe(3);

                        $commentFlags = view.$('.commentflag');
                        $rows = view.$el.find('tbody tr');

                        expect($commentFlags.length).toBe(3);
                        expect(
                            $($commentFlags[2]).find('.commentflag-count')
                                .text())
                            .toBe('1');

                        $commentFlag = $($rows[10]).find('.commentflag');
                        expect($commentFlag.length).toBe(1);
                        expect($commentFlag[0]).toBe($commentFlags[2]);
                        expect($commentFlag.parents('tr').attr('line'))
                            .toBe('11');

                        done();
                    } else {
                        done.fail();
                    }
                });

                view.$('.tests-expand-chunk').click();
            });
        });
    });

    describe('Events', function() {
        describe('Toggle Displayed Unicode Characters', function() {
            let $toggleButton;

            beforeEach(function() {
                view = new DiffReviewableView({
                    el: $(diffTableTemplate({
                        chunks: [
                            {
                                extraClass: 'whitespace-chunk',
                                numRows: 5,
                                startRow: 1,
                                type: 'replace',
                            },
                        ],
                        fileAlertHTML: dedent`
                        `,
                    })),
                    model: new DiffReviewable({
                        reviewRequest: reviewRequest,
                    }),
                });

                const $el = view.render().$el;
                const $fileAlert = $(fileAlertHTMLTemplate({
                    contentHTML: dedent`
                        <button class="rb-o-toggle-ducs"
                                data-hide-chars-label="Hide chars"
                                data-show-chars-label="Show chars">
                        </button>
                    `,
                }));

                $fileAlert.insertBefore($el[0].tHead);
                $el.appendTo($container);

                $toggleButton = view.$('.rb-o-toggle-ducs');
                expect($toggleButton.length).toBe(1);
            });

            it('Show Displayed Unicode Characters', function() {
                $toggleButton
                    .text('Hide chars')
                    .click();

                expect(view.el).toHaveClass('-hide-ducs');
                expect($toggleButton.text()).toBe('Show chars');
            });

            it('Hide Displayed Unicode Characters', function() {
                view.$el.addClass('-hide-ducs');

                $toggleButton
                    .text('Show chars')
                    .click();

                expect(view.el).not.toHaveClass('-hide-ducs');
                expect($toggleButton.text()).toBe('Hide chars');
            });
        });
    });

    describe('Methods', function() {
        describe('toggleWhitespaceOnlyChunks', function() {
            beforeEach(function() {
                view = new DiffReviewableView({
                    el: $(diffTableTemplate({
                        chunks: [
                            {
                                extraClass: 'whitespace-chunk',
                                numRows: 5,
                                startRow: 1,
                                type: 'replace',
                            },
                        ],
                    })),
                    model: new DiffReviewable({
                        reviewRequest: reviewRequest,
                    }),
                });
                view.render().$el.appendTo($container);
            });

            describe('Toggle on', function() {
                it('Chunk classes', function() {
                    view.toggleWhitespaceOnlyChunks();

                    const $tbodies = view.$('tbody');
                    const $tbody = $($tbodies[0]);
                    const $children = $tbody.children();

                    expect($tbody.hasClass('replace')).toBe(false);
                    expect($($children[0]).hasClass('first')).toBe(true);
                    expect($($children[$children.length - 1]).hasClass('last'))
                        .toBe(true);
                });

                it('chunkDimmed event triggered', function() {
                    spyOn(view, 'trigger');

                    view.toggleWhitespaceOnlyChunks();

                    expect(view.trigger)
                        .toHaveBeenCalledWith('chunkDimmed', '0.0');
                });

                it('Whitespace-only file classes', function() {
                    const $tbodies = view.$el.children('tbody');
                    const $whitespaceChunk = $('<tbody>')
                            .addClass('whitespace-file')
                            .hide()
                            .html('<tr><td></td></tr>')
                            .appendTo(view.$el);

                    expect($whitespaceChunk.is(':visible')).toBe(false);
                    expect($tbodies.is(':visible')).toBe(true);

                    view.toggleWhitespaceOnlyChunks();

                    expect($whitespaceChunk.is(':visible')).toBe(true);
                    expect($tbodies.is(':visible')).toBe(false);
                });
            });

            describe('Toggle off', function() {
                it('Chunk classes', function() {
                    view.toggleWhitespaceOnlyChunks();
                    view.toggleWhitespaceOnlyChunks();

                    const $tbodies = view.$('tbody');
                    const $tbody = $($tbodies[0]);
                    const $children = $tbody.children();

                    expect($tbody.hasClass('replace')).toBe(true);
                    expect($($children[0]).hasClass('first')).toBe(false);
                    expect($($children[$children.length - 1]).hasClass('last'))
                        .toBe(false);
                });

                it('chunkDimmed event triggered', function() {
                    view.toggleWhitespaceOnlyChunks();

                    spyOn(view, 'trigger');

                    view.toggleWhitespaceOnlyChunks();

                    expect(view.trigger)
                        .toHaveBeenCalledWith('chunkUndimmed', '0.0');
                });

                it('Whitespace-only file classes', function() {
                    const $tbodies = view.$el.children('tbody');
                    const $whitespaceChunk = $('<tbody>')
                            .addClass('whitespace-file')
                            .html('<tr><td></td></tr>')
                            .hide()
                            .appendTo(view.$el);

                    expect($whitespaceChunk.is(':visible')).toBe(false);
                    expect($tbodies.is(':visible')).toBe(true);

                    view.toggleWhitespaceOnlyChunks();
                    view.toggleWhitespaceOnlyChunks();

                    expect($whitespaceChunk.is(':visible')).toBe(false);
                    expect($tbodies.is(':visible')).toBe(true);
                });
            });
        });
    });
});
