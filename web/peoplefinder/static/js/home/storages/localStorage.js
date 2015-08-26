(function ($, pf) {
    pf.modules.localStorage = {};
    $.extend(pf.modules.localStorage, {
        get: function (key) {
            return localStorage.getItem(key);
        },

        getJson: function (key) {
            return JSON.parse(localStorage.getItem(key));
        },

        set: function (key, value) {
             if (typeof value === 'object') {
                localStorage.setItem(key, JSON.stringify(isObj));
            } else {
                localStorage.setItem(key, value);
            }
        },

        isAvailable: function () {
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