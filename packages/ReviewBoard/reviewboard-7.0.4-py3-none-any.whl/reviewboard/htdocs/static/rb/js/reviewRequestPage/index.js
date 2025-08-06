(function (global, factory) {
    typeof exports === 'object' && typeof module !== 'undefined' ? factory(exports, require('@beanbag/spina')) :
    typeof define === 'function' && define.amd ? define(['exports', '@beanbag/spina'], factory) :
    (global = typeof globalThis !== 'undefined' ? globalThis : global || self, factory(global.RB = global.RB || {}, global.Spina));
})(this, (function (exports, spina) { 'use strict';

    var _class, _class2;


    /**
     * Options for the ReviewReplyDraftBannerView.
     *
     * Version Added:
     *     6.0
     */

    /**
     * A banner that represents a pending reply to a review.
     *
     * The banner offers actions for publishing and discarding the review.
     */
    let ReviewReplyDraftBannerView = spina.spina(_class = class ReviewReplyDraftBannerView extends RB.FloatingBannerView {
      static className = 'banner';
      static events = {
        'click .discard-button': '_onDiscardClicked',
        'click .publish-button': '_onPublishClicked'
      };
      static modelEvents = {
        'publishError': '_onPublishError',
        'saved': '_onSaved',
        'saving destroying': '_onSavingOrDestroying'
      };
      static template = _.template(`<h1>${gettext("This reply is a draft.")}</h1>
<p>${gettext("Be sure to publish when finished.")}</p>
<span class="banner-actions">
 <input type="button" value="${gettext("Publish")}"
        class="publish-button">
 <input type="button" value="${gettext("Discard")}"
        class="discard-button">
</span>
<% if (showSendEmail) { %>
 <label>
  <input type="checkbox" class="send-email" checked>
  ${gettext("Send E-Mail")}
</label>
<% } %>`);

      /**********************
       * Instance variables *
       **********************/

      #reviewRequestEditor;

      /**
       * Initialize the view.
       *
       * Args:
       *     options (ReviewReplyDraftBannerViewOptions):
       *         Options for the view.
       */
      initialize(options) {
        super.initialize(options);
        this.#reviewRequestEditor = options.reviewRequestEditor;
      }

      /**
       * Render the banner.
       *
       * Returns:
       *     RB.ReviewRequestPage.ReviewReplyDraftBannerView:
       *     This object, for chaining.
       */
      onInitialRender() {
        super.onInitialRender();
        this.$el.html(ReviewReplyDraftBannerView.template({
          showSendEmail: this.#reviewRequestEditor.get('showSendEmail')
        }));
      }

      /**
       * Handler for when Publish is clicked.
       *
       * Publishes the reply.
       */
      _onPublishClicked() {
        const $sendEmail = this.$('.send-email');
        this.model.publish({
          trivial: $sendEmail.length === 1 && !$sendEmail.is(':checked')
        });
      }

      /**
       * Handler for when Discard is clicked.
       *
       * Discards the reply.
       */
      _onDiscardClicked() {
        this.model.destroy();
      }

      /**
       * Handler for when there's an error publishing.
       *
       * The error will be displayed in an alert.
       *
       * Args:
       *     errorText (string):
       *         The publish error text to show.
       */
      _onPublishError(errorText) {
        alert(errorText);
      }

      /**
       * Handler for when the draft is saving or being destroyed.
       *
       * This will disable the buttons on the banner while the operation is
       * in progress.
       */
      _onSavingOrDestroying() {
        this.$('input').prop('disabled', true);
      }

      /**
       * Handler for when the draft is saved.
       *
       * This will re-enable the buttons on the banner.
       */
      _onSaved() {
        this.$('input').prop('disabled', false);
      }
    }) || _class;

    /**
     * A static banner for review replies.
     *
     * This is used when the unified banner is enabled.
     *
     * Version Added:
     *     6.0
     */
    let ReviewReplyDraftStaticBannerView = spina.spina(_class2 = class ReviewReplyDraftStaticBannerView extends spina.BaseView {
      static className = 'banner';
      static template = _.template(`<h1><%- draftText %></h1>
<p><%- reminderText %></p>`);

      /**
       * Render the banner.
       */
      onInitialRender() {
        this.$el.html(ReviewReplyDraftStaticBannerView.template({
          draftText: gettext("This reply is a draft."),
          reminderText: gettext("Be sure to publish when finished.")
        }));
      }
    }) || _class2;

    /* Define a namespace for RB.ReviewRequestPage. */
    const ReviewRequestPage = {
      ReviewReplyDraftBannerView,
      ReviewReplyDraftStaticBannerView
    };

    exports.ReviewRequestPage = ReviewRequestPage;

    Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

}));
//# sourceMappingURL=index.js.map
