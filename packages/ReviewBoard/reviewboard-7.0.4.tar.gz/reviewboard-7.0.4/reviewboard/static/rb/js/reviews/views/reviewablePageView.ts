/**
 * A page managing reviewable content for a review request.
 */
import {
    craft,
    renderInto,
} from '@beanbag/ink';
import {
    type EventsHash,
    BaseView,
    spina,
} from '@beanbag/spina';

import {
    EnabledFeatures,
    PageView,
    UserSession,
} from 'reviewboard/common';
import { type PageViewOptions } from 'reviewboard/common/views/pageView';
import {
    type ReviewRequestAttrs,
} from 'reviewboard/common/resources/models/reviewRequestModel';
import { DnDUploader } from 'reviewboard/ui';

import { type ReviewRequestEditor } from '../models/reviewRequestEditorModel';
import { type ReviewablePage } from '../models/reviewablePageModel';
import { UnifiedBanner } from '../models/unifiedBannerModel';
import { ReviewDialogView } from './reviewDialogView';
import { ReviewRequestEditorView } from './reviewRequestEditorView';
import { UnifiedBannerView } from './unifiedBannerView';


/**
 * Update information as received from the server.
 */
interface UpdateInfo {
    /** The summary of the update. */
    summary: string;

    /** Information about the user who made the update. */
    user: {
        fullname?: string,
        url: string,
        username: string,
    };
}


/**
 * Options for the UpdatesBubbleView.
 */
interface UpdatesBubbleViewOptions {
    /** Information about the update, fetched from the server. */
    updateInfo: UpdateInfo;
}


/**
 * An update bubble showing an update to the review request or a review.
 */
@spina
class UpdatesBubbleView extends BaseView<
    undefined,
    HTMLDivElement,
    UpdatesBubbleViewOptions
> {
    static className = 'rb-c-page-updates-bubble';
    static id = 'updates-bubble';

    static events: EventsHash = {
        'click [data-action=ignore]': '_onIgnoreClicked',
        'click [data-action=update]': '_onUpdatePageClicked',
    };

    /**********************
     * Instance variables *
     **********************/

    /** Options for the view. */
    options: UpdatesBubbleViewOptions;

    /**
     * Initialize the view.
     *
     * Args:
     *     options (UpdatesBubbleViewOptions):
     *         Options for the view.
     */
    initialize(options: UpdatesBubbleViewOptions) {
        this.options = options;
    }

    /**
     * Render the bubble with the information provided during construction.
     *
     * The bubble starts hidden. The caller must call open() to display it.
     */
    protected onInitialRender() {
        const el = this.el;
        const updateInfo = this.options.updateInfo;
        const user = updateInfo.user;

        el.setAttribute('role', 'status');

        const updateText = _`Update page`;
        const closeText = _`Close notification`;

        /*
         * NOTE: Icons are elements within an <a>, instead of mixed in to the
         *       action, in order to ensure focus outlines work correctly
         *       across all browsers.
         */
        renderInto(this.el, craft`
            <div class="rb-c-page-updates-bubble__message">
             ${`${updateInfo.summary} by `}
             <a href="${user.url}">
              ${user.fullname || user.username}
             </a>
            </div>
            <div class="rb-c-page-updates-bubble__actions">
             <a class="rb-c-page-updates-bubble__action"
                data-action="update"
                title="${updateText}"
                role="button"
                tabindex="0"
                href="#">
              <span class="ink-i-refresh" aria-hidden="true"></span>
             </a>
             <a class="rb-c-page-updates-bubble__action"
                data-action="ignore"
                title="${closeText}"
                role="button"
                tabindex="0"
                href="#">
              <span class="ink-i-close" aria-hidden="true"></span>
             </a>
            </div>
        `);
    }

    /**
     * Open the bubble on the screen.
     */
    open() {
        /* Give the element time to settle before we animate it. */
        _.defer(() => this.el.classList.add('-is-open'));
    }

    /**
     * Close the update bubble.
     *
     * After closing, the bubble will be removed from the DOM.
     */
    close() {
        this.el.classList.remove('-is-open');

        _.defer(() => {
            this.trigger('closed');
            this.remove();
        });
    }

    /**
     * Handle clicks on the "Update Page" link.
     *
     * Loads the review request page.
     *
     * Args:
     *     e (JQuery.ClickEvent):
     *         The event which triggered the action.
     */
    protected _onUpdatePageClicked(e: JQuery.ClickEvent) {
        e.preventDefault();
        e.stopPropagation();

        this.trigger('updatePage');
    }

    /*
     * Handle clicks on the "Ignore" link.
     *
     * Ignores the update and closes the page.
     *
     * Args:
     *     e (JQuery.ClickEvent):
     *         The event which triggered the action.
     */
    protected _onIgnoreClicked(e: JQuery.ClickEvent) {
        e.preventDefault();
        e.stopPropagation();

        this.close();
    }
}


/**
 * Options for the ReviewablePageView.
 */
export interface ReviewablePageViewOptions extends PageViewOptions {
    /** The model attributes for a new ReviewRequest instance. */
    reviewRequestData?: ReviewRequestAttrs;

    /** The model attributes for a new ReviewRequestEditor instance. */
    editorData?: Partial<ReviewRequestEditorAttrs>;

    /** The last known timestamp for activity on this review request. */
    lastActivityTimestamp?: string;

    /** The type of updates to check for. */
    checkUpdatesType?: string;
}


/**
 * A page managing reviewable content for a review request.
 *
 * This provides common functionality for any page associated with a review
 * request, such as the diff viewer, review UI, or the review request page
 * itself.
 */
@spina
export class ReviewablePageView<
    TModel extends ReviewablePage = ReviewablePage,
    TElement extends HTMLDivElement = HTMLDivElement,
    TExtraViewOptions extends ReviewablePageViewOptions =
        ReviewablePageViewOptions
> extends PageView<TModel, TElement, TExtraViewOptions> {
    static events: EventsHash = {
        'click #action-legacy-edit-review': '_onEditReviewClicked',
        'click #action-legacy-add-general-comment': 'addGeneralComment',
        'click #action-legacy-ship-it': 'shipIt',
        'click .rb-o-mobile-menu-label': '_onMenuClicked',
    };

    /**********************
     * Instance variables *
     **********************/

    /** The review request editor. */
    reviewRequestEditorView: ReviewRequestEditorView;

    /** The draft review banner, if present. */
    draftReviewBanner: RB.DraftReviewBannerView;

    /** The unified banner, if present. */
    unifiedBanner: UnifiedBannerView = null;

    /** The star manager. */
    #starManager: RB.StarManagerView;

    /** The URL to the default favicon. */
    #favIconURL: string = null;

    /** The URL to the favicon showing an active notification. */
    #favIconNotifyURL: string = null;

    /** The URL to the logo image to use for notifications. */
    #logoNotificationsURL: string = null;

    /** The updates bubble view. */
    _updatesBubble: UpdatesBubbleView = null;

    /**
     * Initialize the page.
     *
     * This will construct a ReviewRequest, CommentIssueManager,
     * ReviewRequestEditor, and other required objects, based on data
     * provided during construction.
     *
     * Args:
     *     options (ReviewablePageViewOptions):
     *         Options for the view.
     */
    initialize(options: ReviewablePageViewOptions) {
        super.initialize(options);

        this.options = options;

        DnDUploader.create();

        this.reviewRequestEditorView = new ReviewRequestEditorView({
            el: $('#review-request'),
            inMobileMode: this.inMobileMode,
            model: this.model.reviewRequestEditor,
        });

        /*
         * Some extensions, like Power Pack and rbstopwatch, expect a few
         * legacy attributes on the view. Set these here so these extensions
         * can access them. Note that extensions should ideally use the new
         * form, if they're able to support Review Board 3.0+.
         */
        ['reviewRequest', 'pendingReview'].forEach(attrName => {
            this[attrName] = this.model.get(attrName);

            this.listenTo(this.model, `change:${attrName}`, () => {
                this[attrName] = this.model.get(attrName);
            });
        });

        /*
         * Allow the browser to report notifications, if the user has this
         * enabled.
         */
        RB.NotificationManager.instance.setup();

        if (UserSession.instance.get('authenticated')) {
            this.#starManager = new RB.StarManagerView({
                el: this.$('.star').parent(),
                model: new RB.StarManager(),
            });
        }

        this.listenTo(this.model, 'reviewRequestUpdated',
                      this._onReviewRequestUpdated);
    }

    /**
     * Render the page.
     */
    renderPage() {
        const $favicon = $('head').find('link[rel="shortcut icon"]');

        this.#favIconURL = $favicon.attr('href');
        this.#favIconNotifyURL = STATIC_URLS['rb/images/favicon_notify.ico'];
        this.#logoNotificationsURL = STATIC_URLS['rb/images/logo.png'];

        const pendingReview = this.model.get('pendingReview');
        const reviewRequest = this.model.get('reviewRequest');

        if (EnabledFeatures.unifiedBanner) {
            if (UserSession.instance.get('authenticated')) {
                this.unifiedBanner = new UnifiedBannerView({
                    el: $('#unified-banner'),
                    model: new UnifiedBanner({
                        pendingReview: pendingReview,
                        reviewRequest: reviewRequest,
                        reviewRequestEditor: this.model.reviewRequestEditor,
                    }),
                    reviewRequestEditorView: this.reviewRequestEditorView,
                });
                this.unifiedBanner.render();
            }
        } else {
            this.draftReviewBanner = RB.DraftReviewBannerView.create({
                el: $('#review-banner'),
                model: pendingReview,
                reviewRequestEditor: this.model.reviewRequestEditor,
            });

            this.listenTo(pendingReview, 'destroy published',
                          () => this.draftReviewBanner.hideAndReload());
        }

        this.listenTo(this.model.reviewRequestEditor,
                      'change:viewingUserDraft',
                      this._onViewingUserDraftChanged);

        this.reviewRequestEditorView.render();
    }

    /**
     * Remove this view from the page.
     *
     * Returns:
     *     ReviewablePageView:
     *     This object, for chaining.
     */
    remove(): this {
        if (this.draftReviewBanner) {
            this.draftReviewBanner.remove();
        }

        if (this.unifiedBanner) {
            this.unifiedBanner.remove();
        }

        return super.remove();
    }

    /**
     * Return data to use for assessing cross-tab page reloads.
     *
     * This returns a filter blob that will be recognized by all other tabs
     * that have the same review request.
     *
     * Version Added:
     *     6.0
     */
    getReloadData(): unknown {
        return {
            'review-request': this.model.get('reviewRequest').id,
        };
    }

    /**
     * Return the review request editor view.
     *
     * Returns:
     *     ReviewRequestEditorView:
     *     The review request editor view.
     */
    getReviewRequestEditorView(): ReviewRequestEditorView {
        return this.reviewRequestEditorView;
    }

    /**
     * Return the review request editor model.
     *
     * Returns:
     *     ReviewRequestEditor:
     *     The review request editor model.
     */
    getReviewRequestEditorModel(): ReviewRequestEditor {
        return this.model.reviewRequestEditor;
    }

    /**
     * Handle mobile mode changes.
     *
     * This will set the mobile mode on the review request editor view.
     *
     * Version Added:
     *     7.0.3
     *
     * Args:
     *     inMobileMode (boolean):
     *         Whether the UI is now in mobile mode. This will be the same
     *         value as :js:attr:`inMobileMode`, and is just provided for
     *         convenience.
     */
    onMobileModeChanged(inMobileMode: boolean) {
        this.reviewRequestEditorView.inMobileMode = inMobileMode;
    }

    /**
     * Catch the review updated event and send the user a visual update.
     *
     * This function will handle the review updated event and decide whether
     * to send a notification depending on browser and user settings.
     *
     * Args:
     *     info (UpdateInfo):
     *         The last update information for the request.
     */
    _onReviewRequestUpdated(info: UpdateInfo) {
        this.#updateFavIcon(this.#favIconNotifyURL);

        if (RB.NotificationManager.instance.shouldNotify()) {
            this._showDesktopNotification(info);
        }

        this._showUpdatesBubble(info);
    }

    /**
     * Create the updates bubble showing information about the last update.
     *
     * Args:
     *     info (UpdateInfo):
     *         The last update information for the request.
     */
    _showUpdatesBubble(info: UpdateInfo) {
        if (this._updatesBubble) {
            this._updatesBubble.remove();
        }

        const reviewRequest = this.model.get('reviewRequest');

        this._updatesBubble = new UpdatesBubbleView({
            updateInfo: info,
        });

        this.listenTo(this._updatesBubble, 'closed',
                      () => this.#updateFavIcon(this.#favIconURL));

        this.listenTo(this._updatesBubble, 'updatePage', () => {
            RB.navigateTo(reviewRequest.get('reviewURL'));
        });

        this._updatesBubble.render().$el.appendTo(this.$el);
        this._updatesBubble.open();
    }

    /**
     * Show the user a desktop notification for the last update.
     *
     * This function will create a notification if the user has not
     * disabled desktop notifications and the browser supports HTML5
     * notifications.
     *
     *  Args:
     *     info (UpdateInfo):
     *         The last update information for the request.
     */
    _showDesktopNotification(info: UpdateInfo) {
        const reviewRequest = this.model.get('reviewRequest');
        const name = info.user.fullname || info.user.username;

        RB.NotificationManager.instance.notify({
            body: _`Review request #${reviewRequest.id}, by ${name}`,
            iconURL: this.#logoNotificationsURL,
            onClick: () => {
                RB.navigateTo(reviewRequest.get('reviewURL'));
            },
            title: info.summary,
        });
    }

    /**
     * Update the favicon for the page.
     *
     * This is used to change the favicon shown on the page based on whether
     * there's a server-side update notification for the review request.
     *
     * Args:
     *     url (string):
     *         The URL to use for the shortcut icon.
     */
    #updateFavIcon(url: string) {
        $('head')
            .find('link[rel="shortcut icon"]')
                .remove()
            .end()
            .append($('<link>')
                .attr({
                    href: url,
                    rel: 'shortcut icon',
                    type: 'image/x-icon',
                }));
    }

    /**
     * Handle a click on the "Edit Review" button.
     *
     * Displays a review dialog.
     *
     * Args:
     *     e (JQuery.ClickEvent):
     *         The event which triggered the action.
     */
    _onEditReviewClicked(e: JQuery.ClickEvent) {
        e.preventDefault();
        e.stopPropagation();

        ReviewDialogView.create({
            review: this.model.get('pendingReview'),
            reviewRequestEditor: this.model.reviewRequestEditor,
        });

        return false;
    }

    /**
     * Add a new general comment.
     *
     * Args:
     *     e (JQuery.ClickEvent, optional):
     *         The event which triggered the action.
     */
    addGeneralComment(e?: JQuery.ClickEvent) {
        if (e) {
            e.preventDefault();
            e.stopPropagation();
        }

        const pendingReview = this.model.get('pendingReview');
        const comment = pendingReview.createGeneralComment(
            undefined,
            UserSession.instance.get('commentsOpenAnIssue'));

        if (!EnabledFeatures.unifiedBanner) {
            this.listenTo(comment, 'saved',
                          () => RB.DraftReviewBannerView.instance.show());
        }

        RB.CommentDialogView.create({
            comment: comment,
            reviewRequestEditor: this.model.reviewRequestEditor,
        });

        return false;
    }

    /**
     * Handle a click on the "Ship It" button.
     *
     * Confirms that the user wants to post the review, and then posts it
     * and reloads the page.
     *
     * Args:
     *     e (JQuery.ClickEvent, optional):
     *         The event which triggered the action, if available.
     */
    async shipIt(e?: JQuery.ClickEvent) {
        if (e) {
            e.preventDefault();
            e.stopPropagation();
        }

        if (confirm(_`Are you sure you want to post this review?`)) {
            await this.model.markShipIt();

            const reviewRequest = this.model.get('reviewRequest');
            RB.navigateTo(reviewRequest.get('reviewURL'));
        }

        return false;
    }

    /**
     * Generic handler for menu clicks.
     *
     * This simply prevents the click from bubbling up or invoking the
     * default action. This function is used for dropdown menu titles
     * so that their links do not send a request to the server when one
     * of their dropdown actions are clicked.
     *
     * Args:
     *     e (JQuery.ClickEvent):
     *         The event which triggered the action.
     */
    _onMenuClicked(e: JQuery.ClickEvent) {
        e.preventDefault();
        e.stopPropagation();

        const $menuButton = $(e.currentTarget).find('a');

        const expanded = $menuButton.attr('aria-expanded');
        const target = $menuButton.attr('aria-controls');
        const $target = this.$(`#${target}`);

        if (expanded === 'false') {
            $menuButton.attr('aria-expanded', 'true');
            $target.addClass('-is-visible');
        } else {
            $menuButton.attr('aria-expanded', 'false');
            $target.removeClass('-is-visible');
        }
    }

    /**
     * Callback for when the viewingUserDraft attribute of the editor changes.
     *
     * This will reload the page with the new value of the ``view-draft`` query
     * parameter.
     *
     * Args:
     *     model (ReviewRequestEditor):
     *         The review request editor model.
     *
     *     newValue (boolean):
     *         The new value of the viewingUserDraft attribute.
     */
    protected _onViewingUserDraftChanged(
        model: ReviewRequestEditor,
        newValue: boolean,
    ) {
        const location = window.location;
        const params = new URLSearchParams(location.search);

        if (newValue) {
            params.set('view-draft', '1');
        } else {
            params.delete('view-draft');
        }

        let url = location.pathname;

        if (params.size) {
            url += `?${params}`;
        }

        RB.navigateTo(url);
    }
}
