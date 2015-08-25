(function ($, pf) {
    pf.modules.unreadSmsStorage = {};
    $.extend(pf.modules.unreadSmsStorage, {
        _key: 'pf:unreadSms',
        _currentSmsState: null,
        _unreadSms: {'_verify': ''},
        _storage: null,
        init: function () {
            this._storage = pf.modules.localStorage.isAvailable() ? pf.modules.localStorage : Cookies;
            this.createUnreadSmsStorage();
        },

        loadUnreadSmsStorage: function () {
            var valueFromStorage = this._storage.get(this._key),
                verifiedValue = this.verifyValueFromStorage(valueFromStorage);

            if (verifiedValue) {
                this._unreadSms = verifiedValue;
            } else {
                this.initStorage();
            }
        },

        verifyValueFromStorage: function (valueFromStorage) {
            var jsonStorage = null,
                valueVerified = false;

            try {
                jsonStorage = JSON.parse(valueFromStorage);
                if (jsonStorage.hasOwnProperty('_verify')) {
                    valueVerified = true;
                }
            } catch (e) {
                console.log('_unreadSms parsing is failed');
            }

            return valueVerified ? jsonStorage : false;
        },

        initStorage: function () {
            this._storage.set(this._key, this._unreadSms, {expires: 365});
        },

        updateUnreadMessages: function (messagesFromServer) {

        },

        saveMessagesCount: function (messagesSmsObj) {
            var readToWriteObj,
                stringifySmsObj;
            if (messagesSmsObj) {
                readToWriteObj = $.extend({'_verify': ''}, messagesSmsObj);
            } else {
                readToWriteObj = {'_verify': ''};
            }

            stringifySmsObj = JSON.stringify(readToWriteObj);
            this._unreadSms = stringifySmsObj;
            this._storage.set(this._key, stringifySmsObj, {expires: 365});
        },

        smsChanged: function (smsObj) {
            var smsChanged = JSON.stringify(smsObj) !== this._currentSmsState;
            if (smsChanged) {
                this._currentSmsState = JSON.stringify(smsObj);
            }
            return smsChanged;
        }
    });
}(jQuery, pf));