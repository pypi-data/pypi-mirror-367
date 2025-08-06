/**
 * The unified banner view.
 */
import {
    MenuButtonView,
    MenuItem,
    MenuItemType,
    MenuItemsCollection,
    MenuView,
    craft,
    paint,
    renderInto,
} from '@beanbag/ink';
import {
    type EventsHash,
    BaseView,
    spina,
} from '@beanbag/spina';
import _ from 'underscore';

import {
    ClientCommChannel,
    ReviewRequest,
    UserSession,
} from 'reviewboard/common';
import {
    FloatingBannerView,
    contentViewport,
} from 'reviewboard/ui';

import {
    type DraftMode,
    UnifiedBanner,
} from '../models/unifiedBannerModel';
import { type ReviewRequestEditorView } from './reviewRequestEditorView';
import { ChangeDescriptionFieldView } from './reviewRequestFieldViews';


/**
 * A view for a dropdown menu within the unified banner.
 *
 * Version Added:
 *     6.0
 */
@spina
class DraftModeMenu extends BaseView<UnifiedBanner> {
    static className = 'rb-c-unified-banner__menu';

    /**
     * The events to listen to.
     */
    static events: EventsHash = {
        'focusout': '_onFocusOut',
        'keydown': '_onKeyDown',
        'mouseenter': '_openMenu',
        'mouseleave': '_closeMenu',
        'touchstart': '_onTouchStart',
    };

    static modelEvents = {
        'change:draftModes change:selectedDraftMode': '_update',
    };

    /**********************
     * Instance variables *
     **********************/

    #$arrow: JQuery;
    #$label: JQuery;
    #menuView: MenuView;

    /**
     * Render the view.
     */
    protected onInitialRender() {
        const labelID = 'unified-banner-mode-label';

        const menuView = craft<MenuView>`
            <Ink.Menu aria-labelledby="${labelID}"
                      controllerEl=${this.el}/>
        `;
        this.#menuView = menuView;

        renderInto(this.el, paint`
            <a class="rb-c-unified-banner__mode" tabindex="0">
             <label class="rb-c-unified-banner__menu-label"
                    id="${labelID}">
              <span class="rb-icon rb-icon-edit-review"
                    aria-hidden="true"/>
              ${_`Mode`}
             </label>
             <span class="ink-i-dropdown"></span>
            </a>
            ${menuView}
        `);

        this.#$label = this.$('.rb-c-unified-banner__menu-label');
        this.#$arrow = this.$('.ink-i-dropdown');

        this._update();
    }

    /**
     * Open the menu.
     */
    private _openMenu() {
        if (!this.#menuView.menuItems.isEmpty()) {
            this.#menuView.open({
                animate: false,
            });
        }
    }

    /**
     * Close the menu.
     */
    private _closeMenu() {
        if (!this.#menuView.menuItems.isEmpty()) {
            this.#menuView.close({
                animate: false,
            });
        }
    }

    /**
     * Handle a focus-out event.
     *
     * Args:
     *     evt (FocusEvent):
     *         The event object.
     */
    private _onFocusOut(evt: FocusEvent) {
        evt.stopPropagation();

        /*
         * Only close the menu if the focus has moved to something outside of
         * this component.
         */
        const currentTarget = evt.currentTarget as Element;

        if (!currentTarget.contains(evt.relatedTarget as Element)) {
            this.#menuView.close({
                animate: false,
            });
        }
    }

    /**
     * Handle a key down event.
     *
     * When the menu has focus, this will take care of handling keyboard
     * operations, allowing the menu to be opened or closed. Opening the menu
     * will transfer the focus to the menu items.
     *
     * Args:
     *     evt (KeyboardEvent):
     *         The keydown event.
     */
    private _onKeyDown(evt: KeyboardEvent) {
        if (evt.key === 'ArrowDown' ||
            evt.key === 'ArrowUp' ||
            evt.key === 'Enter' ||
            evt.key === ' ') {
            evt.preventDefault();
            evt.stopPropagation();

            this.#menuView.open({
                animate: false,
                currentItemIndex: 0,
            });
        } else if (evt.key === 'Escape') {
            evt.preventDefault();
            evt.stopPropagation();

            this.#menuView.close({
                animate: false,
            });
        }
    }

    /**
     * Handle a touchstart event.
     *
     * Version Added:
     *    7.0.3
     *
     * Args:
     *     e (TouchEvent):
     *         The touch event.
     */
    private _onTouchStart(e: TouchEvent) {
        const $target = $(e.target);

        if (!($target.hasClass('.ink-c-menu__item') ||
              $target.parents('.ink-c-menu__item').length)) {
            /* Open or close the menu if its not a touch on an item. */
            e.stopPropagation();
            e.preventDefault();

            if (this.#menuView.isOpen) {
                this._closeMenu();
            } else {
                this._openMenu();
            }
        }
    }

    /**
     * Update the state of the draft mode selector.
     */
    private _update() {
        const model = this.model;
        const draftModes = model.get('draftModes');
        const selectedDraftMode = model.get('selectedDraftMode');

        const newMenuItems: MenuItem[] = [];

        for (let i = 0; i < draftModes.length; i++) {
            const text = draftModes[i].text;

            if (i === selectedDraftMode) {
                renderInto(
                    this.#$label[0],
                    paint`
                        <span class="rb-icon rb-icon-edit-review"
                              aria-hidden="true"/>
                        ${text}
                    `,
                    {empty: true});
            } else {
                newMenuItems.push(new MenuItem({
                    label: text,
                    onClick: () => model.set('selectedDraftMode', i),
                }));
            }
        }

        this.#menuView.menuItems.reset(newMenuItems);

        this.#$arrow.toggle(draftModes.length > 1);
    }
}


/**
 * The publish button.
 *
 * Version Added:
 *     6.0
 */
@spina
class PublishButtonView extends MenuButtonView<UnifiedBanner> {
    static modelEvents = {
        'change:draftModes change:selectedDraftMode': '_update',
    };

    /**********************
     * Instance variables *
     **********************/

    #$archiveCheckbox: JQuery;
    #$trivialCheckbox: JQuery;

    /**
     * Initialize the view.
     */
    initialize() {
        const reviewRequestEditor = this.model.get('reviewRequestEditor');
        const menuItems = new MenuItemsCollection();

        let showSendEmailItem: MenuItem | null = null;

        if (reviewRequestEditor.get('showSendEmail')) {
            showSendEmailItem = new MenuItem({
                checked: true,
                label: _`Send E-Mail`,
                type: MenuItemType.CHECKBOX_ITEM,
            });
            menuItems.add(showSendEmailItem);
        }

        const archiveItem = new MenuItem({
            label: _`Archive after publishing`,
            type: MenuItemType.CHECKBOX_ITEM,
        });
        menuItems.add(archiveItem);

        super.initialize({
            dropdownButtonAriaLabel: _`Open publish options`,
            hasActionButton: true,
            label: _`Publish All`,
            menuAriaLabel: _`Publish options`,
            menuIconName: 'fa fa-gear',
            menuItems: menuItems,
            onActionButtonClick: () => {
                this.trigger('publish', {
                    archive: archiveItem.get('checked'),
                    trivial: showSendEmailItem === null ||
                             !showSendEmailItem.get('checked'),
                });
            },
        });
    }

    /**
     * Handle the initial rendering of the menu button.
     */
    protected onComponentInitialRender() {
        super.onComponentInitialRender();

        this._update()
    }

    /**
     * Update the state of the publish button.
     */
    private _update() {
        const model = this.model;
        const draftModes = model.get('draftModes');
        const selectedDraftMode = model.get('selectedDraftMode');

        if (!this.rendered || draftModes.length === 0) {
            return;
        }

        this.label = (draftModes[selectedDraftMode].multiple
                      ? _`Publish All`
                      : _`Publish`);
    }
}


/**
 * Options for the unified banner view.
 *
 * Version Added:
 *     6.0
 */
interface UnifiedBannerViewOptions {
    /** The review request editor. */
    reviewRequestEditorView: ReviewRequestEditorView;
}


/**
 * The unified banner.
 *
 * This is a unified, multi-mode banner that provides basic support for
 * publishing, editing, and discarding reviews, review requests, and
 * review replies.
 *
 * The banner displays at the top of the page under the topbar and floats to
 * the top of the browser window when the user scrolls down.
 *
 * Version Added:
 *     6.0
 */
@spina
export class UnifiedBannerView extends FloatingBannerView<
    UnifiedBanner,
    HTMLDivElement,
    UnifiedBannerViewOptions
> {
    static instance: UnifiedBannerView = null;

    static events: EventsHash = {
        'click #btn-review-request-discard': '_discardDraft',
        'click .rb-c-unified-banner__unpublished-draft a':
            '_toggleViewUserDraft',
    };

    static modelEvents = {
        'change': '_update',
        'change:selectedDraftMode': '_scrollToReviewReply',
    };

    /**********************
     * Instance variables *
     **********************/

    /** The change description editor. */
    #$changedesc: JQuery;

    /** The discard draft button. */
    #$discardButton: JQuery;

    /**
     * The dock container.
     *
     * Version Added:
     *     7.0.3
     */
    #$dock: JQuery;

    /** The container for all draft action buttons/menus. */
    #$draftActions: JQuery;

    /** The link for accessing the interdiff for a new draft diff. */
    #$interdiffLink: JQuery;

    /** The mode selector menu. */
    #$modeSelector: JQuery;

    /** The container for all review-related controls in the banner. */
    #$review: JQuery;

    /**
     * The message for showing other users' drafts to admins.
     *
     * Version Added:
     *     7.0.2
     */
    #$userDraftMessage: JQuery = null;

    /** The draft mode menu. */
    #modeMenu: DraftModeMenu;

    /** The publish button. */
    #publishButton: PublishButtonView;

    /** The review request editor view. */
    #reviewRequestEditorView: ReviewRequestEditorView;

    /**
     * Reset the UnifiedBannerView instance.
     *
     * This is used in unit tests to reset the state after tests run.
     */
    static resetInstance() {
        if (this.instance !== null) {
            this.instance.remove();
            this.instance = null;
        }
    }

    /**
     * Return the UnifiedBannerView instance.
     *
     * If the banner does not yet exist, this will create it.
     *
     * Args:
     *     required (boolean, optional):
     *         Whether the instance is required to exist.
     *
     * Returns:
     *     RB.UnifiedBannerView:
     *     The banner view.
     */
    static getInstance(
        required = false,
    ): UnifiedBannerView {
        if (required) {
            console.assert(
                this.instance,
                'Unified banner instance has not been created');
        }

        return this.instance;
    }

    /**
     * Initialize the banner.
     *
     * Args:
     *     options (object):
     *         Options for the banner. See :js:class:`RB.FloatingBannerView`
     *         for details.
     */
    initialize(options: UnifiedBannerViewOptions) {
        super.initialize(_.defaults(options, {
            $floatContainer: $('#page-container'),
            noFloatContainerClass: 'collapsed',
        }));

        this.#reviewRequestEditorView = options.reviewRequestEditorView;
        UnifiedBannerView.instance = this;
    }

    /**
     * Remove the banner from the DOM.
     *
     * This will stop tracking for the content viewport and then remove
     * the element.
     *
     * Returns:
     *     UnifiedBannerView:
     *     This instance, for chaining.
     */
    remove(): this {
        contentViewport.untrackElement(this.el);

        return super.remove();
    }

    /**
     * Render the banner.
     */
    protected onInitialRender() {
        if (!UserSession.instance.get('authenticated')) {
            return;
        }

        super.onInitialRender();

        const model = this.model;

        this.#$dock = this.$('.rb-c-unified-banner__dock');
        this.#$modeSelector = this.$('.rb-c-unified-banner__mode-selector');
        this.#$draftActions = this.$('.rb-c-unified-banner__draft-actions');
        this.#$review = this.$('.rb-c-unified-banner__review');
        this.#$changedesc = this.$('.rb-c-unified-banner__changedesc');
        this.#$interdiffLink = $(dedent`
                <div class="rb-c-unified-banner__interdiff-link">
                ${gettext('This draft adds a new diff.')}
                <a>${gettext('Show changes')}</a>
                </div>
            `)
            .appendTo(this.#$changedesc);

        this.#modeMenu = new DraftModeMenu({
            model: model,
        });
        this.#modeMenu.renderInto(this.#$modeSelector);

        this.#publishButton = new PublishButtonView({
            model: model,
        });
        this.#publishButton.$el.prependTo(this.#$draftActions);
        this.listenTo(this.#publishButton, 'publish', this.publish);
        this.#publishButton.render();

        this.#$discardButton =
            $(paint`
                <Ink.Button id="btn-review-request-discard">
                 ${_`Discard`}
                </Ink.Button>
            `)
            .appendTo(this.#$draftActions);

        const reviewRequestEditor = model.get('reviewRequestEditor');
        const reviewRequest = model.get('reviewRequest');

        const $changeDescription = this.$('#field_change_description')
            .html(reviewRequestEditor.get('changeDescriptionRenderedText'))
            .toggleClass('editable', reviewRequestEditor.get('mutableByUser'))
            .toggleClass('rich-text',
                         reviewRequest.get('changeDescriptionRichText'));

        this.#reviewRequestEditorView.addFieldView(
            new ChangeDescriptionFieldView({
                el: $changeDescription,
                fieldID: 'change_description',
                model: reviewRequestEditor,
            }));

        contentViewport.trackElement({
            el: this.el,
            side: 'top',
        });
    }

    /**
     * Handle re-renders.
     */
    protected onRender() {
        this._update(true);
    }

    /**
     * Update the state of the banner.
     *
     * Version Changed:
     *     7.0:
     *     Added the ``forceUpdate`` argument.
     *
     * Args:
     *     forceUpdate (boolean, optional):
     *         Whether to force updating the state of the banner.
     *
     *         If not provided, this will only update if already rendered.
     *
     *         Version Added:
     *             7.0
     */
    private _update(
        forceUpdate?: boolean,
    ) {
        if (!this.rendered && !forceUpdate) {
            return;
        }

        const model = this.model;
        const draftModes = model.get('draftModes');
        const selectedDraftMode = model.get('selectedDraftMode');
        const numDrafts = model.get('numDrafts');

        const reviewRequest = model.get('reviewRequest');
        const reviewRequestPublic = reviewRequest.get('public');

        const userDraftMessage = model.get('userDraftMessage');

        this.#$discardButton.toggle(
            draftModes.length > 0 &&
            !draftModes[selectedDraftMode].multiple);
        this.#$modeSelector.toggle(numDrafts > 0);
        this.#$draftActions.toggle(numDrafts > 0);
        this.#$changedesc.toggle(
            reviewRequestPublic &&
            draftModes.length > 0 &&
            draftModes[selectedDraftMode].hasReviewRequest);

        const interdiffLink = reviewRequest.draft.get('interdiffLink');

        if (interdiffLink) {
            this.#$interdiffLink
                .show()
                .children('a').attr('href', interdiffLink);
        } else {
            this.#$interdiffLink.hide();
        }

        if (userDraftMessage) {
            if (this.#$userDraftMessage === null) {
                this.#$userDraftMessage =
                    $('<div class="rb-c-unified-banner__unpublished-draft">')
                    .appendTo(this.getDock());
            }

            this.#$userDraftMessage.html(userDraftMessage);
        } else {
            if (this.#$userDraftMessage) {
                this.#$userDraftMessage.remove();
                this.#$userDraftMessage = null;
            }
        }

        this.$el
            .toggleClass('-has-draft',
                         (reviewRequestPublic === false || numDrafts > 0))
            .toggleClass('-has-multiple', numDrafts > 1)
            .show();
    }

    /**
     * Return the height of the banner.
     *
     * Args:
     *     withDock (boolean, optional):
     *         Whether to include the dock portion of the banner in the height
     *         value.
     *
     * Returns:
     *     number:
     *     The height of the banner, in pixels.
     */
    getHeight(withDock = true): number {
        if (withDock) {
            return this.$el.outerHeight();
        } else {
            return this.#$review.outerHeight();
        }
    }

    /**
     * Return the dock element.
     *
     * Returns:
     *     JQuery:
     *     The dock element.
     */
    getDock(): JQuery {
        return this.#$dock;
    }

    /**
     * Publish the current draft.
     *
     * This triggers an event which is handled by ReviewRequestEditorView.
     */
    async publish(
        options: {
            archive: boolean,
            trivial: boolean,
        },
    ): Promise<void> {
        const model = this.model;
        const selectedDraftMode = model.get('selectedDraftMode');
        const draftModes = model.get('draftModes');
        const draftMode = draftModes[selectedDraftMode];
        const reviewRequestEditor = model.get('reviewRequestEditor');
        const reviewRequest = reviewRequestEditor.get('reviewRequest');
        const pendingReview = model.get('pendingReview');
        const reviewReplyDrafts = model.get('reviewReplyDrafts');

        const reviews: number[] = [];
        const reviewRequests: number[] = [];

        ClientCommChannel.getInstance().reload();

        if (draftMode.hasReviewRequest) {
            await reviewRequest.ready();
            reviewRequests.push(reviewRequest.get('id'));
        }

        if (draftMode.hasReview) {
            await pendingReview.ready();
            reviews.push(pendingReview.get('id'));
        }

        if (draftMode.singleReviewReply !== undefined) {
            const reply = reviewReplyDrafts[draftMode.singleReviewReply];
            await reply.ready();
            reviews.push(reply.get('id'));
        } else if (draftMode.hasReviewReplies) {
            for (const reply of reviewReplyDrafts) {
                await reply.ready();
                reviews.push(reply.get('id'));
            }
        }

        await this.#reviewRequestEditorView.saveOpenEditors();

        try {
            await this.#runPublishBatch(reviewRequest.get('localSitePrefix'),
                                        reviewRequests,
                                        reviews,
                                        !!options.trivial,
                                        !!options.archive);
        } catch (err) {
            alert(err);
        }

        RB.navigateTo(reviewRequest.get('reviewURL'));
    }

    /**
     * Run the publish batch operation.
     *
     * Args:
     *     localSitePrefix (string):
     *         The URL prefix for the local site, if present.
     *
     *     reviewRequests (Array of number):
     *         The set of review request IDs to publish.
     *
     *     reviews (Array of number):
     *         The set of review IDs to publish.
     *
     *     trivial (boolean):
     *         Whether to suppress notification e-mails.
     *
     *     archive (boolean):
     *         Whether to archive the affected review request after publishing.
     *
     * Returns:
     *     Promise:
     *     A promise which resolves when the operation is complete or rejects
     *     with an error string.
     */
    #runPublishBatch(
        localSitePrefix: string,
        reviewRequests: number[],
        reviews: number[],
        trivial: boolean,
        archive: boolean,
    ): Promise<void> {
        return new Promise((resolve, reject) => {
            RB.apiCall({
                data: {
                    batch: JSON.stringify({
                        archive: archive,
                        op: 'publish',
                        review_requests: reviewRequests,
                        reviews: reviews,
                        trivial: trivial,
                    }),
                },
                url: `${SITE_ROOT}${localSitePrefix}r/_batch/`,

                error: xhr => {
                    const rsp = xhr.responseJSON;

                    if (rsp && rsp.stat) {
                        reject(rsp.error);
                    } else {
                        console.error(
                            'Failed to run publish batch operation', xhr);
                        reject(xhr.statusText);
                    }
                },
                success: () => {
                    resolve();
                },
            });
        });
    }

    /**
     * Discard the current draft.
     *
     * Depending on the selected view mode, this will either discard the
     * pending review, discard the current review request draft, or close the
     * (unpublished) review request as discarded.
     */
    private async _discardDraft() {
        const model = this.model;
        const selectedDraftMode = model.get('selectedDraftMode');
        const draftModes = model.get('draftModes');
        const draftMode = draftModes[selectedDraftMode];
        const reviewRequest = model.get('reviewRequest');

        ClientCommChannel.getInstance().reload();

        try {
            if (await this._confirmDiscard(draftMode) === false) {
                return;
            }

            if (draftMode.hasReview) {
                const pendingReview = model.get('pendingReview');
                await pendingReview.destroy();

                RB.navigateTo(reviewRequest.get('reviewURL'));
            } else if (draftMode.hasReviewRequest) {
                if (!reviewRequest.get('public')) {
                    await reviewRequest.close({
                        type: ReviewRequest.CLOSE_DISCARDED,
                    });
                } else if (!reviewRequest.draft.isNew()) {
                    await reviewRequest.draft.destroy();
                }

                RB.navigateTo(reviewRequest.get('reviewURL'));
            } else if (draftMode.singleReviewReply !== undefined) {
                const reviewReplyDrafts = model.get('reviewReplyDrafts');
                const reply = reviewReplyDrafts[draftMode.singleReviewReply];

                await reply.destroy();
            } else {
                console.error('Discard reached with no active drafts.');
            }
        } catch(err) {
            alert(err.xhr.errorText);
        }
    }

    /**
     * Ask the user to confirm a discard operation.
     *
     * Args:
     *     draftMode (DraftMode):
     *         The current draft mode being discarded.
     *
     * Returns:
     *     Promise:
     *     A promise which resolves to either ``true`` (proceed) or ``false``
     *     (cancel).
     */
    private _confirmDiscard(
        draftMode: DraftMode,
    ): Promise<boolean> {
        return new Promise(resolve => {
            const text = draftMode.hasReview
                ? _`
                    If you discard this review, all unpublished comments
                    will be deleted.
                `
                : _`
                    If you discard this review request draft, all unpublished
                    data will be deleted.
                `;
            const title = draftMode.hasReview
                ? _`Are you sure you want to discard this review?`
                : _`
                    Are you sure you want to discard this review request
                    draft?
                `;

            function resolveAndClose(result: boolean) {
                resolve(result);
                $dlg.modalBox('destroy');
            }

            const $dlg = $('<p>')
                .text(text)
                .modalBox({
                    buttons: paint<HTMLButtonElement[]>`
                        <Ink.Button onClick=${() => resolveAndClose(false)}>
                         ${_`Cancel`}
                        </Ink.Button>
                        <Ink.Button type="danger"
                                    onClick=${() => resolveAndClose(true)}>
                         ${_`Discard`}
                        </Ink.Button>
                    `,
                    title: title,
                })
                .on('close', () => {
                    $dlg.modalBox('destroy');
                    resolve(false);
                });
        });
    }

    /**
     * Handler for when the selected draft mode changes.
     *
     * If the newly selected mode is a review reply, scroll the document to
     * that review.
     */
    private _scrollToReviewReply() {
        const selectedDraftMode = this.model.get('selectedDraftMode');
        const draftModes = this.model.get('draftModes');
        const draftMode = draftModes[selectedDraftMode];

        if (draftMode.singleReviewReply !== undefined) {
            const reviewReplyDrafts = this.model.get('reviewReplyDrafts');
            const reply = reviewReplyDrafts[draftMode.singleReviewReply];
            const originalReview = reply.get('parentObject').get('id');

            const $review = $(`#review${originalReview}`);
            const reviewTop = $review.offset().top;
            const bannerHeight = this.$el.outerHeight(true);

            $(document).scrollTop(reviewTop - bannerHeight - 20);
        }
    }

    /**
     * Toggle whether to view unpublished draft data owned by another user.
     *
     * It is up to the page view to reload based on this value changing.
     */
    private _toggleViewUserDraft() {
        const reviewRequestEditor = this.model.get('reviewRequestEditor');
        const viewingUserDraft = reviewRequestEditor.get('viewingUserDraft');

        reviewRequestEditor.set('viewingUserDraft', !viewingUserDraft);
    }
}
