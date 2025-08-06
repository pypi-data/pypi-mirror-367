/**
 * A collection of RB.DiffReviewable instances.
 */

import { BaseCollection, spina } from '@beanbag/spina';
import { type ReviewRequest } from 'reviewboard/common';

import { DiffReviewable } from '../models/diffReviewableModel';
import { type DiffFileCollection } from './diffFileCollection';


/**
 * Options for the DiffReviewableCollection.
 *
 * Version Added:
 *     7.0
 */
export interface DiffReviewableCollectionOptions {
    /** The review request. */
    reviewRequest: ReviewRequest;
}


/**
 * A collection of RB.DiffReviewable instances.
 *
 * This manages a collection of :js:class:`RB.DiffReviewable`s and can
 * populate itself based on changes to a collection of files.
 *
 * When repopulating, this will emit a ``populating`` event. After populating,
 * it will emit a ``populated`` event.
 */
@spina
export class DiffReviewableCollection extends BaseCollection<
    DiffReviewable,
    DiffReviewableCollectionOptions
> {
    static model = DiffReviewable;

    /**********************
     * Instance variables *
     **********************/

    /** The review request. */
    reviewRequest: ReviewRequest;

    /**
     * Initialize the collection.
     *
     * Args:
     *     models (Array):
     *         Optional array of models.
     *
     *     options (object):
     *         Options for the collection.
     *
     * Option Args:
     *     reviewRequest (RB.ReviewRequest):
     *         The review request for the collection. This must be provided.
     */
    initialize(
        models: DiffReviewable[],
        options: DiffReviewableCollectionOptions,
    ) {
        super.initialize(models, options);

        this.reviewRequest = options.reviewRequest;
    }

    /**
     * Watch for changes to a collection of files.
     *
     * When the files change (and when invoking this method), this collection
     * will be rebuilt based on those files.
     *
     * Args:
     *     files (RB.DiffFileCollection):
     *         The collection of files to watch.
     */
    watchFiles(files: DiffFileCollection) {
        this.listenTo(files, 'reset', () => this._populateFromFiles(files));
        this._populateFromFiles(files);
    }

    /**
     * Populate this collection from a collection of files.
     *
     * This will clear this collection and then loop through each file,
     * adding a corresponding :js:class:`RB.DiffReviewable`.
     *
     * After clearing, but prior to adding any entries, this will emit a
     * ``populating`` event. After all reviewables have been added, this
     * will emit a ``populated`` event.
     *
     * Args:
     *     files (RB.DiffFileCollection):
     *         The collection of files to populate from.
     */
    _populateFromFiles(files: DiffFileCollection) {
        const reviewRequest = this.reviewRequest;

        console.assert(
            !!reviewRequest,
            'RB.DiffReviewableCollection.reviewRequest must be set');

        this.reset();
        this.trigger('populating');

        files.each(file => {
            const filediff = file.get('filediff');
            const interfilediff = file.get('interfilediff');
            let interdiffRevision = null;

            if (interfilediff) {
                interdiffRevision = interfilediff.revision;
            } else if (file.get('forceInterdiff')) {
                interdiffRevision = file.get('forceInterdiffRevision');
            }

            this.add({
                baseFileDiffID: file.get('baseFileDiffID'),
                file: file,
                fileDiffID: filediff.id,
                interFileDiffID: interfilediff ? interfilediff.id : null,
                interdiffRevision: interdiffRevision,
                public: file.get('public'),
                reviewRequest: reviewRequest,
                revision: filediff.revision,
                serializedCommentBlocks: file.get('serializedCommentBlocks'),
            });
        });

        this.trigger('populated');
    }
}
