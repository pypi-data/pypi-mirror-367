import { suite } from '@beanbag/jasmine-suites';
import {
    describe,
    expect,
    it,
    spyOn,
} from 'jasmine-core';

import {
    Review,
    ReviewRequest,
} from 'reviewboard/common';
import { ReviewablePage } from 'reviewboard/reviews';


suite('rb/pages/models/ReviewablePage', function() {
    describe('Construction', function() {
        it('Child objects created', function() {
            const reviewRequest = new ReviewRequest();
            const page = new ReviewablePage({
                editorData: {
                    hasDraft: true,
                    showSendEmail: false,
                },
                pendingReview: new Review(),
                reviewRequest: reviewRequest,
            });

            expect(page.commentIssueManager).toBeTruthy();
            expect(page.commentIssueManager.get('reviewRequest'))
                .toBe(reviewRequest);

            expect(page.reviewRequestEditor.get('commentIssueManager'))
                .toBe(page.commentIssueManager);
            expect(page.reviewRequestEditor.get('reviewRequest'))
                .toBe(reviewRequest);
            expect(page.reviewRequestEditor.get('showSendEmail')).toBe(false);
            expect(page.reviewRequestEditor.get('hasDraft')).toBe(true);
        });
    });

    describe('parse', function() {
        it('{}', function() {
            const page = new ReviewablePage({}, {parse: true});

            expect(page.get('reviewRequest')).toBeTruthy();
            expect(page.get('pendingReview')).toBeTruthy();
            expect(page.get('lastActivityTimestamp')).toBe(null);
            expect(page.get('checkForUpdates')).toBe(false);
            expect(page.get('checkUpdatesType')).toBe(null);

            /* These shouldn't be attributes. */
            expect(page.get('editorData')).toBe(undefined);
            expect(page.get('reviewRequestData')).toBe(undefined);
        });

        it('reviewRequestData', function() {
            const page = new ReviewablePage({
                reviewRequestData: {
                    branch: 'my-branch',
                    bugTrackerURL: 'http://bugs.example.com/--bug_id--/',
                    bugsClosed: [101, 102, 103],
                    closeDescription: 'This is closed',
                    closeDescriptionRichText: true,
                    description: 'This is a description',
                    descriptionRichText: true,
                    hasDraft: true,
                    id: 123,
                    lastUpdatedTimestamp: '2017-08-23T15:10:20Z',
                    localSitePrefix: 's/foo/',
                    public: true,
                    repository: {
                        id: 200,
                        name: 'My repo',
                        requiresBasedir: true,
                        requiresChangeNumber: true,
                        scmtoolName: 'My Tool',
                        supportsPostCommit: true,
                    },
                    reviewURL: '/s/foo/r/123/',
                    state: 'CLOSE_SUBMITTED',
                    summary: 'This is a summary',
                    targetGroups: [
                        {
                            name: 'Some group',
                            url: '/s/foo/groups/some-group/',
                        },
                    ],
                    targetPeople: [
                        {
                            url: '/s/foo/users/some-user/',
                            username: 'some-user',
                        },
                    ],
                    testingDone: 'This is testing done',
                    testingDoneRichText: true,
                    visibility: 'ARCHIVED',
                },
            }, {
                parse: true,
            });

            expect(page.get('pendingReview')).toBeTruthy();
            expect(page.get('checkForUpdates')).toBe(false);
            expect(page.get('reviewRequestData')).toBe(undefined);

            /* Check the review request. */
            const reviewRequest = page.get('reviewRequest');
            expect(reviewRequest).toBeTruthy();
            expect(reviewRequest.id).toBe(123);
            expect(reviewRequest.url())
                .toBe('/s/foo/api/review-requests/123/');
            expect(reviewRequest.get('bugTrackerURL'))
                .toBe('http://bugs.example.com/--bug_id--/');
            expect(reviewRequest.get('localSitePrefix')).toBe('s/foo/');
            expect(reviewRequest.get('branch')).toBe('my-branch');
            expect(reviewRequest.get('bugsClosed')).toEqual([101, 102, 103]);
            expect(reviewRequest.get('closeDescription'))
                .toBe('This is closed');
            expect(reviewRequest.get('closeDescriptionRichText')).toBe(true);
            expect(reviewRequest.get('description'))
                .toBe('This is a description');
            expect(reviewRequest.get('descriptionRichText')).toBe(true);
            expect(reviewRequest.get('hasDraft')).toBe(true);
            expect(reviewRequest.get('lastUpdatedTimestamp'))
                .toBe('2017-08-23T15:10:20Z');
            expect(reviewRequest.get('public')).toBe(true);
            expect(reviewRequest.get('reviewURL')).toBe('/s/foo/r/123/');
            expect(reviewRequest.get('state'))
                .toBe(ReviewRequest.CLOSE_SUBMITTED);
            expect(reviewRequest.get('summary'))
                .toBe('This is a summary');
            expect(reviewRequest.get('targetGroups')).toEqual([{
                name: 'Some group',
                url: '/s/foo/groups/some-group/',
            }]);
            expect(reviewRequest.get('targetPeople')).toEqual([{
                url: '/s/foo/users/some-user/',
                username: 'some-user',
            }]);
            expect(reviewRequest.get('testingDone'))
                .toBe('This is testing done');
            expect(reviewRequest.get('testingDoneRichText')).toBe(true);
            expect(reviewRequest.get('visibility'))
                .toBe(ReviewRequest.VISIBILITY_ARCHIVED);

            /* Check the review request's repository. */
            const repository = reviewRequest.get('repository');
            expect(repository.id).toBe(200);
            expect(repository.get('name')).toBe('My repo');
            expect(repository.get('requiresBasedir')).toBe(true);
            expect(repository.get('requiresChangeNumber')).toBe(true);
            expect(repository.get('scmtoolName')).toBe('My Tool');
            expect(repository.get('supportsPostCommit')).toBe(true);
        });

        it('extraReviewRequestDraftData', function() {
            const page = new ReviewablePage({
                extraReviewRequestDraftData: {
                    changeDescription: 'Draft change description',
                    changeDescriptionRichText: true,
                    interdiffLink: '/s/foo/r/123/diff/1-2/',
                },
            }, {
                parse: true,
            });

            expect(page.get('pendingReview')).toBeTruthy();
            expect(page.get('checkForUpdates')).toBe(false);
            expect(page.get('reviewRequestData')).toBe(undefined);

            const draft = page.get('reviewRequest').draft;
            expect(draft.get('changeDescription'))
                .toBe('Draft change description');
            expect(draft.get('changeDescriptionRichText')).toBe(true);
            expect(draft.get('interdiffLink')).toBe('/s/foo/r/123/diff/1-2/');
        });

        it('editorData', function() {
            const page = new ReviewablePage({
                editorData: {
                    changeDescriptionRenderedText: 'Change description',
                    closeDescriptionRenderedText: 'This is closed',
                    hasDraft: true,
                    mutableByUser: true,
                    showSendEmail: true,
                    statusMutableByUser: true,
                },
            }, {
                parse: true,
            });

            expect(page.get('pendingReview')).toBeTruthy();
            expect(page.get('checkForUpdates')).toBe(false);
            expect(page.get('editorData')).toBe(undefined);

            /* Check the ReviewRequestEditor. */
            const editor = page.reviewRequestEditor;
            expect(editor.get('changeDescriptionRenderedText'))
                .toBe('Change description');
            expect(editor.get('closeDescriptionRenderedText'))
                .toBe('This is closed');
            expect(editor.get('hasDraft')).toBe(true);
            expect(editor.get('mutableByUser')).toBe(true);
            expect(editor.get('showSendEmail')).toBe(true);
            expect(editor.get('statusMutableByUser')).toBe(true);
        });

        it('lastActivityTimestamp', function() {
            const page = new ReviewablePage({
                lastActivityTimestamp: '2017-08-22T18:20:30Z',
                checkUpdatesType: 'diff',
            }, {
                parse: true,
            });

            expect(page.get('lastActivityTimestamp'))
                .toBe('2017-08-22T18:20:30Z');
        });

        it('checkUpdatesType', function() {
            const page = new ReviewablePage({
                checkUpdatesType: 'diff',
            }, {
                parse: true,
            });

            expect(page.get('pendingReview')).toBeTruthy();
            expect(page.get('checkUpdatesType')).toBe('diff');
        });
    });

    describe('Actions', function() {
        it('markShipIt', async function() {
            const page = new ReviewablePage({}, {parse: true});
            const pendingReview = page.get('pendingReview');

            spyOn(pendingReview, 'ready').and.resolveTo();
            spyOn(pendingReview, 'publish');

            await page.markShipIt();

            expect(pendingReview.publish).toHaveBeenCalled();
            expect(pendingReview.get('shipIt')).toBe(true);
            expect(pendingReview.get('bodyTop')).toBe('Ship It!');
        });
    });
});
