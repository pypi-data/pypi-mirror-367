import { suite } from '@beanbag/jasmine-suites';
import {
    beforeEach,
    describe,
    expect,
    it,
    spyOn,
} from 'jasmine-core';

import { ReviewRequest } from 'reviewboard/common';
import { DiffViewerPage } from 'reviewboard/reviews';


suite('rb/pages/models/DiffViewerPage', function() {
    describe('parse', function() {
        it('{}', function() {
            const page = new DiffViewerPage({}, {parse: true});

            expect(page.get('allChunksCollapsed')).toBeFalse();
            expect(page.get('canDownloadDiff')).toBeFalse();
            expect(page.get('canToggleExtraWhitespace')).toBeFalse();
            expect(page.get('reviewRequest')).toBeTruthy();
            expect(page.get('pendingReview')).toBeTruthy();
            expect(page.get('lastActivityTimestamp')).toBe(null);
            expect(page.get('checkForUpdates')).toBe(false);
            expect(page.get('checkUpdatesType')).toBe(null);
            expect(page.get('numDiffs')).toBe(0);

            expect(page.commentsHint).not.toBe(null);
            expect(page.files).not.toBe(null);
            expect(page.pagination).not.toBe(null);
            expect(page.revision).not.toBe(null);

            /* These shouldn't be attributes. */
            expect(page.get('editorData')).toBe(undefined);
            expect(page.get('reviewRequestData')).toBe(undefined);
        });

        it('Diff view options', function() {
            const page = new DiffViewerPage({
                allChunksCollapsed: true,
                canToggleExtraWhitespace: true,
            }, {
                parse: true,
            });

            expect(page.get('allChunksCollapsed')).toBeTrue();
            expect(page.get('canToggleExtraWhitespace')).toBeTrue();
        });

        it('reviewRequestData', function() {
            const page = new DiffViewerPage({
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
            const page = new DiffViewerPage({
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
            const page = new DiffViewerPage({
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
            const page = new DiffViewerPage({
                checkUpdatesType: 'diff',
                lastActivityTimestamp: '2017-08-22T18:20:30Z',
            }, {
                parse: true,
            });

            expect(page.get('lastActivityTimestamp'))
                .toBe('2017-08-22T18:20:30Z');
        });

        it('checkUpdatesType', function() {
            const page = new DiffViewerPage({
                checkUpdatesType: 'diff',
            }, {
                parse: true,
            });

            expect(page.get('pendingReview')).toBeTruthy();
            expect(page.get('checkUpdatesType')).toBe('diff');
        });

        it('comments_hint', function() {
            const page = new DiffViewerPage({
                comments_hint: {
                    commits_with_comments: [
                        {
                            base_commit_id: '18375be',
                            base_commit_pk: 34,
                            is_current: false,
                            revision: 1,
                            tip_commit_id: 'efd582c',
                            tip_commit_pk: 39,
                        },
                    ],
                    diffsets_with_comments: [
                        {
                            is_current: false,
                            revision: 1,
                        },
                    ],
                    has_other_comments: true,
                    interdiffs_with_comments: [
                        {
                            is_current: true,
                            new_revision: 2,
                            old_revision: 1,
                        },
                    ],
                },
            }, {
                parse: true,
            });

            const commentsHint = page.commentsHint;
            expect(commentsHint.get('hasOtherComments')).toBe(true);
            expect(commentsHint.get('commitsWithComments')).toEqual([
                {
                    baseCommitID: '18375be',
                    baseCommitPK: 34,
                    isCurrent: false,
                    revision: 1,
                    tipCommitID: 'efd582c',
                    tipCommitPK: 39,
                },
            ]),
            expect(commentsHint.get('diffsetsWithComments')).toEqual([
                {
                    isCurrent: false,
                    revision: 1,
                },
            ]);
            expect(commentsHint.get('interdiffsWithComments')).toEqual([
                {
                    isCurrent: true,
                    newRevision: 2,
                    oldRevision: 1,
                },
            ]);
        });
    });

    describe('loadDiffRevision', function() {
        let page;

        beforeEach(function() {
            page = new DiffViewerPage({
                reviewRequestData: {
                    id: 123,
                },
            }, {
                parse: true,
            });

            spyOn($, 'ajax').and.callFake(url => {
                const query = {};
                const queryParams = url.split('?')[1].split('&');

                for (let i = 0; i < queryParams.length; i++) {
                    const pair = queryParams[i].split('=');
                    query[decodeURIComponent(pair[0])] =
                        decodeURIComponent(pair[1]);
                }

                return {
                    done: cb => cb({
                        diff_context: {
                            revision: {
                                interdiff_revision:
                                    query['interdiff-revision'] || null,
                                revision: query.revision,
                            },
                        },
                    }),
                };
            });
        });

        describe('Generates URL for', function() {
            it('First page, normal diffs', function() {
                page.loadDiffRevision({
                    page: 1,
                    revision: 1,
                });

                expect($.ajax).toHaveBeenCalledWith(
                    '/api/review-requests/123/diff-context/?revision=1');
            });

            it('Other page, normal diffs', function() {
                page.loadDiffRevision({
                    page: 2,
                    revision: 1,
                });

                expect($.ajax).toHaveBeenCalledWith(
                    '/api/review-requests/123/diff-context/' +
                    '?revision=1&page=2');
            });

            it('First page, interdiffs', function() {
                page.loadDiffRevision({
                    interdiffRevision: 2,
                    page: 1,
                    revision: 1,
                });

                expect($.ajax).toHaveBeenCalledWith(
                    '/api/review-requests/123/diff-context/' +
                    '?revision=1&interdiff-revision=2');
            });

            it('Other page, interdiffs', function() {
                page.loadDiffRevision({
                    interdiffRevision: 2,
                    page: 2,
                    revision: 1,
                });

                expect($.ajax).toHaveBeenCalledWith(
                    '/api/review-requests/123/diff-context/' +
                    '?revision=1&interdiff-revision=2&page=2');
            });

            it('Filename patterns', function() {
                page.loadDiffRevision({
                    filenamePatterns: '*.txt,src/*',
                    page: 2,
                    revision: 1,
                });

                expect($.ajax).toHaveBeenCalledWith(
                    '/api/review-requests/123/diff-context/' +
                    '?revision=1&page=2&filenames=*.txt%2Csrc%2F*');
            });
        });

        describe('Sets canDownloadDiff to', function() {
            it('true for normal diffs', function() {
                page.loadDiffRevision({
                    revision: 1,
                });
                expect(page.get('canDownloadDiff')).toBe(true);
            });

            it('false for interdiffs', function() {
                page.loadDiffRevision({
                    interdiffRevision: 2,
                    revision: 1,
                });
                expect(page.get('canDownloadDiff')).toBe(false);
            });
        });
    });
});
