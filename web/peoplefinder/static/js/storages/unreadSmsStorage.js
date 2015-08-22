(function ($, pf) {
    pf.modules.unreadSmsStorage = {};
    $.extend(pf.modules.unreadSmsStorage, {
        _key: 'pf.unreadSms',
        _unreadSms: {},
        _storage: null,
        init: function () {
            this._storage = this._localStorageAvailable() ? $.localStorage : $.cookieStorage;
        },

        _localStorageAvailable: function () {
            var test = 'pf.test';
            try {
                localStorage.setItem(test, test);
                localStorage.removeItem(test);
                return true;
            } catch (e) {
                return false;
            }
        }
    });
}(jQuery, pf));