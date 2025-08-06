import {
    type MenuView,
    MenuItemType,
    MenuItemsCollection,
    craft,
    renderInto,
} from '@beanbag/ink';
import {
    type EventsHash,
    spina,
} from '@beanbag/spina';

import { type MenuAction } from '../models/menuActionModel';
import { ActionView } from './actionView';


/**
 * Base class for menu actions.
 *
 * Version Added:
 *     6.0
 */
@spina
export class MenuActionView<
    TModel extends MenuAction = MenuAction,
    TElement extends HTMLDivElement = HTMLDivElement,
    TExtraViewOptions extends object = object
> extends ActionView<TModel, TElement, TExtraViewOptions> {
    static events: EventsHash = {
        'focusout': 'onFocusOut',
        'keydown': 'onKeyDown',
        'mouseenter': 'openMenu',
        'mouseleave': 'closeMenu',
        'touchstart': 'onTouchStart',
    };

    /**********************
     * Instance variables *
     **********************/

    /** The menu view. */
    menu: MenuView;

    /**
     * Render the view.
     */
    protected onInitialRender() {
        const menuItems = new MenuItemsCollection();
        const page = RB.PageManager.getPage();

        for (const childId of this.model.get('children')) {
            if (childId === '--') {
                menuItems.add({
                    type: MenuItemType.SEPARATOR,
                });
            } else {
                const childActionView = page.getActionView(childId);

                if (childActionView) {
                    const childAction = childActionView.model;
                    const visible = childAction.get('visible');
                    const domID = childAction.get('domID');

                    const onClick =
                        childActionView['activate']
                        ? () => childActionView.activate()
                        : null;

                    if (childAction.get('isCustomRendered')) {
                        menuItems.add({
                            childEl: childActionView.el,
                            id: domID,
                            onClick: onClick,
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
                            url: url,
                        });

                        /* Update the menu item when these change. */
                        this.listenTo(
                            childAction,
                            'change:iconClass',
                            (model, newIconClass) => {
                                menuItem.set('iconName', newIconClass);
                            });

                        this.listenTo(
                            childAction,
                            'change:label',
                            (model, newLabel) => {
                                menuItem.set('label', newLabel);
                            });

                        this.listenTo(
                            childAction,
                            'change:url',
                            (model, newURL) => {
                                menuItem.set('url', newURL);
                            });
                    }
                } else {
                    console.error('Unable to find action for %s', childId);
                }
            }
        }

        this.menu = craft<MenuView>`
            <Ink.Menu controllerEl=${this.el}
                      menuItems=${menuItems}/>
        `;
        renderInto(this.el, this.menu);

        this.listenTo(this.menu, 'opening', this.positionMenu.bind(this));
    }

    /**
     * Open the menu.
     */
    protected openMenu() {
        if (!this.menu.menuItems.isEmpty()) {
            this.menu.open({ animate: true });
        }
    }

    /**
     * Close the menu.
     */
    protected closeMenu() {
        if (!this.menu.menuItems.isEmpty()) {
            this.menu.close({ animate: true });
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
    protected positionMenu() {
        const $menuEl = this.menu.$el;
        const menuWidth = $menuEl.width();
        const windowWidth = $(window).width();
        const elOffsetLeft = this.$el.offset().left;

        let newMenuLeft: string | number = 'auto';

        if (elOffsetLeft + menuWidth > windowWidth) {
            /*
             * The right side of the menu is being clipped. Move to the left
             * so that the full menu fits on screen.
             */
            newMenuLeft = (
                windowWidth -
                (elOffsetLeft + Math.min(menuWidth, windowWidth))
            );
        }

        $menuEl.css({
            left: newMenuLeft,
            'max-width': windowWidth,
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
    protected onFocusOut(evt: FocusEvent) {
        evt.stopPropagation();

        /*
         * Only close the menu if the focus has moved to something outside of
         * this component.
         */
        const currentTarget = <Element>evt.currentTarget;

        if (!currentTarget.contains(<Element>evt.relatedTarget)) {
            this.menu.close({
                animate: false,
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
    protected onKeyDown(evt: KeyboardEvent) {
        if (evt.key === ' ' ||
            evt.key === 'ArrowDown' ||
            evt.key === 'ArrowUp' ||
            evt.key === 'Enter') {
            /* Open the menu and select the first item. */
            evt.stopPropagation();
            evt.preventDefault();

            this.menu.open({
                animate: false,
                currentItemIndex: 0,
            });
        } else if (evt.key === 'Escape') {
            /* Close the menu. */
            evt.stopPropagation();
            evt.preventDefault();

            this.menu.close({
                animate: false,
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
    protected onTouchStart(e: TouchEvent) {
        const $target = $(e.target);

        if (!($target.hasClass('.ink-c-menu__item') ||
              $target.parents('.ink-c-menu__item').length)) {
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
}


/**
 * Base class for an action within a menu.
 *
 * This handles event registration for the click and touch events in order to
 * behave properly on both desktop and mobile.
 *
 * Version Added:
 *     6.0
 */
@spina
export class MenuItemActionView extends ActionView {
    static events: EventsHash = {
        'click': '_onClick',
        'touchstart': '_onTouchStart',
    };

    /**
     * Handle a click event.
     *
     * Args:
     *     e (MouseEvent):
     *         The event.
     */
    protected _onClick(e: MouseEvent) {
        e.stopPropagation();
        e.preventDefault();

        this.activate();
    }

    /**
     * Handle a touchstart event.
     */
    protected _onTouchStart() {
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
}
