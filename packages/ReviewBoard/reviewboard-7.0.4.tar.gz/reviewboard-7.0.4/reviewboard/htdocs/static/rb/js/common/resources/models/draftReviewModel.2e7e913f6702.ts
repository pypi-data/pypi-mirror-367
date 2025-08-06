/**
 * A draft review.
 */

import {
    type Result,
    spina,
} from '@beanbag/spina';

import * as JSONSerializers from '../utils/serializers';
import {
    type SerializerMap,
    type SaveOptions,
} from './baseResourceModel';
import { DraftResourceModelMixin } from './draftResourceModelMixin';
import {
    type ReviewAttrs,
    type ReviewResourceData,
    Review,
} from './reviewModel';


/**
 * Attributes for the DraftReview model.
 *
 * Version Added:
 *     6.0
 */
export interface DraftReviewAttrs extends ReviewAttrs {
    /** Whether to archive the review request after publishing the review. */
    publishAndArchive: boolean;

    /** Whether to limit e-mails to only the owner of the review request. */
    publishToOwnerOnly: boolean;
}


/**
 * Resource data for the DraftReview model.
 *
 * Version Added:
 *     7.0
 */
export interface DraftReviewResourceData extends ReviewResourceData {
    publish_and_archive: boolean;
    publish_to_owner_only: boolean;
}


/**
 * A draft review.
 *
 * Draft reviews are more complicated than most objects. A draft may already
 * exist on the server, in which case we need to be able to get its ID. A
 * special resource exists at /reviews/draft/ which will redirect to the
 * existing draft if one exists, and return 404 if not.
 */
@spina({
    mixins: [DraftResourceModelMixin],
})
export class DraftReview extends Review<
    DraftReviewAttrs,
    DraftReviewResourceData
> {
    static defaults: Result<Partial<DraftReviewAttrs>> = {
        publishAndArchive: false,
        publishToOwnerOnly: false,
    };

    static attrToJsonMap: { [key: string]: string } = {
        publishAndArchive: 'publish_and_archive',
        publishToOwnerOnly: 'publish_to_owner_only',
    };

    static serializedAttrs = [
        'publishAndArchive',
        'publishToOwnerOnly',
    ].concat(Review.serializedAttrs);

    static serializers: SerializerMap = {
        publishAndArchive: JSONSerializers.onlyIfValue,
        publishToOwnerOnly: JSONSerializers.onlyIfValue,
    };

    /**
     * Publish the review.
     *
     * Before publish, the "publishing" event will be triggered.
     *
     * After the publish has succeeded, the "published" event will be
     * triggered.
     *
     * Version Changed:
     *     5.0:
     *     Deprecated the callbacks and added a promise return value.
     *
     * Args:
     *     options (object, optional):
     *         Options for the operation.
     *
     *     context (object, optional):
     *         Context to bind when calling callbacks.
     *
     * Returns:
     *     Promise:
     *     A promise which resolves when the operation is complete.
     */
    async publish(
        options: SaveOptions = {},
        context: object = undefined,
    ) {
        if (_.isFunction(options.success) ||
            _.isFunction(options.error) ||
            _.isFunction(options.complete)) {
            console.warn(`RB.DraftReview.publish was called using callbacks.
                          Callers should be updated to use promises instead.`);

            return RB.promiseToCallbacks(
                options, context, newOptions => this.publish(newOptions));
        }

        this.trigger('publishing');

        await this.ready();

        this.set('public', true);

        try {
            await this.save({ attrs: options.attrs });
        } catch (err) {
            this.trigger('publishError', err.xhr.errorText);
            throw err;
        }

        this.trigger('published');
    }
}
