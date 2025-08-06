(function (global, factory) {
    typeof exports === 'object' && typeof module !== 'undefined' ? factory(exports, require('@beanbag/spina'), require('@beanbag/ink')) :
    typeof define === 'function' && define.amd ? define(['exports', '@beanbag/spina', '@beanbag/ink'], factory) :
    (global = typeof globalThis !== 'undefined' ? globalThis : global || self, factory(global.RB = global.RB || {}, global.Spina, global.Ink));
})(this, (function (exports, spina, ink) { 'use strict';

    var _class$l;

    /**
     * Attributes for the Action model.
     *
     * Version Changed:
     *     7.0:
     *     Added ``domID``, ``iconClass``, ``isCustomRendered``, ``label``, and
     *     ``url`` actions.
     *
     * Version Added:
     *     6.0
     */

    /**
     * Base model for actions.
     *
     * Subclasses may add their own attributes by passing in their own attribute
     * interface when extending this.
     *
     * Version Added:
     *     6.0
     */
    let Action = spina.spina(_class$l = class Action extends spina.BaseModel {
      static defaults = {
        actionId: '',
        domID: null,
        iconClass: null,
        isCustomRendered: false,
        label: null,
        url: null,
        visible: false
      };
    }) || _class$l;

    var _class$k;

    /**
     * Attributes for the MenuAction model.
     *
     * Version Added:
     *     6.0
     */

    /**
     * Base model for menu actions.
     *
     * Version Added:
     *     6.0
     */
    let MenuAction = spina.spina(_class$k = class MenuAction extends Action {
      static defaults() {
        return {
          children: []
        };
      }
    }) || _class$k;

    var _class$j;
    /**
     * Base view for actions.
     *
     * Version Added:
     *     6.0
     */
    let ActionView = spina.spina(_class$j = class ActionView extends spina.BaseView {}) || _class$j;

    var _class$i, _class2$2;

    /**
     * Base class for menu actions.
     *
     * Version Added:
     *     6.0
     */
    let MenuActionView = spina.spina(_class$i = class MenuActionView extends ActionView {
      static events = {
        'focusout': 'onFocusOut',
        'keydown': 'onKeyDown',
        'mouseenter': 'openMenu',
        'mouseleave': 'closeMenu',
        'touchstart': 'onTouchStart'
      };

      /**********************
       * Instance variables *
       **********************/

      /** The menu view. */

      /**
       * Render the view.
       */
      onInitialRender() {
        const menuItems = new ink.MenuItemsCollection();
        const page = RB.PageManager.getPage();
        for (const childId of this.model.get('children')) {
          if (childId === '--') {
            menuItems.add({
              type: ink.MenuItemType.SEPARATOR
            });
          } else {
            const childActionView = page.getActionView(childId);
            if (childActionView) {
              const childAction = childActionView.model;
              const visible = childAction.get('visible');
              const domID = childAction.get('domID');
              const onClick = childActionView['activate'] ? () => childActionView.activate() : null;
              if (childAction.get('isCustomRendered')) {
                menuItems.add({
                  childEl: childActionView.el,
                  id: domID,
                  onClick: onClick
                });
                if (visible) {
                  childActionView.$el.show();
                }
              } else {
                if (!visible) {
                  /*
                   * Don't include this at all.
                   *
                   * In the future, we may want to re-add this
                   * (or rebuild the whole menu) if this changes.
                   */
                  continue;
                }

                /*
                 * "#" is the default URL, and really indicates that
                 * a JavaScript-backed action is taking place. If we
                 * get this, normalize it to null.
                 */
                let url = childAction.get('url');
                if (url === '#') {
                  url = null;
                }
                const menuItem = menuItems.add({
                  iconName: childAction.get('iconClass'),
                  id: domID,
                  label: childAction.get('label'),
                  onClick: onClick,
                  url: url
                });

                /* Update the menu item when these change. */
                this.listenTo(childAction, 'change:iconClass', (model, newIconClass) => {
                  menuItem.set('iconName', newIconClass);
                });
                this.listenTo(childAction, 'change:label', (model, newLabel) => {
                  menuItem.set('label', newLabel);
                });
                this.listenTo(childAction, 'change:url', (model, newURL) => {
                  menuItem.set('url', newURL);
                });
              }
            } else {
              console.error('Unable to find action for %s', childId);
            }
          }
        }
        this.menu = ink.craftComponent("Ink.Menu", {
          controllerEl: this.el,
          menuItems: menuItems
        });
        ink.renderInto(this.el, this.menu);
        this.listenTo(this.menu, 'opening', this.positionMenu.bind(this));
      }

      /**
       * Open the menu.
       */
      openMenu() {
        if (!this.menu.menuItems.isEmpty()) {
          this.menu.open({
            animate: true
          });
        }
      }

      /**
       * Close the menu.
       */
      closeMenu() {
        if (!this.menu.menuItems.isEmpty()) {
          this.menu.close({
            animate: true
          });
        }
      }

      /**
       * Position the menu.
       *
       * This will make sure the full menu appears within the screen without
       * being clipped.
       *
       * Version Added:
       *     7.0.3
       */
      positionMenu() {
        const $menuEl = this.menu.$el;
        const menuWidth = $menuEl.width();
        const windowWidth = $(window).width();
        const elOffsetLeft = this.$el.offset().left;
        let newMenuLeft = 'auto';
        if (elOffsetLeft + menuWidth > windowWidth) {
          /*
           * The right side of the menu is being clipped. Move to the left
           * so that the full menu fits on screen.
           */
          newMenuLeft = windowWidth - (elOffsetLeft + Math.min(menuWidth, windowWidth));
        }
        $menuEl.css({
          left: newMenuLeft,
          'max-width': windowWidth
        });
      }

      /**
       * Handle a focus-out event.
       *
       * If the keyboard focus has moved to something outside of the menu, close
       * it.
       *
       * Args:
       *     evt (FocusEvent):
       *         The event object.
       */
      onFocusOut(evt) {
        evt.stopPropagation();

        /*
         * Only close the menu if the focus has moved to something outside of
         * this component.
         */
        const currentTarget = evt.currentTarget;
        if (!currentTarget.contains(evt.relatedTarget)) {
          this.menu.close({
            animate: false
          });
        }
      }

      /**
       * Handle a key-down event.
       *
       * When the menu has focus, this will take care of handling keyboard
       * operations, allowing the menu to be opened or closed. Opening the menu
       * will transfer the focus to the menu items.
       *
       * Args:
       *     evt (KeyboardEvent):
       *         The keydown event.
       */
      onKeyDown(evt) {
        if (evt.key === ' ' || evt.key === 'ArrowDown' || evt.key === 'ArrowUp' || evt.key === 'Enter') {
          /* Open the menu and select the first item. */
          evt.stopPropagation();
          evt.preventDefault();
          this.menu.open({
            animate: false,
            currentItemIndex: 0
          });
        } else if (evt.key === 'Escape') {
          /* Close the menu. */
          evt.stopPropagation();
          evt.preventDefault();
          this.menu.close({
            animate: false
          });
        }
      }

      /**
       * Handle a touchstart event.
       *
       * Args:
       *     e (TouchEvent):
       *         The touch event.
       */
      onTouchStart(e) {
        const $target = $(e.target);
        if (!($target.hasClass('.ink-c-menu__item') || $target.parents('.ink-c-menu__item').length)) {
          /* Open or close the menu if its not a touch on an item. */
          e.stopPropagation();
          e.preventDefault();
          if (this.menu.isOpen) {
            this.closeMenu();
          } else {
            this.openMenu();
          }
        }
      }
    }) || _class$i;

    /**
     * Base class for an action within a menu.
     *
     * This handles event registration for the click and touch events in order to
     * behave properly on both desktop and mobile.
     *
     * Version Added:
     *     6.0
     */
    let MenuItemActionView = spina.spina(_class2$2 = class MenuItemActionView extends ActionView {
      static events = {
        'click': '_onClick',
        'touchstart': '_onTouchStart'
      };

      /**
       * Handle a click event.
       *
       * Args:
       *     e (MouseEvent):
       *         The event.
       */
      _onClick(e) {
        e.stopPropagation();
        e.preventDefault();
        this.activate();
      }

      /**
       * Handle a touchstart event.
       */
      _onTouchStart() {
        /*
         * For touch events, we explicitly let the event bubble up so that the
         * parent menu can close.
         */
        this.activate();
      }

      /**
       * Activate the action.
       */
      activate() {
        // This is expected to be overridden by subclasses.
      }
    }) || _class2$2;

    const Actions = {
      Action,
      ActionView,
      MenuAction,
      MenuActionView,
      MenuItemActionView
    };

    var _class$h;

    /**
     * The base class used for Review Board collections.
     *
     * This is a thin subclass over Backbone.Collection that just provides
     * some useful additional abilities.
     */
    let BaseCollection = spina.spina(_class$h = class BaseCollection extends spina.BaseCollection {
      /**
       * Fetch models from the server.
       *
       * This behaves just like Backbone.Collection.fetch, except it
       * takes a context parameter for callbacks and can return promises.
       *
       * Version Changed:
       *     5.0:
       *     This method was changed to return a promise. Using callbacks instead
       *     of the promise is deprecated, and will be removed in Review Board
       *     6.0.
       *
       * Args:
       *     options (object):
       *         Options for the fetch operation.
       *
       *     context (object):
       *         Context to be used when calling callbacks.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the fetch operation is complete.
       */
      fetch(options = {}, context = undefined) {
        if (_.isFunction(options.success) || _.isFunction(options.error)) {
          console.warn('RB.BaseCollection.fetch was called using ' + 'callbacks. Callers should be updated to use ' + 'promises instead.');
          return RB.promiseToCallbacks(options, context, newOptions => this.fetch(newOptions));
        }
        return new Promise((resolve, reject) => {
          super.fetch(_.defaults({
            error: (model, xhr, options) => reject(new BackboneError(model, xhr, options)),
            success: result => resolve(result)
          }, options));
        });
      }

      /**
       * Handle all AJAX communication for the collection.
       *
       * Backbone.js will internally call the model's sync function to
       * communicate with the server, which usually uses Backbone.sync.
       *
       * This will parse error response from Review Board so we can provide
       * a more meaningful error callback.
       *
       * Args:
       *     method (string):
       *         The HTTP method to use for the AJAX request.
       *
       *     model (object):
       *         The model to sync.
       *
       *     options (object):
       *         Options for the sync operation.
       */
      sync(method, model, options = {}) {
        return Backbone.sync.call(this, method, model, _.defaults({
          error: (xhr, textStatus, errorThrown) => {
            RB.storeAPIError(xhr);
            if (_.isFunction(options.error)) {
              options.error(xhr, textStatus, errorThrown);
            }
          }
        }, options));
      }
    }) || _class$h;

    var _class$g;

    /** Options for the ResourceCollection object. */

    /** Options for the ResourceCollection.fetch method. */

    /** Options for the ResourceCollection.parse method. */

    /**
     * Base collection for resource models.
     *
     * ResourceCollection handles the fetching of models from resource lists
     * in the API.
     *
     * It can do pagination by using fetchNext/fetchPrev. Callers can check
     * hasNext/hasPrev to determine if they've reached the end.
     *
     * To fetch one page at a time, use fetch(). This can take an optional
     * starting point.
     *
     * Use fetchAll to automatically paginate through all items and store them
     * all within the collection.
     */
    let ResourceCollection = spina.spina(_class$g = class ResourceCollection extends BaseCollection {
      /**********************
       * Instance variables *
       **********************/

      /** The parent resource of the collection. */

      /** Extra data to send with the HTTP request. */

      /** The number of results to fetch at a time. */

      /** Whether there is a previous page that can be fetched. */
      hasPrev = false;

      /** Whether there is a next page that can be fetched. */
      hasNext = false;

      /** The current page to fetch. */
      currentPage = 0;

      /** The total number of results, if available. */

      /** The URL to use when fetching. */
      _fetchURL = null;

      /** The links returned by the resource. */

      /**
       * Initialize the collection.
       *
       * Args:
       *     models (Array of object):
       *         Initial set of models for the collection.
       *
       *     options (object):
       *         Options for the collection.
       *
       * Option Args:
       *     parentResource (RB.BaseResource):
       *         The parent API resource.
       *
       *     extraQueryData (object):
       *         Additional attributes to include in the API request query
       *         string.
       */
      initialize(models, options) {
        this.parentResource = options.parentResource;
        this.extraQueryData = options.extraQueryData;
        this.maxResults = options.maxResults;

        /*
         * Undefined means "we don't know how many results there are."
         * This is a valid value when parsing the payload later. It
         * may also be a number.
         */
        this.totalResults = undefined;
        this._fetchURL = null;
        this._links = null;
      }

      /**
       * Return the URL for fetching models.
       *
       * This will make use of a URL provided by fetchNext/fetchPrev/fetchAll,
       * if provided.
       *
       * Otherwise, this will try to get the URL from the parent resource.
       *
       * Returns:
       *     string:
       *     The URL to fetch.
       */
      url() {
        if (this._fetchURL) {
          return this._fetchURL;
        }
        if (this.parentResource) {
          const links = this.parentResource.get('links');
          const listKey = _.result(this.model.prototype, 'listKey');
          const link = links[listKey];
          return link ? link.href : null;
        }
        return null;
      }

      /**
       * Parse the results from the list payload.
       *
       * Args:
       *     rsp (object):
       *         The response from the server.
       *
       *     options (ResourceCollectionParseOptions):
       *         The options that were used for the fetch operation.
       */
      parse(rsp, options = {}) {
        const listKey = _.result(this.model.prototype, 'listKey');
        this._links = rsp.links || null;
        this.totalResults = rsp.total_results;
        if (options.fetchingAll) {
          this.hasPrev = false;
          this.hasNext = false;
          this.currentPage = 0;
        } else {
          this.totalResults = rsp.total_results;
          this.hasPrev = this._links !== null && this._links.prev !== undefined;
          this.hasNext = this._links !== null && this._links.next !== undefined;
          this.currentPage = options.page;
        }
        return rsp[listKey];
      }

      /**
       * Fetch models from the list.
       *
       * By default, this will replace the list of models in this collection.
       * That can be changed by providing `reset: false` in options.
       *
       * The first page of resources will be fetched unless options.start is
       * set. The value is the start position for the number of objects, not
       * pages.
       *
       * Version Changed:
       *     5.0:
       *     Deprecated callbacks and added a promise return value.
       *
       * Args:
       *     options (ResourceCollectionFetchOptions):
       *         Options for the fetch operation.
       *
       *     context (object):
       *         Context to be used when calling callbacks.
       */
      async fetch(options = {}, context = undefined) {
        if (_.isFunction(options.success) || _.isFunction(options.error) || _.isFunction(options.complete)) {
          console.warn('RB.ResourceCollection.fetch was called using ' + 'callbacks. Callers should be updated to use ' + 'promises instead.');
          return RB.promiseToCallbacks(options, context, newOptions => this.fetch(newOptions));
        }
        const data = _.extend({}, options.data);
        if (options.start !== undefined) {
          data.start = options.start;
        }

        /*
         * There's a couple different ways that the max number of results
         * can be specified. We'll want to support them all.
         *
         * If a value is passed in extraQueryData, it takes precedence.
         * We'll just set it further down. Otherwise, options.maxResults
         * will be used if passed, falling back on the maxResults passed
         * during collection construction.
         */
        if (!this.extraQueryData || this.extraQueryData['max-results'] === undefined) {
          if (options.maxResults !== undefined) {
            data['max-results'] = options.maxResults;
          } else if (this.maxResults) {
            data['max-results'] = this.maxResults;
          }
        }
        if (options.reset === undefined) {
          options.reset = true;
        }

        /*
         * Versions of Backbone prior to 1.1 won't respect the reset option,
         * instead requiring we use 'remove'. Support this for compatibility,
         * until we move to Backbone 1.1.
         */
        options.remove = options.reset;
        const expandedFields = this.model.prototype.expandedFields;
        if (expandedFields.length > 0) {
          data.expand = expandedFields.join(',');
        }
        if (this.extraQueryData) {
          _.defaults(data, this.extraQueryData);
        }
        options.data = data;
        if (this.parentResource) {
          await this.parentResource.ready();
        }
        await super.fetch(options);
      }

      /**
       * Fetch the previous batch of models from the resource list.
       *
       * This requires hasPrev to be true, from a prior fetch.
       *
       * The collection's list of models will be replaced with the new list
       * after the fetch succeeds. Each time fetchPrev is called, the collection
       * will consist only of that page's batch of models. This can be overridden
       * by providing `reset: false` in options.
       *
       * Version Changed:
       *     5.0:
       *     Deprecated callbacks and added a promise return value.
       *
       * Args:
       *     options (ResourceCollectionFetchOptions):
       *         Options for the fetch operation.
       *
       *     context (object):
       *         Context to bind when calling callbacks.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the operation is complete.
       */
      fetchPrev(options = {}, context = undefined) {
        if (_.isFunction(options.success) || _.isFunction(options.error) || _.isFunction(options.complete)) {
          console.warn('RB.ResourceCollection.fetchPrev was called using ' + 'callbacks. Callers should be updated to use ' + 'promises instead.');
          return RB.promiseToCallbacks(options, context, newOptions => this.fetchPrev(newOptions));
        }
        if (!this.hasPrev) {
          return Promise.resolve();
        }
        this._fetchURL = this._links.prev.href;
        return this.fetch(_.defaults({
          page: this.currentPage - 1
        }, options));
      }

      /**
       * Fetch the next batch of models from the resource list.
       *
       * This requires hasNext to be true, from a prior fetch.
       *
       * The collection's list of models will be replaced with the new list
       * after the fetch succeeds. Each time fetchNext is called, the collection
       * will consist only of that page's batch of models. This can be overridden
       * by providing `reset: false` in options.
       *
       * Version Changed:
       *     5.0:
       *     Deprecated callbacks and added a promise return value.
       *
       * Args:
       *     options (ResourceCollectionFetchOptions):
       *         Options for the fetch operation.
       *
       *     context (object):
       *         Context to bind when calling callbacks.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the operation is complete.
       */
      fetchNext(options = {}, context = undefined) {
        if (_.isFunction(options.success) || _.isFunction(options.error) || _.isFunction(options.complete)) {
          console.warn('RB.ResourceCollection.fetchNext was called using ' + 'callbacks. Callers should be updated to use ' + 'promises instead.');
          return RB.promiseToCallbacks(options, context, newOptions => this.fetchNext(newOptions));
        }
        if (!this.hasNext && options.enforceHasNext !== false) {
          return Promise.resolve();
        }
        this._fetchURL = this._links.next.href;
        return this.fetch(_.defaults({
          page: this.currentPage + 1
        }, options));
      }

      /**
       * Fetch all models from the resource list.
       *
       * This will fetch all the models from a resource list on a server,
       * paginating automatically until all models are fetched. The result is
       * a list of models on the server.
       *
       * This differs from fetch/fetchPrev/fetchNext, which will replace the
       * collection each time a page of resources are loaded.
       *
       * This can end up slowing down the server. Use it carefully.
       *
       * Version Changed:
       *     5.0:
       *     Deprecated callbacks and added a promise return value.
       *
       * Args:
       *     options (ResourceCollectionFetchOptions):
       *         Options for the fetch operation.
       *
       *     context (object):
       *         Context to bind when calling callbacks.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the operation is complete.
       */
      async fetchAll(options = {}, context = undefined) {
        if (_.isFunction(options.success) || _.isFunction(options.error) || _.isFunction(options.complete)) {
          console.warn('RB.ResourceCollection.fetchNext was called using ' + 'callbacks. Callers should be updated to use ' + 'promises instead.');
          return RB.promiseToCallbacks(options, context, newOptions => this.fetchAll(newOptions));
        }
        const fetchOptions = _.defaults({
          enforceHasNext: false,
          fetchingAll: true,
          maxResults: 50,
          reset: false
        }, options);
        this._fetchURL = null;
        this.reset();
        await this.fetch(fetchOptions);
        while (this._links.next) {
          await this.fetchNext(fetchOptions);
        }
      }

      /**
       * Prepare the model for the collection.
       *
       * This overrides Collection's _prepareModel to ensure that the resource
       * has the proper parentObject set.
       *
       * Returns:
       *     Backbone.Model:
       *     The new model.
       */
      _prepareModel(attributes, options) {
        const model = super._prepareModel(attributes, options);
        model.set('parentObject', this.parentResource);
        return model;
      }
    }) || _class$g;

    var _class$f;

    /**
     * A model for holding a resource's extra data.
     *
     * Contains utility methods for serializing it.
     */
    let ExtraData = spina.spina(_class$f = class ExtraData extends spina.BaseModel {
      /**
       * JSONify the extra data.
       *
       * The extra data is serialized such that each key is prefixed with
       * "extra_data." so that the API can understand it. The result of this
       * function should be merged into the serialization of the parent object.
       *
       * Returns:
       *     object:
       *     An object suitable for serializing to JSON.
       */
      toJSON() {
        const data = {};
        for (const [key, value] of Object.entries(this.attributes)) {
          data[`extra_data.${key}`] = value;
        }
        return data;
      }
    }) || _class$f;

    /**
     * A mixin to add a new extra data API to a model.
     *
     * The model this is attached to gains an extraData property that is backed by
     * the extraData key of the model's attributes object. This new API also
     * enhances the model such that extraData object can be interacted with on in a
     * key-value manner instead of dealing with the whole object.
     *
     * Any class that inherits this mixin should call _setupExtraData in its
     * initialize function to ensure that the mixin will work properly. This will
     * set up the property and event listeners.
     */
    const ExtraDataMixin = {
      /**
       * Set up the resource to add the new extra data API.
       *
       * This function should be called in the model's initialize function.
       *
       * This adds an extraData attribute that is backed by the model's
       * attribute.extraData. This new model.extraData can be used directly in a
       * model.extraData.get/set fashion to get or set individual keys in the
       * extra data, instead of getting and setting the extra data all at once.
       *
       * This will also set up event listeners so that changes to extraData
       * through the ExtraData instance will trigger changed events on the
       * model itself
       */
      _setupExtraData() {
        this.extraData = new ExtraData();
        this.extraData.attributes = this.attributes.extraData;
        this.listenTo(this.extraData, 'change', this._onExtraDataChanged);
      },
      /**
       * Set the key to the value with the given options.
       *
       * This is a special case of Backbone.Model's set which does some extra
       * work when dealing with a extraData member. It ensures that extraData is
       * only ever set to an instance of ExtraData and sets up a listener
       * to fire change events when the extraData fires a change event.
       *
       * Args:
       *     key (string):
       *         The key to set.
       *
       *     value (*):
       *         The value to set.
       *
       *     options (object):
       *         Options for the set operation.
       *
       * Returns:
       *     ExtraDataMixin:
       *     This object, for chaining.
       */
      set(key, value, options) {
        let attrs;
        if (_.isObject(key)) {
          attrs = key;
          options = value;
        } else {
          attrs = {};
          attrs[key] = value;
        }
        const useExtraData = _.has(attrs, 'extraData') && _.has(this, 'extraData');
        if (useExtraData) {
          if (attrs.extraData instanceof ExtraData) {
            /*
             * We don't want to assign an ExtraData instance to the
             * model's extraData attribute because it expects a plain
             * JavaScript object.
             */
            attrs.extraData = _.clone(attrs.extraData.attributes);
          }
        }
        Backbone.Model.prototype.set.call(this, attrs, options);
        if (useExtraData) {
          this.extraData.attributes = this.attributes.extraData;
        }
        return this;
      },
      /**
       * Handle a change event fired from the model's extra data.
       *
       * This fires both the change and change:extraData for this model.
       *
       * Args:
       *     extraData (object):
       *         The key:value mapping for the extra data.
       *
       *     options (object):
       *         Options to pass along to event handlers.
       */
      _onExtraDataChanged(extraData, options) {
        this.trigger('change:extraData', this, extraData, options);
        this.trigger('change', this, options);
      },
      /**
       * Get the key from the model's extra data.
       *
       * This should only be used when the model has an extraData attribute.
       *
       * Args:
       *     key (string):
       *         The key to fetch.
       *
       * Returns:
       *     *:
       *     The value of the data.
       */
      getExtraData(key) {
        return this.extraData.get(key);
      },
      /**
       * Set the key in the model's extra data to the value.
       *
       * This should only be used when the model has an extraData attribute.
       *
       * Args:
       *     key (string):
       *         The key to set.
       *
       *     value (*):
       *         The value to set.
       */
      setExtraData(key, value) {
        this.extraData.set(key, value);
      }
    };

    var _dec$4, _class$e;

    /** A link within the resource tree. */

    /**
     * Attributes for the BaseResource model.
     *
     * Version Added:
     *     6.0
     */

    /**
     * Resource data returned by the server.
     *
     * Version Added:
     *     7.0
     */

    /**
     * Options for the ready operation.
     *
     * Version Added:
     *     6.0
     */

    /**
     * Options for the save operation.
     *
     * Version Added:
     *     6.0
     */

    /**
     * Options for saving the resource with files.
     *
     * Version Added:
     *     6.0
     */

    /**
     * The base model for all API-backed resource models.
     *
     * This provides a common set of attributes and functionality for working
     * with Review Board's REST API. That includes fetching data for a known
     * resource, creating resources, saving, deleting, and navigating children
     * resources by way of a payload's list of links.
     *
     * Other resource models are expected to extend this. In particular, they
     * should generally be extending toJSON() and parse().
     */
    let BaseResource = (_dec$4 = spina.spina({
      automergeAttrs: ['attrToJsonMap', 'deserializers', 'serializers'],
      mixins: [ExtraDataMixin],
      prototypeAttrs: ['attrToJsonMap', 'deserializedAttrs', 'deserializers', 'expandedFields', 'extraQueryArgs', 'listKey', 'payloadFileKeys', 'rspNamespace', 'serializedAttrs', 'serializers', 'supportsExtraData', 'urlIDAttr']
    }), _dec$4(_class$e = class BaseResource extends spina.BaseModel {
      static strings = {
        INVALID_EXTRADATA_TYPE: 'extraData must be an object or undefined',
        INVALID_EXTRADATA_VALUE_TYPE: 'extraData.{key} must be null, a number, boolean, or string',
        UNSET_PARENT_OBJECT: 'parentObject must be set'
      };
      /** The key for the namespace for the object's payload in a response. */
      static rspNamespace = '';
      /** The attribute used for the ID in the URL. */
      static urlIDAttr = 'id';
      /** The list of fields to expand in resource payloads. */
      static expandedFields = [];
      /**
       * Extra query arguments for GET requests.
       *
       * This may also be a function that returns the extra query arguments.
       *
       * These values can be overridden by the caller when making a request.
       * They function as defaults for the queries.
       */
      static extraQueryArgs = {};
      /** Whether or not extra data can be associated on the resource. */
      static supportsExtraData = false;
      /**
       * A map of attribute names to resulting JSON field names.
       *
       * This is used to auto-generate a JSON payload from attribute names
       * in toJSON().
       *
       * It's also needed if using attribute names in any save({attrs: [...]})
       * calls.
       */
      static attrToJsonMap = {};
      /** A list of attributes to serialize in toJSON(). */
      static serializedAttrs = [];
      /** A list of attributes to deserialize in parseResourceData(). */
      static deserializedAttrs = [];
      /** Special serializer functions called in toJSON(). */
      static serializers = {};
      /** Special deserializer functions called in parseResourceData(). */
      static deserializers = {};
      /** Files to send along with the API payload. */
      static payloadFileKeys = [];
      /**
       * Return default values for the model attributes.
       *
       * Returns:
       *     object:
       *     The attribute defaults.
       */
      static defaults() {
        return {
          extraData: {},
          links: null,
          loaded: false,
          parentObject: null
        };
      }

      /**
       * Return the key to use when accessing the list resource.
       *
       * Returns:
       *     string:
       *     The name of the key to use when loading data from the list resource.
       */
      static listKey() {
        return this.rspNamespace + 's';
      }

      /**********************
       * Instance variables *
       **********************/

      /**
       * Extra data storage.
       *
       * This will be set by ExtraDataMixin if the resource supports extra data,
       * and should otherwise be undefined.
       */

      /**
       * Initialize the model.
       *
       * Args:
       *     attributes (object):
       *         Initial attribute values for the model.
       *
       *     options (object):
       *         Options for the model.
       */
      initialize(attributes, options) {
        if (this.supportsExtraData) {
          this._setupExtraData();
        }
      }

      /**
       * Return the URL for this resource's instance.
       *
       * If this resource is loaded and has a URL to itself, that URL will
       * be returned. If not yet loaded, it'll try to get it from its parent
       * object, if any.
       *
       * Returns:
       *     string:
       *     The URL to use when fetching the resource. If the URL cannot be
       *     determined, this will return null.
       */
      url() {
        let links = this.get('links');
        if (links) {
          return links.self.href;
        }
        const parentObject = this.get('parentObject');
        if (parentObject) {
          links = parentObject.get('links');
          if (links) {
            const key = _.result(this, 'listKey');
            const link = links[key];
            if (link) {
              const baseURL = link.href;
              return this.isNew() ? baseURL : baseURL + this.get(this.urlIDAttr) + '/';
            }
          }
        }
        return null;
      }

      /**
       * Call a function when the object is ready to use.
       *
       * An object is ready it has an ID and is loaded, or is a new resource.
       *
       * When the object is ready, options.ready() will be called. This may
       * be called immediately, or after one or more round trips to the server.
       *
       * If we fail to load the resource, objects.error() will be called instead.
       *
       * Version Changed:
       *     5.0:
       *     Deprecated callbacks and changed to return a promise.
       *
       * Args:
       *     options (ReadyOptions):
       *         Options for the fetch operation.
       *
       *     context (object):
       *         Context to bind when executing callbacks.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the operation is complete.
       */
      async ready(options = {}, context = undefined) {
        if (_.isFunction(options.success) || _.isFunction(options.error) || _.isFunction(options.complete) || _.isFunction(options.ready)) {
          console.warn('BaseResource.ready was called using callbacks. ' + 'Callers should be updated to use promises instead.');
          return RB.promiseToCallbacks(options, context, () => this.ready());
        }
        const parentObject = this.get('parentObject');
        if (!this.get('loaded')) {
          if (!this.isNew()) {
            // Fetch data from the server
            await this.fetch({
              data: options.data
            });
          } else if (parentObject) {
            /*
             * This is a new object, which means there's nothing to fetch
             * from the server, but we still need to ensure that the
             * parent is loaded in order for it to have valid links.
             */
            await parentObject.ready();
          }
        }
      }

      /**
       * Call a function when we know an object exists server-side.
       *
       * This works like ready() in that it's used to delay operating on the
       * resource until we have a server-side representation. Unlike ready(),
       * it will attempt to create it if it doesn't exist first.
       *
       * If we fail to create the object, options.error() will be called
       * instead.
       *
       * Version Changed:
       *     5.0:
       *     Deprecated callbacks and added a promise return value.
       *
       * Args:
       *     options (object, optional):
       *         Object with success and error callbacks.
       *
       *     context (object, optional):
       *         Context to bind when executing callbacks.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the operation is complete.
       */
      async ensureCreated(options = {}, context = undefined) {
        if (_.isFunction(options.success) || _.isFunction(options.error) || _.isFunction(options.complete)) {
          console.warn('BaseResource.ensureCreated was called using ' + 'callbacks. Callers should be updated to use ' + 'promises instead.');
          return RB.promiseToCallbacks(options, context, () => this.ensureCreated());
        }
        await this.ready();
        if (!this.get('loaded')) {
          await this.save();
        }
      }

      /**
       * Fetch the object's data from the server.
       *
       * An object must have an ID before it can be fetched. Otherwise,
       * options.error() will be called.
       *
       * If this has a parent resource object, we'll ensure that's ready before
       * fetching this resource.
       *
       * The resource must override the parse() function to determine how
       * the returned resource data is parsed and what data is stored in
       * this object.
       *
       * Version Changed:
       *     5.0:
       *     Deprecated the callbacks and added a promise return value.
       *
       * Args:
       *     options (object, optional):
       *         Options to pass through to the base Backbone fetch operation.
       *
       *     context (object, optional):
       *         Context to bind when executing callbacks.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the operation is complete.
       */
      async fetch(options = {}, context = undefined) {
        if (_.isFunction(options.success) || _.isFunction(options.error) || _.isFunction(options.complete)) {
          console.warn('BaseResource.fetch was called using callbacks. ' + 'Callers should be updated to use promises instead.');
          return RB.promiseToCallbacks(options, context, newOptions => this.fetch(newOptions));
        }
        if (this.isNew()) {
          throw new Error('fetch cannot be used on a resource without an ID');
        }
        const parentObject = this.get('parentObject');
        if (parentObject) {
          await parentObject.ready();
        }
        return new Promise((resolve, reject) => {
          super.fetch(_.extend({
            error: (model, xhr, options) => reject(new BackboneError(model, xhr, options)),
            success: () => resolve()
          }, options));
        });
      }

      /**
       * Save the object's data to the server.
       *
       * If the object has an ID already, it will be saved to its known
       * URL using HTTP PUT. If it doesn't have an ID, it will be saved
       * to its parent list resource using HTTP POST
       *
       * If this has a parent resource object, we'll ensure that's created
       * before saving this resource.
       *
       * An object must either be loaded or have a parent resource linking to
       * this object's list resource URL for an object to be saved.
       *
       * The resource must override the toJSON() function to determine what
       * data is saved to the server.
       *
       * If we successfully save the resource, options.success() will be
       * called, and the "saved" event will be triggered.
       *
       * If we fail to save the resource, options.error() will be called.
       *
       * Version Changed:
       *     5.0:
       *     Deprecated the callbacks and added a promise return value.
       *
       * Args:
       *     options (object, optional):
       *         Options for the save operation.
       *
       *     context (object, optional):
       *         Context to bind when executing callbacks.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the operation is complete.
       */
      async save(options = {}, context = undefined) {
        options ??= {};
        if (_.isFunction(options.success) || _.isFunction(options.error) || _.isFunction(options.complete)) {
          console.warn('BaseResource.save was called using callbacks. ' + 'Callers should be updated to use promises instead.');
          return RB.promiseToCallbacks(options, context, newOptions => this.save(newOptions));
        }
        this.trigger('saving', options);
        await this.ready();
        const parentObject = this.get('parentObject');
        if (parentObject) {
          await parentObject.ensureCreated();
        }
        return this._saveObject(options);
      }

      /**
       * Handle the actual saving of the object's state.
       *
       * This is called internally by save() once we've handled all the
       * readiness and creation checks of this object and its parent.
       *
       * Args:
       *     options (object):
       *         Options for the save operation.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the operation is complete.
       */
      _saveObject(options) {
        return new Promise((resolve, reject) => {
          const url = _.result(this, 'url');
          if (!url) {
            reject(new Error('The object must either be loaded from the server or ' + 'have a parent object before it can be saved'));
            return;
          }
          const saveOptions = _.defaults({
            error: (model, xhr, options) => {
              this.trigger('saveFailed', options);
              reject(new BackboneError(model, xhr, options));
            },
            success: (model, xhr) => {
              this.trigger('saved', options);
              resolve(xhr);
            }
          }, options);
          saveOptions.attrs = options.attrs || this.toJSON(options);
          const files = [];
          const readers = [];
          if (!options.form) {
            if (this.payloadFileKeys && window.File) {
              /* See if there are files in the attributes we're using. */
              this.payloadFileKeys.forEach(key => {
                const file = saveOptions.attrs[key];
                if (file) {
                  files.push(file);
                }
              });
            }
          }
          if (files.length > 0) {
            files.forEach(file => {
              const reader = new FileReader();
              readers.push(reader);
              reader.onloadend = () => {
                const ready = readers.every(r => r.readyState === FileReader.DONE);
                if (ready) {
                  this._saveWithFiles(files, readers, saveOptions);
                }
              };
              reader.readAsArrayBuffer(file);
            });
          } else {
            super.save({}, saveOptions);
          }
        });
      }

      /**
       * Save the model with a file upload.
       *
       * When doing file uploads, we need to hand-structure a form-data payload
       * to the server. It will contain the file contents and the attributes
       * we're saving. We can then call the standard save function with this
       * payload as our data.
       *
       * Args:
       *     files (Array of object):
       *         A list of files, with ``name`` and ``type`` keys.
       *
       *     fileReaders (Array of FileReader):
       *         Readers corresponding to each item in ``files``.
       *
       *     options (SaveWithFilesOptions):
       *         Options for the save operation.
       */
      _saveWithFiles(files, fileReaders, options) {
        const boundary = options.boundary || '-----multipartformboundary' + new Date().getTime();
        const blob = [];
        const fileIter = _.zip(this.payloadFileKeys, files, fileReaders);
        for (const [key, file, reader] of fileIter) {
          if (!file || !reader) {
            continue;
          }
          blob.push('--' + boundary + '\r\n');
          blob.push('Content-Disposition: form-data; name="' + key + '"; filename="' + file.name + '"\r\n');
          blob.push('Content-Type: ' + file.type + '\r\n');
          blob.push('\r\n');
          blob.push(reader.result);
          blob.push('\r\n');
        }
        for (const [key, value] of Object.entries(options.attrs)) {
          if (!this.payloadFileKeys.includes(key) && value !== undefined && value !== null) {
            blob.push('--' + boundary + '\r\n');
            blob.push('Content-Disposition: form-data; name="' + key + '"\r\n');
            blob.push('\r\n');
            blob.push(value + '\r\n');
          }
        }
        blob.push('--' + boundary + '--\r\n\r\n');
        super.save({}, _.extend({
          contentType: 'multipart/form-data; boundary=' + boundary,
          data: new Blob(blob),
          processData: false
        }, options));
      }

      /**
       * Delete the object's resource on the server.
       *
       * An object must either be loaded or have a parent resource linking to
       * this object's list resource URL for an object to be deleted.
       *
       * Version Changed:
       *     5.0:
       *     Deprecated callbacks and changed to return a promise.
       *
       * Args:
       *     options (object, optional):
       *         Object with success and error callbacks.
       *
       *     context (object, optional):
       *         Context to use when calling callbacks.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the operation is complete.
       */
      async destroy(options = {}, context = undefined) {
        if (_.isFunction(options.success) || _.isFunction(options.error) || _.isFunction(options.complete)) {
          console.warn('BaseResource.destroy was called using ' + 'callbacks. Callers should be updated to use ' + 'promises instead.');
          return RB.promiseToCallbacks(options, context, newOptions => this.destroy(newOptions));
        }
        this.trigger('destroying', options);
        const parentObject = this.get('parentObject');
        if (!this.isNew() && parentObject) {
          /*
           * XXX This is temporary to support older-style resource
           *     objects. We should just use ready() once we're moved
           *     entirely onto BaseResource.
           */
          await parentObject.ready();
        }
        await this._destroyObject(options);
      }

      /**
       * Set up the deletion of the object.
       *
       * This is called internally by destroy() once we've handled all the
       * readiness and creation checks of this object and its parent.
       *
       * Once we've done some work to ensure the URL is valid and the object
       * is ready, we'll finish destruction by calling _finishDestroy.
       *
       * Args:
       *     options (object):
       *         Options object to include with events.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the operation is complete.
       */
      async _destroyObject(options = {}) {
        const url = _.result(this, 'url');
        if (url) {
          await this.ready();
          await this._finishDestroy(options);
        } else {
          if (this.isNew()) {
            /*
             * If both this resource and its parent are new, it's
             * possible that we'll get through here without a url. In
             * this case, all the data is still local to the client
             * and there's not much to clean up; just call
             * Model.destroy and be done with it.
             */
            await this._finishDestroy(options);
          } else {
            throw new Error('The object must either be loaded from the server ' + 'or have a parent object before it can be deleted');
          }
        }
      }

      /**
       * Finish destruction of the object.
       *
       * This will call the parent destroy method, then reset the state
       * of the object on success.
       *
       * Args:
       *     options (object):
       *         Object with success and error callbacks.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the operation is complete.
       */
      _finishDestroy(options) {
        return new Promise((resolve, reject) => {
          const parentObject = this.get('parentObject');
          super.destroy({
            error: (model, xhr, options) => reject(new BackboneError(model, xhr, options)),
            success: () => {
              /*
               * Reset the object so it's new again, but with the same
               * parentObject.
               */
              this.set(_.defaults({
                id: null,
                parentObject: parentObject
              }, _.result(this, 'defaults')));
              this.trigger('destroyed', options);
              resolve();
            },
            wait: true
          });
        });
      }

      /**
       * Parse and returns the payload from an API response.
       *
       * This will by default only return the object's ID and list of links.
       * Subclasses should override this to return any additional data that's
       * needed, but they must include the results of
       * BaseResource.prototype.parse as well.
       *
       * Args:
       *     rsp (object):
       *         The payload received from the server.
       *
       * Returns:
       *     object:
       *     Attributes to set on the model.
       */
      parse(rsp) {
        console.assert(this.rspNamespace, 'rspNamespace must be defined on the resource model');

        /*
         * TODO: we really shouldn't be using the same method to "parse"
         * attributes provided by code and API responses, since they're
         * separate formats.
         *
         * API responses ought to get pre-processed to check stat and pull out
         * the payload, and then pass that data through to here.
         */
        if (rsp.stat !== undefined) {
          /*
           * This resource payload is inside an envelope from an API
           * call. It's not model construction data or from a list
           * resource.
           */
          rsp = rsp[this.rspNamespace];
        }
        return _.defaults({
          extraData: rsp.extra_data,
          id: rsp.id,
          links: rsp.links,
          loaded: true
        }, this.parseResourceData(rsp));
      }

      /*
       * Parse the resource data from a payload.
       *
       * By default, this will make use of attrToJsonMap and any
       * jsonDeserializers to construct a resulting set of attributes.
       *
       * This can be overridden by subclasses.
       *
       * Args:
       *     rsp (object):
       *         The payload received from the server.
       *
       * Returns:
       *     object:
       *     Attributes to set on the model.
       */
      parseResourceData(rsp) {
        const attrs = {};
        for (const attrName of this.deserializedAttrs) {
          const deserializer = this.deserializers[attrName];
          const jsonField = this.attrToJsonMap[attrName] || attrName;
          let value = rsp[jsonField];
          if (deserializer) {
            value = deserializer.call(this, value);
          }
          if (value !== undefined) {
            attrs[attrName] = value;
          }
        }
        return attrs;
      }

      /**
       * Serialize and return object data for the purpose of saving.
       *
       * When saving to the server, the only data that will be sent in the
       * API PUT/POST call will be the data returned from toJSON().
       *
       * This will build the list based on the serializedAttrs, serializers,
       * and attrToJsonMap properties.
       *
       * Subclasses can override this to create custom serialization behavior.
       *
       * Args:
       *     options (object):
       *         Options for the save operation.
       *
       * Returns:
       *     object:
       *     The serialized data.
       */
      toJSON(options) {
        const serializerState = {
          isNew: this.isNew(),
          loaded: this.get('loaded')
        };
        const data = {};
        for (const attrName of this.serializedAttrs) {
          const serializer = this.serializers[attrName];
          let value = this.get(attrName);
          if (serializer) {
            value = serializer.call(this, value, serializerState);
          }
          const jsonField = this.attrToJsonMap[attrName] || attrName;
          data[jsonField] = value;
        }
        if (this.supportsExtraData) {
          _.extend(data, this.extraData.toJSON());
        }
        return data;
      }

      /**
       * Handle all AJAX communication for the model and its subclasses.
       *
       * Backbone.js will internally call the model's sync function to
       * communicate with the server, which usually uses Backbone.sync.
       *
       * We wrap this to convert the data to encoded form data (instead
       * of Backbone's default JSON payload).
       *
       * We also parse the error response from Review Board so we can provide
       * a more meaningful error callback.
       *
       * Args:
       *     method (string):
       *         The HTTP method to use.
       *
       *     model (Backbone.Model):
       *         The model to sync.
       *
       *     options (SyncOptions):
       *         Options for the operation.
       */
      sync(method, model, options = {}) {
        let data;
        let contentType;
        if (method === 'read') {
          data = options.data || {};
          const extraQueryArgs = _.result(this, 'extraQueryArgs', {});
          if (!_.isEmpty(extraQueryArgs)) {
            data = _.extend({}, extraQueryArgs, data);
          }
        } else {
          if (options.form) {
            data = null;
          } else if (options.attrs && !_.isArray(options.attrs)) {
            data = options.attrs;
          } else {
            data = model.toJSON(options);
            if (options.attrs) {
              data = _.pick(data, options.attrs.map(attr => this.attrToJsonMap[attr] || attr));
            }
          }
          contentType = 'application/x-www-form-urlencoded';
        }
        const syncOptions = _.defaults({}, options, {
          /* Use form data instead of a JSON payload. */
          contentType: contentType,
          data: data,
          processData: true
        });
        if (!options.form && this.expandedFields.length > 0) {
          syncOptions.data.expand = this.expandedFields.join(',');
        }
        syncOptions.error = (xhr, textStatus, jqXHR) => {
          RB.storeAPIError(xhr);
          const rsp = xhr.errorPayload;
          if (rsp && _.has(rsp, this.rspNamespace)) {
            /*
             * The response contains the current version of the object,
             * which we want to preserve, in case it did any partial
             * updating of data.
             */
            this.set(this.parse(rsp));
          }
          if (_.isFunction(options.error)) {
            options.error(xhr, textStatus, jqXHR);
          }
        };
        return Backbone.sync.call(this, method, model, syncOptions);
      }

      /**
       * Perform validation on the attributes of the resource.
       *
       * By default, this validates the extraData field, if provided.
       *
       * Args:
       *     attrs (object):
       *         The attributes to validate.
       *
       * Returns:
       *     string:
       *     An error string or ``undefined``.
       */
      validate(attrs) {
        if (this.supportsExtraData && attrs.extraData !== undefined) {
          const strings = BaseResource.strings;
          if (!_.isObject(attrs.extraData)) {
            return strings.INVALID_EXTRADATA_TYPE;
          }
          for (const [key, value] of Object.entries(attrs.extraData)) {
            if (!_.isNull(value) && (!_.isNumber(value) || _.isNaN(value)) && !_.isBoolean(value) && !_.isString(value)) {
              return strings.INVALID_EXTRADATA_VALUE_TYPE.replace('{key}', key);
            }
          }
        }
      }
    }) || _class$e);

    var _class$d, _class2$1, _class3;

    /** Attributes for the StoredItems model. */
    /**
     * An item in a StoredItems list.
     *
     * These are used internally to proxy object registration into a store list.
     * It is meant to be a temporary, internal object that can be created with
     * the proper data and then immediately saved or deleted.
     *
     * Model Attributes:
     *     baseURL (string):
     *         The root of the URL for the resource list.
     *
     *     loaded (boolean):
     *         Whether the item is loaded from the server.
     *
     *     objectID (string):
     *         The ID of the item.
     *
     *     stored (boolean):
     *         Whether or not the item has been stored on the server.
     */
    let Item = spina.spina(_class$d = class Item extends BaseResource {
      /**
       * Return defaults for the model attributes.
       *
       * Returns:
       *     object:
       *     Default values for the attributes.
       */
      static defaults = {
        baseURL: null,
        loaded: true,
        objectID: null,
        stored: false
      };

      /**
       * Return the URL for the item resource.
       *
       * Returns:
       *     string:
       *     The URL to use for updating the item.
       */
      url() {
        let url = this.get('baseURL');
        if (this.get('stored')) {
          url += this.get('objectID') + '/';
        }
        return url;
      }

      /**
       * Return whether the item is new (not yet stored on the server).
       *
       * Returns:
       *     boolean:
       *     Whether the item is new.
       */
      isNew() {
        return !this.get('stored');
      }

      /**
       * Return a JSON-serializable representation of the item.
       *
       * Returns:
       *    object:
       *    A representation of the item suitable for serializing to JSON.
       */
      toJSON() {
        return {
          object_id: this.get('objectID') || undefined
        };
      }

      /**
       * Parse the response from the server.
       */
      parse(/* rsp */
      ) {
        return undefined;
      }
    }) || _class$d;
    /** Attributes for the StoredItems model. */
    /**
     * Manages a list of stored objects.
     *
     * This interfaces with a Watched Items resource (for groups or review
     * requests) and a Hidden Items resource, allowing immediate adding/removing
     * of objects.
     */
    let StoredItems = spina.spina(_class2$1 = class StoredItems extends BaseResource {
      /**
       * Return the defaults for the model attributes.
       *
       * Returns:
       *     object:
       *     The default values for the model attributes.
       */
      defaults() {
        return _.defaults({
          addError: '',
          removeError: ''
        }, super.defaults());
      }

      /**
       * Return the URL for the resource.
       *
       * Returns:
       *     string:
       *     The URL for the resource.
       */
      url() {
        return this.get('url');
      }

      /**
       * Immediately add an object to a stored list on the server.
       *
       * Version Changed:
       *     6.0:
       *     Removed options and context parameters.
       *
       * Version Changed:
       *     5.0:
       *     Deprecated the options and context parameters and changed to return
       *     a promise.
       *
       * Args:
       *     obj (Backbone.Model):
       *         The item to add.
       *
       *     options (object, optional):
       *         Options for the save operation.
       *
       *     context (object, optional):
       *         Context to use when calling the callbacks in ``options``.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the operation is complete.
       */
      addImmediately(obj) {
        const url = this.url();
        if (url) {
          const item = new Item({
            baseURL: url,
            objectID: String(obj.id)
          });
          return item.save();
        } else {
          return Promise.reject(new Error(this.attributes.addError));
        }
      }

      /**
       * Immediately remove an object from a stored list on the server.
       *
       * Version Changed:
       *     6.0:
       *     Removed options and context parameters.
       *
       * Version Changed:
       *     5.0:
       *     Deprecated the options and context parameters and changed to return
       *     a promise.
       *
       * Args:
       *     obj (Backbone.Model):
       *         The item to remove.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the operation is complete.
       */
      removeImmediately(obj) {
        const url = this.url();
        return new Promise((resolve, reject) => {
          if (url) {
            const item = new Item({
              baseURL: url,
              objectID: String(obj.id),
              stored: true
            });
            resolve(item.destroy());
          } else {
            reject(new Error(this.attributes.removeError));
          }
        });
      }
    }) || _class2$1;
    /** Attributes for the UserSession model. */
    /**
     * Manages the user's active session.
     *
     * This stores basic information on the user (the username and session API URL)
     * and utility objects such as the watched groups, watched review requests and
     * hidden review requests lists.
     *
     * There should only ever be one instance of a UserSession. It should always
     * be created through UserSession.create, and retrieved through
     * UserSession.instance.
     */
    let UserSession = spina.spina(_class3 = class UserSession extends spina.BaseModel {
      /** The singleton instance of the session object. */
      static instance = null;

      /**
       * Create the UserSession for the current user.
       *
       * Only one will ever exist. Calling this a second time will assert.
       *
       * Args:
       *     attributes (object):
       *         Attributes to pass into the UserSession initializer.
       *
       * Returns:
       *     UserSession:
       *     The user session instance.
       */
      static create(attributes) {
        console.assert(!this.instance, 'UserSession.create can only be called once.');
        this.instance = new this(attributes);
        return this.instance;
      }
      defaults = {
        archivedReviewRequestsURL: null,
        authenticated: false,
        diffsShowExtraWhitespace: false,
        fullName: null,
        loginURL: null,
        mutedReviewRequestsURL: null,
        readOnly: false,
        sessionURL: null,
        showReviewDialogTips: true,
        timezoneOffset: '0',
        userFileAttachmentsURL: null,
        userPageURL: null,
        username: null,
        watchedReviewGroupsURL: null,
        watchedReviewRequestsURL: null
      };

      /**********************
       * Instance variables *
       **********************/

      /** The API endpoint for archiving. */

      /** The API endpoint for muting. */

      /** The API endpoint for starring groups. */

      /** The API endpoint for starring review requests. */

      /**
       * Initialize the model.
       */
      initialize() {
        this.watchedGroups = new StoredItems({
          url: this.get('watchedReviewGroupsURL'),
          addError: gettext("Must log in to add a watched item."),
          removeError: gettext("Must log in to remove a watched item.")
        });
        this.watchedReviewRequests = new StoredItems({
          url: this.get('watchedReviewRequestsURL'),
          addError: gettext("Must log in to add a watched item."),
          removeError: gettext("Must log in to remove a watched item.")
        });
        this.archivedReviewRequests = new StoredItems({
          url: this.get('archivedReviewRequestsURL'),
          removeError: gettext("Must log in to remove a archived item."),
          addError: gettext("Must log in to add an archived item.")
        });
        this.mutedReviewRequests = new StoredItems({
          url: this.get('mutedReviewRequestsURL'),
          removeError: gettext("Must log in to remove a muted item."),
          addError: gettext("Must log in to add a muted item.")
        });
        this._bindCookie({
          attr: 'diffsShowExtraWhitespace',
          cookieName: 'show_ew',
          deserialize: value => value !== 'false'
        });
        this._bindCookie({
          attr: 'showReviewDialogTips',
          cookieName: 'show_review_dialog_tips',
          deserialize: value => value !== 'false'
        });
      }

      /**
       * Toggle a boolean attribute.
       *
       * The attribute will be the inverse of the prior value.
       *
       * Args:
       *     attr (string):
       *         The name of the attribute to toggle.
       */
      toggleAttr(attr) {
        this.set(attr, !this.get(attr));
      }

      /*
       * Return avatar HTML for the user with the given size.
       *
       * Version Added:
       *     3.0.19
       *
       * Args:
       *     size (Number):
       *         The size of the avatar, in pixels. This is both the width and
       *         height.
       *
       * Return:
       *     string:
       *     The HTML for the avatar.
       */
      getAvatarHTML(size) {
        const urls = this.get('avatarHTML') || {};
        return urls[size] || '';
      }

      /**
       * Bind a cookie to an attribute.
       *
       * The initial value of the attribute will be set to that of the cookie.
       *
       * When the attribute changes, the cookie will be updated.
       *
       * Args:
       *     options (object):
       *         Options for the bind.
       *
       * Option Args:
       *    attr (string):
       *        The name of the attribute to bind.
       *
       *    cookieName (string):
       *        The name of the cookie to store.
       *
       *    deserialize (function, optional):
       *        A deserialization function to use when fetching the attribute
       *        value.
       *
       *    serialize (function, optional):
       *        A serialization function to use when storing the attribute value.
       */
      _bindCookie(options) {
        const deserialize = options.deserialize || _.identity;
        const serialize = options.serialize || (value => value.toString());
        this.set(options.attr, deserialize($.cookie(options.cookieName)));
        this.on(`change:${options.attr}`, (model, value) => {
          $.cookie(options.cookieName, serialize(value), {
            path: SITE_ROOT
          });
        });
      }
    }) || _class3;

    /**
     * JSON serialization helpers for API resources.
     */

    /** Resource state to use for serializer methods. */

    /**
     * Serialize only if the resource is not loaded.
     *
     * Args:
     *     value (unknown):
     *         The value to serialize.
     *
     *     state (SerializerState):
     *         The resource state.
     */
    function onlyIfUnloaded(value, state) {
      return state.loaded ? undefined : value;
    }

    /**
     * Serialize only if the resource is not loaded and the value exists.
     *
     * Args:
     *     value (unknown):
     *         The value to serialize.
     *
     *     state (SerializerState):
     *         The resource state.
     */
    function onlyIfUnloadedAndValue(value, state) {
      if (!state.loaded && value) {
        return value;
      } else {
        return undefined;
      }
    }

    /**
     * Serialize only if the value exists.
     *
     * Args:
     *     value (unknown):
     *         The value to serialize.
     *
     *     state (SerializerState):
     *         The resource state.
     */
    function onlyIfValue(value) {
      return value || undefined;
    }

    /**
     * Serialize only if the resource has not yet been created on the server.
     *
     * Args:
     *     value (unknown):
     *         The value to serialize.
     *
     *     state (SerializerState):
     *         The resource state.
     */
    function onlyIfNew(value, state) {
      return state.isNew ? value : undefined;
    }

    /**
     * Serializer for text type fields.
     *
     * Args:
     *     value (unknown):
     *         The value to serialize.
     *
     *     state (SerializerState):
     *         The resource state.
     */
    function textType(value) {
      return value ? 'markdown' : 'plain';
    }

    const serializers = /*#__PURE__*/Object.defineProperty({
        __proto__: null,
        onlyIfNew,
        onlyIfUnloaded,
        onlyIfUnloadedAndValue,
        onlyIfValue,
        textType
    }, Symbol.toStringTag, { value: 'Module' });

    var _class$c;

    /**
     * A valid issue status type.
     *
     * Version Added:
     *     7.0
     */
    let CommentIssueStatusType = /*#__PURE__*/function (CommentIssueStatusType) {
      CommentIssueStatusType["DROPPED"] = "dropped";
      CommentIssueStatusType["OPEN"] = "open";
      CommentIssueStatusType["RESOLVED"] = "resolved";
      CommentIssueStatusType["VERIFYING_DROPPED"] = "verifying-dropped";
      CommentIssueStatusType["VERIFYING_RESOLVED"] = "verifying-resolved";
      return CommentIssueStatusType;
    }({});

    /**
     * Attributes for the BaseComment model.
     *
     * Version Added:
     *     7.0
     */

    /**
     * Base comment resource data returned by the server.
     *
     * Version Added:
     *     7.0
     */

    /**
     * The base model for a comment.
     *
     * This provides all the common properties, serialization, deserialization,
     * validation, and other functionality of comments. It's meant to be
     * subclassed by more specific implementations.
     */
    let BaseComment = spina.spina(_class$c = class BaseComment extends BaseResource {
      /**
       * Return default values for the model attributes.
       *
       * Returns:
       *     BaseCommentAttrs:
       *     The default values for the model attributes.
       */
      static defaults() {
        return {
          forceTextType: null,
          html: null,
          includeTextTypes: null,
          issueOpened: null,
          issueStatus: null,
          markdownTextFields: {},
          rawTextFields: {},
          richText: null,
          text: ''
        };
      }

      /**
       * Return extra arguments to add to API query strings.
       *
       * Returns:
       *     object:
       *     Any extra query arguments for GET requests.
       */
      static extraQueryArgs() {
        let textTypes = 'raw';
        if (UserSession.instance.get('defaultUseRichText')) {
          textTypes += ',markdown';
        }
        return {
          'force-text-type': 'html',
          'include-text-types': textTypes
        };
      }
      static supportsExtraData = true;
      static attrToJsonMap = {
        forceTextType: 'force_text_type',
        includeTextTypes: 'include_text_types',
        issueOpened: 'issue_opened',
        issueStatus: 'issue_status',
        richText: 'text_type'
      };
      static serializedAttrs = ['forceTextType', 'includeTextTypes', 'issueOpened', 'issueStatus', 'richText', 'text'];
      static deserializedAttrs = ['issueOpened', 'issueStatus', 'text', 'html'];
      static serializers = {
        forceTextType: onlyIfValue,
        includeTextTypes: onlyIfValue,
        issueStatus: function (value) {
          if (this.get('loaded')) {
            const parentObject = this.get('parentObject');
            if (parentObject.get('public')) {
              return value;
            }
          }
          return undefined;
        },
        richText: textType
      };

      /*
       * Legacy definitions for an issue status type.
       *
       * These remain around for compatibility reasons, but are pending
       * deprecation.
       */
      static STATE_DROPPED = CommentIssueStatusType.DROPPED;
      static STATE_OPEN = CommentIssueStatusType.OPEN;
      static STATE_RESOLVED = CommentIssueStatusType.RESOLVED;
      static STATE_VERIFYING_DROPPED = CommentIssueStatusType.VERIFYING_DROPPED;
      static STATE_VERIFYING_RESOLVED = CommentIssueStatusType.VERIFYING_RESOLVED;
      static strings = {
        INVALID_ISSUE_STATUS: `issueStatus must be one of STATE_DROPPED, STATE_OPEN,
STATE_RESOLVED, STATE_VERIFYING_DROPPED, or
STATE_VERIFYING_RESOLVED.`
      };

      /**
       * Return whether the given state should be considered open or closed.
       *
       * Args:
       *     state (string):
       *         The state to check.
       *
       * Returns:
       *     boolean:
       *     ``true`` if the given state is open.
       */
      static isStateOpen(state) {
        return state === CommentIssueStatusType.OPEN || state === CommentIssueStatusType.VERIFYING_DROPPED || state === CommentIssueStatusType.VERIFYING_RESOLVED;
      }

      /**
       * Destroy the comment if and only if the text is empty.
       *
       * This works just like destroy(), and will in fact call destroy()
       * with all provided arguments, but only if there's some actual
       * text in the comment.
       */
      destroyIfEmpty() {
        if (!this.get('text')) {
          this.destroy();
        }
      }

      /**
       * Deserialize comment data from an API payload.
       *
       * This must be overloaded by subclasses, and the parent version called.
       *
       * Args:
       *     rsp (object):
       *         The response from the server.
       *
       * Returns:
       *     object:
       *     Attribute values to set on the model.
       */
      parseResourceData(rsp) {
        const rawTextFields = rsp.raw_text_fields || rsp;
        const data = super.parseResourceData(rsp);
        data.richText = rawTextFields['text_type'] === 'markdown';
        if (rsp.raw_text_fields) {
          data.rawTextFields = {
            text: rsp.raw_text_fields.text
          };
        }
        if (rsp.markdown_text_fields) {
          data.markdownTextFields = {
            text: rsp.markdown_text_fields.text
          };
        }
        if (rsp.html_text_fields) {
          data.html = rsp.html_text_fields.text;
        }
        return data;
      }

      /**
       * Perform validation on the attributes of the model.
       *
       * By default, this validates the issueStatus field. It can be
       * overridden to provide additional validation, but the parent
       * function must be called.
       *
       * Args:
       *     attrs (object):
       *         Attribute values to validate.
       *
       * Returns:
       *     string:
       *     An error string, if appropriate.
       */
      validate(attrs) {
        if (_.has(attrs, 'parentObject') && !attrs.parentObject) {
          return BaseResource.strings.UNSET_PARENT_OBJECT;
        }
        const issueStatus = attrs.issueStatus;
        if (issueStatus && issueStatus !== CommentIssueStatusType.DROPPED && issueStatus !== CommentIssueStatusType.OPEN && issueStatus !== CommentIssueStatusType.RESOLVED && issueStatus !== CommentIssueStatusType.VERIFYING_DROPPED && issueStatus !== CommentIssueStatusType.VERIFYING_RESOLVED) {
          return BaseComment.strings.INVALID_ISSUE_STATUS;
        }
        return super.validate(attrs);
      }

      /**
       * Return whether this comment issue requires verification before closing.
       *
       * Returns:
       *     boolean:
       *     True if the issue is marked to require verification.
       */
      requiresVerification() {
        const extraData = this.get('extraData');
        return extraData && extraData.require_verification === true;
      }

      /**
       * Return the username of the author of the comment.
       *
       * Returns:
       *     string:
       *     The username of the comment's author.
       */
      getAuthorUsername() {
        const review = this.get('parentObject');
        return review.get('links').user.title;
      }
    }) || _class$c;

    var _class$b;

    /**
     * Attributes for the DefaultReviewer model.
     *
     * Version Added:
     *     7.0.1
     */

    /**
     * Resource data for the DefaultReviewer model.
     *
     * Version Added:
     *     7.0.1
     */

    /**
     * A default reviewer configuration.
     *
     * Default reviewers auto-populate the list of reviewers for a review request
     * based on the files modified.
     *
     * The support for default reviewers is currently limited to the most basic
     * information. The lists of users, repositories and groups cannot yet be
     * provided.
     */
    let DefaultReviewer = spina.spina(_class$b = class DefaultReviewer extends BaseResource {
      static defaults = {
        fileRegex: null,
        name: null
      };
      static rspNamespace = 'default_reviewer';
      static attrToJsonMap = {
        fileRegex: 'file_regex'
      };
      static serializedAttrs = ['fileRegex', 'name'];
      static deserializedAttrs = ['fileRegex', 'name'];

      /**
       * Return the URL for syncing the model.
       *
       * Returns:
       *     string:
       *     The URL to use when making HTTP requests.
       */
      url() {
        const localSitePrefix = this.get('localSitePrefix') || '';
        const url = `${SITE_ROOT}${localSitePrefix}api/default-reviewers/`;
        return this.isNew() ? url : `${url}${this.id}/`;
      }
    }) || _class$b;

    /** Mixin for resources that are children of a draft resource. */

    /**
     * Mixin for resources that are children of a draft resource.
     *
     * This will ensure that the draft is in a proper state before operating
     * on the resource.
     */
    const DraftResourceChildModelMixin = {
      /**
       * Delete the object's resource on the server.
       *
       * This will ensure the draft is created before deleting the object,
       * in order to record the deletion as part of the draft.
       *
       * Args:
       *     options (object, optional):
       *         Options for the operation, including callbacks.
       *
       *     context (object, optional):
       *         Context to bind when calling callbacks.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the operation is complete.
       */
      async destroy(options = {}, context = undefined) {
        if (_.isFunction(options.success) || _.isFunction(options.error) || _.isFunction(options.complete)) {
          console.warn('RB.DraftResourceChildModelMixin.destroy was ' + 'called using callbacks. Callers should be updated ' + 'to use promises instead.');
          return RB.promiseToCallbacks(options, context, newOptions => this.destroy(newOptions));
        }
        await this.get('parentObject').ensureCreated();
        await _super(this).destroy.call(this, options);
      },
      /**
       * Call a function when the object is ready to use.
       *
       * This will ensure the draft is created before ensuring the object
       * is ready.
       *
       * Version Changed:
       *     5.0:
       *     Deprecated callbacks and changed to return a promise.
       *
       * Args:
       *     options (object, optional):
       *         Options for the operation, including callbacks.
       *
       *     context (object, optional):
       *         Context to bind when calling callbacks.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the operation is complete.
       */
      async ready(options = {}, context = undefined) {
        if (_.isFunction(options.success) || _.isFunction(options.error) || _.isFunction(options.complete) || _.isFunction(options.ready)) {
          console.warn('RB.DraftResourceChildModelMixin.ready was ' + 'called using callbacks. Callers should be updated ' + 'to use promises instead.');
          return RB.promiseToCallbacks(options, context, newOptions => this.ready());
        }
        await this.get('parentObject').ensureCreated();
        await _super(this).ready.call(this);
      }
    };

    var _class$a;

    /**
     * States for file attachments.
     *
     * This coincides with
     * :py:class:`reviewboard.reviews.models.review_request.FileAttachmentState`.
     *
     * Version Added:
     *     6.0
     */
    let FileAttachmentStates = /*#__PURE__*/function (FileAttachmentStates) {
      FileAttachmentStates["DELETED"] = "deleted";
      FileAttachmentStates["DRAFT"] = "draft";
      FileAttachmentStates["NEW"] = "new";
      FileAttachmentStates["NEW_REVISION"] = "new-revision";
      FileAttachmentStates["PENDING_DELETION"] = "pending-deletion";
      FileAttachmentStates["PUBLISHED"] = "published";
      return FileAttachmentStates;
    }({});

    /**
     * Attributes for the FileAttachment model.
     *
     *
     * Version Changed:
     *     7.0.3:
     *     Added the ``canAccessReviewUI`` attribute.
     *
     * Version Added:
     *     6.0
     */

    /**
     * Resource data for the FileAttachment model.
     *
     * Version Added:
     *     7.0
     */

    /**
     * Represents a new or existing file attachment.
     */
    let FileAttachment = spina.spina(_class$a = class FileAttachment extends BaseResource {
      /**
       * Return default values for the model attributes.
       *
       * Returns:
       *     object:
       *     The attribute defaults.
       */
      static defaults = {
        'attachmentHistoryID': null,
        'canAccessReviewUI': null,
        'caption': null,
        'downloadURL': null,
        'file': null,
        'filename': null,
        'publishedCaption': null,
        'reviewURL': null,
        'revision': null,
        'state': FileAttachmentStates.NEW,
        'thumbnailHTML': null
      };
      static rspNamespace = 'file_attachment';
      static payloadFileKeys = ['path'];
      static supportsExtraData = true;
      static attrToJsonMap = {
        attachmentHistoryID: 'attachment_history_id',
        canAccessReviewUI: 'is_review_ui_accessible_by',
        downloadURL: 'url',
        file: 'path',
        reviewURL: 'review_url',
        thumbnailHTML: 'thumbnail'
      };
      static serializedAttrs = ['attachmentHistoryID', 'caption', 'file'];
      static deserializedAttrs = ['attachmentHistoryID', 'canAccessReviewUI', 'caption', 'downloadURL', 'filename', 'reviewURL', 'revision', 'state', 'thumbnailHTML'];
      static serializers = {
        'attachmentHistoryID': onlyIfNew,
        'file': onlyIfNew
      };
    }) || _class$a;

    var _dec$3, _class$9;

    /**
     * A file attachment that's part of a draft.
     */
    let DraftFileAttachment = (_dec$3 = spina.spina({
      mixins: [DraftResourceChildModelMixin]
    }), _dec$3(_class$9 = class DraftFileAttachment extends FileAttachment {
      static rspNamespace = 'draft_file_attachment';
    }) || _class$9);

    /**
     * Mixin for resources that have special "draft" URLs.
     */



    /**
     * Options for the ready operation.
     *
     * Version Added:
     *     6.0
     */

    /**
     * Mixin for resources that have special "draft" URLs.
     *
     * Some resources contain a "draft/" singleton URL that will either redirect to
     * the URL for an existing draft, or indicate there's no draft (and requiring
     * that one be created).
     *
     * These resources need a little more logic to look up the draft state and
     * craft the proper URL. They can use this mixin to do that work for them.
     */
    const DraftResourceModelMixin = {
      /**
       * Call a function when the object is ready to use.
       *
       * If the object is unloaded, we'll likely need to grab the draft
       * resource, particularly if we haven't already retrieved a draft.
       *
       * Otherwise, we delegate to the parent's ready().
       *
       * Version Changed:
       *     5.0:
       *     Deprecated callbacks and changed to return a promise.
       *
       * Args:
       *     options (object, optional):
       *         Options for the operation, including callbacks.
       *
       *     context (object, optional):
       *         Context to bind when calling callbacks.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the operation is complete.
       */
      async ready(options = {}, context = undefined) {
        if (_.isFunction(options.success) || _.isFunction(options.error) || _.isFunction(options.complete) || _.isFunction(options.ready)) {
          console.warn('RB.DraftResourceModelMixin.ready was ' + 'called using callbacks. Callers should be updated ' + 'to use promises instead.');
          return RB.promiseToCallbacks(options, context, newOptions => this.ready(newOptions));
        }
        if (!this.get('loaded') && this.isNew() && this._needDraft === undefined) {
          this._needDraft = true;
        }
        await _super(this).ready.call(this, options);
        if (this._needDraft) {
          /*
           * Start by delegating to the parent ready() function. Because the
           * object is "new", this will make sure that the parentObject is
           * ready.
           */
          await this._retrieveDraft(options);
        }
      },
      /**
       * Destroy the object.
       *
       * If destruction is successful, we'll reset the needDraft state so we'll
       * look up the draft the next time an operation is performed.
       *
       * Version Changed:
       *     5.0:
       *     Deprecated callbacks and changed to return a promise.
       *
       * Args:
       *     options (object, optional):
       *         Options for the operation, including callbacks.
       *
       *     context (object, optional):
       *         Context to bind when calling callbacks.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the operation is complete.
       */
      async destroy(options = {}, context = undefined) {
        if (_.isFunction(options.success) || _.isFunction(options.error) || _.isFunction(options.complete)) {
          console.warn('RB.DraftResourceModelMixin.destroy was ' + 'called using callbacks. Callers should be updated ' + 'to use promises instead.');
          return RB.promiseToCallbacks(options, context, newOptions => this.destroy(newOptions));
        }
        await this.ready();
        await _super(this).destroy.call(this, options);

        /* We need to fetch the draft resource again. */
        this._needDraft = true;
      },
      /**
       * Return the URL to use when syncing the model.
       *
       * Custom URL implementation which will return the special draft resource
       * if we have yet to redirect and otherwise delegate to the prototype
       * implementation.
       *
       * Returns:
       *     string:
       *     The URL to use for the resource.
       */
      url() {
        if (this._needDraft) {
          const parentObject = this.get('parentObject');
          const linkName = _.result(this, 'listKey');
          const links = parentObject.get('links');

          /*
           * Chrome hyper-aggressively caches things it shouldn't, and
           * appears to do so in a subtly broken way.
           *
           * If we do a DELETE on a reply's URL, then later a GET (resulting
           * from a redirect from a GET to draft/), Chrome will somehow get
           * confused and associate the GET's caching information with a 404.
           *
           * In order to prevent this, we need to make requests to draft/
           * appear unique. We can do this by appending the timestamp here.
           * Chrome will no longer end up with broken state for our later
           * GETs.
           *
           * Much of this is only required in the case of sqlite, which,
           * with Django, may reuse row IDs, causing problems when making
           * a reply, deleting, and making a new one. In production, this
           * shouldn't be a problem, but it's very confusing during
           * development.
           */
          return links[linkName].href + 'draft/?' + $.now();
        } else {
          return _super(this).url.call(this);
        }
      },
      /**
       * Try to retrieve an existing draft from the server.
       *
       * This uses the special draft/ resource within the resource list, which
       * will redirect to an existing draft if one exists.
       *
       * Args:
       *     options (object):
       *         Options for the operation, including callbacks.
       */
      _retrieveDraft(options) {
        if (!RB.UserSession.instance.get('authenticated')) {
          return Promise.reject(new BackboneError(this, {
            errorText: gettext("You must be logged in to retrieve the draft.")
          }, {}));
        }
        let data = options.data || {};
        const extraQueryArgs = _.result(this, 'extraQueryArgs', {});
        if (!_.isEmpty(extraQueryArgs)) {
          data = _.extend({}, extraQueryArgs, data);
        }
        return new Promise((resolve, reject) => {
          Backbone.Model.prototype.fetch.call(this, {
            data: data,
            error: (model, xhr, options) => {
              if (xhr.status === 404) {
                /*
                 * We now know we don't have an existing draft to work
                 * with, and will eventually need to POST to create a
                 * new one.
                 */
                this._needDraft = false;
                resolve();
              } else {
                reject(new BackboneError(model, xhr, options));
              }
            },
            processData: true,
            success: () => {
              /*
               * There was an existing draft, and we were redirected to
               * it and pulled data from it. We're done.
               */
              this._needDraft = false;
              resolve();
            }
          });
        });
      }
    };

    var _dec$2, _class$8;

    /**
     * Attributes for the ReviewReply model.
     *
     * Version Added:
     *     6.0
     */

    /**
     * ReviewReply resource data returned by the server.
     *
     * Version Added:
     *     6.0
     */

    /**
     * Options for the publish operation.
     *
     * Version Added:
     *     6.0
     */

    /**
     * A review reply.
     *
     * Encapsulates replies to a top-level review.
     */
    let ReviewReply = (_dec$2 = spina.spina({
      mixins: [DraftResourceModelMixin],
      prototypeAttrs: ['COMMENT_LINK_NAMES', 'extraQueryArgs']
    }), _dec$2(_class$8 = class ReviewReply extends BaseResource {
      /**
       * Return default values for the model attributes.
       *
       * Returns:
       *     ReviewReplyAttrs:
       *     The default attributes.
       */
      static defaults() {
        return {
          bodyBottom: null,
          bodyBottomRichText: false,
          bodyTop: null,
          bodyTopRichText: false,
          forceTextType: null,
          includeTextTypes: null,
          'public': false,
          rawTextFields: {},
          review: null,
          timestamp: null
        };
      }
      static rspNamespace = 'reply';
      static listKey = 'replies';
      static extraQueryArgs = {
        'force-text-type': 'html',
        'include-text-types': 'raw'
      };
      static attrToJsonMap = {
        bodyBottom: 'body_bottom',
        bodyBottomRichText: 'body_bottom_text_type',
        bodyTop: 'body_top',
        bodyTopRichText: 'body_top_text_type',
        forceTextType: 'force_text_type',
        includeTextTypes: 'include_text_types'
      };
      static serializedAttrs = ['bodyBottom', 'bodyBottomRichText', 'bodyTop', 'bodyTopRichText', 'forceTextType', 'includeTextTypes', 'public'];
      static deserializedAttrs = ['bodyBottom', 'bodyTop', 'public', 'timestamp'];
      static serializers = {
        bodyBottomRichText: textType,
        bodyTopRichText: textType,
        forceTextType: onlyIfValue,
        includeTextTypes: onlyIfValue,
        'public': value => {
          return value ? true : undefined;
        }
      };
      static COMMENT_LINK_NAMES = ['diff_comments', 'file_attachment_comments', 'general_comments', 'screenshot_comments'];

      /**
       * Parse the response from the server.
       *
       * Args:
       *     rsp (object):
       *         The response from the server.
       *
       * Returns:
       *     object:
       *     The attribute values to set on the model.
       */
      parseResourceData(rsp) {
        const rawTextFields = rsp.raw_text_fields || rsp;
        const data = super.parseResourceData(rsp);
        data.bodyTopRichText = rawTextFields.body_top_text_type === 'markdown';
        data.bodyBottomRichText = rawTextFields.body_bottom_text_type === 'markdown';
        data.rawTextFields = rsp.raw_text_fields || {};
        return data;
      }

      /**
       * Publish the reply.
       *
       * Before publishing, the "publishing" event will be triggered.
       * After successfully publishing, "published" will be triggered.
       *
       * Version Changed:
       *     5.0:
       *     Deprecated callbacks and added a promise return value.
       *
       * Args:
       *     options (object, optional):
       *         Options for the save operation.
       *
       *     context (object, optional):
       *         Context to bind when calling callbacks.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the operation is complete.
       */
      async publish(options = {}, context = undefined) {
        if (_.isFunction(options.success) || _.isFunction(options.error) || _.isFunction(options.complete)) {
          console.warn('RB.ReviewReply.publish was called using ' + 'callbacks. Callers should be updated to use ' + 'promises instead.');
          return RB.promiseToCallbacks(options, context, newOptions => this.publish(newOptions));
        }
        this.trigger('publishing');
        await this.ready();
        this.set('public', true);
        try {
          await this.save({
            data: {
              'public': 1,
              trivial: options.trivial ? 1 : 0
            }
          });
        } catch (err) {
          this.trigger('publishError', err.message);
          throw err;
        }
        this.trigger('published');
      }

      /**
       * Discard the reply if it's empty.
       *
       * If the reply doesn't have any remaining comments on the server, then
       * this will discard the reply.
       *
       * Version Changed:
       *     5.0:
       *     Changed to deprecate options and return a promise.
       *
       * Args:
       *     options (object, optional):
       *         Options for the save operation.
       *
       *     context (object, optional):
       *         Context to bind when calling callbacks.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the operation is complete. The
       *     resolution value will be true if discarded, false otherwise.
       */
      async discardIfEmpty(options = {}, context = undefined) {
        if (_.isFunction(options.success) || _.isFunction(options.error) || _.isFunction(options.complete)) {
          console.warn('RB.ReviewReply.discardIfEmpty was called using ' + 'callbacks. Callers should be updated to use ' + 'promises instead.');
          return RB.promiseToCallbacks(options, context, newOptions => this.discardIfEmpty(newOptions));
        }
        await this.ready();
        if (this.isNew() || this.get('bodyTop') || this.get('bodyBottom')) {
          return false;
        } else {
          return this._checkCommentsLink(0);
        }
      }

      /**
       * Check if there are comments, given the comment type.
       *
       * This is part of the discardIfEmpty logic.
       *
       * If there are comments, we'll give up and call options.success(false).
       *
       * If there are no comments, we'll move on to the next comment type. If
       * we're done, the reply is discarded, and options.success(true) is called.
       *
       * Args:
       *     linkNamesIndex (number):
       *         An index into the ``COMMENT_LINK_NAMES`` Array.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the operation is complete. The
       *     resolution value will be true if discarded, false otherwise.
       */
      _checkCommentsLink(linkNameIndex) {
        return new Promise((resolve, reject) => {
          const linkName = ReviewReply.COMMENT_LINK_NAMES[linkNameIndex];
          const url = this.get('links')[linkName].href;
          RB.apiCall({
            error: (model, xhr, options) => reject(new BackboneError(model, xhr, options)),
            success: rsp => {
              if (rsp[linkName].length > 0) {
                resolve(false);
              } else if (linkNameIndex < ReviewReply.COMMENT_LINK_NAMES.length - 1) {
                resolve(this._checkCommentsLink(linkNameIndex + 1));
              } else {
                resolve(this.destroy().then(() => true));
              }
            },
            type: 'GET',
            url: url
          });
        });
      }
    }) || _class$8);

    var _class$7;

    /**
     * Attributes for the review model.
     *
     * Version Added:
     *     6.0
     */

    /**
     * Review resource data returned by the server.
     *
     * Version Added:
     *     6.0
     */

    /**
     * Options for the create diff comment operation.
     *
     * Version Added:
     *     6.0
     */

    /**
     * A review.
     *
     * This corresponds to a top-level review. Replies are encapsulated in
     * ReviewReply.
     */
    let Review = spina.spina(_class$7 = class Review extends BaseResource {
      /**
       * Return default values for the model attributes.
       *
       * Returns:
       *     ReviewAttrs:
       *     The attribute defaults.
       */
      static defaults() {
        return {
          'authorName': null,
          'bodyBottom': null,
          'bodyBottomRichText': false,
          'bodyTop': null,
          'bodyTopRichText': false,
          'draftReply': null,
          'forceTextType': null,
          'htmlTextFields': {},
          'includeTextTypes': null,
          'markdownTextFields': {},
          'public': false,
          'rawTextFields': {},
          'shipIt': false,
          'timestamp': null
        };
      }
      static rspNamespace = 'review';
      static attrToJsonMap = {
        bodyBottom: 'body_bottom',
        bodyBottomRichText: 'body_bottom_text_type',
        bodyTop: 'body_top',
        bodyTopRichText: 'body_top_text_type',
        forceTextType: 'force_text_type',
        includeTextTypes: 'include_text_types',
        shipIt: 'ship_it'
      };
      static serializedAttrs = ['forceTextType', 'includeTextTypes', 'shipIt', 'bodyTop', 'bodyTopRichText', 'bodyBottom', 'bodyBottomRichText', 'public'];
      static deserializedAttrs = ['shipIt', 'bodyTop', 'bodyBottom', 'public', 'timestamp'];
      static serializers = {
        'bodyBottomRichText': textType,
        'bodyTopRichText': textType,
        'forceTextType': onlyIfValue,
        'includeTextTypes': onlyIfValue,
        'public': value => {
          return value ? 1 : undefined;
        }
      };
      static supportsExtraData = true;

      /**
       * Parse the response from the server.
       *
       * Args:
       *    rsp (object):
       *        The response from the server.
       *
       * Returns:
       *     object:
       *     Attribute values to set on the model.
       */
      parseResourceData(rsp) {
        const rawTextFields = rsp.raw_text_fields || rsp;
        const data = super.parseResourceData(rsp);
        data.bodyTopRichText = rawTextFields.body_top_text_type === 'markdown';
        data.bodyBottomRichText = rawTextFields.body_bottom_text_type === 'markdown';
        if (rsp.raw_text_fields) {
          data.rawTextFields = {
            bodyBottom: rsp.raw_text_fields.body_bottom,
            bodyTop: rsp.raw_text_fields.body_top
          };
        }
        if (rsp.markdown_text_fields) {
          data.markdownTextFields = {
            bodyBottom: rsp.markdown_text_fields.body_bottom,
            bodyTop: rsp.markdown_text_fields.body_top
          };
        }
        if (rsp.html_text_fields) {
          data.htmlTextFields = {
            bodyBottom: rsp.html_text_fields.body_bottom,
            bodyTop: rsp.html_text_fields.body_top
          };
        }
        return data;
      }

      /**
       * Create a new diff comment for this review.
       *
       * Args:
       *     options (object):
       *         Options for creating the review.
       *
       * Option Args:
       *     id (number):
       *         The ID for the new model (in the case of existing comments).
       *
       *     fileDiffID (number):
       *         The ID of the FileDiff that this comment is for.
       *
       *     interFileDiffID (number):
       *         The ID of the FileDiff that represents the "new" side of an
       *         interdiff. If this is specified, the ``fileDiffID`` argument
       *         represents the "old" side.
       *
       *         This option is mutually exclusive with ``baseFileDiffID``.
       *
       *     beginLineNum (number):
       *         The line number of the start of the comment.
       *
       *     endLineNum (number):
       *         The line number of the end of the comment.
       *
       *     baseFileDiffID (number):
       *         The ID of the base FileDiff in the cumulative diff that the
       *         comment is to be made upon.
       *
       *         This option is mutually exclusive with ``interFileDiffID``.
       *
       * Returns:
       *     RB.DiffComment:
       *     The new comment object.
       */
      createDiffComment(options) {
        if (!!options.interFileDiffID && !!options.baseFileDiffID) {
          console.error('Options `interFileDiffID` and `baseFileDiffID` for ' + 'RB.Review.createDiffComment() are mutually exclusive.');
          return null;
        }
        return new RB.DiffComment(_.defaults({
          parentObject: this
        }, options));
      }

      /**
       * Create a new screenshot comment for this review.
       *
       * Args:
       *     id (number):
       *         The ID for the new model (in the case of existing comments).
       *
       *     screenshotID (number):
       *         The ID of the Screenshot that this comment is for.
       *
       *     x (number):
       *         The X coordinate of the pixel for the upper left of the comment
       *         region.
       *
       *     y (number):
       *         The Y coordinate of the pixel for the upper left of the comment
       *         region.
       *
       *     width (number):
       *         The width of the comment region, in pixels.
       *
       *     height (number):
       *         The height of the comment region, in pixels.
       *
       * Returns:
       *     RB.ScreenshotComment:
       *     The new comment object.
       */
      createScreenshotComment(id, screenshotID, x, y, width, height) {
        return new RB.ScreenshotComment({
          height: height,
          id: id,
          parentObject: this,
          screenshotID: screenshotID,
          width: width,
          x: x,
          y: y
        });
      }

      /**
       * Create a new file attachment comment for this review.
       *
       * Args:
       *     id (number):
       *         The ID for the new model (in the case of existing comments).
       *
       *     fileAttachmentID (number):
       *         The ID of the FileAttachment that this comment is for.
       *
       *     diffAgainstFileAttachmentID (number, optional):
       *         The ID of the FileAttachment that the ``fileAttachmentID`` is
       *         diffed against, if the comment is for a file diff.
       *
       * Returns:
       *     RB.FileAttachmentComment:
       *     The new comment object.
       */
      createFileAttachmentComment(id, fileAttachmentID, diffAgainstFileAttachmentID) {
        return new RB.FileAttachmentComment({
          diffAgainstFileAttachmentID: diffAgainstFileAttachmentID,
          fileAttachmentID: fileAttachmentID,
          id: id,
          parentObject: this
        });
      }

      /**
       * Create a new general comment for this review.
       *
       * Args:
       *     id (number):
       *         The ID for the new model (in the case of existing comments).
       *
       *     issueOpened (boolean, optional):
       *         Whether this comment should have an open issue.
       *
       * Returns:
       *     RB.GeneralComment:
       *     The new comment object.
       */
      createGeneralComment(id, issueOpened) {
        return new RB.GeneralComment({
          id: id,
          issueOpened: issueOpened,
          parentObject: this
        });
      }

      /**
       * Create a new reply.
       *
       * If an existing draft reply exists, return that. Otherwise create a draft
       * reply.
       *
       * Returns:
       *     RB.ReviewReply:
       *     The new reply object.
       */
      createReply() {
        let draftReply = this.get('draftReply');
        if (draftReply === null) {
          draftReply = new ReviewReply({
            parentObject: this
          });
          this.set('draftReply', draftReply);
          draftReply.once('published', () => {
            const reviewRequest = this.get('parentObject');
            reviewRequest.markUpdated(draftReply.get('timestamp'));
            this.set('draftReply', null);
          });
        }
        return draftReply;
      }
    }) || _class$7;

    var _dec$1, _class$6;

    /**
     * Attributes for the DraftReview model.
     *
     * Version Added:
     *     6.0
     */

    /**
     * Resource data for the DraftReview model.
     *
     * Version Added:
     *     7.0
     */

    /**
     * A draft review.
     *
     * Draft reviews are more complicated than most objects. A draft may already
     * exist on the server, in which case we need to be able to get its ID. A
     * special resource exists at /reviews/draft/ which will redirect to the
     * existing draft if one exists, and return 404 if not.
     */
    let DraftReview = (_dec$1 = spina.spina({
      mixins: [DraftResourceModelMixin]
    }), _dec$1(_class$6 = class DraftReview extends Review {
      static defaults = {
        publishAndArchive: false,
        publishToOwnerOnly: false
      };
      static attrToJsonMap = {
        publishAndArchive: 'publish_and_archive',
        publishToOwnerOnly: 'publish_to_owner_only'
      };
      static serializedAttrs = ['publishAndArchive', 'publishToOwnerOnly'].concat(Review.serializedAttrs);
      static serializers = {
        publishAndArchive: onlyIfValue,
        publishToOwnerOnly: onlyIfValue
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
      async publish(options = {}, context = undefined) {
        if (_.isFunction(options.success) || _.isFunction(options.error) || _.isFunction(options.complete)) {
          console.warn(`RB.DraftReview.publish was called using callbacks.
                          Callers should be updated to use promises instead.`);
          return RB.promiseToCallbacks(options, context, newOptions => this.publish(newOptions));
        }
        this.trigger('publishing');
        await this.ready();
        this.set('public', true);
        try {
          await this.save({
            attrs: options.attrs
          });
        } catch (err) {
          this.trigger('publishError', err.xhr.errorText);
          throw err;
        }
        this.trigger('published');
      }
    }) || _class$6);

    var _class$5;

    /**
     * Attributes for the Repository model.
     *
     * Version Added:
     *     7.0.1
     */

    /**
     * Resource data for the Repository model.
     *
     * Version Added:
     *     7.0.1
     */

    /**
     * Options for the getCommits operation.
     *
     * Version Added:
     *     7.0.1
     */

    /**
     * A client-side representation of a repository on the server.
     */
    let Repository = spina.spina(_class$5 = class Repository extends BaseResource {
      static defaults = {
        filesOnly: false,
        localSitePrefix: null,
        name: null,
        requiresBasedir: false,
        requiresChangeNumber: false,
        scmtoolName: null,
        supportsPostCommit: false
      };
      static rspNamespace = 'repository';
      static attrToJsonMap = {
        name: 'name',
        requiresBasedir: 'requires_basedir',
        requiresChangeNumber: 'requires_change_number',
        scmtoolName: 'tool',
        supportsPostCommit: 'supports_post_commit'
      };
      static deserializedAttrs = ['name', 'requiresBasedir', 'requiresChangeNumber', 'scmtoolName', 'supportsPostCommit'];
      static listKey = 'repositories';

      /**********************
       * Instance variables *
       **********************/

      /** The repository branches collection. */

      /**
       * Initialize the model.
       */
      initialize(attributes, options) {
        super.initialize(attributes, options);
        this.branches = new RB.RepositoryBranches();
        this.branches.url = _.result(this, 'url') + 'branches/';
      }

      /**
       * Return a collection of commits from a given starting point.
       *
       * Args:
       *     options (GetRepositoryCommitsOptions):
       *         Options for the commits collection.
       *
       * Returns:
       *     RB.RepositoryCommits:
       *     The commits collection.
       */
      getCommits(options) {
        return new RB.RepositoryCommits([], {
          branch: options.branch,
          start: options.start,
          urlBase: _.result(this, 'url') + 'commits/'
        });
      }

      /**
       * Return the URL for syncing the model.
       *
       * Returns:
       *     string:
       *     The URL to use when syncing the model.
       */
      url() {
        const url = SITE_ROOT + (this.get('localSitePrefix') || '') + 'api/repositories/';
        return this.isNew() ? url : `${url}${this.id}/`;
      }
    }) || _class$5;

    var _class$4, _class2;

    /**
     * Attributes for the GroupMember model.
     *
     * Version Added:
     *     7.0.1
     */

    /**
     * Resource data for the GroupMember model.
     *
     * Version Added:
     *     7.0.1
     */
    /**
     * A member of a review group.
     *
     * This is used to handle adding a user to a group or removing from a group.
     */
    let GroupMember = spina.spina(_class$4 = class GroupMember extends BaseResource {
      static defaults = {
        added: false,
        loaded: true,
        username: null
      };
      static serializedAttrs = ['username'];

      /**
       * Return a URL for this resource.
       *
       * If this represents an added user, the URL will point to
       * <groupname>/<username>/. Otherwise, it just points to <groupname>/.
       *
       * Returns:
       *     string:
       *     The URL to use when syncing the model.
       */
      url() {
        let url = this.get('baseURL');
        if (this.get('added')) {
          url += this.get('username') + '/';
        }
        return url;
      }

      /**
       * Return whether the group membership is "new".
       *
       * A non-added user is new, meaning the save operation will trigger
       * a POST to add the user.
       *
       * Returns:
       *     boolean:
       *     Whether this member is newly-added to the group.
       */
      isNew() {
        return !this.get('added');
      }

      /**
       * Parse the result payload.
       *
       * We don't really care about the result, so we don't bother doing any
       * work to parse.
       */
      parse(rsp) {
        // Do nothing.
        return {};
      }
    }) || _class$4;
    /**
     * Attributes for the ReviewGroup model.
     *
     * Version Added:
     *     7.0.1
     */
    /**
     * Resource data for the ReviewGroup model.
     *
     * Version Added:
     *     7.0.1
     */
    /**
     * A review group.
     *
     * This provides some utility functions for working with an existing
     * review group.
     *
     * At the moment, this consists of marking a review group as
     * starred/unstarred.
     */
    let ReviewGroup = spina.spina(_class2 = class ReviewGroup extends BaseResource {
      static defaults = {
        name: null
      };
      static rspNamespace = 'group';

      /**
       * Return the URL to the review group.
       *
       * If this is a new group, the URL will point to the base groups/ URL.
       * Otherwise, it points to the URL for the group itself.
       *
       * Returns:
       *     string:
       *     The URL to use when syncing the model.
       */
      url() {
        let url = SITE_ROOT + (this.get('localSitePrefix') || '') + 'api/groups/';
        if (!this.isNew()) {
          url += this.get('name') + '/';
        }
        return url;
      }

      /**
       * Mark a review group as starred or unstarred.
       *
       * Version Changed:
       *     5.0:
       *     Deprecated the options and context parameters and changed to return
       *     a promise.
       *
       * Args:
       *     starred (boolean):
       *         Whether or not the group is starred.
       *
       *     options (object, optional):
       *         Additional options for the save operation, including callbacks.
       *
       *     context (object, optional):
       *         Context to bind when calling callbacks.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the operation is complete.
       */
      setStarred(starred, options = {}, context = undefined) {
        if (_.isFunction(options.success) || _.isFunction(options.error) || _.isFunction(options.complete)) {
          console.warn('RB.ReviewGroup.setStarred was called using ' + 'callbacks. Callers should be updated to use ' + 'promises instead.');
          return RB.promiseToCallbacks(options, context, newOptions => this.setStarred(starred));
        }
        const watched = UserSession.instance.watchedGroups;
        return starred ? watched.addImmediately(this) : watched.removeImmediately(this);
      }

      /**
       * Add a user to this group.
       *
       * Sends the request to the server to add the user, and notifies on
       * success or failure.
       *
       * Version Changed:
       *     5.0:
       *     Deprecated callbacks and added a promise return value.
       *
       * Args:
       *     username (string):
       *         The username of the new user.
       *
       *     options (object, optional):
       *         Additional options for the save operation.
       *
       *     context (object, optional):
       *         Context to bind when calling callbacks.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the operation is complete.
       */
      addUser(username, options = {}, context = undefined) {
        if (_.isFunction(options.success) || _.isFunction(options.error) || _.isFunction(options.complete)) {
          console.warn('RB.ReviewGroup.addUser was called using ' + 'callbacks. Callers should be updated to use ' + 'promises instead.');
          return RB.promiseToCallbacks(options, context, newOptions => this.addUser(username));
        }
        const url = this.url() + 'users/';
        if (url && !this.isNew()) {
          const member = new GroupMember({
            baseURL: url,
            username: username
          });
          return member.save();
        } else {
          return Promise.reject(new BackboneError(this, {
            errorText: 'Unable to add to the group.'
          }, options));
        }
      }

      /*
       * Remove a user from this group.
       *
       * Sends the request to the server to remove the user, and notifies on
       * success or failure.
       *
       * Version Changed:
       *     5.0:
       *     Deprecated callbacks and added a promise return value.
       *
       * Args:
       *     username (string):
       *         The username of the new user.
       *
       *     options (object, optional):
       *         Additional options for the save operation.
       *
       *     context (object, optional):
       *         Context to bind when calling callbacks.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the operation is complete.
       */
      removeUser(username, options = {}, context = undefined) {
        if (_.isFunction(options.success) || _.isFunction(options.error) || _.isFunction(options.complete)) {
          console.warn('RB.ReviewGroup.removeUser was called using ' + 'callbacks. Callers should be updated to use ' + 'promises instead.');
          return RB.promiseToCallbacks(options, context, newOptions => this.removeUser(username));
        }
        const url = this.url() + 'users/';
        if (url && !this.isNew()) {
          const member = new GroupMember({
            added: true,
            baseURL: url,
            username: username
          });
          return member.destroy();
        } else {
          return Promise.reject(new BackboneError(this, {
            errorText: 'Unable to remove from the group.'
          }, options));
        }
      }
    }) || _class2;

    var _class$3;

    /**
     * Attributes for the ReviewRequest model.
     *
     * Version Added:
     *     7.0
     */

    /**
     * Resource data for the ReviewRequest model.
     *
     * Version Added:
     *     7.0
     */

    /**
     * Options for the ReviewRequest model.
     *
     * Version Added:
     *     7.0
     */

    /**
     * A review request.
     *
     * ReviewRequest is the starting point for much of the resource API. Through
     * it, the caller can create drafts, diffs, file attachments, and screenshots.
     *
     * Fields on a ReviewRequest are set by accessing the ReviewRequest.draft
     * object. Through there, fields can be set like any other model and then
     * saved.
     *
     * A review request can be closed by using the close() function, reopened
     * through reopen(), or even permanently destroyed by calling destroy().
     */
    let ReviewRequest = spina.spina(_class$3 = class ReviewRequest extends BaseResource {
      /**
       * Return default values for the model attributes.
       *
       * Returns:
       *     ReviewRequestAttrs:
       *     Default values for the model attributes.
       */
      static defaults() {
        return {
          approvalFailure: null,
          approved: false,
          branch: null,
          bugTrackerURL: null,
          bugsClosed: null,
          closeDescription: null,
          closeDescriptionRichText: false,
          commitID: null,
          dependsOn: [],
          description: null,
          descriptionRichText: false,
          draftReview: null,
          lastUpdated: null,
          localSitePrefix: null,
          'public': null,
          repository: null,
          reviewURL: null,
          state: null,
          summary: null,
          targetGroups: [],
          targetPeople: [],
          testingDone: null,
          testingDoneRichText: false
        };
      }
      static rspNamespace = 'review_request';
      static extraQueryArgs = {
        'force-text-type': 'html',
        'include-text-types': 'raw'
      };
      static attrToJsonMap = {
        approvalFailure: 'approval_failure',
        bugsClosed: 'bugs_closed',
        closeDescription: 'close_description',
        closeDescriptionRichText: 'close_description_text_type',
        dependsOn: 'depends_on',
        descriptionRichText: 'description_text_type',
        lastUpdated: 'last_updated',
        reviewURL: 'url',
        targetGroups: 'target_groups',
        targetPeople: 'target_people',
        testingDone: 'testing_done',
        testingDoneRichText: 'testing_done_text_type'
      };
      static deserializedAttrs = ['approved', 'approvalFailure', 'branch', 'bugsClosed', 'closeDescription', 'dependsOn', 'description', 'lastUpdated', 'public', 'reviewURL', 'summary', 'targetGroups', 'targetPeople', 'testingDone'];
      static CHECK_UPDATES_MSECS = 5 * 60 * 1000; // Every 5 minutes

      static CLOSE_DISCARDED = 1;
      static CLOSE_SUBMITTED = 2;
      static PENDING = 3;
      static VISIBILITY_VISIBLE = 1;
      static VISIBILITY_ARCHIVED = 2;
      static VISIBILITY_MUTED = 3;

      /**********************
       * Instance variables *
       **********************/

      /** The current draft of the review request, if any. */

      /** The collection of reviews for this review request. */
      reviews = new spina.Collection([], {
        model: Review
      });

      /**
       * Initialize the model.
       *
       * Args:
       *     attrs (object):
       *         Initial values for the model attributes.
       *
       *     options (object):
       *         Additional options for the object construction.
       *
       * Option Args:
       *     extraDraftAttrs (object):
       *         Additional attributes to include when creating a review request
       *         draft.
       */
      initialize(attrs, options = {}) {
        super.initialize(attrs, options);
        this.draft = new RB.DraftReviewRequest(_.defaults({
          branch: this.get('branch'),
          bugsClosed: this.get('bugsClosed'),
          dependsOn: this.get('dependsOn'),
          description: this.get('description'),
          descriptionRichText: this.get('descriptionRichText'),
          parentObject: this,
          summary: this.get('summary'),
          targetGroups: this.get('targetGroups'),
          targetPeople: this.get('targetPeople'),
          testingDone: this.get('testingDone'),
          testingDoneRichText: this.get('testingDoneRichText')
        }, options.extraDraftAttrs));
      }

      /**
       * Return the URL for syncing this model.
       *
       * Returns:
       *     string:
       *     The URL for the API resource.
       */
      url() {
        const url = SITE_ROOT + (this.get('localSitePrefix') || '') + 'api/review-requests/';
        return this.isNew() ? url : `${url}${this.id}/`;
      }

      /**
       * Create the review request from an existing commit.
       *
       * This can only be used for new ReviewRequest instances, and requires
       * a commitID option.
       *
       * Version Changed:
       *     7.0:
       *     Removed the old callback usage.
       *
       * Version Changed:
       *     5.0:
       *     Changed the arguments to take the commit ID directly, and return a
       *     promise rather than use callbacks.
       *
       * Args:
       *     commitID (string):
       *         A string containing the commit ID to create the review
       *         request from.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the operation is complete.
       */
      createFromCommit(commitID) {
        console.assert(!!commitID);
        console.assert(this.isNew());
        this.set('commitID', commitID);
        return this.save({
          createFromCommit: true
        });
      }

      /**
       * Create a Diff object for this review request.
       *
       * Returns:
       *     RB.Diff:
       *     The new diff model.
       */
      createDiff() {
        return new RB.Diff({
          parentObject: this
        });
      }

      /**
       * Create a Review object for this review request.
       *
       * If an ID is specified, the Review object will reference that ID.
       * Otherwise, it is considered a draft review, and will either return
       * the existing one (if the draftReview attribute is set), or create
       * a new one (and set the attribute).
       *
       * Args:
       *     reviewID (number):
       *         The ID of the review, for existing reviews.
       *
       *     extraAttrs (object):
       *         Additional attributes to set on new models.
       *
       * Returns:
       *     RB.Review:
       *     The new review object.
       */
      createReview(reviewID, extraAttrs = {}) {
        let review;
        if (reviewID === undefined) {
          review = this.get('draftReview');
          if (review === null) {
            review = new RB.DraftReview({
              parentObject: this
            });
            this.set('draftReview', review);
          }
        } else {
          review = this.reviews.get(reviewID);
          if (!review) {
            review = new Review(_.defaults({
              id: reviewID,
              parentObject: this
            }, extraAttrs));
            this.reviews.add(review);
          }
        }
        return review;
      }

      /**
       * Create a Screenshot object for this review request.
       *
       * Args:
       *     screenshotID (number):
       *         The ID of the screenshot, for existing screenshots.
       *
       * Returns:
       *     RB.Screenshot:
       *     The new screenshot object.
       */
      createScreenshot(screenshotID) {
        return new RB.Screenshot({
          id: screenshotID,
          parentObject: this
        });
      }

      /**
       * Create a FileAttachment object for this review request.
       *
       * Args:
       *     attributes (object):
       *         Additional attributes to include on the new model.
       *
       * Returns:
       *     RB.FileAttachment:
       *     The new file attachment object.
       */
      createFileAttachment(attributes) {
        return new FileAttachment(_.defaults({
          parentObject: this
        }, attributes));
      }

      /**
       * Mark a review request as starred or unstarred.
       *
       * Version Changed:
       *     7.0:
       *     Got rid of old callbacks-style invocation.
       *
       * Args:
       *     starred (boolean):
       *         Whether the review request is starred.
       *
       *     options (object, optional):
       *         Options for the save operation.
       *
       *     context (object, optional):
       *         Context to bind when calling callbacks.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the operation is complete.
       */
      async setStarred(starred) {
        const watched = UserSession.instance.watchedReviewRequests;
        if (starred) {
          await watched.addImmediately(this);
        } else {
          await watched.removeImmediately(this);
        }
      }

      /**
       * Close the review request.
       *
       * A 'type' option must be provided, which must match one of the
       * close types (ReviewRequest.CLOSE_DISCARDED or
       * ReviewRequest.CLOSE_SUBMITTED).
       *
       * An optional description can be set by passing a 'description' option.
       *
       * Version Changed:
       *     7.0:
       *     Got rid of old callbacks-style invocation.
       *
       * Version Changed:
       *     5.0:
       *     Deprecated callbacks and changed to return a promise.
       *
       * Args:
       *     options (object):
       *         Options for the save operation.
       *
       *     context (object, optional):
       *         Context to bind when calling callbacks.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the operation is complete.
       */
      async close(options) {
        const data = {};
        console.assert(options);
        if (options.type === ReviewRequest.CLOSE_DISCARDED) {
          data.status = 'discarded';
        } else if (options.type === ReviewRequest.CLOSE_SUBMITTED) {
          data.status = 'submitted';
        } else {
          return Promise.reject(new Error('Invalid close type'));
        }
        if (options.description !== undefined) {
          data.close_description = options.description;
        }
        if (options.richText !== undefined) {
          data.close_description_text_type = options.richText ? 'markdown' : 'plain';
        }
        if (options.postData !== undefined) {
          _.extend(data, options.postData);
        }
        const changingState = options.type !== this.get('state');
        const saveOptions = _.defaults({
          data: data
        }, options);
        delete saveOptions.type;
        delete saveOptions.description;
        await this.save(saveOptions);
        if (changingState) {
          this.trigger('closed');
        }
        this.markUpdated(this.get('lastUpdated'));
      }

      /**
       * Reopen the review request.
       *
       * Version Changed:
       *     7.0:
       *     Got rid of old callbacks-style invocation.
       *
       * Version Changed:
       *     5.0:
       *     Deprecated callbacks and changed to return a promise.
       *
       * Returns:
       *     Promise:
       *     A promise which resolves when the operation is complete.
       */
      async reopen() {
        await this.save({
          data: {
            status: 'pending'
          }
        });
        this.trigger('reopened');
        this.markUpdated(this.get('lastUpdated'));
      }

      /**
       * Marks the review request as having been updated at the given timestamp.
       *
       * This should be used when an action will trigger an update to the
       * review request's Last Updated timestamp, but where we don't want
       * a notification later on. The local copy of the timestamp can be
       * bumped to mark it as up-to-date.
       *
       * Args:
       *     timestamp (string):
       *         The timestamp to store.
       */
      markUpdated(timestamp) {
        this._lastUpdateTimestamp = timestamp;
      }

      /**
       * Begin checking for server-side updates to the review request.
       *
       * The 'updated' event will be triggered when there's a new update.
       *
       * Args:
       *     updateType (string):
       *         The type of updates to check for.
       *
       *     lastUpdateTimestamp (string):
       *         The timestamp of the last known update.
       */
      async beginCheckForUpdates(updateType, lastUpdateTimestamp) {
        this._checkUpdatesType = updateType;
        this._lastUpdateTimestamp = lastUpdateTimestamp;
        await this.ready();
        setTimeout(this._checkForUpdates.bind(this), ReviewRequest.CHECK_UPDATES_MSECS);
      }

      /**
       * Check for updates.
       *
       * This is called periodically after an initial call to
       * beginCheckForUpdates. It will see if there's a new update yet on the
       * server, and if there is, trigger the 'updated' event.
       */
      _checkForUpdates() {
        RB.apiCall({
          noActivityIndicator: true,
          prefix: this.get('sitePrefix'),
          success: rsp => {
            const lastUpdate = rsp.last_update;
            if ((!this._checkUpdatesType || this._checkUpdatesType === lastUpdate.type) && this._lastUpdateTimestamp !== lastUpdate.timestamp) {
              this.trigger('updated', lastUpdate);
            }
            this._lastUpdateTimestamp = lastUpdate.timestamp;
            setTimeout(this._checkForUpdates.bind(this), ReviewRequest.CHECK_UPDATES_MSECS);
          },
          type: 'GET',
          url: this.get('links').last_update.href
        });
      }

      /**
       * Serialize for sending to the server.
       *
       * Args:
       *     options (object):
       *         Options for the save operation.
       *
       * Option Args:
       *     createFromCommit (boolean):
       *         Whether this save is going to create a new review request from
       *         an existing committed change.
       *
       * Returns:
       *     object:
       *     Data suitable for passing to JSON.stringify.
       */
      toJSON(options = {}) {
        if (this.isNew()) {
          const commitID = this.get('commitID');
          const repository = this.get('repository');
          const result = {};
          if (commitID) {
            result.commit_id = commitID;
            if (options.createFromCommit) {
              result.create_from_commit_id = true;
            }
          }
          if (repository) {
            result.repository = repository;
          }
          return result;
        } else {
          return super.toJSON(options);
        }
      }

      /**
       * Parse the response from the server.
       *
       * Args:
       *     rsp (object):
       *         The response from the server.
       *
       * Returns:
       *     object:
       *     Attribute values to set on the model.
       */
      parseResourceData(rsp) {
        const state = {
          discarded: ReviewRequest.CLOSE_DISCARDED,
          pending: ReviewRequest.PENDING,
          submitted: ReviewRequest.CLOSE_SUBMITTED
        }[rsp.status];
        const rawTextFields = rsp.raw_text_fields || rsp;
        const data = super.parseResourceData(rsp);
        data.state = state;
        data.closeDescriptionRichText = rawTextFields['close_description_text_type'] === 'markdown';
        data.descriptionRichText = rawTextFields['description_text_type'] === 'markdown';
        data.testingDoneRichText = rawTextFields['testing_done_text_type'] === 'markdown';
        return data;
      }
    }) || _class$3;

    var _class$2;

    /**
     * A message to send on the channel.
     *
     * Version Added:
     *     6.0.
     */

    /**
     * Communication channel to sync between tabs/windows.
     *
     * Version Added:
     *     6.0
     */
    let ClientCommChannel = spina.spina(_class$2 = class ClientCommChannel extends spina.BaseModel {
      static instance = null;

      /**
       * Return the ClientCommChannel instance.
       *
       * Returns:
       *     ClientCommChannel:
       *     The singleton instance.
       */
      static getInstance() {
        return this.instance;
      }

      /**********************
       * Instance variables *
       **********************/

      /** The broadcast channel instance. */
      #channel;

      /**
       * Initialize the model.
       */
      initialize() {
        console.assert(ClientCommChannel.instance === null);
        this.#channel = new BroadcastChannel('reviewboard');
        this.#channel.addEventListener('message', event => {
          const message = event.data;
          switch (message.event) {
            case 'reload':
              this._onReload(message);
              break;
            default:
              console.warn('Received unknown event from BroadcastChannel', message);
              break;
          }
        });
        ClientCommChannel.instance = this;
      }

      /**
       * Close the communication channel.
       */
      close() {
        this.#channel.close();
        console.assert(ClientCommChannel.instance === this);
        ClientCommChannel.instance = null;
      }

      /**
       * Send a reload signal to other tabs.
       */
      reload() {
        const page = RB.PageManager.getPage();
        const pageData = page.getReloadData();
        if (pageData === null) {
          console.warn(`Ignoring page reload request: No page data to send over the
broadcast channel. This would have affected all tabs without
reload data!`);
        } else {
          this.#channel.postMessage({
            data: pageData,
            event: 'reload'
          });
        }
      }

      /**
       * Handle a reload message from another tab.
       *
       * Args:
       *     message (Message):
       *         The message from the other tab.
       */
      _onReload(message) {
        const page = RB.PageManager.getPage();
        if (page) {
          const pageData = page.getReloadData();
          if (pageData !== null && _.isEqual(message.data, pageData)) {
            this.trigger('reload');
          }
        }
      }
    }) || _class$2;

    var _class$1;

    /**
     * Base class for page models.
     *
     * This doesn't provide any functionality by itself, but may be used in the
     * future for introducing additional logic for pages.
     *
     * This is intended for use by page views that are set by
     * :js:class:`RB.PageManager`.
     */
    let Page = spina.spina(_class$1 = class Page extends spina.BaseModel {}) || _class$1;

    var _dec, _class;
    /**
     * Base class for page views.
     *
     * This is responsible for setting up and handling the page's UI, including
     * the page header, mobile mode handling, and sidebars. It also provides some
     * utilities for setting up common UI elements.
     *
     * The page will respect the ``-has-sidebar`` and ``-is-content-full-page``
     * CSS classes on the document ``<body>``. These will control the behavior
     * and layout of the page.
     *
     * This is intended for use by page views that are set by
     * :js:class:`RB.PageManager`.
     */
    let PageView = (_dec = spina.spina({
      prototypeAttrs: ['windowResizeThrottleMS']
    }), _dec(_class = class PageView extends spina.BaseView {
      /**
       * The maximum frequency at which resize events should be handled.
       *
       * Subclasses can override this if they need to respond to window
       * resizes at a faster or slower rate.
       */
      static windowResizeThrottleMS = 100;

      /**********************
       * Instance variables *
       **********************/

      /** The client (tab to tab) communication channel. */
      #commChannel = null;

      /** The sidebar element. */
      $mainSidebar = null;

      /** The page container element. */
      $pageContainer = null;

      /** The page content element. */
      $pageContent = null;

      /** The window, wrapped in JQuery. */

      /** The currently-shown pane for the sidebar. */
      _$mainSidebarPane = null;

      /** The page sidebar element */
      _$pageSidebar = null;

      /** The set of all panes in the sidebar. */
      _$pageSidebarPanes = null;

      /** A list of all registered action views. */
      _actionViews = [];

      /** The pop-out drawer, if the page has one. */
      drawer = null;

      /** Whether the page has a sidebar. */
      hasSidebar = null;

      /** The view for the page header. */
      headerView = null;

      /** Whether the page is currently in a mobile view. */
      inMobileMode = null;

      /** Whether the page is rendered in full-page content mode. */
      isFullPage = null;

      /**
       * Whether the page is rendered.
       *
       * Deprecated:
       *     6.0:
       *     Users should use :js:attr:`rendered` instead.
       */
      isPageRendered = false;
      /**
       * Initialize the page.
       *
       * Args:
       *     options (PageViewOptions, optional):
       *         Options for the page.
       */
      initialize(options = {}) {
        this.options = options;
        this.$window = $(window);
        if (!window.rbRunningTests) {
          this.#commChannel = new ClientCommChannel();
          this.listenTo(this.#commChannel, 'reload', () => {
            alert(gettext("This page is out of date and needs to be reloaded."));
            RB.reload();
          });
        }
      }

      /**
       * Remove the page from the DOM and disable event handling.
       *
       * Returns:
       *     PageView:
       *     This object, for chaining.
       */
      remove() {
        if (this.$window) {
          this.$window.off('resize.rbPageView');
        }
        if (this.headerView) {
          this.headerView.remove();
        }
        return super.remove();
      }

      /**
       * Render the page.
       *
       * Subclasses should not override this. Instead, they should override
       * :js:func:`RB.PageView.renderPage``.
       */
      onInitialRender() {
        const options = this.options;
        const $body = options.$body || $(document.body);
        this.$pageContainer = options.$pageContainer || $('#page-container');
        this.$pageContent = options.$pageContent || $('#content');
        this._$pageSidebar = options.$pageSidebar || $('#page-sidebar');
        this._$pageSidebarPanes = this._$pageSidebar.children('.rb-c-page-sidebar__panes');
        this._$mainSidebarPane = this._$pageSidebarPanes.children('.rb-c-page-sidebar__pane.-is-shown');
        this.$mainSidebar = this._$mainSidebarPane.children('.rb-c-page-sidebar__pane-content');
        this.headerView = new RB.HeaderView({
          $body: $body,
          $pageSidebar: this._$pageSidebar,
          el: options.$headerBar || $('#headerbar')
        });
        this.headerView.render();
        this.hasSidebar = $body.hasClass('-has-sidebar') || $body.hasClass('has-sidebar');
        this.isFullPage = $body.hasClass('-is-content-full-page') || $body.hasClass('full-page-content');
        this.inMobileMode = this.headerView.inMobileMode;
        this.renderPage();

        /*
         * Now that we've rendered the elements, we can show the page.
         */
        $body.addClass('-is-loaded');
        this.$window.on('resize.rbPageView', _.throttle(() => this._updateSize(), this.windowResizeThrottleMS));
        this.listenTo(this.headerView, 'mobileModeChanged', this._onMobileModeChanged);
        this._onMobileModeChanged(this.inMobileMode);
        this._actionViews.forEach(actionView => actionView.render());
        this.isPageRendered = true;
      }

      /**
       * Return data to use for assessing cross-tab page reloads.
       *
       * This is intended to be overridden by subclasses in order to filter which
       * reload signals apply to this page.
       *
       * Version Added:
       *     6.0
       */
      getReloadData() {
        return null;
      }

      /**
       * Set a drawer that can be shown over the sidebar.
       *
       * This is used by a page to set a drawer that should be displayed.
       * Drawers are shown over the sidebar area in desktop mode, or docked to
       * the bottom of the screen in mobile mode.
       *
       * Only one drawer can be set per page. Drawers also require a page with
       * sidebars enabled.
       *
       * Callers must instantiate the drawer but should not render it or
       * add it to the DOM.
       *
       * Args:
       *     drawer (RB.Drawer):
       *         The drawer to set.
       */
      setDrawer(drawer) {
        console.assert(this.drawer === null, 'A drawer has already been set up for this page.');
        console.assert(this.hasSidebar, 'Drawers can only be set up on pages with a sidebar.');
        this.drawer = drawer;
        drawer.render();
        this._reparentDrawer();
        this.listenTo(drawer, 'visibilityChanged', this._updateSize);
      }

      /**
       * Render the page contents.
       *
       * This should be implemented by subclasses that need to render any
       * UI elements.
       */
      renderPage() {
        // Do nothing.
      }

      /**
       * Resize an element to take the full height of a parent container.
       *
       * By default, this will size the element to the height of the main
       * page container. A specific parent can be specified for more specific
       * use cases.
       *
       * Args:
       *     $el (jQuery):
       *         The jQuery-wrapped element to resize.
       *
       *     $parent (jQuery, optional):
       *         The specific jQuery-wrapped parent element to base the size on.
       */
      resizeElementForFullHeight($el, $parent) {
        if ($parent === undefined) {
          $parent = this.$pageContainer;
        }
        $el.outerHeight($parent.height() - $el.position().top);
      }

      /**
       * Handle page resizes.
       *
       * This will be called whenever the page's size (or the window size)
       * has changed, allowing subclasses to adjust any UI elements as
       * appropriate.
       *
       * In the case of window sizes, calls to this function will be throttled,
       * called no more frequently than the configured
       * :js:attr:`windowResizeThrottleMS`.
       */
      onResize() {
        // Do nothing.
      }

      /**
       * Handle mobile mode changes.
       *
       * This will be called whenever the page goes between mobile/desktop
       * mode, allowing subclasses to adjust any UI elements as appropriate.
       *
       * Args:
       *     inMobileMode (boolean):
       *         Whether the UI is now in mobile mode. This will be the same
       *         value as :js:attr:`inMobileMode`, and is just provided for
       *         convenience.
       */
      onMobileModeChanged(inMobileMode) {
        // Do nothing.
      }

      /**
       * Add an action to the page.
       *
       * Args:
       *     actionView (RB.ActionView):
       *         The action instance.
       */
      addActionView(actionView) {
        this._actionViews.push(actionView);
        if (this.isPageRendered) {
          actionView.render();
        }
      }

      /**
       * Return the action view for the given action ID.
       *
       * Args:
       *     actionId (string):
       *         The ID of the action.
       *
       * Returns:
       *     RB.ActionView:
       *     The view for the given action.
       */
      getActionView(actionId) {
        for (const view of this._actionViews) {
          if (view.model.get('actionId') === actionId) {
            return view;
          }
        }
        return null;
      }

      /**
       * Update the size of the page.
       *
       * This will be called in response to window resizes and certain other
       * events. It will calculate the appropriate size for the sidebar (if
       * on the page) and the page container (if in full-page content mode),
       * update any elements as appropriate, and then call
       * :js:func:`RB.PageView.onResize` so that subclasses can update their
       * elements.
       */
      _updateSize() {
        const windowHeight = this.$window.height();
        let pageContainerHeight = null;
        let sidebarHeight = null;
        if (this.isFullPage) {
          pageContainerHeight = windowHeight - this.$pageContainer.offset().top;
        }
        if (this.inMobileMode) {
          if (pageContainerHeight !== null && this.drawer !== null && this.drawer.isVisible) {
            /*
             * If we're constraining the page container's height, and
             * there's a drawer present, reduce the page container's
             * height by the drawer size, so we don't make some content
             * inaccessible due to an overlap.
             */
            pageContainerHeight -= this.drawer.$el.outerHeight();
          }
        } else {
          if (pageContainerHeight !== null) {
            /*
             * If we're constraining the page container's height,
             * constrain the sidebar's as well.
             */
            sidebarHeight = windowHeight - this._$pageSidebar.offset().top;
          }
        }
        if (pageContainerHeight === null) {
          this.$pageContainer.css('height', '');
        } else {
          this.$pageContainer.outerHeight(pageContainerHeight);
        }
        if (sidebarHeight === null) {
          this._$pageSidebar.css('height', '');
        } else {
          this._$pageSidebar.outerHeight(sidebarHeight);
        }
        this.onResize();
      }

      /**
       * Set the new parent for the drawer.
       *
       * In mobile mode, this will place the drawer within the main
       * ``#container``, right before the sidebar, allowing it to appear docked
       * along the bottom of the page.
       *
       * In desktop mode, this will place the drawer within the sidebar area,
       * ensuring that it overlaps it properly.
       */
      _reparentDrawer() {
        const $el = this.drawer.$el.detach();
        if (this.inMobileMode) {
          $el.insertBefore(this._$pageSidebar);
        } else {
          $el.appendTo(this._$pageSidebarPanes);
        }
      }

      /**
       * Handle a transition between mobile and desktop mode.
       *
       * This will set the :js:attr:`inMobileMode` flag and trigger the
       * ``inMobileModeChanged`` event, so that pages can listen and update
       * their layout as appropriate.
       *
       * It will also update the size and reparent the drawer.
       *
       * Args:
       *     inMobileMode (boolean):
       *         Whether the page shell is in mobile mode.
       */
      _onMobileModeChanged(inMobileMode) {
        this.inMobileMode = inMobileMode;
        this._updateSize();
        if (this.drawer !== null) {
          this._reparentDrawer();
        }
        this.onMobileModeChanged(this.inMobileMode);
        this.trigger('inMobileModeChanged', this.inMobileMode);
      }
    }) || _class);

    /**
     * Library for the base-level state and functionality for Review Board.
     *
     * Version Added:
     *     6.0
     */

    /**
     * An interface defining the structure of enabled feature maps.
     *
     * Version Added:
     *     6.0
     */

    /**
     * An interface defining the product information for Review Board.
     *
     * Version Added:
     *     6.0
     */

    /**
     * A mapping of enabled features.
     *
     * Each key corresponds to a feature ID, and each value is set to ``true``.
     *
     * This is filled in on page load. It's empty by default.
     *
     * Version Added:
     *     3.0
     */
    const EnabledFeatures = {};

    /**
     * Information on the running version of Review Board.
     *
     * This is filled in on page load. It's set to mostly blank values by default.
     *
     * Version Added:
     *     4.0
     */
    const Product = {
      isRelease: false,
      manualURL: '',
      name: 'Review Board',
      version: '',
      versionInfo: [0, 0, 0, 0, '', 0]
    };

    exports.Actions = Actions;
    exports.BaseCollection = BaseCollection;
    exports.BaseComment = BaseComment;
    exports.BaseResource = BaseResource;
    exports.ClientCommChannel = ClientCommChannel;
    exports.CommentIssueStatusType = CommentIssueStatusType;
    exports.DefaultReviewer = DefaultReviewer;
    exports.DraftFileAttachment = DraftFileAttachment;
    exports.DraftResourceChildModelMixin = DraftResourceChildModelMixin;
    exports.DraftResourceModelMixin = DraftResourceModelMixin;
    exports.DraftReview = DraftReview;
    exports.EnabledFeatures = EnabledFeatures;
    exports.ExtraData = ExtraData;
    exports.ExtraDataMixin = ExtraDataMixin;
    exports.FileAttachment = FileAttachment;
    exports.FileAttachmentStates = FileAttachmentStates;
    exports.JSONSerializers = serializers;
    exports.Page = Page;
    exports.PageView = PageView;
    exports.Product = Product;
    exports.Repository = Repository;
    exports.ResourceCollection = ResourceCollection;
    exports.Review = Review;
    exports.ReviewGroup = ReviewGroup;
    exports.ReviewReply = ReviewReply;
    exports.ReviewRequest = ReviewRequest;
    exports.UserSession = UserSession;

    Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

}));
//# sourceMappingURL=index.js.map
