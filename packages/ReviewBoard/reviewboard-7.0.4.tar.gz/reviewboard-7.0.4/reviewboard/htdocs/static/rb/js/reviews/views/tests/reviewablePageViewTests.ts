import { suite } from '@beanbag/jasmine-suites';
import {
    afterEach,
    beforeEach,
    describe,
    expect,
    it,
    pending,
    spyOn,
} from 'jasmine-core';

import {
    EnabledFeatures,
    ReviewRequest,
} from 'reviewboard/common';
import {
    ReviewablePage,
    ReviewDialogView,
    ReviewablePageView,
    UnifiedBannerView,
} from 'reviewboard/reviews';
import { DnDUploader } from 'reviewboard/ui';


suite('rb/pages/views/ReviewablePageView', function() {
    const pageTemplate = dedent`
        <div id="review-banner"></div>
        <div id="unified-banner">
         <div class="rb-c-unified-banner__mode-selector"></div>
        </div>
        <a href="#" id="action-legacy-edit-review">Edit Review</a>
        <a href="#" id="action-legacy-ship-it">Ship It</a>
    `;

    let $editReview;
    let page;
    let pageView;

    beforeEach(function() {
        const $container = $('<div>')
            .html(pageTemplate)
            .appendTo($testsScratch);

        DnDUploader.instance = null;

        $editReview = $container.find('#action-legacy-edit-review');

        page = new ReviewablePage({
            checkForUpdates: false,
            editorData: {
                mutableByUser: true,
                statusMutableByUser: true,
            },
            reviewRequestData: {
                id: 123,
                loaded: true,
                state: ReviewRequest.PENDING,
            },
        }, {
            parse: true,
        });

        spyOn(RB.HeaderView.prototype, '_ensureSingleton');

        pageView = new ReviewablePageView({
            el: $container,
            model: page,
        });

        const reviewRequest = page.get('reviewRequest');
        spyOn(reviewRequest, 'ready').and.resolveTo();
        spyOn(reviewRequest.draft, 'ready').and.resolveTo();
        spyOn(page.get('pendingReview'), 'ready').and.resolveTo();
        spyOn(RB, 'navigateTo');

        pageView.render();
    });

    afterEach(function() {
        DnDUploader.instance = null;

        if (EnabledFeatures.unifiedBanner) {
            UnifiedBannerView.resetInstance();
        }

        pageView.remove();
    });

    describe('Public objects', function() {
        it('reviewRequest', function() {
            expect(page.get('reviewRequest')).not.toBe(undefined);
        });

        it('pendingReview', function() {
            const pendingReview = page.get('pendingReview');

            expect(pendingReview).not.toBe(undefined);
            expect(pendingReview.get('parentObject'))
                .toBe(page.get('reviewRequest'));
        });

        it('commentIssueManager', function() {
            expect(page.commentIssueManager).not.toBe(undefined);
            expect(page.commentIssueManager.get('reviewRequest'))
                .toBe(page.get('reviewRequest'));
        });

        it('reviewRequestEditor', function() {
            const reviewRequestEditor = page.reviewRequestEditor;

            expect(reviewRequestEditor).not.toBe(undefined);
            expect(reviewRequestEditor.get('reviewRequest'))
                .toBe(page.get('reviewRequest'));
            expect(reviewRequestEditor.get('commentIssueManager'))
                .toBe(page.commentIssueManager);
            expect(reviewRequestEditor.get('editable')).toBe(true);
        });

        it('reviewRequestEditorView', function() {
            expect(pageView.reviewRequestEditorView).not.toBe(undefined);
            expect(pageView.reviewRequestEditorView.model)
                .toBe(page.reviewRequestEditor);
        });
    });

    describe('Actions', function() {
        it('Edit Review', function() {
            if (EnabledFeatures.unifiedBanner) {
                pending();

                return;
            }

            spyOn(ReviewDialogView, 'create');

            $editReview.click();

            expect(ReviewDialogView.create).toHaveBeenCalled();

            const options = ReviewDialogView.create.calls.argsFor(0)[0];
            expect(options.review).toBe(page.get('pendingReview'));
            expect(options.reviewRequestEditor).toBe(page.reviewRequestEditor);
        });

        describe('Ship It', function() {
            let pendingReview;

            beforeEach(function() {
                pendingReview = page.get('pendingReview');
            });

            it('Confirmed', async function() {
                if (EnabledFeatures.unifiedBanner) {
                    pending();

                    return;
                }

                spyOn(window, 'confirm').and.returnValue(true);
                spyOn(pendingReview, 'save').and.resolveTo();
                spyOn(pendingReview, 'publish').and.callThrough();

                if (!EnabledFeatures.unifiedBanner) {
                    spyOn(pageView.draftReviewBanner, 'hideAndReload')
                        .and.callFake(() => {
                            expect(window.confirm).toHaveBeenCalled();
                            expect(pendingReview.ready).toHaveBeenCalled();
                            expect(pendingReview.publish).toHaveBeenCalled();
                            expect(pendingReview.save).toHaveBeenCalled();
                            expect(pendingReview.get('shipIt')).toBe(true);
                            expect(pendingReview.get('bodyTop'))
                                .toBe('Ship It!');
                        });
                }

                await pageView.shipIt();
            });

            it('Canceled', async function() {
                if (EnabledFeatures.unifiedBanner) {
                    pending();

                    return;
                }

                spyOn(window, 'confirm').and.returnValue(false);

                await pageView.shipIt();

                expect(window.confirm).toHaveBeenCalled();
                expect(pendingReview.ready).not.toHaveBeenCalled();
            });
        });
    });

    describe('Update bubble', () => {
        const summary = 'My summary';
        const user = {
            fullname: 'Mr. User',
            url: '/users/foo/',
            username: 'user',
        };
        let $bubble;
        let bubbleView;

        beforeEach(() => {
            page.get('reviewRequest').trigger('updated', {
                summary: summary,
                user: user,
            });

            $bubble = $('#updates-bubble');
            bubbleView = pageView._updatesBubble;
        });

        it('Displays', () => {
            expect($bubble.length).toBe(1);
            expect(bubbleView.$el[0]).toBe($bubble[0]);
            expect($bubble.is(':visible')).toBe(true);
            expect($bubble.find('.rb-c-page-updates-bubble__message').html())
                .toBe('My summary by <a href="/users/foo/">Mr. User</a>');
        });

        describe('Actions', () => {
            it('Ignore', done => {
                spyOn(bubbleView, 'close').and.callThrough();
                spyOn(bubbleView, 'trigger').and.callThrough();
                spyOn(bubbleView, 'remove').and.callThrough();

                $bubble.find('[data-action="ignore"]').click();

                _.defer(() => {
                    expect(bubbleView.close).toHaveBeenCalled();
                    expect(bubbleView.remove).toHaveBeenCalled();
                    expect(bubbleView.trigger).toHaveBeenCalledWith('closed');

                    done();
                });
            });

            it('Update Page displays Updates Bubble', () => {
                spyOn(bubbleView, 'trigger');

                $bubble.find('[data-action="update"]').click();

                expect(bubbleView.trigger).toHaveBeenCalledWith('updatePage');
            });

            it('Update Page calls notify if shouldNotify', () => {
                const info = {
                    user: {
                        fullname: 'Hello',
                    },
                };

                RB.NotificationManager.instance._canNotify = true;
                spyOn(RB.NotificationManager.instance, 'notify');
                spyOn(RB.NotificationManager.instance,
                      '_haveNotificationPermissions').and.returnValue(true);
                spyOn(pageView, '_showUpdatesBubble');

                pageView._onReviewRequestUpdated(info);

                expect(RB.NotificationManager.instance.notify)
                    .toHaveBeenCalled();
                expect(pageView._showUpdatesBubble).toHaveBeenCalled();
            });
        });
    });
});
