import { suite } from '@beanbag/jasmine-suites';
import {
    beforeEach,
    describe,
    expect,
    it,
    spyOn,
} from 'jasmine-core';

import {
    BaseComment,
    BaseResource,
    ReviewRequest,
    UserSession,
} from 'reviewboard/common';
import { CommentEditor } from 'reviewboard/reviews';


suite('rb/models/CommentEditor', function() {
    let editor;
    let reviewRequest;
    let comment;

    function createComment() {
        return new BaseComment({
            parentObject: new BaseResource({
                'public': true,
            }),
        });
    }

    beforeEach(function() {
        reviewRequest = new ReviewRequest();

        editor = new CommentEditor({
            canEdit: true,
            reviewRequest: reviewRequest,
        });
    });

    describe('Attribute defaults', function() {
        describe('canEdit', function() {
            it('When logged in and hasDraft=false', function() {
                UserSession.instance.set('authenticated', true);

                editor = new CommentEditor({
                    reviewRequest: reviewRequest,
                });
                expect(editor.get('canEdit')).toBe(true);
            });

            it('When logged in and hasDraft=true', function() {
                UserSession.instance.set('authenticated', true);
                reviewRequest.set('hasDraft', true);

                editor = new CommentEditor({
                    reviewRequest: reviewRequest,
                });
                expect(editor.get('canEdit')).toBe(true);
            });

            it('When logged out', function() {
                UserSession.instance.set('authenticated', false);

                editor = new CommentEditor({
                    reviewRequest: reviewRequest,
                });
                expect(editor.get('canEdit')).toBe(false);
            });

            it('With explicitly set value', function() {
                UserSession.instance.set('authenticated', false);

                editor = new CommentEditor({
                    canEdit: true,
                    reviewRequest: reviewRequest,
                });
                expect(editor.get('canEdit')).toBe(true);
            });
        });

        describe('openIssue', function() {
            it('When user preference is true', function() {
                UserSession.instance.set('commentsOpenAnIssue', true);

                editor = new CommentEditor({
                    reviewRequest: reviewRequest,
                });
                expect(editor.get('openIssue')).toBe(true);
            });

            it('When user preference is false', function() {
                UserSession.instance.set('commentsOpenAnIssue', false);

                editor = new CommentEditor({
                    reviewRequest: reviewRequest,
                });
                expect(editor.get('openIssue')).toBe(false);
            });

            it('With explicitly set value', function() {
                UserSession.instance.set('commentsOpenAnIssue', false);

                editor = new CommentEditor({
                    openIssue: true,
                    reviewRequest: reviewRequest,
                });
                expect(editor.get('openIssue')).toBe(true);
            });

            it('When reloading the page with explicitly set value', function() {
                UserSession.instance.set('commentsOpenAnIssue', true);

                comment = createComment();
                comment.set({
                    issueOpened: false,
                    loaded: false,
                });

                editor = new CommentEditor({
                    comment: comment,
                    reviewRequest: reviewRequest,
                });
                expect(editor.get('openIssue')).toBe(false);
            });
        });

        describe('richText', function() {
            it('When user preference is true', function() {
                UserSession.instance.set('defaultUseRichText', true);

                editor = new CommentEditor({
                    reviewRequest: reviewRequest,
                });
                expect(editor.get('richText')).toBe(true);
            });

            it('When user preference is false', function() {
                UserSession.instance.set('defaultUseRichText', false);

                editor = new CommentEditor({
                    reviewRequest: reviewRequest,
                });
                expect(editor.get('richText')).toBe(false);
            });

            it('With explicitly set value', function() {
                UserSession.instance.set('defaultUseRichText', false);

                editor = new CommentEditor({
                    reviewRequest: reviewRequest,
                    richText: true,
                });
                expect(editor.get('richText')).toBe(true);
            });
        });
    });

    describe('Loading comment', function() {
        describe('With comment richText=true', function() {
            let comment;

            beforeEach(function() {
                comment = createComment();

                comment.set({
                    id: 123,
                    loaded: true,
                    markdownTextFields: {
                        text: 'this \\_is\\_ a _test_',
                    },
                    rawTextFields: {
                        text: 'this \\_is\\_ a _test_',
                    },
                    richText: true,
                    text: '<p>this _is_ a <em>test</em></p>',
                });
            });

            it('When defaultUseRichText=true', function() {
                UserSession.instance.set('defaultUseRichText', true);
                editor.set('comment', comment);
                editor.beginEdit();

                expect(editor.get('dirty')).toBe(false);
                expect(editor.get('richText')).toBe(true);
                expect(editor.get('text')).toBe('this \\_is\\_ a _test_');
            });

            it('When defaultUseRichText=false', function() {
                UserSession.instance.set('defaultUseRichText', false);
                editor.set('comment', comment);
                editor.beginEdit();

                expect(editor.get('dirty')).toBe(false);
                expect(editor.get('richText')).toBe(true);
                expect(editor.get('text')).toBe('this \\_is\\_ a _test_');
            });
        });

        describe('With comment richText=false', function() {
            let comment;

            beforeEach(function() {
                comment = createComment();

                comment.set({
                    id: 123,
                    loaded: true,
                    markdownTextFields: {
                        text: 'this \\_is\\_ a \\_test\\_',
                    },
                    rawTextFields: {
                        text: 'this _is_ a _test_',
                    },
                    richText: false,
                    text: '<p>this _is_ a test</p>',
                });
            });

            it('When defaultUseRichText=true', function() {
                UserSession.instance.set('defaultUseRichText', true);
                editor.set('comment', comment);
                editor.beginEdit();

                expect(editor.get('dirty')).toBe(false);
                expect(editor.get('richText')).toBe(true);
                expect(editor.get('text')).toBe('this \\_is\\_ a \\_test\\_');
            });

            it('When defaultUseRichText=false', function() {
                UserSession.instance.set('defaultUseRichText', false);
                editor.set('comment', comment);
                editor.beginEdit();

                expect(editor.get('dirty')).toBe(false);
                expect(editor.get('richText')).toBe(false);
                expect(editor.get('text')).toBe('this _is_ a _test_');
            });
        });
    });

    describe('Capability states', function() {
        describe('canDelete', function() {
            it('When not editing', function() {
                expect(editor.get('editing')).toBe(false);
                expect(editor.get('canDelete')).toBe(false);
            });

            it('When editing new comment', function() {
                editor.set('comment', createComment());

                editor.beginEdit();
                expect(editor.get('canDelete')).toBe(false);
            });

            it('When editing existing comment', function() {
                const comment = createComment();
                comment.set({
                    id: 123,
                    loaded: true,
                });
                editor.set('comment', comment);

                editor.beginEdit();
                expect(editor.get('canDelete')).toBe(true);
            });

            it('When editing existing comment with canEdit=false', function() {
                const comment = createComment();
                comment.set({
                    id: 123,
                    loaded: true,
                });

                editor.set({
                    canEdit: false,
                    comment: comment,
                });

                expect(() => editor.beginEdit()).toThrow();
                expect(console.assert).toHaveBeenCalled();
                expect(editor.get('canDelete')).toBe(false);
            });
        });

        describe('canSave', function() {
            it('When not editing', function() {
                expect(editor.get('editing')).toBe(false);
                expect(editor.get('canSave')).toBe(false);
            });

            it('When editing comment with text', function() {
                const comment = createComment();
                editor.set('comment', comment);
                editor.beginEdit();
                editor.set('text', 'Foo');
                expect(editor.get('canSave')).toBe(true);
            });

            it('When editing comment with initial state', function() {
                const comment = createComment();
                editor.set('comment', comment);
                editor.beginEdit();
                expect(editor.get('canSave')).toBe(false);
            });

            it('When editing comment without text', function() {
                const comment = createComment();
                editor.set('comment', comment);
                editor.beginEdit();
                editor.set('text', '');
                expect(editor.get('canSave')).toBe(false);
            });
        });
    });

    describe('States', function() {
        describe('dirty', function() {
            it('Initial state', function() {
                expect(editor.get('dirty')).toBe(false);
            });

            it('After new comment', function() {
                const comment = createComment();
                editor.set('dirty', true);
                editor.set('comment', comment);

                expect(editor.get('dirty')).toBe(false);
            });

            it('After text change', function() {
                editor.set('comment', createComment());
                editor.beginEdit();
                editor.set('text', 'abc');
                expect(editor.get('dirty')).toBe(true);
            });

            it('After toggling Open Issue', function() {
                editor.set('comment', createComment());
                editor.beginEdit();
                editor.set('openIssue', 'true');
                expect(editor.get('dirty')).toBe(true);
            });

            it('After saving', async function() {
                const comment = createComment();
                editor.set('comment', comment);

                editor.beginEdit();
                editor.set('text', 'abc');
                expect(editor.get('dirty')).toBe(true);

                spyOn(comment, 'save').and.resolveTo();

                await editor.save();
                expect(editor.get('dirty')).toBe(false);
            });

            it('After deleting', async function() {
                const comment = createComment();
                comment.set({
                    id: 123,
                    loaded: true,
                });
                editor.set('comment', comment);

                editor.beginEdit();
                editor.set('text', 'abc');
                expect(editor.get('dirty')).toBe(true);

                spyOn(comment, 'destroy').and.resolveTo();

                await editor.deleteComment();
                expect(editor.get('dirty')).toBe(false);
            });
        });
    });

    describe('Operations', function() {
        it('setExtraData', function() {
            editor.setExtraData('key1', 'strvalue');
            editor.setExtraData('key2', 42);

            expect(editor.get('extraData')).toEqual({
                key1: 'strvalue',
                key2: 42,
            });
        });

        it('getExtraData', function() {
            editor.set('extraData', {
                mykey: 'value',
            });

            expect(editor.getExtraData('mykey')).toBe('value');
        });

        describe('beginEdit', function() {
            it('With canEdit=true', function() {
                editor.set({
                    canEdit: true,
                    comment: createComment(),
                });

                editor.beginEdit();
                expect(console.assert.calls.argsFor(0)[0]).toBeTruthy();
            });

            it('With canEdit=false', function() {
                editor.set({
                    canEdit: false,
                    comment: createComment(),
                });

                expect(function() { editor.beginEdit(); }).toThrow();
                expect(console.assert.calls.argsFor(0)[0]).toBeFalsy();
            });

            it('With no comment', function() {
                expect(function() { editor.beginEdit(); }).toThrow();
                expect(console.assert.calls.argsFor(0)[0]).toBeTruthy();
                expect(console.assert.calls.argsFor(1)[0]).toBeFalsy();
            });
        });

        describe('cancel', function() {
            beforeEach(function() {
                spyOn(editor, 'close');
                spyOn(editor, 'trigger');
            });

            it('With comment', function() {
                const comment = createComment();
                spyOn(comment, 'destroyIfEmpty');
                editor.set('comment', comment);

                editor.cancel();
                expect(comment.destroyIfEmpty).toHaveBeenCalled();
                expect(editor.trigger).toHaveBeenCalledWith('canceled');
                expect(editor.close).toHaveBeenCalled();
            });

            it('Without comment', function() {
                editor.cancel();
                expect(editor.trigger).not.toHaveBeenCalledWith('canceled');
                expect(editor.close).toHaveBeenCalled();
            });
        });

        describe('destroy', function() {
            let comment;

            beforeEach(function() {
                comment = createComment();

                spyOn(comment, 'destroy').and.resolveTo();
                spyOn(editor, 'close');
                spyOn(editor, 'trigger');
            });

            it('With canDelete=false', async function() {
                /* Set these in order, to override canDelete. */
                editor.set('comment', comment);
                editor.set('canDelete', false);

                await expectAsync(editor.deleteComment()).toBeRejectedWith(
                    Error('deleteComment() called when canDelete is false.'));
                expect(console.assert.calls.argsFor(0)[0]).toBeFalsy();
                expect(comment.destroy).not.toHaveBeenCalled();
                expect(editor.trigger).not.toHaveBeenCalledWith('deleted');
                expect(editor.close).not.toHaveBeenCalled();
            });

            it('With canDelete=true', async function() {
                /* Set these in order, to override canDelete. */
                editor.set('comment', comment);
                editor.set('canDelete', true);

                await editor.deleteComment();
                expect(console.assert.calls.argsFor(0)[0]).toBeTruthy();
                expect(comment.destroy).toHaveBeenCalled();
                expect(editor.trigger).toHaveBeenCalledWith('deleted');
                expect(editor.close).toHaveBeenCalled();
            });
        });

        describe('save', function() {
            let comment;

            beforeEach(function() {
                comment = createComment();
                spyOn(comment, 'save').and.resolveTo();
                spyOn(editor, 'trigger');
            });

            it('With canSave=false', async function() {
                /* Set these in order, to override canSave. */
                editor.set('comment', comment);
                editor.set('canSave', false);

                await expectAsync(editor.save()).toBeRejectedWith(
                    Error('save() called when canSave is false.'));
                expect(console.assert.calls.argsFor(0)[0]).toBeFalsy();
                expect(comment.save).not.toHaveBeenCalled();
                expect(editor.trigger).not.toHaveBeenCalledWith('saved');
            });

            it('With canSave=true', async function() {
                /* Set these in order, to override canSave. */
                const text = 'My text';
                const issueOpened = true;

                comment.set('issueOpened', false);
                editor.set('comment', comment);
                editor.set({
                    canSave: true,
                    issue_opened: issueOpened,
                    richText: true,
                    text: text,
                });
                editor.setExtraData('mykey', 'myvalue');

                await editor.save();

                expect(console.assert.calls.argsFor(0)[0]).toBeTruthy();
                expect(comment.save).toHaveBeenCalled();
                expect(comment.get('text')).toBe(text);
                expect(comment.get('issueOpened')).toBe(issueOpened);
                expect(comment.get('richText')).toBe(true);
                expect(comment.get('extraData')).toEqual({
                    mykey: 'myvalue',
                    require_verification: false,
                });
                expect(editor.get('dirty')).toBe(false);
                expect(editor.trigger).toHaveBeenCalledWith('saved');
            });

            it('With callbacks', function(done) {
                /* Set these in order, to override canSave. */
                const text = 'My text';
                const issueOpened = true;

                comment.set('issueOpened', false);
                editor.set('comment', comment);
                editor.set({
                    canSave: true,
                    issue_opened: issueOpened,
                    richText: true,
                    text: text,
                });
                editor.setExtraData('mykey', 'myvalue');

                spyOn(console, 'warn');

                editor.save({
                    error: () => done.fail(),
                    success: () => {
                        expect(console.assert.calls.argsFor(0)[0])
                            .toBeTruthy();
                        expect(comment.save).toHaveBeenCalled();
                        expect(comment.get('text')).toBe(text);
                        expect(comment.get('issueOpened')).toBe(issueOpened);
                        expect(comment.get('richText')).toBe(true);
                        expect(comment.get('extraData')).toEqual({
                            mykey: 'myvalue',
                            require_verification: false,
                        });
                        expect(editor.get('dirty')).toBe(false);
                        expect(editor.trigger).toHaveBeenCalledWith('saved');
                        expect(console.warn).toHaveBeenCalled();

                        done();
                    },
                });
            });
        });
    });
});
