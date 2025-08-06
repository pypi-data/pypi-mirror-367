"use strict";

suite('rb/ui/views/MenuButtonView', function () {
  describe('Rendering', function () {
    it('With primary button', function () {
      const view = new RB.MenuButtonView({
        ariaMenuLabel: 'Test ARIA label',
        menuItems: [{
          text: 'Item 1'
        }, {
          text: 'Item 2'
        }, {
          text: 'Item 3'
        }],
        onPrimaryButtonClick: () => {},
        text: 'Button label'
      });
      view.render();
      expect(view.el).toHaveClass('rb-c-menu-button');
      expect(view.$el.attr('role')).toBe('group');
      expect(view.$primaryButton.length).toBe(1);
      const $primaryButton = view.$('.rb-c-menu-button__primary');
      expect($primaryButton.length).toBe(1);
      const $toggleButton = view.$('.rb-c-menu-button__toggle');
      expect($toggleButton.length).toBe(1);
      expect($toggleButton[0].id).toBe(view.menu.$el.attr('aria-labelledby'));
      expect($toggleButton.attr('aria-label')).toBe('Test ARIA label');
      expect($toggleButton.children()[0]).toHaveClass('rb-icon-dropdown-arrow');
      expect(view.menu.el.children.length).toBe(3);
    });
    it('Without primary button', function () {
      const view = new RB.MenuButtonView({
        ariaMenuLabel: 'Test ARIA label',
        menuItems: [{
          text: 'Item 1'
        }, {
          text: 'Item 2'
        }],
        text: 'Button label'
      });
      view.render();
      expect(view.el).toHaveClass('rb-c-menu-button');
      expect(view.$el.attr('role')).toBe('group');
      expect(view.$primaryButton).toBeNull();
      const $primaryButton = view.$('.rb-c-menu-button__primary');
      expect($primaryButton.length).toBe(0);
      const $toggleButton = view.$('.rb-c-menu-button__toggle');
      expect($toggleButton.length).toBe(1);
      expect($toggleButton[0].id).toBe(view.menu.$el.attr('aria-labelledby'));
      expect($toggleButton.attr('aria-label')).toBeUndefined();
      expect($toggleButton.text().trim()).toBe('Button label');
      expect($toggleButton.children()[0]).toHaveClass('rb-icon-dropdown-arrow');
      expect(view.menu.el.children.length).toBe(2);
    });
  });
  describe('Events', function () {
    let view;
    function sendDropDownButtonEvent(name, options) {
      const evt = $.Event(name, options);
      view.$('.rb-c-menu-button__toggle').trigger(evt);
      return evt;
    }
    function sendKeyDown(keyCode) {
      sendDropDownButtonEvent('keydown', {
        key: keyCode
      });
    }
    beforeEach(function () {
      view = new RB.MenuButtonView({
        text: 'Text'
      });
      view.render();

      /* Don't let this override any state we set. */
      spyOn(view, 'updateMenuPosition');
    });
    describe('keydown', function () {
      function openMenuTests(keyCode) {
        it('With openDirection=up', function () {
          view.openDirection = 'up';
          spyOn(view.menu, 'focusLastItem');
          sendKeyDown(keyCode);
          expect(view.menu.isOpen).toBeTrue();
          expect(view.menu.focusLastItem).toHaveBeenCalled();
        });
        it('With openDirection=down', function () {
          view.openDirection = 'down';
          spyOn(view.menu, 'focusFirstItem');
          sendKeyDown(keyCode);
          expect(view.menu.isOpen).toBeTrue();
          expect(view.menu.focusFirstItem).toHaveBeenCalled();
        });
      }
      describe('Return key opens menu', function () {
        openMenuTests('Enter');
      });
      describe('Space key opens menu', function () {
        openMenuTests(' ');
      });
      describe('Down key opens menu', function () {
        openMenuTests('ArrowDown');
      });
      describe('Up key opens menu', function () {
        openMenuTests('ArrowUp');
      });
      it('Escape key closes menu', function () {
        view.menu.open({
          animate: false
        });
        expect(view.menu.isOpen).toBeTrue();
        sendKeyDown('Escape');
        expect(view.menu.isOpen).toBeFalse();
      });
    });
    it('focusout closes menu', function () {
      view.menu.open({
        animate: false
      });
      expect(view.menu.isOpen).toBeTrue();
      sendDropDownButtonEvent('focusout', {
        relatedTarget: $testsScratch[0]
      });
      expect(view.menu.isOpen).toBeFalse();
    });
    it('clicking the toggle stops event propagation', function () {
      const evt = sendDropDownButtonEvent('click');
      expect(evt.isPropagationStopped()).toBeTrue();
    });
  });
});

//# sourceMappingURL=menuButtonViewTests.js.map