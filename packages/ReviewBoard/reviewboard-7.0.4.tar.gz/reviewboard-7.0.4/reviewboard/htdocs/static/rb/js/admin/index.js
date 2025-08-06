(function (global, factory) {
    typeof exports === 'object' && typeof module !== 'undefined' ? factory(exports, require('@beanbag/spina')) :
    typeof define === 'function' && define.amd ? define(['exports', '@beanbag/spina'], factory) :
    (global = typeof globalThis !== 'undefined' ? globalThis : global || self, factory(global.RB = global.RB || {}, global.Spina));
})(this, (function (exports, spina) { 'use strict';

    var _class;

    /**
     * The base page view class for admin UI pages.
     */
    let BaseAdminPageView = spina.spina(_class = class BaseAdminPageView extends RB.PageView {}) || _class;

    const Admin = {
      PageView: BaseAdminPageView
    };

    exports.Admin = Admin;
    exports.BaseAdminPageView = BaseAdminPageView;

    Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });

}));
//# sourceMappingURL=index.js.map
