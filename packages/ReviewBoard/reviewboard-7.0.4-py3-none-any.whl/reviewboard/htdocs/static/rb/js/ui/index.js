(function (global, factory) {
    typeof exports === 'object' && typeof module !== 'undefined' ? factory(exports, require('@beanbag/ink'), require('@beanbag/spina'), require('codemirror')) :
    typeof define === 'function' && define.amd ? define(['exports', '@beanbag/ink', '@beanbag/spina', 'codemirror'], factory) :
    (global = typeof globalThis !== 'undefined' ? globalThis : global || self, factory(global.RB = global.RB || {}, global.Ink, global.Spina, global.CodeMirror));
})(this, (function (exports, ink, spina, CodeMirror) { 'use strict';

    var _class$a, _class2$2, _dec$1, _class3$2;

    /**
     * Attributes for the DnDDropTarget model.
     *
     * Version Added:
     *     7.0
     */
    /**
     * A model for creating drag and drop targets.
     *
     * Registering a DnDDropTarget with the DnDUploader will create an
     * overlay on top of the target when files are dragged over the page. This
     * overlay will accept dropped files and run the dropAction for each file
     * dropped on it.
     */
    let DnDDropTarget = spina.spina(_class$a = class DnDDropTarget extends spina.BaseModel {
      static defaults() {
        return {
          $target: $(window),
          callback: _.noop,
          dropText: gettext("Drop to upload")
        };
      }
    }) || _class$a;
    /**
     * Displays an overlay over an element that accepts file drops.
     *
     * The overlay appears as semi-transparent black with the dropText message in
     * the center.
     *
     * If the user cancels the drop or moves the mouse out of the page, the
     * overlay will fade away.
     */
    let DnDDropOverlayView = spina.spina(_class2$2 = class DnDDropOverlayView extends spina.BaseView {
      static className = 'dnd-overlay';
      static events = {
        'dragenter': '_onDragEnter',
        'dragleave': '_onDragLeave',
        'dragover': '_onDragOver',
        'drop': '_onDrop'
      };

      /**
       * Render the view.
       */
      onInitialRender() {
        this.$el.text(this.model.get('dropText'));
      }

      /**
       * Show the overlay.
       *
       * Returns:
       *     DnDDropOverlayView:
       *     This object, for chaining.
       */
      show() {
        const $target = this.model.get('$target');
        $target.addClass('dnd-overlay-visible');

        /*
         * Adding the class to the target may change its visibility or size.
         * Let that clear before trying to position/size the overlay.
         */
        _.defer(() => {
          const offset = $target.offset();
          const width = $target.outerWidth() + 'px';
          const height = $target.outerHeight() + 'px';
          this.$el.css({
            'height': height,
            'left': offset.left + 'px',
            'line-height': height,
            'top': offset.top + 'px',
            'width': width
          }).show();
        });
        return this;
      }

      /**
       * Hide the overlay.
       *
       * Returns:
       *     DnDDropOverlayView:
       *     This object, for chaining.
       */
      hide() {
        this.model.get('$target').removeClass('dnd-overlay-visible');
        this.$el.hide();
        return this;
      }

      /**
       * Close the overlay.
       *
       * The overlay will fade out, and once it's gone, it will emit the "closed"
       * event and remove itself from the page.
       */
      close() {
        this.$el.fadeOut(() => {
          this.trigger('closed');
          this.remove();
        });
      }

      /**
       * Handle drop events on the overlay.
       *
       * This will call the appropriate callback for all dropped files.
       *
       * Args:
       *     e (DragEvent):
       *         The event that triggered the callback.
       */
      _onDrop(e) {
        e.stopPropagation();
        e.preventDefault();
        const dt = e.originalEvent.dataTransfer;
        const files = dt && dt.files;
        if (files) {
          const callback = this.model.get('callback');
          for (const file of Array.from(files)) {
            callback(file);
          }
        }
        this.trigger('closing');
      }

      /**
       * Handle dragenter events on the overlay.
       *
       * If there's files being dragged, the drop effect (usually represented
       * by a mouse cursor) will be set to indicate a copy of the files.
       *
       * Args:
       *     e (DragEvent):
       *         The event that triggered the callback.
       */
      _onDragEnter(e) {
        e.preventDefault();
        const dt = e.originalEvent.dataTransfer;
        if (dt) {
          dt.dropEffect = 'copy';
          this.$el.addClass('dnd-overlay-highlight');
        }
      }

      /**
       * Handle dragover events on the overlay.
       *
       * This merely prevents the default action, which indicates to the
       * underlying API that this element can be dropped on.
       *
       * Args:
       *     e (DragEvent):
       *         The event which triggered the callback.
       */
      _onDragOver(e) {
        e.preventDefault();
      }

      /**
       * Handle dragleave events on the overlay.
       *
       * If there were files previously being dragged over the overlay,
       * the drop effect will be reset.
       *
       * The overlay is always closed on a dragleave.
       *
       * Args:
       *     e (DragEvent):
       *         The event that triggered the callback.
       */
      _onDragLeave(e) {
        e.preventDefault();
        const dt = e.originalEvent.dataTransfer;
        if (dt) {
          dt.dropEffect = 'none';
          this.$el.removeClass('dnd-overlay-highlight');
        }
      }
    }) || _class2$2;
    /*
     * Handles drag-and-drop file uploads for a review request.
     *
     * This makes it possible to drag files from a file manager and drop them
     * into Review Board. This requires browser support for HTML 5 file
     * drag-and-drop, which is available in most modern browsers.
     *
     * The moment the DnDUploader is created, it will begin listening for
     * DnD-related events on the window.
     */
    let DnDUploader = (_dec$1 = spina.spina({
      prototypeAttrs: ['instance']
    }), _dec$1(_class3$2 = class DnDUploader extends spina.BaseView {
      static instance = null;

      /**
       * Create the DnDUploader instance.
       *
       * Returns:
       *     DnDUploader:
       *     The new instance.
       */
      static create() {
        console.assert(this.instance === null, 'DnDUploader.create may only be called once');
        this.instance = new this();
        return this.instance;
      }

      /**********************
       * Instance variables *
       **********************/

      /**
       * The set of drop targets for the page.
       */
      #dropTargets;

      /**
       * The overlay views.
       */
      #dropOverlays = [];

      /**
       * The timeout identifier for hiding the overlays.
       */
      #hideOverlayTimeout = null;

      /**
       * Whether the drop overlays are visible.
       */
      #overlaysVisible = false;

      /**
       * Whether the drop overlays are in the process of hiding.
       */
      #overlaysHiding = false;

      /**
       * Initialize the view.
       */
      initialize() {
        this.#dropTargets = new spina.Collection();
        _.bindAll(this, '_showOverlays', '_hideOverlays');
        $(window).on('dragstart dragenter dragover', this._showOverlays).on('dragend dragleave', this._hideOverlays);
      }

      /**
       * Register a new drop target.
       *
       * Args:
       *     $target (jQuery):
       *         The target element for drops.
       *
       *     dropText (string):
       *         The text to show on the overlay.
       *
       *     callback (function):
       *         The function to call when a file is dropped. This takes a single
       *         file argument, and will be called for each file that is dropped
       *         on the target.
       */
      registerDropTarget($target, dropText, callback) {
        if (this.#dropTargets.findWhere({
          $target
        }) === undefined) {
          const target = new DnDDropTarget({
            $target,
            callback,
            dropText
          });
          this.#dropTargets.add(target);
          const overlay = new DnDDropOverlayView({
            model: target
          });
          overlay.render().$el.hide().appendTo(document.body);
          this.listenTo(overlay, 'closing', this._hideOverlays);
          this.#dropOverlays.push(overlay);
        } else {
          console.error('Drop target was already registered!', $target);
        }
      }

      /**
       * Unregister an existing drop target.
       *
       * Args:
       *     $target (jQuery):
       *         The target element for drops.
       */
      unregisterDropTarget($target) {
        const target = this.#dropTargets.findWhere({
          $target: $target
        });
        const overlayIx = this.#dropOverlays.findIndex(overlay => overlay.model === target);
        if (overlayIx !== -1) {
          this.#dropOverlays[overlayIx].remove();
          this.#dropOverlays.splice(overlayIx, 1);
        }
        if (target !== undefined) {
          this.#dropTargets.remove(target);
        }
      }

      /**
       * Show the drop overlays.
       *
       * An overlay will be displayed over all the registered drop targets to
       * give the user a place to drop the files onto. The overlay will report
       * any files dropped.
       *
       * Args:
       *     e (DragEvent):
       *         The event that triggered the callback.
       */
      _showOverlays(e) {
        if (e.originalEvent.dataTransfer !== undefined && Array.from(e.originalEvent.dataTransfer.types).includes('Files')) {
          this.#overlaysHiding = false;
          if (!this.#overlaysVisible) {
            this.#overlaysVisible = true;
            this.#dropOverlays.forEach(overlay => overlay.show());
          }
        }
      }

      /**
       * Hide the drop overlays.
       */
      _hideOverlays() {
        /*
         * This will get called many times because the event bubbles up from
         * all the children of the document. We only want to hide the overlays
         * when the drag exits the window.
         *
         * In order to make this work reliably, we only hide the overlays after
         * a timeout (to make sure there's not a dragenter event coming
         * immediately after this).
         */
        if (this.#hideOverlayTimeout) {
          clearTimeout(this.#hideOverlayTimeout);
        }
        this.#overlaysHiding = true;
        this.#hideOverlayTimeout = setTimeout(() => {
          if (this.#overlaysHiding) {
            this.#overlaysVisible = false;
            this.#dropOverlays.forEach(overlay => overlay.hide());
          }
        }, 200);
      }
    }) || _class3$2);

    var _class$9, _class2$1, _class3$1, _class4$1;

    /*
     * Define a CodeMirror mode we can plug in as the default below.
     *
     * This mode won't have any special highlighting, but will avoid the Markdown
     * mode's default behavior of rendering "plain/text" code (the default) the
     * same way as literal code, which we really want to avoid.
     */
    CodeMirror.defineSimpleMode('rb-text-plain', {
      start: [{
        next: 'start',
        regex: /.*/,
        token: 'rb-cm-codeblock-plain'
      }]
    });
    CodeMirror.defineMIME('text/plain', 'rb-text-plain');

    /**
     * Options for the editor wrapper views.
     *
     * Version Added:
     *     6.0
     */
    /**
     * Wraps CodeMirror, providing a standard interface for TextEditorView's usage.
     */
    let CodeMirrorWrapper = spina.spina(_class$9 = class CodeMirrorWrapper extends spina.BaseView {
      static className = 'rb-c-text-editor__textarea -is-rich';

      /**********************
       * Instance variables *
       **********************/

      /**
       * Initialize CodeMirrorWrapper.
       *
       * This will set up CodeMirror based on the objects, add it to the parent,
       * and begin listening to events.
       *
       * Args:
       *     options (EditorWrapperOptions):
       *         Options for the wrapper.
       */
      initialize(options) {
        const codeMirrorOptions = {
          electricChars: false,
          extraKeys: {
            'End': 'goLineRight',
            'Enter': 'newlineAndIndentContinueMarkdownList',
            'Home': 'goLineLeft',
            'Shift-Tab': false,
            'Tab': false
          },
          lineWrapping: true,
          mode: {
            highlightFormatting: true,
            name: 'gfm',
            /*
             * The following token type overrides will be prefixed with
             * ``cm-`` when used as classes.
             */
            tokenTypeOverrides: {
              code: 'rb-markdown-code',
              list1: 'rb-markdown-list1',
              list2: 'rb-markdown-list2',
              list3: 'rb-markdown-list3'
            }
          },
          styleSelectedText: true,
          theme: 'rb default',
          viewportMargin: options.autoSize ? Infinity : 10
        };
        this._codeMirror = new CodeMirror(options.parentEl, codeMirrorOptions);
        const wrapperEl = this._codeMirror.getWrapperElement();
        wrapperEl.classList.add('rb-c-text-editor__textarea', '-is-rich');
        this.setElement(wrapperEl);
        if (options.minHeight !== undefined) {
          this.$el.css('min-height', options.minHeight);
        }
        this._codeMirror.on('viewportChange', () => this.$el.triggerHandler('resize'));
        this._codeMirror.on('change', () => this.trigger('change'));
      }

      /**
       * Return whether or not the editor's contents have changed.
       *
       * Args:
       *     initialValue (string):
       *         The initial value of the editor.
       *
       * Returns:
       *     boolean:
       *     Whether or not the editor is dirty.
       */
      isDirty(initialValue) {
        /*
         * We cannot trust codeMirror's isClean() method.
         *
         * It is also possible for initialValue to be undefined, so we use an
         * empty string in that case instead.
         */
        return (initialValue || '') !== this.getText();
      }

      /**
       * Set the cursor position within the editor.
       *
       * This uses client coordinates (which are relative to the viewport).
       *
       * Version Added:
       *     6.0
       *
       * Args:
       *     x (number):
       *         The client X coordinate to set.
       *
       *     y (number):
       *         The client Y coordinate to set.
       */
      setCursorPosition(x, y) {
        const codeMirror = this._codeMirror;
        codeMirror.setCursor(codeMirror.coordsChar({
          left: x,
          top: y
        }, 'window'));
      }

      /**
       * Set the text in the editor.
       *
       * Args:
       *     text (string):
       *         The new text for the editor.
       */
      setText(text) {
        this._codeMirror.setValue(text);
      }

      /**
       * Return the text in the editor.
       *
       * Returns:
       *     string:
       *     The current contents of the editor.
       */
      getText() {
        return this._codeMirror.getValue();
      }

      /**
       * Insert a new line of text into the editor.
       *
       * If the editor has focus, insert at the cursor position. Otherwise,
       * insert at the end.
       *
       * Args:
       *     text (string):
       *         The text to insert.
       */
      insertLine(text) {
        let position;
        if (this._codeMirror.hasFocus()) {
          const cursor = this._codeMirror.getCursor();
          const line = this._codeMirror.getLine(cursor.line);
          position = CodeMirror.Pos(cursor.line, line.length - 1);
          if (line.length !== 0) {
            /*
             * If the current line has some content, insert the new text on
             * the line after it.
             */
            text = '\n' + text;
          }
          if (!text.endsWith('\n')) {
            text += '\n';
          }
        } else {
          position = CodeMirror.Pos(this._codeMirror.lastLine());
          text = '\n' + text;
        }
        this._codeMirror.replaceRange(text, position);
      }

      /**
       * Return the full client height of the content.
       *
       * Returns:
       *     number:
       *     The client height of the editor.
       */
      getClientHeight() {
        return this._codeMirror.getScrollInfo().clientHeight;
      }

      /**
       * Set the size of the editor.
       *
       * Args:
       *     width (number):
       *         The new width of the editor.
       *
       *     height (number):
       *         The new height of the editor.
       */
      setSize(width, height) {
        this._codeMirror.setSize(width, height);
        this._codeMirror.refresh();
      }

      /**
       * Focus the editor.
       */
      focus() {
        this._codeMirror.focus();
      }
    }) || _class$9;
    /**
     * Wraps <textarea>, providing a standard interface for TextEditorView's usage.
     */
    let TextAreaWrapper = spina.spina(_class2$1 = class TextAreaWrapper extends spina.BaseView {
      static className = 'rb-c-text-editor__textarea -is-plain';
      static tagName = 'textarea';

      /**********************
       * Instance variables *
       **********************/

      /*
       * Initialize TextAreaWrapper.
       *
       * This will set up the element based on the provided options, begin
       * listening for events, and add the element to the parent.
       *
       * Args:
       *     options (EditorWrapperOptions):
       *         Options for the wrapper.
       */
      initialize(options) {
        this.options = options;
        if (options.autoSize) {
          this.$el.autoSizeTextArea();
        }
        this.$el.css('width', '100%').appendTo(options.parentEl).on('change keydown keyup keypress', () => this.trigger('change'));
        if (options.minHeight !== undefined) {
          if (options.autoSize) {
            this.$el.autoSizeTextArea('setMinHeight', options.minHeight);
          } else {
            this.$el.css('min-height', this.options.minHeight);
          }
        }
      }

      /**
       * Return whether or not the editor's contents have changed.
       *
       * Args:
       *     initialValue (string):
       *         The initial value of the editor.
       *
       * Returns:
       *     boolean:
       *     Whether or not the editor is dirty.
       */
      isDirty(initialValue) {
        const value = this.el.value || '';
        return value.length !== initialValue.length || value !== initialValue;
      }

      /**
       * Set the cursor position within the editor.
       *
       * This uses client coordinates (which are relative to the viewport).
       *
       * Setting the cursor position works in Firefox and WebKit/Blink-based
       * browsers. Not all browsers support the required APIs.
       *
       * Version Added:
       *     6.0
       *
       * Args:
       *     x (number):
       *         The client X coordinate to set.
       *
       *     y (number):
       *         The client Y coordinate to set.
       */
      setCursorPosition(x, y) {
        if (!document.caretPositionFromPoint && !document.caretRangeFromPoint) {
          /*
           * We don't have what need to reliably return a caret position for
           * the text.
           *
           * There are tricks we can try in order to attempt to compute the
           * right position, based on line heights and character sizes, but
           * it gets more difficult with wrapping.
           *
           * In reality, both of the above methods are widespread enough to
           * rely upon, and if they don't exist, we just won't set the
           * cursor position.
           */
          return;
        }
        const $el = this.$el;
        const el = this.el;

        /*
         * We need a proxy element for both the Firefox and WebKit/Blink
         * implementations, because neither version works quite right with
         * a <textarea>.
         *
         * On Firefox, Document.caretPositionFromPoint will generally work
         * with a <textarea>, so long as you're clicking within a line. If
         * you click past the end of a line, however, you get a caret position
         * at the end of the <textarea>. Not ideal. This behavior doesn't
         * manifest for standard DOM nodes, so we can use a proxy here.
         *
         * On WebKit/Blink, Document.caretRangeFromPoint doesn't even work
         * with a <textarea> at all, so we're forced to use a proxy element
         * (See https://bugs.webkit.org/show_bug.cgi?id=30604).
         *
         * A second caveat here is that, in either case, we can't get a
         * position for off-screen elements (apparently). So we have to overlay
         * this exactly. We carefully align it and then use an opacity of 0 to
         * hide it,
         */
        const offset = $el.offset();
        const bounds = el.getBoundingClientRect();
        const $proxy = $('<pre>').move(offset.left, offset.top, 'absolute').css({
          'border': 0,
          'font': $el.css('font'),
          'height': `${bounds.height}px`,
          'line-height': $el.css('line-height'),
          'margin': 0,
          'opacity': 0,
          'padding': $el.css('padding'),
          'white-space': 'pre-wrap',
          'width': `${bounds.width}px`,
          'word-wrap': 'break-word',
          'z-index': 10000
        }).text(this.el.value).appendTo(document.body);
        let pos = null;
        if (document.caretPositionFromPoint) {
          /* Firefox */
          const caret = document.caretPositionFromPoint(x, y);
          if (caret) {
            pos = caret.offset;
          }
        } else if (document.caretRangeFromPoint) {
          /* Webkit/Blink. */
          const caret = document.caretRangeFromPoint(x, y);
          if (caret) {
            pos = caret.startOffset;
          }
        }
        $proxy.remove();
        if (pos !== null) {
          el.setSelectionRange(pos, pos);
        }
      }

      /**
       * Set the text in the editor.
       *
       * Args:
       *     text (string):
       *         The new text for the editor.
       */
      setText(text) {
        this.el.value = text;
        if (this.options.autoSize) {
          this.$el.autoSizeTextArea('autoSize');
        }
      }

      /**
       * Return the text in the editor.
       *
       * Returns:
       *     string:
       *     The current contents of the editor.
       */
      getText() {
        return this.el.value;
      }

      /**
       * Insert a new line of text into the editor.
       *
       * Args:
       *     text (string):
       *         The text to insert.
       */
      insertLine(text) {
        if (this.$el.is(':focus')) {
          const value = this.el.value;
          const cursor = this.el.selectionEnd;
          const endOfLine = value.indexOf('\n', cursor);
          if (endOfLine === -1) {
            // The cursor is on the last line.
            this.el.value += '\n' + text;
          } else {
            // The cursor is in the middle of the text.
            this.el.value = value.slice(0, endOfLine + 1) + '\n' + text + '\n' + value.slice(endOfLine);
          }
        } else {
          this.el.value += '\n' + text;
        }
      }

      /**
       * Return the full client height of the content.
       *
       * Returns:
       *     number:
       *     The client height of the editor.
       */
      getClientHeight() {
        return this.el.clientHeight;
      }

      /**
       * Set the size of the editor.
       *
       * Args:
       *     width (number):
       *         The new width of the editor.
       *
       *     height (number):
       *         The new height of the editor.
       */
      setSize(width, height) {
        if (width !== null) {
          this.$el.innerWidth(width);
        }
        if (height !== null) {
          if (height === 'auto' && this.options.autoSize) {
            this.$el.autoSizeTextArea('autoSize', true);
          } else {
            this.$el.innerHeight(height);
          }
        }
      }

      /**
       * Focus the editor.
       */
      focus() {
        this.el.focus();
      }
    }) || _class2$1;
    /**
     * Options for the FormattingToolbarView.
     *
     * Version Added:
     *     6.0
     */
    /**
     * Options for a group on the formatting toolbar.
     *
     * Version Added:
     *     6.0
     */
    /**
     * Options for an item on the formatting toolbar.
     *
     * Version Added:
     *     6.0
     */
    /**
     * Information on an item group in the formatting toolbar.
     *
     * Version Added:
     *     6.0
     */
    /**
     * Information on an item in the formatting toolbar.
     *
     * Version Added:
     *     6.0
     */
    /**
     * The formatting toolbar for rich text fields.
     *
     * Version Added:
     *     6.0
     */
    let FormattingToolbarView = spina.spina(_class3$1 = class FormattingToolbarView extends spina.BaseView {
      static className = 'rb-c-formatting-toolbar';

      /**********************
       * Instance variables *
       **********************/

      /**
       * A mapping of button group IDs to information.
       */
      buttonGroups = {};

      /**
       * The CodeMirror instance.
       */
      #codeMirror;

      /**
       * The ID of the editor being managed.
       */
      #editorID;

      /**
       * Initialize the view.
       *
       * Args:
       *     options (FormattingToolbarViewOptions):
       *         Options for the view.
       */
      initialize(options) {
        const editor = options.editor;
        const editorID = editor.el.id;
        console.assert(!!editorID);
        this.#codeMirror = editor._codeMirror;
        this.#editorID = editorID;
        this.addGroup({
          ariaLabel: gettext("Text formatting"),
          id: 'text',
          items: [{
            ariaLabel: gettext("Bold"),
            className: 'rb-c-formatting-toolbar__btn-bold',
            id: 'bold',
            onClick: this.#onBoldBtnClick.bind(this)
          }, {
            ariaLabel: gettext("Italic"),
            className: 'rb-c-formatting-toolbar__btn-italic',
            id: 'italic',
            onClick: this.#onItalicBtnClick.bind(this)
          }, {
            ariaLabel: gettext("Strikethrough"),
            className: 'rb-c-formatting-toolbar__btn-strikethrough',
            id: 'strikethrough',
            onClick: this.#onStrikethroughBtnClick.bind(this)
          }, {
            ariaLabel: gettext("Code literal"),
            className: 'rb-c-formatting-toolbar__btn-code',
            id: 'code',
            onClick: this.#onCodeBtnClick.bind(this)
          }]
        });
        this.addGroup({
          ariaLabel: gettext("Special formatting and media"),
          id: 'media',
          items: [{
            ariaLabel: gettext("Insert link"),
            className: 'rb-c-formatting-toolbar__btn-link',
            id: 'link',
            onClick: this.#onLinkBtnClick.bind(this)
          }, {
            $el: $(`<label class="rb-c-formatting-toolbar__btn"
       role="button" tabindex="0">`).append($('<input type="file" style="display: none;">').on('change', this.#onImageUpload.bind(this))),
            ariaLabel: gettext("Upload image"),
            className: 'rb-c-formatting-toolbar__btn-image',
            id: 'upload-image'
          }]
        });
        this.addGroup({
          ariaLabel: gettext("Lists"),
          id: 'lists',
          items: [{
            ariaLabel: gettext("Insert unordered list"),
            className: 'rb-c-formatting-toolbar__btn-list-ul',
            id: 'list-ul',
            onClick: this.#onUListBtnClick.bind(this)
          }, {
            ariaLabel: gettext("Insert ordered list"),
            className: 'rb-c-formatting-toolbar__btn-list-ol',
            id: 'list-ol',
            onClick: this.#onOListBtnClick.bind(this)
          }]
        });
      }

      /**
       * Render the view.
       */
      onInitialRender() {
        this.$el.attr({
          'aria-controls': this.#editorID,
          'aria-label': gettext("Text formatting toolbar"),
          'role': 'toolbar'
        });
      }

      /**
       * Add a group on the toolbar for placing items.
       *
       * This may optionally take items to add to the group.
       *
       * Args:
       *     options (FormattingToolbarGroupOptions):
       *         Options for the group.
       */
      addGroup(options) {
        const id = options.id;
        console.assert(!this.buttonGroups.hasOwnProperty(id), `Toolbar group "${id}" was already registered.`);
        const $buttonGroup = $('<div>').addClass('rb-c-formatting-toolbar__btn-group').attr('aria-label', options.ariaLabel);
        const group = {
          $el: $buttonGroup,
          id: id,
          items: {}
        };
        this.buttonGroups[id] = group;
        if (options.items) {
          for (const item of options.items) {
            this.addItem(id, item);
          }
        }
        $buttonGroup.appendTo(this.$el);
      }

      /**
       * Add an item to a group.
       *
       * Args:
       *     groupID (string):
       *         The ID of the group to add to.
       *
       *     options (FormattingToolbarItemOptions):
       *         Options for the item to add.
       */
      addItem(groupID, options) {
        const group = this.buttonGroups[groupID];
        console.assert(!!group, `Toolbar group "${groupID}" does not exist.`);
        let $el = options.$el;
        if ($el === undefined) {
          $el = $(ink.paintComponent("Ink.Button", {
            "class": "rb-c-formatting-toolbar__btn",
            "aria-pressed": "false",
            tabindex: "0"
          }));
        }
        if (options.ariaLabel) {
          $el.attr({
            'aria-label': options.ariaLabel,
            'title': options.ariaLabel
          });
        }
        if (options.className) {
          $el.addClass(options.className);
        }
        if (options.onClick) {
          $el.on('click', options.onClick);
        }
        $el.appendTo(group.$el);
      }

      /**
       * Handle a click on the "bold" button.
       *
       * Args:
       *     e (JQuery.ClickEvent):
       *         The event object.
       */
      #onBoldBtnClick(e) {
        e.stopPropagation();
        e.preventDefault();
        this.#toggleInlineTextFormat(['**']);
      }

      /**
       * Handle a click on the "code" button.
       *
       * Args:
       *     e (JQuery.ClickEvent):
       *         The event object.
       */
      #onCodeBtnClick(e) {
        e.stopPropagation();
        e.preventDefault();
        this.#toggleInlineTextFormat(['`']);
      }

      /**
       * Handle a click on the "italic" button.
       *
       * Args:
       *     e (JQuery.ClickEvent):
       *         The event object.
       */
      #onItalicBtnClick(e) {
        e.stopPropagation();
        e.preventDefault();
        this.#toggleInlineTextFormat(['_', '*']);
      }

      /**
       * Handle a click on the "link" button.
       *
       * Args:
       *     e (JQuery.ClickEvent):
       *         The event object.
       */
      #onLinkBtnClick(e) {
        e.stopPropagation();
        e.preventDefault();
        this.#toggleLinkSyntax();
      }

      /**
       * Handle an image upload from clicking the "image" button.
       *
       * Args:
       *     e (JQuery.ClickEvent):
       *         The event object.
       */
      #onImageUpload(e) {
        const files = e.target.files;
        const token = this.#getCurrentTokenGroup()[0];
        this.#codeMirror.focus();
        this.#codeMirror.setCursor(token);
        if (files) {
          this.trigger('uploadImage', files[0]);
        }
        e.stopPropagation();
        e.preventDefault();
      }

      /**
       * Handle a click on the "ordered list" button.
       *
       * Args:
       *     e (JQuery.ClickEvent):
       *         The event object.
       */
      #onOListBtnClick(e) {
        e.stopPropagation();
        e.preventDefault();
        this.#toggleListSyntax(true);
      }

      /**
       * Handle a click on the "strikethrough" button.
       *
       * Args:
       *     e (JQuery.ClickEvent):
       *         The event object.
       */
      #onStrikethroughBtnClick(e) {
        e.stopPropagation();
        e.preventDefault();
        this.#toggleInlineTextFormat(['~~']);
      }

      /**
       * Handle a click on the "unordered list" button.
       *
       * Args:
       *     e (JQuery.ClickEvent):
       *         The event object.
       */
      #onUListBtnClick(e) {
        e.stopPropagation();
        e.preventDefault();
        this.#toggleListSyntax(false);
      }

      /**
       * Toggle the state of the given inline text format.
       *
       * This toggles the syntax for inline markup such as bold, italic,
       * strikethrough, or code.
       *
       * Args:
       *     symbols (Array of string):
       *         The surrounding markup to add or remove.
       */
      #toggleInlineTextFormat(symbols) {
        const codeMirror = this.#codeMirror;
        const selection = codeMirror.getSelection();
        if (selection === '') {
          /*
           * If the syntax being toggled does not exist in the group where
           * the cursor is positioned, insert the syntax and position the
           * cursor between the inserted symbols. Otherwise, remove the
           * syntax.
           */
          const [groupStart, groupEnd] = this.#getCurrentTokenGroup();
          const range = codeMirror.getRange(groupStart, groupEnd);
          let wasReplaced = false;
          for (const sym of symbols) {
            if (range.startsWith(sym) && range.endsWith(sym)) {
              const trimmedRange = this.#removeSyntax(range, sym);
              codeMirror.replaceRange(trimmedRange, groupStart, groupEnd);
              wasReplaced = true;
              break;
            }
          }
          if (!wasReplaced) {
            const sym = symbols[0];
            codeMirror.replaceRange(`${sym}${range}${sym}`, groupStart, groupEnd);
            const cursor = codeMirror.getCursor();
            cursor.ch -= sym.length;
            codeMirror.setCursor(cursor);
          }
        } else {
          let wasReplaced = false;
          for (const sym of symbols) {
            if (selection.startsWith(sym) && selection.endsWith(sym)) {
              /*
               * The selection starts and ends with syntax matching the
               * provided symbol, so remove them.
               *
               * For example: |**bold text**|
               */
              const newSelection = this.#removeSyntax(selection, sym);
              codeMirror.replaceSelection(newSelection, 'around');
              wasReplaced = true;
              break;
            }
          }
          if (!wasReplaced) {
            /*
             * There is an existing selection that may have syntax outside
             * of it, so find the beginning and end of the entire token
             * group, including both word and punctuation characters.
             *
             * For example: **|bold text|**
             */
            const [groupStart, groupEnd] = this.#getCurrentTokenGroup();

            /* Update the selection for replacement. */
            codeMirror.setSelection(groupStart, groupEnd);
            const group = codeMirror.getSelection();
            for (const sym of symbols) {
              if (group.startsWith(sym) && group.endsWith(sym)) {
                const newGroup = this.#removeSyntax(group, sym);
                codeMirror.replaceSelection(newGroup, 'around');
                wasReplaced = true;
                break;
              }
            }
            if (!wasReplaced) {
              /* The selection is not formatted, so add syntax. */
              const sym = symbols[0];

              /* Format each line of the selection. */
              const lines = group.split('\n').map(line => {
                if (line === '') {
                  return line;
                } else if (line.startsWith(sym) && line.endsWith(sym)) {
                  /* Remove the formatting. */
                  return this.#removeSyntax(line, sym);
                } else {
                  return `${sym}${line}${sym}`;
                }
              });
              codeMirror.replaceSelection(lines.join('\n'), 'around');
            }
          }
        }
        codeMirror.focus();
      }

      /**
       * Return the current token group for the cursor/selection.
       *
       * This will find the surrounding text given the current user's cursor
       * position or selection.
       *
       * Returns:
       *     Array of number:
       *     A 2-element array containing the start and end position of the
       *     current token group.
       */
      #getCurrentTokenGroup() {
        const codeMirror = this.#codeMirror;
        const cursorStart = codeMirror.getCursor(true);
        const cursorEnd = codeMirror.getCursor(false);
        const groupStart = Object.assign({}, cursorStart);
        for (let curToken = codeMirror.getTokenAt(cursorStart, true); curToken.string !== ' ' && groupStart.ch !== 0; curToken = codeMirror.getTokenAt(groupStart, true)) {
          groupStart.ch -= 1;
        }
        const line = codeMirror.getLine(cursorStart.line);
        const lineLength = line.length;
        const groupEnd = Object.assign({}, cursorEnd);
        for (let curToken = codeMirror.getTokenAt(cursorEnd, true); curToken.string !== ' ' && groupEnd.ch < lineLength; curToken = codeMirror.getTokenAt(groupEnd, true)) {
          groupEnd.ch += 1;
        }
        if (groupEnd.ch !== lineLength && groupStart.line === groupEnd.line) {
          groupEnd.ch -= 1;
        }
        return [groupStart, groupEnd];
      }

      /**
       * Remove the given syntax from the provided text.
       *
       * Args:
       *     text (string):
       *         The text to edit.
       *
       *     sym (string):
       *         The markup to remove from the text.
       *
       * Returns:
       *     string:
       *     The text with the surrounding markup removed.
       */
      #removeSyntax(text, sym) {
        let escapedSymbol;
        if (sym === '*') {
          escapedSymbol = '\\*';
        } else if (sym === '**') {
          escapedSymbol = '\\*\\*';
        } else {
          escapedSymbol = sym;
        }
        const regex = new RegExp(`^(${escapedSymbol})(.*)\\1$`, 'gm');
        return text.replace(regex, '$2');
      }

      /**
       * Toggle markdown list syntax for the current cursor position.
       *
       * Args:
       *     isOrderedList (boolean):
       *         ``true`` if toggling syntax for an ordered list, ``false`` for
       *         an unordered list.
       */
      #toggleListSyntax(isOrderedList) {
        const regex = isOrderedList ? /^[0-9]+\.\s/ : /^[\*|\+|-]\s/;
        const listSymbol = isOrderedList ? '1.' : '-';
        const codeMirror = this.#codeMirror;
        const cursor = codeMirror.getCursor();
        const line = codeMirror.getLine(cursor.line);
        const selection = codeMirror.getSelection();
        if (selection === '') {
          /*
           * If the list syntax being toggled exists on the current line,
           * remove it. Otherwise, add the syntax to the current line. In
           * both cases, preserve the relative cursor position if the line is
           * not empty.
           */
          if (regex.test(line)) {
            const newText = line.replace(regex, '');
            codeMirror.replaceRange(newText, {
              ch: 0,
              line: cursor.line
            }, {
              line: cursor.line
            });
            if (line) {
              cursor.ch -= listSymbol.length + 1;
              codeMirror.setCursor(cursor);
            }
          } else {
            codeMirror.replaceRange(`${listSymbol} ${line}`, {
              ch: 0,
              line: cursor.line
            }, {
              line: cursor.line
            });
            if (line) {
              cursor.ch += listSymbol.length + 1;
              codeMirror.setCursor(cursor);
            }
          }
        } else {
          if (regex.test(selection)) {
            const newText = selection.replace(regex, '');
            codeMirror.replaceSelection(newText, 'around');
          } else {
            const cursorStart = codeMirror.getCursor(true);
            const cursorEnd = codeMirror.getCursor(false);
            const precedingText = codeMirror.getLineTokens(cursor.line).filter(t => t.start < cursorStart.ch).reduce((acc, token) => acc + token.string, '');
            if (regex.test(precedingText)) {
              /*
               * There may be markup before theselection that needs to be
               * removed, so extend the selection to be replaced if
               * necessary.
               */
              const newText = selection.replace(regex, '');
              codeMirror.setSelection({
                ch: 0,
                line: cursor.line
              }, cursorEnd);
              codeMirror.replaceSelection(newText, 'around');
            } else {
              /* The selection is not already formatted. Add syntax. */
              codeMirror.replaceSelection(`${listSymbol} ${selection}`, 'around');
            }
          }
        }
        codeMirror.focus();
      }

      /**
       * Toggle link syntax for the current cursor/selection.
       */
      #toggleLinkSyntax() {
        const regex = /\[(?<text>.*)\]\(.*\)/;
        const codeMirror = this.#codeMirror;
        const selection = codeMirror.getSelection();
        let cursor = codeMirror.getCursor();
        if (selection === '') {
          /*
           * If the group where the cursor is positioned is already a link,
           * remove the syntax. Otherwise, insert the syntax and position the
           * cursor where the text to be displayed will go.
           */
          const [groupStart, groupEnd] = this.#getCurrentTokenGroup();
          const range = codeMirror.getRange(groupStart, groupEnd);
          if (range === '') {
            /*
             * If the group where the cursor is positioned is empty, insert
             * the syntax and position the cursor where the text to display
             * should go.
             */
            codeMirror.replaceSelection(`[](url)`);
            codeMirror.setCursor(CodeMirror.Pos(cursor.line, cursor.ch + 1));
          } else {
            const match = range.match(regex);
            if (match && match.groups) {
              /*
               * If there is a non-empty token group that is a formatted
               * link, replace the syntax with the text.
               */
              const text = match.groups.text;
              codeMirror.replaceRange(text, groupStart, groupEnd);
            } else {
              /*
               * Otherwise, insert the syntax using the token group as
               * the text to display and position the selection where the
               * URL will go.
               */
              codeMirror.replaceRange(`[${range}](url)`, groupStart, groupEnd);
              cursor = codeMirror.getCursor();
              codeMirror.setSelection(CodeMirror.Pos(cursor.line, cursor.ch - 4), CodeMirror.Pos(cursor.line, cursor.ch - 1));
            }
          }
        } else {
          let match = selection.match(regex);
          if (match && match.groups) {
            /*
             * If the entire selection matches a formatted link, replace
             * the selection with the text.
             */
            codeMirror.replaceSelection(match.groups.text);
          } else {
            /*
             * The selection may be part of a formatted link, so get the
             * current token group to test against the regex and remove the
             * syntax if it matches.
             */
            const [groupStart, groupEnd] = this.#getCurrentTokenGroup();
            const range = codeMirror.getRange(groupStart, groupEnd);
            match = range.match(regex);
            if (match && match.groups) {
              codeMirror.replaceRange(match.groups.text, groupStart, groupEnd);
            } else {
              /*
               * The selection is not already formatted, so insert the
               * syntax using the current selection as the text to
               * display, and position the selection where the URL will
               * go.
               */
              codeMirror.replaceSelection(`[${selection}](url)`);
              cursor = codeMirror.getCursor();
              codeMirror.setSelection(CodeMirror.Pos(cursor.line, cursor.ch - 4), CodeMirror.Pos(cursor.line, cursor.ch - 1));
            }
          }
        }
      }
    }) || _class3$1;
    /**
     * Options for the TextEditorView.
     *
     * Version Added:
     *     6.0
     */
    /**
     * Provides an editor for editing plain or Markdown text.
     *
     * The editor allows for switching between plain or Markdown text on-the-fly.
     *
     * When editing plain text, this uses a standard textarea widget.
     *
     * When editing Markdown, this makes use of CodeMirror. All Markdown content
     * will be formatted as the user types, making it easier to notice when a
     * stray _ or ` will cause Markdown-specific behavior.
     */
    let TextEditorView = spina.spina(_class4$1 = class TextEditorView extends spina.BaseView {
      static className = 'rb-c-text-editor';
      static defaultOptions = {
        autoSize: true,
        minHeight: 70
      };
      static events = {
        'focus': 'focus',
        'remove': '_onRemove'
      };

      /**********************
       * Instance variables *
       **********************/

      /** The view options. */

      /** Whether the editor is using rich text. */

      /**
       * The markdown formatting toolbar view.
       *
       * Version Added:
       *     6.0
       */
      #formattingToolbar = null;

      /** The saved previous height, used to trigger the resize event . */
      #prevClientHeight = null;

      /** Whether the rich text state is unsaved. */
      #richTextDirty = false;

      /**
       * The cursor position to set when starting edit mode.
       *
       * Version Added:
       *     6.0
       */
      #startCursorPos = null;

      /** The current value of the editor. */
      #value;

      /** The editor wrapper. */

      /**
       * Initialize the view with any provided options.
       *
       * Args:
       *     options (TextEditorViewOptions, optional):
       *         Options for view construction.
       */
      initialize(options = {}) {
        this._editor = null;
        this.#prevClientHeight = null;
        this.options = _.defaults(options, TextEditorView.defaultOptions);
        this.richText = !!this.options.richText;
        this.#value = this.options.text || '';
        this.#richTextDirty = false;
        if (this.options.bindRichText) {
          this.bindRichTextAttr(this.options.bindRichText.model, this.options.bindRichText.attrName);
        }

        /*
         * If the user is defaulting to rich text, we're going to want to
         * show the rich text UI by default, even if any bound rich text
         * flag is set to False.
         *
         * This requires cooperation with the template or API results
         * that end up backing this TextEditor. The expectation is that
         * those will be providing escaped data for any plain text, if
         * the user's set to use rich text by default. If this expectation
         * holds, the user will have a consistent experience for any new
         * text fields.
         */
        if (RB.UserSession.instance.get('defaultUseRichText')) {
          this.setRichText(true);
        }
      }

      /**
       * Render the text editor.
       *
       * This will set the class name on the element, ensuring we have a
       * standard set of styles, even if this editor is bound to an existing
       * element.
       */
      onInitialRender() {
        this.$el.addClass(this.className);
      }

      /**
       * Set whether or not rich text (Markdown) is to be used.
       *
       * This can dynamically change the text editor to work in plain text
       * or Markdown.
       *
       * Args:
       *     richText (boolean):
       *         Whether the editor should use rich text.
       */
      setRichText(richText) {
        if (richText === this.richText) {
          return;
        }
        if (this._editor) {
          this.hideEditor();
          this.richText = richText;
          this.showEditor();
          this.#richTextDirty = true;
          this.$el.triggerHandler('resize');
        } else {
          this.richText = richText;
        }
        this.trigger('change:richText', richText);
        this.trigger('change');
      }

      /**
       * Bind a richText attribute on a model to the mode on this editor.
       *
       * This editor's richText setting will stay in sync with the attribute
       * on the given mode.
       *
       * Args:
       *     model (Backbone.Model):
       *         A model to bind to.
       *
       *     attrName (string):
       *         The name of the attribute to bind.
       */
      bindRichTextAttr(model, attrName) {
        this.setRichText(model.get(attrName));
        this.listenTo(model, `change:${attrName}`, (model, value) => this.setRichText(value));
      }

      /**
       * Bind an Enable Markdown checkbox to this text editor.
       *
       * The checkbox will initially be set to the value of the editor's
       * richText property. Toggling the checkbox will then manipulate that
       * property.
       *
       * Args:
       *     $checkbox (jQuery):
       *         The checkbox to bind.
       */
      bindRichTextCheckbox($checkbox) {
        $checkbox.prop('checked', this.richText).on('change', () => this.setRichText($checkbox.prop('checked')));
        this.on('change:richText', () => $checkbox.prop('checked', this.richText));
      }

      /**
       * Bind the visibility of an element to the richText property.
       *
       * If richText is true, the element will be shown. Otherwise, it
       * will be hidden.
       *
       * Args:
       *     $el (jQuery):
       *         The element to show when richText is true.
       */
      bindRichTextVisibility($el) {
        $el.toggle(this.richText);
        this.on('change:richText', () => $el.toggle(this.richText));
      }

      /**
       * Return whether or not the editor's contents have changed.
       *
       * Args:
       *     initialValue (string):
       *         The initial value of the editor.
       *
       * Returns:
       *     boolean:
       *     Whether or not the editor is dirty.
       */
      isDirty(initialValue) {
        return this._editor !== null && (this.#richTextDirty || this._editor.isDirty(initialValue || ''));
      }

      /**
       * Set the cursor position within the editor.
       *
       * This uses client coordinates (which are relative to the viewport).
       *
       * Version Added:
       *     6.0
       *
       * Args:
       *     x (number):
       *         The client X coordinate to set.
       *
       *     y (number):
       *         The client Y coordinate to set.
       */
      setCursorPosition(x, y) {
        if (this._editor) {
          this._editor.setCursorPosition(x, y);
        } else {
          this.#startCursorPos = [x, y];
        }
      }

      /**
       * Set the text in the editor.
       *
       * Args:
       *     text (string):
       *         The new text for the editor.
       */
      setText(text) {
        if (text !== this.getText()) {
          if (this._editor) {
            this._editor.setText(text);
          } else {
            this.#value = text;
          }
        }
        this.trigger('change');
      }

      /**
       * Return the text in the editor.
       *
       * Returns:
       *     string:
       *     The current contents of the editor.
       */
      getText() {
        return this._editor ? this._editor.getText() : this.#value;
      }

      /**
       * Insert a new line of text into the editor.
       *
       * Args:
       *     text (string):
       *         The text to insert.
       */
      insertLine(text) {
        if (this._editor) {
          this._editor.insertLine(text);
        } else {
          if (this.#value.endsWith('\n')) {
            this.#value += text + '\n';
          } else {
            this.#value += '\n' + text;
          }
        }
        this.trigger('change');
      }

      /**
       * Set the size of the editor.
       *
       * Args:
       *     width (number):
       *         The new width of the editor.
       *
       *     height (number):
       *         The new height of the editor.
       */
      setSize(width, height) {
        if (this._editor) {
          if (this.#formattingToolbar !== null) {
            height -= this.#formattingToolbar.$el.outerHeight(true);
          }
          this._editor.setSize(width, height);
        }
      }

      /**
       * Show the editor.
       *
       * Returns:
       *     TextEditorView:
       *     This object, for chaining.
       */
      show() {
        this.$el.show();
        this.showEditor();
        return this;
      }

      /**
       * Hide the editor.
       *
       * Returns:
       *     TextEditorView:
       *     This object, for chaining.
       */
      hide() {
        this.hideEditor();
        this.$el.hide();
        return this;
      }

      /**
       * Focus the editor.
       */
      focus() {
        if (this._editor) {
          this._editor.focus();
        }
      }

      /**
       * Handler for the remove event.
       *
       * Disables the drag-and-drop overlay.
       */
      _onRemove() {
        if (DnDUploader.instance !== null) {
          DnDUploader.instance.unregisterDropTarget(this.$el);
        }
      }

      /**
       * Show the actual editor wrapper.
       *
       * Any stored text will be transferred to the editor, and the editor
       * will take control over all operations.
       */
      showEditor() {
        if (this.richText) {
          DnDUploader.instance.registerDropTarget(this.$el, gettext("Drop to add an image"), this._uploadImage.bind(this));
          this._editor = new CodeMirrorWrapper({
            autoSize: this.options.autoSize,
            minHeight: this.options.minHeight,
            parentEl: this.el
          });
          this._editor.el.id = _.uniqueId('rb-c-text-editor_');
          this.#formattingToolbar = new FormattingToolbarView({
            _uploadImage: this._uploadImage.bind(this),
            editor: this._editor
          });
          this.#formattingToolbar.renderInto(this.$el);
          this.listenTo(this.#formattingToolbar, 'uploadImage', this._uploadImage);
        } else {
          this._editor = new TextAreaWrapper({
            autoSize: this.options.autoSize,
            minHeight: this.options.minHeight,
            parentEl: this.el
          });
        }
        this._editor.setText(this.#value);
        const startCursorPos = this.#startCursorPos;
        if (startCursorPos !== null) {
          this._editor.setCursorPosition(startCursorPos[0], startCursorPos[1]);
        }
        this.#value = '';
        this.#richTextDirty = false;
        this.#prevClientHeight = null;
        this._editor.$el.on('resize', _.throttle(() => this.$el.triggerHandler('resize'), 250));
        this.listenTo(this._editor, 'change', _.throttle(() => {
          /*
           * Make sure that the editor wasn't closed before the throttled
           * handler was reached.
           */
          if (this._editor === null) {
            return;
          }
          const clientHeight = this._editor.getClientHeight();
          if (clientHeight !== this.#prevClientHeight) {
            this.#prevClientHeight = clientHeight;
            this.$el.triggerHandler('resize');
          }
          this.trigger('change');
        }, 500));
        this.focus();
      }

      /**
       * Hide the actual editor wrapper.
       *
       * The last value from the editor will be stored for later retrieval.
       */
      hideEditor() {
        DnDUploader.instance.unregisterDropTarget(this.$el);
        if (this._editor) {
          this.#value = this._editor.getText();
          this.#richTextDirty = false;
          this._editor.remove();
          this._editor = null;
          this.$el.empty();
        }
        if (this.#formattingToolbar) {
          this.#formattingToolbar.remove();
          this.#formattingToolbar = null;
        }
      }

      /**
       * Return whether or not a given file is an image.
       *
       * Args:
       *     file (File):
       *         The file to check.
       *
       * Returns:
       *     boolean:
       *     True if the given file appears to be an image.
       */
      _isImage(file) {
        if (file.type) {
          return file.type.split('/')[0] === 'image';
        }
        const filename = file.name.toLowerCase();
        return ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.tiff', '.svg'].some(extension => filename.endsWith(extension));
      }

      /**
       * Upload the image and append an image link to the editor's contents.
       *
       * Creates an instance of UserFileAttachment and saves it without the file,
       * then updates the model with the file. This allows the file to be
       * uploaded asynchronously after we get the link that is generated when the
       * UserFileAttachment is created.
       *
       * Args:
       *     file (File):
       *         The image file to upload.
       */
      _uploadImage(file) {
        if (!this._isImage(file)) {
          return;
        }
        const userFileAttachment = new RB.UserFileAttachment({
          caption: file.name
        });
        userFileAttachment.save().then(() => {
          this.insertLine(`![Image](${userFileAttachment.get('downloadURL')})`);
          userFileAttachment.set('file', file);
          userFileAttachment.save().catch(err => alert(err.message));
        }).catch(err => alert(err.message));
      }
    }) || _class4$1;

    var _dec, _class$8, _class2, _class3, _class4;
    /**
     * A view for inline editors.
     *
     * This provides the framework for items which are "editable". These provide a
     * way to switch between a normal view and an edit view, which is usually a
     * text box (either single- or multiple-line).
     */
    let InlineEditorView = (_dec = spina.spina({
      prototypeAttrs: ['defaultOptions']
    }), _dec(_class$8 = class InlineEditorView extends spina.BaseView {
      /**
       * Defaults for the view options.
       */
      static defaultOptions = {
        animationSpeedMS: 200,
        deferEventSetup: false,
        editDragThreshold: 3,
        editIconClass: null,
        editIconPath: null,
        enabled: true,
        extraHeight: 100,
        fieldLabel: null,
        focusOnOpen: true,
        formClass: '',
        formatResult: value => _.escape(value),
        getFieldValue: editor => editor.$field.val(),
        hasRawValue: false,
        isFieldDirty: (editor, initialValue) => {
          const value = editor.getValue() || '';
          const normValue = (editor.options.hasRawValue ? value : _.escape(value)) || '';
          initialValue = editor.normalizeText(initialValue);
          return normValue.length !== initialValue.length || normValue !== initialValue;
        },
        matchHeight: true,
        multiline: false,
        notifyUnchangedCompletion: false,
        promptOnCancel: true,
        rawValue: null,
        setFieldValue: (editor, value) => editor.$field.val(value),
        showButtons: true,
        showEditIcon: true,
        showRequiredFlag: false,
        startOpen: false
      };

      /**********************
       * Instance variables *
       **********************/

      /** The save/cancel buttons. */

      /** The field used to edit the value. */

      /** The saved options for the editor. */

      /** The edit icon. */

      /**
       * The wrapper for the edit field.
       *
       * Version Added:
       *     6.0
       */

      /** The form element */

      /** Whether the editor is dirty */
      _dirty = false;

      /** The dirty calculation timeout ID. */
      _dirtyCalcTimeout = null;

      /** Whether the editor is currently open. */
      _editing = false;

      /** The initial value of the editor. */
      _initialValue = null;

      /** Whether the editor uses a textarea. */

      /**
       * Initialize the view.
       *
       * Args:
       *     options (InlineEditorViewOptions):
       *         Options for the view.
       */
      initialize(options) {
        this.options = _.defaults(options, this.defaultOptions);
      }

      /**
       * Render the view.
       */
      onInitialRender() {
        const options = this.options;
        const multiline = options.multiline;
        const fieldLabel = options.fieldLabel;
        const hasShortButtons = options.hasShortButtons;
        const editorID = _.uniqueId('rb-c-inline-editor');
        this.$el.data('inline-editor', this);
        const $form = $('<form>').addClass('rb-c-inline-editor').addClass(multiline ? '-is-multi-line' : '-is-single-line').attr({
          'aria-label': fieldLabel ? interpolate(gettext("Edit the %(fieldLabel)s field"), {
            "fieldLabel": fieldLabel
          }, true) : gettext("Edit the field"),
          'id': editorID
        });
        if (options.formClass) {
          $form.addClass(options.formClass);
        }
        if (hasShortButtons) {
          $form.addClass('-has-short-buttons');
        }
        this._$form = $form;
        const $fieldWrapper = $('<div class="rb-c-inline-editor__field">').appendTo($form);
        this._$fieldWrapper = $fieldWrapper;
        this.$field = this.createField().appendTo($fieldWrapper);
        this._isTextArea = this.$field[0].tagName === 'TEXTAREA';
        this.$buttons = $();
        if (options.showButtons) {
          this.$buttons = $(ink.paintComponent("div", {
            "class": "rb-c-inline-editor__actions"
          }, ink.paintComponent("Ink.Button", {
            "aria-label": fieldLabel ? interpolate(gettext("Save %(fieldLabel)s"), {
              "fieldLabel": fieldLabel
            }, true) : gettext("Save the field"),
            "data-action": "save",
            iconName: "ink-i-check",
            onClick: () => this.submit()
          }, !hasShortButtons && gettext("Save")), ink.paintComponent("Ink.Button", {
            "aria-label": fieldLabel ? interpolate(gettext("Cancel editing %(fieldLabel)s and discard changes"), {
              "fieldLabel": fieldLabel
            }, true) : gettext("Cancel editing and discard changes"),
            "data-action": "cancel",
            iconName: "ink-i-close",
            onClick: () => this.cancel()
          }, !hasShortButtons && gettext("Cancel")))).hide().appendTo($form);
        }
        this._$editIcon = $();
        if (options.showEditIcon) {
          const editText = fieldLabel ? interpolate(gettext("Edit the %(fieldLabel)s field"), {
            "fieldLabel": fieldLabel
          }, true) : gettext("Edit this field");
          this._$editIcon = $('<a href="#" role="button">').addClass('rb-c-inline-editor-edit-icon').attr({
            'aria-controls': editorID,
            'aria-label': editText,
            'tabindex': 0,
            'title': editText
          }).on('click', e => {
            e.preventDefault();
            e.stopPropagation();
            this.startEdit();
          });
          if (options.editIconPath) {
            this._$editIcon.append(`<img src="${options.editIconPath}">`);
          } else if (options.editIconClass) {
            this._$editIcon.append(`<div class="${options.editIconClass}" aria-hidden="true">`);
          }
          if (options.showRequiredFlag) {
            const requiredText = gettext("This field is required");
            $('<span class="required-flag">*</span>').attr({
              'aria-label': requiredText,
              'title': requiredText
            }).appendTo(this._$editIcon);
          }
          if (multiline && this.$el[0].id) {
            $(`label[for="${this.$el[0].id}"]`).append(this._$editIcon);
          } else {
            this._$editIcon.insertAfter(this.$el);
          }
        }
        $form.hide().insertBefore(this.$el);
        if (!options.deferEventSetup) {
          this.setupEvents();
        }
        if (options.startOpen) {
          this.startEdit({
            preventAnimation: true
          });
        }
        if (options.enabled) {
          this.enable();
        } else {
          this.disable();
        }
      }

      /**
       * Create and return the field to use for the input element.
       *
       * Returns:
       *     jQuery:
       *     The newly created input element.
       */
      createField() {
        if (this.options.multiline) {
          return $('<textarea>').autoSizeTextArea();
        } else {
          return $('<input type="text">');
        }
      }

      /**
       * Remove the view.
       *
       * Returns:
       *     InlineEditorView:
       *     This object, for chaining.
       */
      remove() {
        super.remove();
        $(window).off(this.cid);
        return this;
      }

      /**
       * Connect events.
       */
      setupEvents() {
        const options = this.options;
        this.$field.keydown(e => {
          e.stopPropagation();
          if (e.key === 'Enter') {
            if (!options.multiline || e.ctrlKey) {
              this.submit();
            }
            if (!options.multiline) {
              e.preventDefault();
            }
          } else if (e.key === 'Escape') {
            this.cancel();
          } else if (e.key === 's' || e.key === 'S') {
            if (e.ctrlKey) {
              this.submit();
              e.preventDefault();
            }
          }
        }).keypress(e => e.stopPropagation()).keyup(e => {
          e.stopPropagation();
          e.preventDefault();
          this._scheduleUpdateDirtyState();
        }).on('cut paste', () => this._scheduleUpdateDirtyState());
        if (!options.useEditIconOnly) {
          /*
           * Check if the mouse was dragging, so that the editor isn't opened
           * when text is selected.
           */
          let lastX = null;
          let lastY = null;
          let isDragging = true;
          this.$el.on('click', 'a', e => e.stopPropagation()).on('click', e => {
            e.stopPropagation();
            e.preventDefault();
            if (!isDragging) {
              this.startEdit({
                clickX: e.clientX,
                clickY: e.clientY
              });
            }
            isDragging = true;
          }).on('mousedown', e => {
            isDragging = false;
            lastX = e.clientX;
            lastY = e.clientY;
            this.$el.on('mousemove', e2 => {
              const threshold = options.editDragThreshold;
              isDragging = isDragging || Math.abs(e2.clientX - lastX) > threshold || Math.abs(e2.clientY - lastY) > threshold;
            });
          }).on('mouseup', () => {
            this.$el.off('mousemove');
            lastX = null;
            lastY = null;
          });
        }
      }

      /**
       * Start editing.
       *
       * Args:
       *     options (EditOptions, optional):
       *         Options for the operation.
       */
      startEdit(options = {}) {
        if (this._editing || !this.options.enabled) {
          return;
        }

        /*
         * We trigger a "startEdit" native JS event on the view's element
         * before actually doing anything. This allows users to listen for
         * that event and call preventDefault() in order to stop the edit
         * from happening.
         */
        const doEdit = this.el.dispatchEvent(new Event('startEdit', {
          cancelable: true
        }));
        if (!doEdit) {
          return;
        }
        let value;
        if (this.options.hasRawValue) {
          this._initialValue = this.options.rawValue;
          value = this._initialValue;
        } else {
          this._initialValue = this.$el.text();
          value = _.unescape(this.normalizeText(this._initialValue));
        }
        this._editing = true;
        this.options.setFieldValue(this, value);
        this.trigger('beginEditPreShow', options);
        this.showEditor(options);
        this.trigger('beginEdit', options);
      }

      /**
       * Show the editor.
       *
       * Args:
       *     options (EditOptions, optional):
       *         Options for the operation.
       */
      showEditor(options = {}) {
        const $editIcon = this._$editIcon;
        if (this.options.multiline && !options.preventAnimation) {
          $editIcon.fadeOut(this.options.animationSpeedMS, () => $editIcon.css({
            display: '',
            visibility: 'hidden'
          }));
        } else {
          $editIcon.css('display', 'none');
        }
        this.$el.hide();
        this._$form.show();
        if (this.options.multiline) {
          const elHeight = this.$el.outerHeight();
          const newHeight = elHeight + this.options.extraHeight;
          if (this._isTextArea) {
            if (this.options.matchHeight) {
              this.$field.autoSizeTextArea('setMinHeight', newHeight).css('overflow', 'hidden');
              if (options.preventAnimation) {
                this.$field.height(newHeight);
              } else {
                this.$field.height(elHeight).animate({
                  height: newHeight
                }, this.options.animationSpeedMS);
              }
            } else {
              /*
               * If there's significant processing that happens between
               * the text and what's displayed in the element, it's
               * likely that the rendered size will be different from the
               * editor size. In that case, don't try to match sizes,
               * just ask the field to auto-size itself to the size of
               * the source text.
               */
              this.$field.autoSizeTextArea('autoSize', true, false, elHeight);
            }
          }
        }
        this.$buttons.show();

        // Execute this after the animation, if we performed one.
        this.$field.queue(() => {
          if (this.options.multiline && this._isTextArea) {
            this.$field.css('overflow', 'auto');
          }
          if (this.options.focusOnOpen) {
            this.$field.focus();
          }
          if (!this.options.multiline && this.$field[0].tagName === 'INPUT') {
            this.$field[0].select();
          }
          this.$field.dequeue();
        });
      }

      /**
       * Hide the inline editor.
       */
      hideEditor() {
        const $editIcon = this._$editIcon;
        this.$field.blur();
        this.$buttons.hide();
        if (this.options.multiline) {
          $editIcon.fadeIn(this.options.animationSpeedMS, () => $editIcon.css('visibility', 'visible'));
        } else {
          $editIcon.css('display', '');
        }
        if (this.options.multiline && this.options.matchHeight && this._editing && this._isTextArea) {
          this.$field.css('overflow', 'hidden').animate({
            height: this.$el.outerHeight()
          }, this.options.animationSpeedMS);
        }
        this.$field.queue(() => {
          this.$el.show();
          this._$form.hide();
          this.$field.dequeue();
        });
        this._editing = false;
        this._updateDirtyState();
      }

      /**
       * Save the value of the editor.
       *
       * Args:
       *     options (SaveOptions):
       *         Options for the save operation.
       *
       * Returns:
       *     unknown:
       *     The new value, if available.
       */
      save(options = {}) {
        const value = this.getValue();
        const initialValue = this._initialValue;
        const dirty = this.isDirty();
        if (dirty) {
          this.$el.html(this.options.formatResult(value));
          this._initialValue = this.$el.text();
        }
        if (dirty || this.options.notifyUnchangedCompletion) {
          if (!options.preventEvents) {
            this.trigger('complete', value, initialValue);
          }
          if (this.options.hasRawValue) {
            this.options.rawValue = value;
          }
          return value;
        } else {
          if (!options.preventEvents) {
            this.trigger('cancel', this._initialValue);
          }
        }
      }

      /**
       * Submit the editor.
       *
       * Args:
       *     options (SaveOptions):
       *         Options for the save operation.
       *
       * Returns:
       *     unknown:
       *     The new value, if available.
       */
      submit(options = {}) {
        // hideEditor() resets the _dirty flag, so we need to save() first.
        const value = this.save(options);
        this.hideEditor();
        return value;
      }

      /**
       * Cancel the edit.
       */
      cancel() {
        if (!this.isDirty() || !this.options.promptOnCancel || confirm(gettext("You have unsaved changes. Are you sure you want to discard them?"))) {
          this.hideEditor();
          this.trigger('cancel', this._initialValue);
        }
      }

      /**
       * Return the dirty state of the editor.
       *
       * Returns:
       *     boolean:
       *     Whether the editor is currently dirty.
       */
      isDirty() {
        if (this._dirtyCalcTimeout !== null) {
          clearTimeout(this._dirtyCalcTimeout);
          this._updateDirtyState();
        }
        return this._dirty;
      }

      /**
       * Return the value in the field.
       *
       * Returns:
       *     *:
       *     The current value of the field.
       */
      getValue() {
        return this.options.getFieldValue(this);
      }

      /**
       * Set the value in the field.
       *
       * Args:
       *     value (*):
       *     The new value for the field.
       */
      setValue(value) {
        this.options.setFieldValue(this, value);
        this._updateDirtyState();
      }

      /**
       * Enable the editor.
       */
      enable() {
        if (this._editing) {
          this.showEditor();
        }
        this._$editIcon.css('visibility', 'visible');
        this.options.enabled = true;
      }

      /**
       * Disable the editor.
       */
      disable() {
        if (this._editing) {
          this.hideEditor();
        }
        this._$editIcon.css('visibility', 'hidden');
        this.options.enabled = false;
      }

      /**
       * Return whether the editor is currently in edit mode.
       *
       * Returns:
       *     boolean:
       *     true if the inline editor is open.
       */
      editing() {
        return this._editing;
      }

      /**
       * Normalize the given text.
       *
       * Args:
       *     text (string):
       *         The text to normalize.
       *
       * Returns:
       *     string:
       *     The text with ``<br>`` elements turned into newlines and (in the
       *     case of multi-line data), whitespace collapsed.
       */
      normalizeText(text) {
        if (this.options.stripTags) {
          /*
           * Turn <br> elements back into newlines before stripping out all
           * other tags. Without this, we lose multi-line data when editing
           * some legacy data.
           */
          text = text.replace(/<br>/g, '\n');
          text = text.replace(/<\/?[^>]+>/gi, '');
          text = text.trim();
        }
        if (!this.options.multiline) {
          text = text.replace(/\s{2,}/g, ' ');
        }
        return text;
      }

      /**
       * Schedule an update for the dirty state.
       */
      _scheduleUpdateDirtyState() {
        if (this._dirtyCalcTimeout === null) {
          this._dirtyCalcTimeout = setTimeout(this._updateDirtyState.bind(this), 200);
        }
      }

      /**
       * Update the dirty state of the editor.
       */
      _updateDirtyState() {
        const newDirtyState = this._editing && this.options.isFieldDirty(this, this._initialValue);
        if (this._dirty !== newDirtyState) {
          this._dirty = newDirtyState;
          this.trigger('dirtyStateChanged', this._dirty);
        }
        this._dirtyCalcTimeout = null;
      }
    }) || _class$8);
    /**
     * A view for inline editors which use the CodeMirror editor for Markdown.
     */
    let RichTextInlineEditorView = spina.spina(_class2 = class RichTextInlineEditorView extends InlineEditorView {
      /**
       * Defaults for the view options.
       */
      static defaultOptions = _.defaults({
        getFieldValue: editor => editor.textEditor.getText(),
        isFieldDirty: (editor, initialValue) => {
          initialValue = editor.normalizeText(initialValue);
          return editor.textEditor.isDirty(initialValue);
        },
        matchHeight: false,
        multiline: true,
        setFieldValue: (editor, value) => editor.textEditor.setText(value || '')
      }, InlineEditorView.prototype.defaultOptions);

      /**********************
       * Instance variables *
       **********************/

      /**
       * Create and return the field to use for the input element.
       *
       * Returns:
       *     jQuery:
       *     The newly created input element.
       */
      createField() {
        let origRichText;
        this.textEditor = new TextEditorView(this.options.textEditorOptions);
        this.textEditor.$el.on('resize', () => this.trigger('resize'));
        this.$el.data('text-editor', this.textEditor);
        this.once('beginEdit', () => {
          const $span = $('<span class="enable-markdown">');
          const $checkbox = $('<input type="checkbox">').attr('id', _.uniqueId('markdown_check')).change(() => _.defer(() => this._updateDirtyState())).appendTo($span);
          this.textEditor.bindRichTextCheckbox($checkbox);
          $('<label>').attr('for', $checkbox[0].id).text(gettext("Enable Markdown")).appendTo($span);
          this.$buttons.append($span);
          const $markdownRef = $('<a class="markdown-info" target="_blank">').attr('href', `${MANUAL_URL}users/markdown/`).text(gettext("Markdown Reference")).toggle(this.textEditor.richText).appendTo(this.$buttons);
          this.textEditor.bindRichTextVisibility($markdownRef);
        });
        this.listenTo(this, 'beginEdit', options => {
          if (options.clickX !== undefined && options.clickY !== undefined) {
            this.textEditor.setCursorPosition(options.clickX, options.clickY);
          }
          this.textEditor.showEditor();
          origRichText = this.textEditor.richText;
        });
        this.listenTo(this, 'cancel', () => {
          this.textEditor.hideEditor();
          this.textEditor.setRichText(origRichText);
        });
        this.listenTo(this, 'complete', () => this.textEditor.hideEditor());
        return this.textEditor.render().$el;
      }

      /**
       * Set up events for the view.
       */
      setupEvents() {
        super.setupEvents();
        this.listenTo(this.textEditor, 'change', this._scheduleUpdateDirtyState);
      }
    }) || _class2;
    /**
     * A view for inline editors that edit dates.
     *
     * This view expects a local date in YYYY-MM-DD format to be passed to the
     * ``rawValue`` option and will render a date picker for editing the date.
     *
     * Version Added:
     *     5.0
     */
    let DateInlineEditorView = spina.spina(_class3 = class DateInlineEditorView extends InlineEditorView {
      /**
       * Defaults for the view options.
       */
      static defaultOptions = _.defaults({
        descriptorText: null,
        editIconClass: 'rb-icon rb-icon-edit',
        getFieldValue: editor => editor._$datePickerInput.val(),
        hasRawValue: true,
        isFieldDirty: (editor, initialValue) => editor.getValue() !== initialValue,
        maxDate: null,
        minDate: null,
        multiline: false,
        setFieldValue: (editor, value) => editor._$datePickerInput.val(value),
        useEditIconOnly: true
      }, InlineEditorView.prototype.defaultOptions);

      /**********************
       * Instance variables *
       **********************/

      /**
       * Create and return the date input element.
       *
       * Returns:
       *     jQuery:
       *     The newly created date input element.
       */
      createField() {
        this._$datePickerInput = $('<input type="date">').attr({
          'max': this.options.maxDate,
          'min': this.options.minDate
        });
        this._$datePicker = $('<span class="rb-c-date-inline-editor__picker">').append(this.options.descriptorText, this._$datePickerInput);
        return this._$datePicker;
      }

      /**
       * Connect events.
       */
      setupEvents() {
        super.setupEvents();
        this.$field.change(e => {
          e.stopPropagation();
          e.preventDefault();
          this._scheduleUpdateDirtyState();
        });
      }
    }) || _class3;

    /**
     * A view for inline editors that edit datetimes.
     *
     * This view expects a local datetime in YYYY-MM-DDThh:mm format to be
     * passed to the ``rawValue`` option and will render a datetime picker
     * for editing it.
     *
     * Version Added:
     *     5.0.2
     */
    let DateTimeInlineEditorView = spina.spina(_class4 = class DateTimeInlineEditorView extends DateInlineEditorView {
      /**
       * Create and return the datetime input element.
       *
       * Returns:
       *     jQuery:
       *     The newly created datetime input element.
       */
      createField() {
        this._$datePickerInput = $('<input type="datetime-local">').attr({
          'max': this.options.maxDate,
          'min': this.options.minDate
        });
        this._$datePicker = $('<span class="rb-c-date-time-inline-editor__picker">').append(this.options.descriptorText, this._$datePickerInput);
        return this._$datePicker;
      }
    }) || _class4;

    var _class$7;

    /** Stored data about a centered element. */

    /** Map from a centered element to necessary data. */

    /**
     * Options for the CenteredElementManager view.
     *
     * Version Added:
     *     7.0
     */

    /**
     * A view which ensures that the specified elements are vertically centered.
     */
    let CenteredElementManager = spina.spina(_class$7 = class CenteredElementManager extends spina.BaseView {
      /**********************
       * Instance variables *
       **********************/

      /**
       * The elements being centered.
       *
       * This is public for consumption in unit tests.
       */

      /** A function to throttle position updates. */
      #updatePositionThrottled;

      /**
       * Initialize the view.
       *
       * Args:
       *     options (object):
       *         Options passed to this view.
       *
       * Option Args:
       *     elements (Array, optional):
       *         An initial array of elements to center.
       */
      initialize(options = {}) {
        this.#updatePositionThrottled = () => {
          requestAnimationFrame(() => this.updatePosition());
        };
        this.setElements(options.elements || new Map());
      }

      /**
       * Remove the CenteredElementManager.
       *
       * This will result in the event handlers being removed.
       *
       * Returns:
       *     CenteredElementManager:
       *     This object, for chaining.
       */
      remove() {
        super.remove();
        this.setElements(new Map());
        return this;
      }

      /**
       * Set the elements and their containers.
       *
       * Args:
       *     elements (Map<Element, CenteredElementData>):
       *         The elements to center within their respective containers.
       */
      setElements(elements) {
        this._elements = elements;
        if (elements.size > 0) {
          $(window).on('resize scroll', this.#updatePositionThrottled);
        } else {
          $(window).off('resize scroll', this.#updatePositionThrottled);
        }
      }

      /**
       * Update the position of the elements.
       *
       * This should only be done when the set of elements changed, as the view
       * will handle updating on window resizing and scrolling.
       */
      updatePosition() {
        if (this._elements.size === 0) {
          return;
        }
        const viewportTop = RB.contentViewport.get('top');
        const viewportBottom = RB.contentViewport.get('bottom');
        let windowTop = window.scrollY;
        const windowHeight = window.innerHeight;
        const windowBottom = windowTop + windowHeight - viewportBottom;
        windowTop += viewportTop;
        this._elements.forEach((containers, el) => {
          const $el = $(el);
          const $topContainer = containers.$top;
          const $parentContainer = containers.$parent || $topContainer;
          const $bottomContainer = containers.$bottom || $parentContainer;
          const containerTop = $topContainer.offset().top;
          const containerBottom = $bottomContainer.height() + ($bottomContainer === $topContainer ? containerTop : $bottomContainer.offset().top);

          /*
           * If the top container is above the element's parent container,
           * we'll need to offset the position later.
           */
          const topOffset = $parentContainer === $topContainer ? 0 : $parentContainer.offset().top - containerTop;

          /*
           * We don't have to vertically center the element when its
           * container is not on screen.
           */
          if (containerTop >= windowBottom && containerBottom <= windowTop) {
            return;
          }
          const elStyle = getComputedStyle(el);
          const elHeight = el.offsetHeight;
          const posType = elStyle.position;
          let newCSS = null;
          let newTop = null;

          /*
           * When a container takes up the entire viewport, we can switch
           * the CSS to use position: fixed. This way, we do not have to
           * re-compute its position.
           */
          if (windowTop >= containerTop && windowBottom <= containerBottom) {
            newTop = viewportTop + (windowHeight - viewportTop - viewportBottom - elHeight) / 2;
            if (posType !== 'fixed') {
              newCSS = {
                left: $el.offset().left,
                /* Ensure we're in control of placement. */
                position: 'fixed',
                right: 'auto',
                transform: 'none'
              };
            }
          } else {
            const top = Math.max(windowTop, containerTop);
            const bottom = Math.min(windowBottom, containerBottom);
            const availHeight = bottom - top - elHeight;
            const relTop = top - containerTop;

            /*
             * Make sure the top and bottom never exceeds the
             * calculated boundaries.
             *
             * We'll always position at least at 0, the top of the
             * boundary.
             *
             * We'll cap at availHeight, the bottom of the boundary
             * minus the element height.
             *
             * Optimistically, we'll position half-way through the
             * boundary.
             */
            newTop = Math.max(0, relTop + Math.min(availHeight, availHeight / 2)) - topOffset;
            if (posType === 'fixed') {
              newCSS = {
                position: 'absolute',
                /* Clear these settings to restore defaults. */
                left: '',
                right: '',
                transform: ''
              };
            }
          }
          if (newCSS) {
            $el.css(newCSS);
          }
          if (Math.round(parseInt(elStyle.top)) !== Math.round(newTop)) {
            el.style.top = newTop + 'px';
          }
        });
      }
    }) || _class$7;

    var _class$6;

    /**
     * The possible color themes for the FieldStateLabelView.
     *
     * Version Added:
     *     6.0
     */
    let FieldStateLabelThemes = /*#__PURE__*/function (FieldStateLabelThemes) {
      FieldStateLabelThemes["DRAFT"] = "draft";
      FieldStateLabelThemes["DELETED"] = "deleted";
      return FieldStateLabelThemes;
    }({});

    /**
     * Options for the FieldStateLabelView.
     *
     * Version Added:
     *     6.0
     */

    /**
     * A label that indicates the state of a field in a review request draft.
     *
     * This is useful to show which fields have been modified in a review
     * request draft.
     *
     * Version Added:
     *     6.0
     */
    let FieldStateLabelView = spina.spina(_class$6 = class FieldStateLabelView extends spina.BaseView {
      static className = 'rb-c-field-state-label';

      /**********************
       * Instance variables *
       **********************/

      /**
       * The state text to display in the label.
       */
      #state;

      /**
       * Whether the label should be displayed inline.
       *
       * This defaults to false.
       */
      #inline;

      /**
       * The color theme of the label.
       *
       * This defaults to Draft.
       */
      #theme;

      /**
       * Initialize the menu button.
       *
       * Args:
       *     options (FieldStateLabelViewOptions):
       *         Options for the view.
       */
      initialize(options) {
        this.#state = options.state;
        this.#inline = options.inline || false;
        this.#theme = options.theme || FieldStateLabelThemes.DRAFT;
      }

      /**
       * Render the view.
       */
      onInitialRender() {
        this.$el.addClass(this.className).addClass(`-is-${this.#theme}`).text(this.#state);
        if (this.#inline) {
          this.$el.addClass('-is-inline');
        }
      }
    }) || _class$6;

    var _class$5;

    /**
     * Options for the FloatingBannerView.
     *
     * Version Added:
     *     6.0
     */

    /**
     * Floats a banner on screen within a container.
     *
     * The banner will appear at the top of the container, or the screen,
     * whichever is visible, until the container is no longer on-screen.
     *
     * The banner will keep a spacer in its original location at the top
     * of the container in order to reserve space for it to anchor to.
     * This ensures that the page doesn't jump too horribly.
     */
    let FloatingBannerView = spina.spina(_class$5 = class FloatingBannerView extends spina.BaseView {
      /**********************
       * Instance variables *
       **********************/
      #$floatContainer = null;
      #$floatSpacer = null;
      #noFloatContainerClass = null;

      /**
       * Initialize the view.
       *
       * Args:
       *     options (FloatingBannerViewOptions):
       *         Options for the view.
       */
      initialize(options) {
        super.initialize(options);
        this.#$floatContainer = options.$floatContainer;
        this.#noFloatContainerClass = options.noFloatContainerClass;
      }

      /**
       * Render the banner and listens for scroll and resize updates.
       */
      onInitialRender() {
        $(window).scroll(() => this.#updateFloatPosition()).resize(() => this.#updateSize());
        _.defer(() => this.#updateFloatPosition());
      }

      /**
       * Remove the view from the DOM.
       *
       * This will remove both the banner and the floating spacer (if currently
       * in the DOM).
       *
       * Returns:
       *     FloatingBannerView:
       *     This object, for chaining.
       */
      remove() {
        if (this.#$floatSpacer !== null) {
          this.#$floatSpacer.remove();
          this.#$floatSpacer = null;
        }
        super.remove();
        return this;
      }

      /**
       * Update the size of the banner to match the spacer.
       */
      #updateSize() {
        if (this.#$floatSpacer !== null) {
          if (this.$el.hasClass('floating')) {
            const rect = this.#$floatSpacer.parent()[0].getBoundingClientRect();
            this.$el.width(Math.ceil(rect.width) - Math.max(this.$el.getExtents('bpm', 'lr'), 0));
          } else {
            this.$el.width('auto');
          }
        }
      }

      /**
       * Update the position of the banner.
       *
       * This will factor in how much of the container is visible, based on
       * its size, position, and the scroll offset. It will then attempt
       * to position the banner to the top of the visible portion of the
       * container.
       */
      #updateFloatPosition() {
        if (this.$el.parent().length === 0) {
          return;
        }
        if (this.#$floatSpacer === null) {
          this.#$floatSpacer = this.$el.wrap($('<div>')).parent();
          this.#updateSize();
        }
        const containerTop = this.#$floatContainer.offset().top;
        const containerHeight = this.#$floatContainer.outerHeight();
        const containerBottom = containerTop + containerHeight;
        const windowTop = $(window).scrollTop();
        const topOffset = this.#$floatSpacer.offset().top - windowTop;
        const outerHeight = this.$el.outerHeight(true);
        const wasFloating = this.$el.hasClass('floating');
        if (!this.#$floatContainer.hasClass(this.#noFloatContainerClass) && topOffset < 0 && containerTop < windowTop && windowTop < containerBottom) {
          /*
           * We're floating! If we just entered this state, set the
           * appropriate styles on the element.
           *
           * We'll then want to set the top to 0, unless the user is
           * scrolling the banner out of view. In that case, figure out how
           * much to show, and set the appropriate offset.
           */
          if (!wasFloating) {
            /*
             * Set the spacer to be the dimensions of the docked banner,
             * so that the container doesn't change sizes when we go into
             * float mode.
             */
            this.#$floatSpacer.height(this.$el.outerHeight()).css({
              'margin-bottom': this.$el.css('margin-bottom'),
              'margin-top': this.$el.css('margin-top')
            });
            this.$el.addClass('floating').css({
              'margin-top': 0,
              'position': 'fixed'
            });
          }
          this.$el.css('top', windowTop > containerBottom - outerHeight ? containerBottom - outerHeight - windowTop : 0);
          this.#updateSize();
        } else if (wasFloating) {
          /*
           * We're now longer floating. Unset the styles on the banner and
           * on the spacer (in order to prevent the spacer from taking up
           * any additional room.
           */
          this.$el.removeClass('floating').css({
            'margin-top': '',
            'position': '',
            'top': ''
          });
          this.#$floatSpacer.height('auto').css('margin', 0);
        }
      }
    }) || _class$5;

    var _class$4;

    /**
     * Definitions for the type of menus.
     *
     * Version Added:
     *     6.0
     */
    let MenuType = /*#__PURE__*/function (MenuType) {
      MenuType[MenuType["Standard"] = 1] = "Standard";
      MenuType[MenuType["Button"] = 2] = "Button";
      return MenuType;
    }({});

    /**
     * Options for the MenuView.
     *
     * Version Added:
     *     6.0
     */

    /**
     * Options for menu transitions.
     *
     * Version Added:
     *     6.0
     */

    /**
     * Info about a menu item.
     *
     * Version Added:
     *     6.0
     */

    /**
     * Options for adding separators.
     *
     * Version Added:
     *     6.0
     */

    /**
     * A standard implementation of drop-down menus.
     *
     * This can be used to create and populate a standard drop-down menu or a
     * button menu (where each menu item is a button). It handles animating the
     * opening and closing of the menu, applying ARIA attributes for accessibility,
     * and handling keyboard-based navigation.
     *
     * Menus are (optionally) associated with a controller element, which is the
     * button or element responsible for opening and closing the menu. Like the
     * menu itself, the appropriate ARIA attributes will be set on the element to
     * help screen readers associate it with the menu.
     *
     * Version Added:
     *     4.0
     *
     * Attributes:
     *     $controller (jQuery):
     *         The jQuery-wrapped element that controls the display of this menu.
     *
     *     isOpen (boolean):
     *         The current menu open state.
     *
     *     type (number):
     *         The configured type of menu. This will be one of
     *         :js:attr:`RB.MenuView.TYPE_BUTTON_MENU` or
     *         :js:attr:`RB.MenuView.TYPE_STANDARD_MENU`.
     */
    let MenuView = spina.spina(_class$4 = class MenuView extends spina.BaseView {
      /*
       * These are here for legacy use and will be removed in Review Board 8.0.
       * Callers should use the MenuType enum.
       */
      static TYPE_STANDARD_MENU = MenuType.Standard;
      static TYPE_BUTTON_MENU = MenuType.Button;
      static className = 'rb-c-menu';
      static events = {
        'keydown': '_onKeyDown',
        'touchstart': '_onTouchStart'
      };

      /**********************
       * Instance variables *
       **********************/

      /**
       * The jQuery-wrapped element that controls the display of this menu.
       */
      $controller = null;

      /**
       * Whether the menu is currently open.
       */
      isOpen = false;

      /**
       * The configured type of menu.
       */

      #ariaLabelledBy;
      #ariaLabel;
      #activeItemIndex = null;
      #activeItemEl = null;

      /**
       * Initialize the view.
       *
       * Args:
       *     options (MenuViewOptions, optional):
       *         Options for the view.
       */
      initialize(options = {}) {
        super.initialize(options);
        if (options.type === undefined || options.type === MenuType.Standard) {
          this.type = MenuType.Standard;
        } else if (options.type === MenuType.Button) {
          this.type = MenuType.Button;
        } else {
          console.error('The provided RB.MenuView type (%s) is not ' + 'supported. Defaulting to a standard menu.', options.type);
          this.type = MenuType.Standard;
        }
        if (!this.id) {
          this.id = _.uniqueId('__rb-menu');
        }
        this.$controller = options.$controller;
        this.#ariaLabelledBy = options.ariaLabelledBy;
        this.#ariaLabel = options.ariaLabel;
      }

      /**
       * Render the menu.
       *
       * This will set up the elements for the menu and associate it with the
       * controller.
       */
      onInitialRender() {
        this.$el.attr({
          id: this.id,
          tabindex: '-1'
        });
        if (this.type === MenuType.Button) {
          this.$el.addClass('rb-c-button-group -is-vertical');
        }

        /* Set ARIA attributes on these and on the controller. */
        this.$el.attr('role', 'menu');
        if (this.#ariaLabelledBy) {
          this.$el.attr('aria-labelledby', this.#ariaLabelledBy);
        } else if (this.#ariaLabel) {
          this.$el.attr('aria-label', this.#ariaLabel);
        }
        if (this.$controller) {
          this.$controller.attr({
            'aria-controls': this.id,
            'aria-expanded': 'false',
            'aria-haspopup': 'true'
          });
        }
      }

      /**
       * Add an item to the menu.
       *
       * This appends an item to the bottom of the menu. It can append an
       * explicit element (if one was already created), or it can build a new
       * item appropriate for the type of menu.
       *
       * In either case, this can assign a DOM element ID to the menu item,
       * assign a click event handler, and will set ARIA roles.
       *
       * Version Changed:
       *     6.0:
       *     * Added the $child option argument.
       *     * Added the ``id`` option arg.
       *     * Added the ''prepend`` option arg.
       *
       * Args:
       *     options (MenuItemOptions, optional):
       *         Options for the menu item.
       *
       * Returns:
       *     jQuery:
       *     The jQuery-wrapped element for the menu item.
       */
      addItem(options = {}) {
        let $el;
        if (this.type === MenuType.Button) {
          $el = $('<button class="rb-c-menu__item rb-c-button" type="button">');
        } else if (this.type === MenuType.Standard) {
          $el = $('<div class="rb-c-menu__item">');
        } else {
          /* This shouldn't be able to be reached. */
          console.assert(false, 'RB.MenuView type is not a supported type.');
        }
        if (options.$child !== undefined) {
          options.$child.appendTo($el);
        } else if (options.text !== undefined) {
          $el.text(options.text);
        }
        if (options.onClick !== undefined) {
          $el.on('click', options.onClick);
        }
        if (options.id !== undefined) {
          $el.attr('id', options.id);
        }
        $el.attr({
          role: 'menuitem',
          tabindex: '-1'
        }).on('mousemove', e => this.#onMenuItemMouseMove(e));
        if (options.prepend) {
          $el.prependTo(this.el);
        } else {
          $el.appendTo(this.el);
        }
        return $el;
      }

      /**
       * Add a separator to the menu.
       *
       * Version Added:
       *     6.0
       *
       * Returns:
       *     jQuery:
       *     The jQuery-wrapped element for the separator.
       */
      addSeparator(options = {}) {
        const $el = $('<div class="rb-c-menu__separator" role="separator">');
        if (options.prepend) {
          $el.prependTo(this.el);
        } else {
          $el.appendTo(this.el);
        }
        return $el;
      }

      /**
       * Clear all the menu items.
       */
      clearItems() {
        this.$('.rb-c-menu__item').remove();
      }

      /**
       * Open the menu.
       *
       * This will show the menu on the screen. Before it's shown, an ``opening``
       * event will be emitted. Once shown (and after the animation finishes),
       * the ``opened`` event will be emitted.
       *
       * Args:
       *     options (MenuTransitionOptions, optional):
       *         Options to use when opening the menu.
       */
      open(options = {}) {
        this.#setOpened(true, options);
      }

      /**
       * Close the menu.
       *
       * This will hide the menu. Before it's hidden, a ``closing`` event will
       * be emitted. Once hidden (and after the animation finishes), the
       * ``closed`` event will be emitted.
       *
       * Args:
       *     options (MenuTransitionOptions, optional):
       *         Options to use when closing the menu.
       */
      close(options = {}) {
        this.#setOpened(false, options);
      }

      /**
       * Focus the first item in the menu.
       *
       * This should be used by callers when programmatically displaying the
       * menu (such as a result of keyboard input), when showing the menu below
       * the controller.
       *
       * Once focused, arrow keys can be used to navigate the menu.
       */
      focusFirstItem() {
        if (this.el.children.length > 0) {
          this.focusItem(0);
        }
      }

      /**
       * Focus the last item in the menu.
       *
       * This should be used by callers when programmatically displaying the
       * menu (such as a result of keyboard input), when showing the menu above
       * the controller.
       *
       * Once focused, arrow keys can be used to navigate the menu.
       */
      focusLastItem() {
        const numChildren = this.el.children.length;
        if (numChildren > 0) {
          this.focusItem(numChildren - 1);
        }
      }

      /**
       * Set the menu's open/closed state.
       *
       * This takes care of emitting the opening/opened/closing/closed events,
       * setting active item states, setting the classes or display states, and
       * setting appropriate ARIA attributes on the controller.
       *
       * Args:
       *     opened (boolean):
       *         Whether the menu is set to opened.
       *
       *     options (MenuTransitionOptions, optional):
       *         The options to use when setting state.
       */
      #setOpened(opened, options = {}) {
        if (this.isOpen === opened) {
          return;
        }
        this.#activeItemIndex = null;
        this.#activeItemEl = null;
        if (options.animate === false) {
          this.$el.addClass('js-no-animation');
          _.defer(() => this.$el.removeClass('js-no-animation'));
        }
        this.isOpen = opened;
        const triggerEvents = options.triggerEvents !== false;
        if (triggerEvents) {
          this.trigger(opened ? 'opening' : 'closing');
        }
        this.$el.toggleClass('-is-open', opened);
        if (this.$controller) {
          this.$controller.toggleClass('-is-open', opened).attr('aria-expanded', opened ? 'true' : 'false');
        }
        if (triggerEvents) {
          this.trigger(opened ? 'opened' : 'closed');
        }
      }

      /**
       * Focus an item at the specified index.
       *
       * Args:
       *     index (number):
       *         The index of the menu item to focus. This is expected to be
       *         a valid index in the list of items.
       */
      focusItem(index) {
        this.#activeItemIndex = index;
        this.#activeItemEl = this.el.children[index];
        this.#activeItemEl.focus();
      }

      /**
       * Focus the previous item in the menu.
       *
       * This takes care of wrapping the focus around to the end of the menu,
       * if focus was already on the first item.
       */
      #focusPreviousItem() {
        if (this.#activeItemIndex === null) {
          this.focusFirstItem();
        } else {
          let index = this.#activeItemIndex - 1;
          if (index < 0) {
            index = this.el.children.length - 1;
          }
          this.focusItem(index);
        }
      }

      /**
       * Focus the next item in the menu.
       *
       * This takes care of wrapping the focus around to the beginning of
       * the menu, if focus was already on the last item.
       */
      #focusNextItem() {
        if (this.#activeItemIndex === null) {
          this.focusFirstItem();
        } else {
          let index = this.#activeItemIndex + 1;
          if (index >= this.el.children.length) {
            index = 0;
          }
          this.focusItem(index);
        }
      }

      /**
       * Handle a keydown event.
       *
       * When the menu or a menu item has focus, this will take care of
       * handling keyboard-based navigation, allowing the menu to be closed,
       * or the focused menu item to be changed or activated.
       *
       * Args:
       *     evt (KeyboardEvent):
       *         The keydown event.
       */
      _onKeyDown(evt) {
        let preventDefault = true;
        if (evt.key === 'Enter') {
          /* Activate any selected item. */
          $(this.#activeItemEl).triggerHandler('click');
        } else if (evt.key === 'Escape' || evt.key === 'Tab') {
          /* Close the menu and bring focus back to the controller. */
          if (this.$controller) {
            this.$controller.focus();
          }
          this.close({
            animate: false
          });
        } else if (evt.key === 'ArrowUp') {
          /* Move up an item. */
          this.#focusPreviousItem();
        } else if (evt.key === 'ArrowDown') {
          /* Move down an item. */
          this.#focusNextItem();
        } else if (evt.key === 'Home' || evt.key === 'PageUp') {
          /* Move to the first item. */
          this.focusFirstItem();
        } else if (evt.key === 'End' || evt.key === 'PageDown') {
          /* Move to the last item. */
          this.focusLastItem();
        } else {
          /* Let the default event handlers run. */
          preventDefault = false;
        }
        if (preventDefault) {
          evt.stopPropagation();
          evt.preventDefault();
        }
      }

      /**
       * Handle mousemove events on a menu item.
       *
       * This will move the focus to the menu item.
       *
       * Args:
       *     evt (MouseEvent):
       *         The mousemove event.
       */
      #onMenuItemMouseMove(evt) {
        const targetEl = evt.currentTarget;
        if (targetEl === this.#activeItemEl) {
          /* The mouse has moved but the item hasn't changed. */
          return;
        }
        const menuItems = this.el.children;
        const itemIndex = _.indexOf(menuItems, targetEl);
        if (itemIndex !== -1) {
          this.focusItem(itemIndex);
        }
      }

      /**
       * Return the active item index.
       *
       * This is for use with unit tests.
       *
       * Returns:
       *     number:
       *     The active item index.
       */
      get _activeItemIndex() {
        return this.#activeItemIndex;
      }
    }) || _class$4;

    var _class$3;

    /**
     * Options for the MenuButtonView.
     *
     * Version Added:
     *     6.0
     */

    /**
     * A button that offers a drop-down menu when clicked.
     *
     * Menu buttons have the appearance of a button with a drop-down indicator.
     * When clicked, they display a menu either below or above the button
     * (depending on their position on the screen).
     *
     * They may also be grouped into two buttons, one primary button (which works
     * as a standard, independent button) and one drop-down button (which works
     * as above, but just shows the drop-down indicator).
     *
     * Version Added:
     *     4.0
     */
    let MenuButtonView = spina.spina(_class$3 = class MenuButtonView extends spina.BaseView {
      static className = 'rb-c-menu-button';
      static events = {
        'click .rb-c-menu-button__toggle': '_onToggleClick',
        'focusout': '_onFocusOut',
        'keydown .rb-c-menu-button__toggle': '_onToggleButtonKeyDown',
        'mouseenter .rb-c-menu-button__toggle': '_openMenu',
        'mouseleave': '_closeMenu'
      };
      static template = _.template(`<% if (hasPrimaryButton) { %>
 <div class="rb-c-button-group" role="group">
  <button class="rb-c-menu-button__primary rb-c-button"
          type="button"><%- buttonText %></button>
  <button class="rb-c-menu-button__toggle rb-c-button"
          id="<%- labelID %>"
          type="button"
          aria-label="<%- menuLabel %>">
   <span class="<%- menuIconClass %>"></span>
  </button>
 </div>
<% } else { %>
 <button class="rb-c-button rb-c-menu-button__toggle"
         id="<%- labelID %>"
         type="button">
  <%- buttonText %>
  <span class="<%- menuIconClass %>"></span>
 </button>
<% } %>`);

      /**********************
       * Instance variables *
       **********************/

      /** The primary button, if one is configured. */
      $primaryButton = null;

      /** The menu associated with the button. */
      menu = null;

      /**
       * The direction that the menu will open.
       *
       * This is public so unit tests can set it, but should otherwise not be
       * necessary outside of this class.
       */
      openDirection = 'down';
      #$dropDownButton = null;
      #ariaMenuLabel;
      #buttonText;
      #hasPrimaryButton;
      #menuIconClass;
      #menuItems;
      #menuType;
      #onPrimaryButtonClick;

      /**
       * Initialize the menu button.
       *
       * Args:
       *     options (MenuButtonViewOptions):
       *         Options for the view.
       */
      initialize(options) {
        this.#ariaMenuLabel = options.ariaMenuLabel || gettext("More options");
        this.#menuItems = options.menuItems || [];
        this.#menuType = options.menuType || MenuType.Standard;
        this.#menuIconClass = options.menuIconClass || 'rb-icon rb-icon-dropdown-arrow';
        this.#buttonText = options.text;
        this.#onPrimaryButtonClick = options.onPrimaryButtonClick;
        this.#hasPrimaryButton = !!this.#onPrimaryButtonClick || options.hasPrimaryButton;
      }

      /**
       * Remove the view from the DOM.
       *
       * Returns:
       *     MenuButtonView:
       *     This object, for chaining.
       */
      remove() {
        this.menu.remove();
        super.remove();
        return this;
      }

      /**
       * Render the view.
       */
      onInitialRender() {
        const labelID = _.uniqueId('__rb-menubuttonview__label');
        this.$el.addClass(this.className).attr('role', 'group').html(MenuButtonView.template({
          buttonText: this.#buttonText,
          hasPrimaryButton: this.#hasPrimaryButton,
          labelID: labelID,
          menuIconClass: this.#menuIconClass,
          menuLabel: this.#ariaMenuLabel
        }));
        if (this.#hasPrimaryButton) {
          this.$primaryButton = this.$('.rb-c-menu-button__primary').on('click', this.#onPrimaryButtonClick.bind(this));
          console.assert(this.$primaryButton.length === 1);
        }
        this.#$dropDownButton = this.$('.rb-c-menu-button__toggle');
        console.assert(this.#$dropDownButton.length === 1);

        /* Create and populate the drop-down menu. */
        const menu = new MenuView({
          $controller: this.#$dropDownButton,
          ariaLabelledBy: labelID,
          type: this.#menuType
        });
        menu.render();
        this.listenTo(menu, 'opening', () => {
          this.#$dropDownButton.addClass('js-hover');
          this.updateMenuPosition();
        });
        this.listenTo(menu, 'closing', () => {
          this.#$dropDownButton.removeClass('js-hover');
        });
        for (const item of this.#menuItems) {
          menu.addItem(item);
        }
        menu.$el.appendTo(this.$el);
        this.menu = menu;
      }

      /**
       * Position the drop-down menu above or below the button.
       *
       * This will attempt to determine whether there's enough space below
       * the button for the menu to fully appear. If there is not, then the
       * menu will appear above the button instead.
       *
       * The resulting direction will also impact the styling of the button and
       * menu, helping to create a connected appearance.
       *
       * This is public because unit tests need to be able to spy on it.
       */
      updateMenuPosition() {
        const $button = this.#$dropDownButton;
        const buttonY1 = $button.offset().top;
        const buttonY2 = buttonY1 + $button.innerHeight();
        const pageY1 = window.pageYOffset;
        const pageY2 = window.pageYOffset + window.innerHeight;
        let direction;
        if (pageY1 >= buttonY1) {
          /*
           * The button is at least partially off-screen, above the current
           * viewport. Drop the menu down.
           */
          direction = 'down';
        } else if (pageY2 <= buttonY2) {
          /*
           * The button is at least partially off-screen, below the current
           * viewport. Drop the menu up.
           */
          direction = 'up';
        } else {
          const menuHeight = this.menu.$el.outerHeight();

          /*
           * The button is fully on-screen. See if there's enough room below
           * the button for the menu.
           */
          if (pageY2 >= buttonY2 + menuHeight) {
            /* The menu can fully fit below the button. */
            direction = 'down';
          } else {
            /* The menu cannot fully fit below the button. */
            direction = 'up';
          }
        }
        this.openDirection = direction;
        this.$el.toggleClass('-opens-up', direction === 'up');
        this.menu.$el.css(direction === 'down' ? 'top' : 'bottom', $button.innerHeight());
      }

      /**
       * Show the menu.
       *
       * Args:
       *     options (MenuTransitionOptions):
       *         Options to pass to :js:meth:`RB.MenuView.open`.
       */
      _openMenu(options) {
        this.menu.open(options);
      }

      /**
       * Close the menu.
       *
       * Args:
       *     options (MenuTransitionOptions):
       *         Options to pass to :js:meth:`RB.MenuView.close`.
       */
      _closeMenu(options) {
        this.menu.close(options);
      }

      /**
       * Handle a focus-out event.
       *
       * This will immediately hide the menu, if the newly-focused item is
       * not a child of this view.
       *
       * Args:
       *     evt (FocusEvent):
       *         The focus-in event.
       */
      _onFocusOut(evt) {
        evt.stopPropagation();

        /*
         * Only close the menu if focus has moved to something outside of
         * this component.
         */
        const currentTarget = evt.currentTarget;
        if (!currentTarget.contains(evt.relatedTarget)) {
          this._closeMenu({
            animate: false
          });
        }
      }

      /**
       * Handle a keydown event.
       *
       * When the drop-down button has focus, this will take care of handling
       * keyboard-based navigation, allowing the menu to be opened or closed.
       * Opening the menu will transfer focus to the menu items.
       *
       * Args:
       *     evt (KeyboardEvent):
       *         The keydown event.
       */
      _onToggleButtonKeyDown(evt) {
        if (evt.key === 'ArrowDown' || evt.key === 'ArrowUp' || evt.key === 'Enter' || evt.key === ' ') {
          this._openMenu({
            animate: false
          });
          if (this.openDirection === 'up') {
            this.menu.focusLastItem();
          } else if (this.openDirection === 'down') {
            this.menu.focusFirstItem();
          }
          evt.stopPropagation();
          evt.preventDefault();
        } else if (evt.key === 'Escape') {
          this._closeMenu({
            animate: false
          });
          evt.stopPropagation();
          evt.preventDefault();
        }
      }

      /**
       * Handle a click event on the dropdown toggle.
       *
       * Clicking on the dropdown toggle is not supposed to do anything,
       * since hovering it with the cursor is sufficient for opening the
       * alternatives menu. We handle the click and stop the event from
       * propagating so that the modal library doesn't interpret this as
       * an attempt to close the dialog.
       *
       * Args:
       *     evt (MouseEvent):
       *         The click event.
       */
      _onToggleClick(evt) {
        evt.stopPropagation();
        evt.preventDefault();
      }
    }) || _class$3;

    var _class$2;

    /**
     * An overlay to capture events.
     *
     * Version Added:
     *     6.0
     */
    let OverlayView = spina.spina(_class$2 = class OverlayView extends spina.BaseView {
      static className = 'rb-c-event-overlay';
      static events = {
        'click': '_onClick',
        'touchstart': '_onClick'
      };

      /**
       * Handle a click or other interaction.
       *
       * This will trigger an event which can be handled by the owner.
       */
      _onClick(e) {
        e.stopPropagation();
        e.preventDefault();
        this.trigger('click');
      }
    }) || _class$2;

    var _class$1;

    /**
     * Options for the SlideshowView.
     *
     * Version Added:
     *     6.0
     */

    /**
     * A slideshow for navigating and cycling between content.
     *
     * Slideshows can automatically cycle between content periodically, up to
     * a maximum number of times. Users can choose to navigate to specific pages,
     * which will turn off the automatic navigation.
     *
     * Automatic cycling between slides can be made aware of any animations that
     * need to play in the slide. Setting a ``data-last-animation=`` attribute on
     * the element will cause the slideshow to wait for that particular animation
     * to end before scheduling a switch to another slide.
     *
     * If the user moves the mouse over a slide, automatic cycling will be
     * temporarily paused, allowing the user to spend more time viewing or
     * interacting with the content.
     *
     * Version Added:
     *     6.0
     */
    let SlideshowView = spina.spina(_class$1 = class SlideshowView extends spina.BaseView {
      static events = {
        'click .rb-c-slideshow__nav-item': '_onNavItemClick',
        'click .rb-c-slideshow__nav-next': '_onNextClick',
        'click .rb-c-slideshow__nav-prev': '_onPrevClick',
        'keydown': '_onKeyDown',
        'mouseenter .rb-c-slideshow__slide-content': '_onSlideMouseEnter',
        'mouseleave .rb-c-slideshow__slide-content': '_onSlideMouseLeave'
      };

      /**
       * A selector for matching child elements that need tabindex managed.
       */
      static TABINDEX_SEL = 'a[href], button, input, select, textarea, [tabindex="0"]';

      /**********************
       * Instance variables *
       **********************/

      #$curNavItem = null;
      #$curSlide = null;
      #$navItems = null;
      #$slides = null;
      #$slidesContainer = null;

      /**
       * The time in milliseconds between automatic cyling of slides.
       *
       * If not provided, this will default to either the ``data-cycle-time-ms=``
       * attribute on the element (if present) or 2 seconds.
       *
       * If a slide contains animations, this will be the amount of time after
       * the last animation completes before cycling.
       */
      #autoCycleTimeMS;
      #curIndex = 0;
      #cycleAutomaticallyEnabled = false;
      #cycleAutomaticallyPaused = false;
      #cycleTimeout;
      #maxFullAutoCycles;
      #numFullAutoCycles = 0;
      #numSlides = 0;
      #restartCycleTimeMS;

      /**
       * Initialize the slideshow.
       *
       * Args:
       *     options (SlideshowViewOptions):
       *         Options for the view.
       */
      initialize(options = {}) {
        this.#autoCycleTimeMS = options.autoCycleTimeMS || parseInt(this.$el.data('auto-cycle-time-ms'), 10) || 2000;
        this.#restartCycleTimeMS = options.restartCycleTimeMS || 6000;
        this.#maxFullAutoCycles = options.maxAutoCycles || 5;
        this.#numFullAutoCycles = 0;
      }

      /**
       * Render the view.
       */
      onInitialRender() {
        const $nav = this.$('.rb-c-slideshow__nav');
        this.#$navItems = $nav.children('.rb-c-slideshow__nav-item');
        this.#$slidesContainer = this.$('.rb-c-slideshow__slides');
        this.#$slides = this.#$slidesContainer.children('.rb-c-slideshow__slide');
        this.#numSlides = this.#$slides.length;
        this.#$slides.each((i, el) => {
          const $el = $(el);
          $el.data('slide-index', i);
          this.#disableSlide($el);
        });

        /*
         * If the URL is pointing to a particular slide, then switch to it
         * immediately.
         */
        let slideIndex = 0;
        if (window.location.hash && this.#$navItems.length) {
          const $navItem = this.#$navItems.filter(`[href="${window.location.hash}"]`);
          if ($navItem.length > 0) {
            slideIndex = this.#$navItems.index($navItem[0]);
          }
        }
        this.setSlide(slideIndex);
        this.setAutomaticCyclingEnabled(this.$el.hasClass('-is-auto-cycled'));
      }

      /**
       * Queue automatic cycling to the next slide.
       *
       * This will only queue up a cycle if automatic cycling is enabled and
       * not paused.
       *
       * If the slide has a ``data-last-animation=`` attribute defined, this will
       * wait until that animation has ended before scheduling the next slide.
       */
      queueNextSlide() {
        this.unqueueNextSlide();
        if (!this.#cycleAutomaticallyEnabled || this.#cycleAutomaticallyPaused) {
          return;
        }
        function _scheduleNextSlide() {
          this.#cycleTimeout = setTimeout(this.#autoCycleNext.bind(this), this.#curIndex + 1 >= this.#numSlides ? this.#restartCycleTimeMS : this.#autoCycleTimeMS);
        }
        const $slide = this.#$curSlide;
        const lastAnimation = $slide.data('last-animation');
        if (lastAnimation) {
          const expectedIndex = this.#curIndex;
          $slide.on('animationend.slideshow-queue-slide', e => {
            const origEv = e.originalEvent;
            if (origEv.animationName === lastAnimation && this.#curIndex === expectedIndex) {
              _scheduleNextSlide.call(this);
            }
          });
        } else {
          _scheduleNextSlide.call(this);
        }
      }

      /**
       * Unqueue a previously-queued automatic cycle.
       */
      unqueueNextSlide() {
        if (this.#cycleTimeout) {
          clearTimeout(this.#cycleTimeout);
          this.#cycleTimeout = null;
        }
      }

      /**
       * Immediately switch to the previous slide.
       *
       * If the current slide is the first in the list, this will switch to the
       * last slide.
       */
      prevSlide() {
        this.setSlide(this.#curIndex === 0 ? this.#numSlides - 1 : this.#curIndex - 1);
      }

      /**
       * Immediately switch to the next slide.
       *
       * If the current slide is the last in the list, this will switch to the
       * first slide.
       */
      nextSlide() {
        this.setSlide(this.#curIndex + 1 >= this.#numSlides ? 0 : this.#curIndex + 1);
      }

      /**
       * Set the current slide to the specified index.
       *
       * If automatic cycling is enabled, the next slide will be queued up
       * after the switch.
       *
       * Args:
       *     index (number):
       *         The index of the slide to switch to.
       */
      setSlide(index) {
        const $oldSlide = this.#$curSlide;
        let $newNavItem = null;
        let $newSlide = null;
        if (this.#$navItems.length) {
          /* We're navigating with a full TOC. */
          $newNavItem = this.#$navItems.eq(index);
          const $oldNavItem = this.#$curNavItem;
          if ($oldNavItem) {
            $oldNavItem.attr('aria-selected', 'false');
          }
          $newNavItem.attr('aria-selected', 'true');
          $newSlide = this.#$slides.filter($newNavItem[0].hash);
        } else {
          /* We're navigating with next/prev buttons. */
          $newSlide = this.#$slides.eq(index);
        }
        $newSlide.css('display', 'block');
        const offsetLeft = $newSlide[0].clientLeft;
        if ($oldSlide) {
          this.#disableSlide($oldSlide);
        }
        this.#enableSlide($newSlide);
        $newSlide.css('transform', `translate3d(-${offsetLeft}px, 0, 0)`);
        this.#$slidesContainer.data('selected-index', index).css('transform', `translate3d(-${index * 100}%, 0, 0)`);
        if ($newNavItem) {
          this.#$curNavItem = $newNavItem;
        }
        this.#$curSlide = $newSlide;
        this.#curIndex = index;
        this.queueNextSlide();
      }

      /**
       * Set whether automatic cycling is enabled.
       *
       * Args:
       *     enabled (boolean):
       *         Whether to enable automatic cycling.
       */
      setAutomaticCyclingEnabled(enabled) {
        if (this.#cycleAutomaticallyEnabled === enabled) {
          return;
        }
        this.#cycleAutomaticallyEnabled = enabled;
        this.#$slidesContainer.attr('aria-live', enabled ? 'off' : 'polite');
        this.#$curSlide.off('animationend.slideshow-queue-slide');
        this.unqueueNextSlide();
        if (enabled) {
          this.queueNextSlide();
        }
      }

      /**
       * Automatically cycle to the next slide.
       *
       * This will disable automatic cycling if the number of full auto-cycles
       * is reached after switching to the next slide.
       */
      #autoCycleNext() {
        this.nextSlide();
        if (this.#curIndex === 0) {
          this.#numFullAutoCycles++;
          if (this.#numFullAutoCycles >= this.#maxFullAutoCycles) {
            /*
             * We've rewound and have cycled the full amount of
             * times allowed. Disable any further auto-cycling.
             */
            this.setAutomaticCyclingEnabled(false);
          }
        }
      }

      /**
       * Disable a slide.
       *
       * This will hide it and disable tab navigation to any relevant children.
       *
       * Args:
       *     $slide (jQuery):
       *         The slide element to disable.
       */
      #disableSlide($slide) {
        $slide.off('animationend.slideshow-queue-slide').attr({
          'aria-hidden': 'true',
          'hidden': '',
          'tabindex': '-1'
        }).find(SlideshowView.TABINDEX_SEL).attr('tabindex', '-1');
      }

      /**
       * Enable a slide.
       *
       * This will show it and enable tab navigation to any relevant children.
       *
       * Args:
       *     $slide (jQuery):
       *         The slide element to disable.
       */
      #enableSlide($slide) {
        $slide.attr({
          'aria-hidden': 'false',
          tabindex: '0'
        }).removeAttr('hidden').find(SlideshowView.TABINDEX_SEL).removeAttr('tabindex');
      }

      /**
       * Handle a click on a navigation item.
       *
       * This will switch to the slide referenced by the navigation item, and
       * disable automatic cycling.
       *
       * Args:
       *     e (jQuery.Event):
       *         The click event.
       */
      _onNavItemClick(e) {
        e.preventDefault();
        e.stopPropagation();
        const index = this.#$navItems.index(e.target);
        if (index !== -1) {
          this.setAutomaticCyclingEnabled(false);
          this.setSlide(index);
        }
      }

      /**
       * Handle a click on the "next" navigation item.
       *
       * This will switch to the next slide, and disable automatic cycling.
       *
       * Args:
       *     e (jQuery.ClickEvent):
       *         The click event.
       */
      _onNextClick(e) {
        e.preventDefault();
        e.stopPropagation();
        this.setAutomaticCyclingEnabled(false);
        this.nextSlide();
      }

      /**
       * Handle a click on the "previous" navigation item.
       *
       * This will switch to the previous slide, and disable automatic cycling.
       *
       * Args:
       *     e (jQuery.ClickEvent):
       *         The click event.
       */
      _onPrevClick(e) {
        e.preventDefault();
        e.stopPropagation();
        this.setAutomaticCyclingEnabled(false);
        this.prevSlide();
      }

      /**
       * Handle keydown events on the slideshow.
       *
       * If Left or Right are pressed, this will navigate to the previous or
       * next slide, respectively.
       *
       * Args:
       *     e (jQuery.Event):
       *         The keydown event.
       *
       * Returns:
       *     boolean:
       *     ``false`` if the key is handled. ``undefined`` otherwise.
       */
      _onKeyDown(e) {
        let handled = true;
        switch (e.key) {
          case 'ArrowLeft':
            this.prevSlide();
            this.#$curNavItem.focus();
            break;
          case 'ArrowRight':
            this.nextSlide();
            this.#$curNavItem.focus();
            break;
          default:
            handled = false;
            break;
        }
        if (handled) {
          return false;
        }
      }

      /**
       * Handle a mouseenter event on the slide.
       *
       * This will pause cycling until the user has moved the mouse away.
       */
      _onSlideMouseEnter() {
        this.unqueueNextSlide();
        this.#cycleAutomaticallyPaused = true;
      }

      /**
       * Handle a mouseleave event on the slide.
       *
       * This will unpause cycling.
       */
      _onSlideMouseLeave() {
        this.#cycleAutomaticallyPaused = false;
        if (this.#cycleAutomaticallyEnabled) {
          this.queueNextSlide();
        }
      }
    }) || _class$1;

    var _class;

    /**
     * Attributes for ContentViewport.
     *
     * Version Added:
     *     6.0
     */

    /**
     * A valid viewport side.
     *
     * Version Added:
     *     6.0
     */

    /**
     * Options for tracking an element.
     *
     * Version Added:
     *     6.0
     */

    /**
     * Tracking data for an element.
     *
     * Version Added:
     *     6.0
     */

    /**
     * Management for the viewport in which content is displayed.
     *
     * This provides functionality for defining and inspecting a viewport in which
     * page content will be shown, minus any docked page elements. This can be used
     * to correctly position and align elements related to the content, and to
     * determine where docked elements reside.
     *
     * Docked elements can be tracked, and any size updates will automatically
     * update the viewport.
     *
     * Consumers can listen for the ``change`` signal on the model or on specific
     * sides (e.g., ``change:left``) to determine any updates on the viewport.
     *
     * It's not recommended to set the viewport sizes manually, as they can end up
     * being reset.
     *
     * There is a single instance site-wide, accessible as ``RB.contentViewport``.
     *
     * Version Added:
     *     6.0
     */
    let ContentViewport = spina.spina(_class = class ContentViewport extends spina.BaseModel {
      static defaults = {
        bottom: 0,
        left: 0,
        right: 0,
        top: 0
      };

      /**********************
       * Instance variables *
       **********************/

      /**
       * A mapping of docked elements to tracking data.
       */
      #tracked = null;

      /**
       * A stored observer for monitoring resizes.
       */
      #_resizeObserver = null;

      /**
       * Clear all tracking state, and reset the viewport.
       */
      clearTracking() {
        const tracked = this.#tracked;
        if (tracked) {
          this.set({
            bottom: 0,
            left: 0,
            right: 0,
            top: 0
          });
          this.#tracked = null;
        }
        if (this.#_resizeObserver) {
          this.#_resizeObserver.disconnect();
          this.#_resizeObserver = null;
        }
      }

      /**
       * Track a docked element.
       *
       * This will adjust the size of the viewport based on the docked
       * element and its specified side, and will keep it updated whenever
       * the element has resized.
       *
       * Args:
       *     options (TrackElementOptions):
       *         Options used to track the element.
       */
      trackElement(options) {
        let tracked = this.#tracked;
        const el = options.el;
        const side = options.side;
        if (tracked === null) {
          tracked = new WeakMap();
          this.#tracked = tracked;
        } else if (tracked.has(el)) {
          return;
        }
        const size = this.#getElementSize(el, side);
        tracked.set(el, {
          lastSize: size,
          side: side
        });
        this.attributes[side] += size;
        this.#resizeObserver.observe(el);
      }

      /**
       * Remove a docked element from tracking.
       *
       * This will remove the size of the element from the viewport area and
       * stop tracking it for resizes.
       *
       * Args:
       *     el (Element):
       *         The element to stop tracking.
       */
      untrackElement(el) {
        if (this.#tracked !== null) {
          const data = this.#tracked.get(el);
          if (data !== undefined) {
            this.attributes[data.side] -= data.lastSize;
            this.#tracked.delete(el);
            this.#resizeObserver.unobserve(el);
          }
        }
      }

      /**
       * Return the ResizeObserver for the class.
       *
       * This is constructed and returned the first time it's accessed.
       * Subsequent calls will return the cached copy.
       *
       * Returns:
       *     ResizeObserver:
       *     The resize observer tracking elements.
       */
      get #resizeObserver() {
        let observer = this.#_resizeObserver;
        if (observer === null) {
          observer = new ResizeObserver(this.#onObserveResize.bind(this));
          this.#_resizeObserver = observer;
        }
        return observer;
      }

      /**
       * Return the size of an element on a given side.
       *
       * Args:
       *     el (Element):
       *         The element to calculate the size for.
       *
       *     side (Side):
       *         The side to calculate.
       *
       *     rect (DOMRect, optional):
       *         An optional pre-computed bounding rectangle for the element.
       *
       * Returns:
       *     number:
       *     The element size for the given side.
       */
      #getElementSize(el, side, rect) {
        if (rect === undefined) {
          rect = el.getBoundingClientRect();
        }
        return side === 'top' || side === 'bottom' ? rect.height : rect.width;
      }

      /**
       * Handle resize events on tracked elements.
       *
       * This will adjust the stored sizes of any sides based on the elements
       * that have resized.
       *
       * Args:
       *     entries (ResizeObserverEntry[]):
       *         The entries that have resized.
       */
      #onObserveResize(entries) {
        const tracked = this.#tracked;
        if (tracked === null) {
          return;
        }
        const attrs = this.attributes;
        const newValues = {};
        for (const entry of entries) {
          const el = entry.target;
          const trackedData = tracked.get(el);
          console.assert(trackedData !== undefined);
          const side = trackedData.side;
          const size = this.#getElementSize(el, side, entry.contentRect);
          newValues[side] = (newValues[side] ?? attrs[side]) - trackedData.lastSize + size;
          trackedData.lastSize = size;
        }
        if (newValues) {
          this.set(newValues);
        }
        this.trigger('handledResize');
      }
    }) || _class;

    /**
     * A singleton for the main content viewport.
     *
     * This will be available to any callers as ``RB.contentViewport``.
     */
    const contentViewport = new ContentViewport();

    exports.CenteredElementManager = CenteredElementManager;
    exports.ContentViewport = ContentViewport;
    exports.DateInlineEditorView = DateInlineEditorView;
    exports.DateTimeInlineEditorView = DateTimeInlineEditorView;
    exports.DnDUploader = DnDUploader;
    exports.FieldStateLabelThemes = FieldStateLabelThemes;
    exports.FieldStateLabelView = FieldStateLabelView;
    exports.FloatingBannerView = FloatingBannerView;
    exports.InlineEditorView = InlineEditorView;
    exports.MenuButtonView = MenuButtonView;
    exports.MenuType = MenuType;
    exports.MenuView = MenuView;
    exports.OverlayView = OverlayView;
    exports.RichTextInlineEditorView = RichTextInlineEditorView;
    exports.SlideshowView = SlideshowView;
    exports.TextEditorView = TextEditorView;
    exports.contentViewport = contentViewport;

    Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

}));
//# sourceMappingURL=index.js.map
