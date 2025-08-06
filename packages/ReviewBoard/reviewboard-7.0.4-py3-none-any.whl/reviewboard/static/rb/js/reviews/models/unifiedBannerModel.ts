/**
 * The unified banner model.
 */
import {
    type Result,
    BaseModel,
    spina,
} from '@beanbag/spina';

import {
    type Review,
    type ReviewReply,
    type ReviewRequest,
} from 'reviewboard/common';

import { type ReviewRequestEditor } from './reviewRequestEditorModel';


/**
 * Information about a selectable draft mode.
 *
 * Version Added:
 *     6.0
 */
export interface DraftMode {
    /** The user-visible text to display. */
    text: string;

    /** Whether this mode includes multiple items. */
    multiple: boolean;

    /** Whether this mode includes a review draft. */
    hasReview: boolean;

    /** Whether this mode includes one or more reply drafts. */
    hasReviewReplies: boolean;

    /** Whether this mode includes a review request draft. */
    hasReviewRequest: boolean;

    /** Whether this mode represents a single review reply. */
    singleReviewReply?: number;
}


/**
 * Attributes for the UnifiedBanner model.
 *
 * Version Added:
 *     6.0
 */
interface UnifiedBannerAttrs {
    /** The available draft modes. */
    draftModes: DraftMode[];

    /** The number of total drafts. */
    numDrafts: number;

    /** The pending review, used for any new review content. */
    pendingReview: Review;

    /** The draft review replies. */
    reviewReplyDrafts: ReviewReply[];

    /** The current review request. */
    reviewRequest: ReviewRequest;

    /** The review request editor. */
    reviewRequestEditor: ReviewRequestEditor;

    /** The currently selected draft mode (indexing into draftModes). */
    selectedDraftMode: number;

    /**
     * The message to show about viewing another user's draft.
     *
     * Version Added:
     *     7.0.2
     */
    userDraftMessage: string | null;
}


/**
 * State for the unified banner.
 *
 * Keeps track of drafts for the review request, review, and review replies.
 *
 * Version Added:
 *     6.0
 */
@spina
export class UnifiedBanner extends BaseModel<UnifiedBannerAttrs> {
    static defaults(): Result<Partial<UnifiedBannerAttrs>> {
        return {
            draftModes: [],
            numDrafts: 0,
            pendingReview: null,
            reviewReplyDrafts: [],
            reviewRequest: null,
            reviewRequestEditor: null,
            selectedDraftMode: 0,
            userDraftMessage: null,
        };
    }

    /**
     * Initialize the Unified Review Banner State.
     *
     * Sets listeners on the saved and destroy events for the review request
     * and review to re-check if the state has at least one draft. At the end
     * of initialization, checks if at least one draft exists already.
     */
    initialize() {
        const editor = this.get('reviewRequestEditor');
        const reviewRequest = this.get('reviewRequest');
        const pendingReview = this.get('pendingReview');
        console.assert(!!reviewRequest, 'reviewRequest must be provided');
        console.assert(!!pendingReview, 'pendingReview must be provided');

        this.listenTo(editor, 'change:hasDraft',
                      this.#updateDraftModes);
        this.listenTo(reviewRequest.draft, 'saved destroyed',
                      this.#updateDraftModes);
        this.listenTo(pendingReview, 'saved destroyed',
                      this.#updateDraftModes);

        /*
         * We swallow errors when calling ready() on the draft, because we
         * often will not have permissions to access the draft resource.
         */
        Promise.all([
            reviewRequest.draft.ready()
                .catch(() => undefined),
            pendingReview.ready(),
        ]).then(() => this.#updateDraftModes());
    }

    /**
     * Update the draft state for the given review reply.
     *
     * Args:
     *     reviewReply (ReviewReply):
     *         The review reply model.
     *
     *     hasReviewReplyDraft (boolean):
     *          Whether the reviewReply passed in has a draft.
     */
    updateReplyDraftState(
        reviewReply: ReviewReply,
        hasReviewReplyDraft: boolean,
    ) {
        const reviewReplyDrafts = this.get('reviewReplyDrafts');

        if (hasReviewReplyDraft) {
            if (!reviewReplyDrafts.includes(reviewReply)) {
                reviewReplyDrafts.push(reviewReply);
                this.set('reviewReplyDrafts', reviewReplyDrafts);
            }
        } else {
            this.set('reviewReplyDrafts',
                     _.without(reviewReplyDrafts, reviewReply));
        }

        this.#updateDraftModes();
    }

    /**
     * Update the list of available draft modes.
     */
    #updateDraftModes() {
        const editor = this.get('reviewRequestEditor');
        const forceViewUserDraft = editor.get('forceViewUserDraft');
        const userDraftExists = editor.get('userDraftExists');
        const viewingUserDraft = editor.get('viewingUserDraft');

        const reviewRequest = this.get('reviewRequest');
        const pendingReview = this.get('pendingReview');
        const reviewReplyDrafts = this.get('reviewReplyDrafts');

        const reviewRequestPublic = reviewRequest.get('public');

        const reviewRequestDraft = (
            !reviewRequest.draft.isNew() &&
            !editor.hasUnviewedUserDraft);

        const reviewDraft = !pendingReview.isNew();
        const numReplies = reviewReplyDrafts.length;
        const numDrafts = (numReplies +
                           (reviewRequestDraft ? 1 : 0) +
                           (reviewDraft ? 1 : 0));

        const draftModes: DraftMode[] = [];

        if (!reviewRequestPublic) {
            /* Review request has never been published */

            if (reviewDraft) {
                /* Review request draft + review draft */
                draftModes.push({
                    hasReview: true,
                    hasReviewReplies: false,
                    hasReviewRequest: true,
                    multiple: true,
                    text: _`Draft and review`,
                });

                draftModes.push({
                    hasReview: false,
                    hasReviewReplies: false,
                    hasReviewRequest: true,
                    multiple: false,
                    text: _`Review request draft`,
                });
                draftModes.push({
                    hasReview: true,
                    hasReviewReplies: false,
                    hasReviewRequest: false,
                    multiple: false,
                    text: _`Review of the change`,
                });
            } else {
                draftModes.push({
                    hasReview: false,
                    hasReviewReplies: false,
                    hasReviewRequest: true,
                    multiple: false,
                    text: _`This review request is a draft`,
                });
            }
        } else if (reviewRequestDraft) {
            /* Review request draft */

            if (reviewDraft) {
                /* Review request draft + review draft */
                draftModes.push({
                    hasReview: false,
                    hasReviewReplies: false,
                    hasReviewRequest: true,
                    multiple: false,
                    text: _`Review request changes`,
                });
                draftModes.push({
                    hasReview: true,
                    hasReviewReplies: false,
                    hasReviewRequest: false,
                    multiple: false,
                    text: _`Review of the change`,
                });

                if (numReplies > 0) {
                    /* Review request draft + review draft + reply drafts */
                    draftModes.unshift({
                        hasReview: true,
                        hasReviewReplies: true,
                        hasReviewRequest: true,
                        multiple: true,
                        text: ngettext(
                            `Changes, review, and ${numReplies} reply`,
                            `Changes, review, and ${numReplies} replies`,
                            numReplies),
                    });
                } else {
                    draftModes.unshift({
                        hasReview: true,
                        hasReviewReplies: false,
                        hasReviewRequest: true,
                        multiple: true,
                        text: _`Changes and review`,
                    });
                }
            } else {
                if (numReplies > 0) {
                    /* Review request draft + reply drafts */
                    draftModes.push({
                        hasReview: false,
                        hasReviewReplies: true,
                        hasReviewRequest: true,
                        multiple: true,
                        text: ngettext(`Changes and ${numReplies} reply`,
                                       `Changes and ${numReplies} replies`,
                                       numReplies),
                    });
                    draftModes.push({
                        hasReview: false,
                        hasReviewReplies: false,
                        hasReviewRequest: true,
                        multiple: false,
                        text: _`Review request changes`,
                    });
                } else {
                    /* Review request draft only */
                    draftModes.push({
                        hasReview: false,
                        hasReviewReplies: false,
                        hasReviewRequest: true,
                        multiple: false,
                        text: _`Your review request has changed`,
                    });
                }
            }
        } else if (reviewDraft) {
            /* Review draft */

            if (numReplies > 0) {
                /* Review draft + reply drafts */
                draftModes.push({
                    hasReview: true,
                    hasReviewReplies: true,
                    hasReviewRequest: false,
                    multiple: true,
                    text: ngettext(`Review and ${numReplies} reply`,
                                   `Review and ${numReplies} replies`,
                                   numReplies),
                });
                draftModes.push({
                    hasReview: true,
                    hasReviewReplies: false,
                    hasReviewRequest: false,
                    multiple: false,
                    text: _`Review of the change`,
                });
            } else {
                /* Review draft only */
                draftModes.push({
                    hasReview: true,
                    hasReviewReplies: false,
                    hasReviewRequest: false,
                    multiple: false,
                    text: _`Reviewing this change`,
                });
            }
        } else {
            if (numReplies > 1) {
                /* Multiple reply drafts */
                draftModes.push({
                    hasReview: false,
                    hasReviewReplies: true,
                    hasReviewRequest: false,
                    multiple: true,
                    text: _`${numReplies} replies`,
                });
            }
        }

        for (let i = 0; i < reviewReplyDrafts.length; i++) {
            const replyDraft = reviewReplyDrafts[i];
            const review = replyDraft.get('parentObject');

            draftModes.push({
                hasReview: false,
                hasReviewReplies: true,
                hasReviewRequest: false,
                multiple: false,
                singleReviewReply: i,
                text: _`Replying to ${review.get('authorName')}'s review`,
            });
        }

        let selectedDraftMode = this.get('selectedDraftMode');

        if (selectedDraftMode >= draftModes.length) {
            selectedDraftMode = 0;
        }

        let userDraftMessage: string | null = null;

        /*
         * These handle the case where the user is viewing another user's
         * review request, and they have permission to access/manage
         * the draft. In the case of review requests which are public,
         * they can then switch between the published/draft states.
         */
        if (viewingUserDraft) {
            userDraftMessage = _`
                You are viewing an unpublished draft on a review request owned
                by another user.
            `;

            if (!forceViewUserDraft) {
                userDraftMessage +=
                    ` <a href="#">${_`View only published data.`}</a>`;
            }
        } else if (userDraftExists) {
            userDraftMessage = _`
                This review request has an unpublished draft.
            `;

            if (!forceViewUserDraft) {
                userDraftMessage += ` <a href="#">${_`View draft data.`}</a>`;
            }
        }

        this.set({
            draftModes,
            numDrafts,
            selectedDraftMode,
            userDraftMessage,
        });
    }
}
