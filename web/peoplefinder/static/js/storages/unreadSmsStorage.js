(function ($, pf) {
    pf.modules.unreadSmsStorage = {};
    $.extend(pf.modules.unreadSmsStorage, {
        _key: 'pf:unreadSms',
        _unreadSms: {'_verify': ''},
        _storage: null,
        init: function () {
            this._storage = this._localStorageAvailable() ? pf.modules.localStorage : Cookies;
            this.createUnreadSmsStorage();
        },

        createUnreadSmsStorage: function () {
            var valueFromStorage = this._storage.get(this._key),
                verifiedValue = this.verifyValueFromStorage(valueFromStorage);

            if (verifiedValue) {
                return verifiedValue;
            } else {
                this.saveMessagesCount(null);
            }
        },

        verifyValueFromStorage: function (valueFromStorage) {
            var jsonStorage = null,
                valueVerified = false;

            try {
                jsonStorage = toString.call(valueFromStorage) == '[object String]' ?
                    JSON.parse(valueFromStorage) :
                    valueFromStorage;
                if (jsonStorage.hasOwnProperty('_verify')) {
                    valueVerified = true;
                }
            } catch (e) {
                console.log('_unreadSms parsing is failed');
            }

            return valueVerified ? jsonStorage : false;
        },

        saveMessagesCount: function (messagesSmsObj) {
            var readToWriteObj;
            if (messagesSmsObj) {
                readToWriteObj = $.extend({'_verify': ''}, messagesSmsObj);
            } else {
                readToWriteObj = {'_verify': ''};
            }

            this._unreadSms = readToWriteObj;
            this._storage.set(this._key, JSON.stringify(readToWriteObj), {expires: 365});
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