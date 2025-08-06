import { suite } from '@beanbag/jasmine-suites';
import {
    afterEach,
    beforeEach,
    describe,
    expect,
    fail,
    it,
    spyOn,
} from 'jasmine-core';

import {
    EnabledFeatures,
    Review,
    ReviewRequest,
    UserSession,
} from 'reviewboard/common';
import {
    ReviewDialogView,
    ReviewRequestEditor,
} from 'reviewboard/reviews';
import { DnDUploader } from 'reviewboard/ui';


suite('rb/views/ReviewDialogView', function() {
    const baseEmptyCommentListPayload = {
        links: {},
        stat: 'ok',
        total_results: 0,
    };
    const emptyDiffCommentsPayload = _.defaults({
        diff_comments: [],
    }, baseEmptyCommentListPayload);
    const emptyFileAttachmentCommentsPayload = _.defaults({
        file_attachment_comments: [],
    }, baseEmptyCommentListPayload);
    const emptyGeneralCommentsPayload = _.defaults({
        general_comments: [],
    }, baseEmptyCommentListPayload);
    const emptyScreenshotCommentsPayload = _.defaults({
        screenshot_comments: [],
    }, baseEmptyCommentListPayload);
    const baseCommentPayload = {
        id: 1,
        issue_opened: true,
        issue_status: 'opened',
        text: 'My comment',
    };
    const diffCommentPayload = _.defaults({
        filediff: {
            dest_file: 'my-file',
            id: 1,
            source_file: 'my-file',
            source_revision: '1',
        },
        first_line: 10,
        interfilediff: {
            dest_file: 'my-file',
            id: 2,
            source_file: 'my-file',
            source_revision: '2',
        },
        num_lines: 5,
    }, baseCommentPayload);
    const fileAttachmentCommentPayload = _.defaults({
        extra_data: {},
        file_attachment: {
            filename: 'file.txt',
            icon_url: 'data:image/gif;base64,',
            id: 10,
        },
        link_text: 'my-link-text',
        review_url: '/review-ui/',
        thumbnail_html: '<blink>Boo</blink>',
    }, baseCommentPayload);
    const generalCommentPayload = baseCommentPayload;
    const screenshotCommentPayload = _.defaults({
        h: 40,
        screenshot: {
            caption: 'My caption',
            filename: 'image.png',
            id: 10,
            review_url: '/review-ui/',
        },
        thumbnail_url: 'data:image/gif;base64,',
        w: 30,
        x: 10,
        y: 20,
    }, baseCommentPayload);
    const origGeneralCommentsEnabled = EnabledFeatures.generalComments;
    let reviewRequestEditor;
    let review;
    let dlg;

    async function createReviewDialog() {
        const dlg = ReviewDialogView.create({
            container: $testsScratch,
            review: review,
            reviewRequestEditor: reviewRequestEditor,
        });

        return new Promise(resolve => {
            dlg.once('loadCommentsDone', () => {
                resolve(dlg);
            });
        });
    }

    beforeEach(function() {
        const origMove = $.fn.move;
        const reviewRequest = new ReviewRequest({
            summary: 'My Review Request',
        });

        DnDUploader.create();

        reviewRequestEditor = new ReviewRequestEditor({
            reviewRequest: reviewRequest,
        });

        review = new Review({
            parentObject: reviewRequest,
        });

        spyOn(review, 'ready').and.resolveTo();

        /*
         * modalBox uses move(... 'fixed') for all positioning, which will
         * cause the box to flash on screen during tests. Override this to
         * disallow fixed.
         */
        spyOn($.fn, 'move').and.callFake(function(x, y, pos) {
            if (pos === 'fixed') {
                pos = 'absolute';
            }

            return origMove.call(this, x, y, pos);
        });

        /* Prevent these from being called. */
        spyOn(RB.DiffFragmentQueueView.prototype, 'queueLoad');
        spyOn(RB.DiffFragmentQueueView.prototype, 'loadFragments');

        /* By default, general comments should be enabled. */
        EnabledFeatures.generalComments = true;
    });

    afterEach(function() {
        DnDUploader.instance = null;
        ReviewDialogView.instance = null;
        EnabledFeatures.generalComments = origGeneralCommentsEnabled;
    });

    describe('Class methods', function() {
        describe('create', function() {
            it('Without a review', function() {
                expect(() => ReviewDialogView.create({
                    container: $testsScratch,
                    reviewRequestEditor: reviewRequestEditor,
                })).toThrow();

                expect(ReviewDialogView.instance).toBeFalsy();
                expect($testsScratch.children().length).toBe(0);
            });

            it('With a review', async function() {
                dlg = await createReviewDialog();

                expect(dlg).toBeTruthy();
                expect(ReviewDialogView.instance).toBe(dlg);

                /* One for the dialog, one for the background box. */
                expect($testsScratch.children().length).toBe(2);
            });

            it('With existing instance', async function() {
                dlg = await createReviewDialog();

                try {
                    await createReviewDialog();
                    fail('Expected createReviewDialog to throw');
                } catch {
                }

                expect(ReviewDialogView.instance).toBe(dlg);
                expect($testsScratch.children().length).toBe(2);
            });
        });
    });

    describe('Instances', function() {
        describe('Methods', function() {
            it('close', async function() {
                dlg = await createReviewDialog();
                expect($testsScratch.children().length).toBe(2);

                dlg.close();
                expect($testsScratch.children().length).toBe(0);
                expect(ReviewDialogView.instance).toBe(null);
            });
        });

        describe('Loading', function() {
            it('With new review', async function() {
                expect(review.isNew()).toBe(true);

                dlg = await createReviewDialog();

                expect(dlg._bodyTopView.$editor.text()).toBe('');
                expect(dlg._bodyBottomView.$editor.text()).toBe('');
                expect(dlg._bodyBottomView.$el.is(':visible')).toBe(false);
                expect(dlg._$shipIt.prop('checked')).toBe(false);
                expect(dlg._$spinner).toBe(null);
            });

            describe('With body and top text', function() {
                const bodyTopText = 'My body top';
                const bodyBottomText = 'My body bottom';

                beforeEach(function() {
                    review.set({
                        bodyBottom: bodyBottomText,
                        bodyTop: bodyTopText,
                        loaded: true,
                    });
                });

                it('Clearing body bottom hides footer', async function() {
                    dlg = await createReviewDialog();

                    expect(dlg._bodyBottomView.$editor.text())
                        .toBe(bodyBottomText);
                    expect(dlg._bodyBottomView.$el.is(':visible')).toBe(true);

                    review.set('bodyBottom', '');

                    expect(dlg._bodyBottomView.$el.is(':visible')).toBe(false);
                });
            });

            describe('With existing review', function() {
                const bodyTopText = 'My body top';
                const bodyBottomText = 'My body bottom';
                const shipIt = true;
                let fileAttachmentCommentsPayload;
                let generalCommentsPayload;
                let diffCommentsPayload;
                let screenshotCommentsPayload;
                let commentView;
                let ajaxData;

                beforeEach(function() {
                    review.set({
                        bodyBottom: bodyBottomText,
                        bodyTop: bodyTopText,
                        id: 42,
                        links: {
                            diff_comments: {
                                href: '/diff-comments/',
                            },
                            file_attachment_comments: {
                                href: '/file-attachment-comments/',
                            },
                            general_comments: {
                                href: '/general-comments/',
                            },
                            screenshot_comments: {
                                href: '/screenshot-comments/',
                            },
                            self: {
                                href: '/reviews/42/',
                            },
                        },
                        loaded: true,
                        shipIt: shipIt,
                    });

                    diffCommentsPayload =
                        _.clone(emptyDiffCommentsPayload);
                    screenshotCommentsPayload =
                        _.clone(emptyScreenshotCommentsPayload);
                    fileAttachmentCommentsPayload =
                        _.clone(emptyFileAttachmentCommentsPayload);
                    generalCommentsPayload =
                        _.clone(emptyGeneralCommentsPayload);

                    spyOn($, 'ajax').and.callFake(options => {
                        if (options.type === 'DELETE') {
                            options.success({});
                        } else if (options.url ===
                                   '/file-attachment-comments/') {
                            options.success(fileAttachmentCommentsPayload);
                        } else if (options.url === '/diff-comments/') {
                            options.success(diffCommentsPayload);
                        } else if (options.url === '/screenshot-comments/') {
                            options.success(screenshotCommentsPayload);
                        } else if (options.url === '/general-comments/') {
                            options.success(generalCommentsPayload);
                        }
                    });
                });

                describe('Review properties', function() {
                    function testLoadReview() {
                        return new Promise<void>(resolve => {
                            dlg = ReviewDialogView.create({
                                container: $testsScratch,
                                review: review,
                                reviewRequestEditor: reviewRequestEditor,
                            });

                            dlg.on('loadCommentsDone', () => {
                                expect(dlg._bodyTopView.$editor.text())
                                    .toBe(bodyTopText);
                                expect(dlg._bodyBottomView.$editor.text())
                                    .toBe(bodyBottomText);
                                expect(dlg._bodyBottomView.$el.is(':visible'))
                                    .toBe(true);
                                expect(dlg._$shipIt.prop('checked'))
                                    .toBe(shipIt);
                                expect(dlg.$('.review-comments .draft').length)
                                    .toBe(2);
                                expect(dlg._$spinner).toBe(null);

                                resolve();
                            });
                        });
                    }

                    it('With defaultUseRichText=true', async function() {
                        UserSession.instance.set('defaultUseRichText', true);

                        await testLoadReview();

                        expect(review.ready.calls.argsFor(0)[0].data).toEqual({
                            'force-text-type': 'html',
                            'include-text-types': 'raw,markdown',
                        });
                    });

                    it('With defaultUseRichText=false', async function() {
                        UserSession.instance.set('defaultUseRichText',
                                                 false);

                        await testLoadReview();

                        expect(review.ready.calls.argsFor(0)[0].data)
                            .toEqual({
                                'force-text-type': 'html',
                                'include-text-types': 'raw',
                            });
                    });
                });

                describe('General comments', function() {
                    it('Disabled', async function() {
                        EnabledFeatures.generalComments = false;

                        dlg = await createReviewDialog();

                        const $button = dlg._$buttons.find(
                            'input[value="Add General Comment"]');
                        expect($button.length).toBe(0);

                        expect($.ajax).toHaveBeenCalled();
                        expect($.ajax.calls.argsFor(0)[0].url).not.toBe(
                            '/general-comments/');

                        expect(dlg._commentViews.length).toBe(0);
                    });

                    describe('Enabled', function() {
                        async function testLoadGeneralComments() {
                            generalCommentsPayload.total_results = 1;
                            generalCommentsPayload.general_comments = [
                                generalCommentPayload,
                            ];

                            dlg = await createReviewDialog();

                            const $button = dlg._$buttons.find('button:first');
                            expect($button.length).toBe(1);
                            expect($button.text()).toBe('Add General Comment');

                            expect($.ajax).toHaveBeenCalled();
                            expect($.ajax.calls.argsFor(0)[0].url).toBe(
                                '/general-comments/');
                            ajaxData = $.ajax.calls.argsFor(0)[0].data;

                            expect(dlg._commentViews.length).toBe(1);

                            commentView = dlg._commentViews[0];
                            expect(commentView.$editor.text())
                                .toBe(generalCommentPayload.text);
                            expect(commentView.$issueOpened.prop('checked'))
                                .toBe(generalCommentPayload.issue_opened);

                            expect(dlg._bodyBottomView.$el.is(':visible'))
                                .toBe(true);
                            expect(dlg._$spinner).toBe(null);
                        }

                        it('With defaultUseRichText=true', async function() {
                            UserSession.instance.set('defaultUseRichText',
                                                     true);

                            await testLoadGeneralComments();

                            expect(ajaxData).toEqual({
                                'api_format': 'json',
                                'force-text-type': 'html',
                                'include-text-types': 'raw,markdown',
                                'max-results': 50,
                            });
                        });

                        it('With defaultUseRichText=false', async function() {
                            UserSession.instance.set('defaultUseRichText',
                                                     false);

                            await testLoadGeneralComments();

                            expect(ajaxData).toEqual({
                                'api_format': 'json',
                                'force-text-type': 'html',
                                'include-text-types': 'raw',
                                'max-results': 50,
                            });
                        });

                        it('Deleting comment', async function() {
                            spyOn(window, 'confirm').and.returnValue(true);

                            await testLoadGeneralComments();

                            expect(dlg._generalCommentsCollection.length)
                                .toBe(1);

                            spyOn(dlg._commentViews[0].$el, 'fadeOut')
                                .and.callFake(opts => opts.complete());

                            const caughtEvent = new Promise<void>(resolve => {
                                dlg._generalCommentsCollection.at(0).once(
                                    'destroyed', () => resolve());
                            });

                            dlg.$('.delete-comment').click();

                            await caughtEvent;
                            expect(dlg._generalCommentsCollection.length)
                                .toBe(0);
                        });

                        it('Deleting comment and cancelling', async function() {
                            spyOn(window, 'confirm').and.returnValue(false);

                            await testLoadGeneralComments();

                            expect(dlg._generalCommentsCollection.length)
                                .toBe(1);

                            dlg.$('.delete-comment').click();
                            expect(dlg._generalCommentsCollection.length)
                                .toBe(1);
                        });
                    });
                });

                describe('Diff comments', function() {
                    async function testLoadDiffComments() {
                        const diffQueueProto =
                            RB.DiffFragmentQueueView.prototype;

                        diffCommentsPayload.total_results = 1;
                        diffCommentsPayload.diff_comments =
                            [diffCommentPayload];

                        dlg = await createReviewDialog();

                        expect($.ajax).toHaveBeenCalled();
                        expect($.ajax.calls.argsFor(3)[0].url).toBe(
                            '/diff-comments/');
                        ajaxData = $.ajax.calls.argsFor(3)[0].data;

                        expect(diffQueueProto.queueLoad.calls.count()).toBe(1);
                        expect(diffQueueProto.loadFragments)
                            .toHaveBeenCalled();
                        expect(dlg._commentViews.length).toBe(1);

                        commentView = dlg._commentViews[0];
                        expect(commentView.$editor.text())
                            .toBe(diffCommentPayload.text);
                        expect(commentView.$issueOpened.prop('checked'))
                            .toBe(diffCommentPayload.issue_opened);

                        expect(dlg._bodyBottomView.$el.is(':visible'))
                            .toBe(true);
                        expect(dlg._$spinner).toBe(null);
                    }

                    it('With defaultUseRichText=true', async function() {
                        UserSession.instance.set('defaultUseRichText', true);

                        await testLoadDiffComments();

                        expect(ajaxData).toEqual({
                            'api_format': 'json',
                            'expand': 'filediff,interfilediff',
                            'force-text-type': 'html',
                            'include-text-types': 'raw,markdown',
                            'max-results': 50,
                            'order-by': 'filediff,first_line',
                        });
                    });

                    it('With defaultUseRichText=false', async function() {
                        UserSession.instance.set('defaultUseRichText', false);

                        await testLoadDiffComments();

                        expect(ajaxData).toEqual({
                            'api_format': 'json',
                            'expand': 'filediff,interfilediff',
                            'force-text-type': 'html',
                            'include-text-types': 'raw',
                            'max-results': 50,
                            'order-by': 'filediff,first_line',
                        });
                    });

                    it('Deleting comment', async function() {
                        spyOn(window, 'confirm').and.returnValue(true);

                        await testLoadDiffComments();

                        expect(dlg._diffCommentsCollection.length).toBe(1);

                        spyOn(dlg._commentViews[0].$el, 'fadeOut')
                            .and.callFake(opts => opts.complete());

                        const caughtEvent = new Promise<void>(resolve => {
                            dlg._diffCommentsCollection.at(0).once(
                                'destroyed', () => resolve());
                        });

                        dlg.$('.delete-comment').click();

                        await caughtEvent;
                        expect(dlg._diffCommentsCollection.length).toBe(0);
                    });

                    it('Deleting comment and cancelling', async function() {
                        spyOn(window, 'confirm').and.returnValue(false);

                        await testLoadDiffComments();

                        expect(dlg._diffCommentsCollection.length).toBe(1);
                        dlg.$('.delete-comment').click();
                        expect(dlg._diffCommentsCollection.length).toBe(1);
                    });
                });

                describe('File attachment comments', function() {
                    async function testLoadFileAttachmentComments() {
                        fileAttachmentCommentsPayload.total_results = 1;
                        fileAttachmentCommentsPayload.file_attachment_comments =
                            [fileAttachmentCommentPayload];

                        dlg = await createReviewDialog();

                        expect($.ajax).toHaveBeenCalled();
                        expect($.ajax.calls.argsFor(2)[0].url).toBe(
                            '/file-attachment-comments/');
                        ajaxData = $.ajax.calls.argsFor(2)[0].data;

                        expect(dlg._commentViews.length).toBe(1);

                        commentView = dlg._commentViews[0];
                        expect(commentView.$editor.text())
                            .toBe(fileAttachmentCommentPayload.text);
                        expect(commentView.$issueOpened.prop('checked')).toBe(
                            fileAttachmentCommentPayload.issue_opened);

                        expect(
                            commentView
                            .$('.rb-c-review-comment-thumbnail__header')
                            .attr('href')
                        ).toBe(fileAttachmentCommentPayload.review_url);
                        expect(
                            commentView
                            .$('.rb-c-review-comment-thumbnail__name')
                            .text()
                        ).toBe(fileAttachmentCommentPayload.link_text);
                        expect(
                            commentView
                            .$('.rb-c-review-comment-thumbnail__content')
                            .html()
                        ).toBe(fileAttachmentCommentPayload.thumbnail_html);

                        expect(dlg._bodyBottomView.$el.is(':visible'))
                            .toBe(true);
                        expect(dlg._$spinner).toBe(null);
                    }

                    it('With defaultUseRichText=true', async function() {
                        UserSession.instance.set('defaultUseRichText', true);

                        await testLoadFileAttachmentComments();

                        expect(ajaxData).toEqual({
                            'api_format': 'json',
                            'expand': 'diff_against_file_attachment,' +
                                      'file_attachment',
                            'force-text-type': 'html',
                            'include-text-types': 'raw,markdown',
                            'max-results': 50,
                        });
                    });

                    it('With defaultUseRichText=false', async function() {
                        UserSession.instance.set('defaultUseRichText', false);

                        await testLoadFileAttachmentComments();

                        expect(ajaxData).toEqual({
                            'api_format': 'json',
                            'expand': 'diff_against_file_attachment,' +
                                      'file_attachment',
                            'force-text-type': 'html',
                            'include-text-types': 'raw',
                            'max-results': 50,
                        });
                    });

                    it('Deleting comment', async function() {
                        spyOn(window, 'confirm').and.returnValue(true);

                        await testLoadFileAttachmentComments();

                        expect(dlg._fileAttachmentCommentsCollection.length)
                            .toBe(1);

                        spyOn(dlg._commentViews[0].$el, 'fadeOut')
                            .and.callFake(opts => opts.complete());

                        const caughtEvent = new Promise<void>(resolve => {
                            dlg._fileAttachmentCommentsCollection.at(0).once(
                                'destroyed', () => resolve());
                        });

                        dlg.$('.delete-comment').click();

                        await caughtEvent;
                        expect(dlg._fileAttachmentCommentsCollection.length)
                            .toBe(0);
                    });

                    it('Deleting comment and cancelling', async function() {
                        spyOn(window, 'confirm').and.returnValue(false);

                        await testLoadFileAttachmentComments();

                        expect(dlg._fileAttachmentCommentsCollection.length)
                            .toBe(1);

                        dlg.$('.delete-comment').click();

                        expect(dlg._fileAttachmentCommentsCollection.length)
                            .toBe(1);
                    });
                });

                describe('Screenshot comments', function() {
                    async function testLoadScreenshotComments() {
                        screenshotCommentsPayload.total_results = 1;
                        screenshotCommentsPayload.screenshot_comments = [
                            screenshotCommentPayload,
                        ];

                        dlg = await createReviewDialog();

                        expect($.ajax).toHaveBeenCalled();
                        expect($.ajax.calls.argsFor(1)[0].url).toBe(
                            '/screenshot-comments/');
                        ajaxData = $.ajax.calls.argsFor(1)[0].data;

                        expect(dlg._commentViews.length).toBe(1);

                        commentView = dlg._commentViews[0];
                        expect(commentView.$editor.text())
                            .toBe(screenshotCommentPayload.text);
                        expect(commentView.$issueOpened.prop('checked')).toBe(
                            screenshotCommentPayload.issue_opened);

                        const $img = commentView.$('img');
                        expect($img.attr('src')).toBe(
                            screenshotCommentPayload.thumbnail_url);
                        expect($img.attr('width')).toBe(
                            screenshotCommentPayload.w.toString());
                        expect($img.attr('height')).toBe(
                            screenshotCommentPayload.h.toString());
                        expect($img.attr('alt')).toBe(
                            screenshotCommentPayload.screenshot.caption);

                        expect(
                            commentView
                            .$('.rb-c-review-comment-thumbnail__header')
                            .attr('href')
                        ).toBe(screenshotCommentPayload.screenshot.review_url);
                        expect(
                            commentView
                            .$('.rb-c-review-comment-thumbnail__name')
                            .text()
                        ).toBe(screenshotCommentPayload.screenshot.caption);

                        expect(dlg._bodyBottomView.$el.is(':visible'))
                            .toBe(true);
                        expect(dlg._$spinner).toBe(null);
                    }

                    it('With defaultUseRichText=true', async function() {
                        UserSession.instance.set('defaultUseRichText', true);

                        await testLoadScreenshotComments();

                        expect(ajaxData).toEqual({
                            'api_format': 'json',
                            'expand': 'screenshot',
                            'force-text-type': 'html',
                            'include-text-types': 'raw,markdown',
                            'max-results': 50,
                        });
                    });

                    it('With defaultUseRichText=false', async function() {
                        UserSession.instance.set('defaultUseRichText', false);

                        await testLoadScreenshotComments();

                        expect(ajaxData).toEqual({
                            'api_format': 'json',
                            'expand': 'screenshot',
                            'force-text-type': 'html',
                            'include-text-types': 'raw',
                            'max-results': 50,
                        });
                    });

                    it('Deleting comment', async function() {
                        spyOn(window, 'confirm').and.returnValue(true);

                        await testLoadScreenshotComments();

                        expect(dlg._screenshotCommentsCollection.length)
                            .toBe(1);

                        spyOn(dlg._commentViews[0].$el, 'fadeOut')
                            .and.callFake(opts => opts.complete());

                        const caughtEvent = new Promise<void>(resolve => {
                            dlg._screenshotCommentsCollection.at(0).once(
                                'destroyed', () => resolve());
                        });

                        dlg.$('.delete-comment').click();

                        await caughtEvent;
                        expect(dlg._screenshotCommentsCollection.length)
                            .toBe(0);
                    });

                    it('Deleting comment and cancelling', async function() {
                        spyOn(window, 'confirm').and.returnValue(false);

                        await testLoadScreenshotComments();

                        expect(dlg._screenshotCommentsCollection.length)
                            .toBe(1);

                        dlg.$('.delete-comment').click();

                        expect(dlg._screenshotCommentsCollection.length)
                            .toBe(1);
                    });
                });
            });
        });

        describe('Saving', function() {
            let fileAttachmentCommentsPayload;
            let generalCommentsPayload;
            let diffCommentsPayload;
            let screenshotCommentsPayload;
            let commentView;
            let comment;

            async function testSaveComment(richText) {
                const newCommentText = 'New comment text';

                dlg = await createReviewDialog();

                expect(dlg._commentViews.length).toBe(1);

                commentView = dlg._commentViews[0];
                comment = commentView.model;

                spyOn(comment, 'save').and.callFake(() => {
                    comment.trigger('sync');

                    return Promise.resolve();
                });

                /* Set some new state for the comment. */
                commentView.inlineEditorView.startEdit();
                commentView.inlineEditorView.setValue(newCommentText);
                commentView.textEditor.setRichText(richText);
                await commentView.save();

                expect(comment.save).toHaveBeenCalled();
                expect(comment.get('text')).toBe(newCommentText);
                expect(comment.get('richText')).toBe(richText);
            }

            async function testSaveCommentPreventsXSS() {
                const newCommentText =
                    '"><script>window.rbTestFoundXSS = true;</script>';

                delete window.rbTestFoundXSS;

                dlg = await createReviewDialog();

                expect(dlg._commentViews.length).toBe(1);

                commentView = dlg._commentViews[0];
                comment = commentView.model;

                spyOn(comment, 'save').and.callFake(() => {
                    comment.trigger('sync');

                    return Promise.resolve();
                });

                /* Set some new state for the comment. */
                commentView.inlineEditorView.startEdit();
                commentView.inlineEditorView.setValue(newCommentText);
                commentView.textEditor.setRichText(true);

                await commentView.save();

                expect(comment.save).toHaveBeenCalled();
                expect(comment.get('text')).toBe(newCommentText);
                expect(window.rbTestFoundXSS).toBe(undefined);
            }

            beforeEach(function() {
                review.set({
                    id: 42,
                    links: {
                        diff_comments: {
                            href: '/diff-comments/',
                        },
                        file_attachment_comments: {
                            href: '/file-attachment-comments/',
                        },
                        general_comments: {
                            href: '/general-comments/',
                        },
                        screenshot_comments: {
                            href: '/screenshot-comments/',
                        },
                    },
                    loaded: true,
                });

                diffCommentsPayload =
                    _.clone(emptyDiffCommentsPayload);
                screenshotCommentsPayload =
                    _.clone(emptyScreenshotCommentsPayload);
                fileAttachmentCommentsPayload =
                    _.clone(emptyFileAttachmentCommentsPayload);
                generalCommentsPayload =
                    _.clone(emptyGeneralCommentsPayload);

                spyOn(review, 'save').and.resolveTo();

                spyOn($, 'ajax').and.callFake(options => {
                    if (options.url === '/file-attachment-comments/') {
                        options.success(fileAttachmentCommentsPayload);
                    } else if (options.url === '/diff-comments/') {
                        options.success(diffCommentsPayload);
                    } else if (options.url === '/screenshot-comments/') {
                        options.success(screenshotCommentsPayload);
                    } else if (options.url === '/general-comments/') {
                        options.success(generalCommentsPayload);
                    }
                });
            });

            describe('Review properties', function() {
                function testSelfXSS(bodyView, attrName) {
                    const text = '"><script>window.rbTestFoundXSS = true;' +
                                 '</script>';
                    const editor = bodyView.textEditor;

                    delete window.rbTestFoundXSS;

                    bodyView.openEditor();
                    editor.setText(text);
                    editor.setRichText(true);
                    bodyView.save();

                    expect(editor.getText()).toBe(text);
                    expect(review.save).toHaveBeenCalled();
                    expect(review.get(attrName)).toBe(text);
                    expect(window.rbTestFoundXSS).toBe(undefined);
                }

                beforeEach(async function() {
                    dlg = await createReviewDialog();
                });

                describe('Body Top', function() {
                    function runTest(richText) {
                        const text = 'My new text';
                        const bodyTopEditor = dlg._bodyTopView.textEditor;

                        dlg._bodyTopView.openEditor();
                        bodyTopEditor.setText(text);
                        bodyTopEditor.setRichText(richText);
                        dlg._bodyTopView.save();

                        expect(bodyTopEditor.getText()).toBe(text);
                        expect(review.save).toHaveBeenCalled();
                        expect(review.get('bodyTop')).toBe(text);
                        expect(review.get('bodyTopRichText')).toBe(richText);
                    }

                    it('For Markdown', function() {
                        runTest(true);
                    });

                    it('For plain text', function() {
                        runTest(false);
                    });

                    it('Prevents Self-XSS', function() {
                        testSelfXSS(dlg._bodyTopView, 'bodyTop');
                    });
                });

                describe('Body Bottom', function() {
                    function runTest(richText) {
                        const text = 'My new text';
                        const bodyBottomEditor =
                            dlg._bodyBottomView.textEditor;

                        dlg._bodyBottomView.openEditor();
                        bodyBottomEditor.setText(text);
                        bodyBottomEditor.setRichText(richText);
                        dlg._bodyBottomView.save();

                        expect(bodyBottomEditor.getText()).toBe(text);
                        expect(review.save).toHaveBeenCalled();
                        expect(review.get('bodyBottom')).toBe(text);
                        expect(review.get('bodyBottomRichText'))
                            .toBe(richText);
                    }

                    it('For Markdown', function() {
                        runTest(true);
                    });

                    it('For plain text', function() {
                        runTest(false);
                    });

                    it('Prevents Self-XSS', function() {
                        testSelfXSS(dlg._bodyBottomView, 'bodyBottom');
                    });
                });

                describe('Ship It', function() {
                    async function runTest(shipIt) {
                        dlg._$shipIt.prop('checked', shipIt);

                        spyOn(RB, 'navigateTo');

                        await dlg._saveReview();

                        expect(dlg._$shipIt.prop('checked')).toBe(shipIt);
                    }

                    it('Checked', async function() {
                        await runTest(true);
                    });

                    it('Unchecked', async function() {
                        await runTest(false);
                    });
                });
            });

            describe('Diff comments', function() {
                beforeEach(function() {
                    diffCommentsPayload.total_results = 1;
                    diffCommentsPayload.diff_comments = [diffCommentPayload];
                });

                it('For Markdown', async function() {
                    await testSaveComment(true);
                });

                it('For plain text', async function() {
                    await testSaveComment(false);
                });

                it('Prevents Self-XSS', async function() {
                    await testSaveCommentPreventsXSS();
                });
            });

            describe('File attachment comments', function() {
                beforeEach(function() {
                    fileAttachmentCommentsPayload.total_results = 1;
                    fileAttachmentCommentsPayload.file_attachment_comments = [
                        fileAttachmentCommentPayload,
                    ];
                });

                it('For Markdown', async function() {
                    await testSaveComment(true);
                });

                it('For plain text', async function() {
                    await testSaveComment(false);
                });

                it('Prevents Self-XSS', async function() {
                    await testSaveCommentPreventsXSS();
                });
            });

            describe('General comments', function() {
                beforeEach(function() {
                    generalCommentsPayload.total_results = 1;
                    generalCommentsPayload.general_comments = [
                        generalCommentPayload,
                    ];
                });

                it('For Markdown', async function() {
                    await testSaveComment(true);
                });

                it('For plain text', async function() {
                    await testSaveComment(false);
                });
            });

            describe('Screenshot comments', function() {
                beforeEach(function() {
                    screenshotCommentsPayload.total_results = 1;
                    screenshotCommentsPayload.screenshot_comments = [
                        screenshotCommentPayload,
                    ];
                });

                it('For Markdown', async function() {
                    await testSaveComment(true);
                });

                it('For plain text', async function() {
                    await testSaveComment(false);
                });

                it('Prevents Self-XSS', async function() {
                    await testSaveCommentPreventsXSS();
                });
            });
        });
    });
});
