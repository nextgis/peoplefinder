(function ($, pf) {
    pf.modules.unreadSmsStorage = {};
    $.extend(pf.modules.unreadSmsStorage, {
        _key: 'pf:unreadSms',
        _currentSmsState: '',
        _unreadSms: {'_verify': ''},
        _storage: null,
        _initial: true,
        init: function () {
            this._storage = pf.modules.localStorage.isAvailable() ? pf.modules.localStorage : Cookies;
            this.loadUnreadSmsStorage();
            this.bindEvents();
        },

        loadUnreadSmsStorage: function () {
            var valueFromStorage = this._storage.get(this._key),
                verifiedValue = this.verifyValueFromStorage(valueFromStorage);
            if (verifiedValue) {
                this._unreadSms = verifiedValue;
            } else {
                this.dumpStorage();
            }
        },

        bindEvents: function () {
            var context = this;
            pf.subscriber.subscribe('messages/unread/reset', function (imsi) {
                if (context._unreadSms.hasOwnProperty(imsi)) {
                    context._unreadSms[imsi]._u = 0;
                    pf.modules.imsiTable.updateUnreadSmsCount(imsi, context._unreadSms[imsi]._u);
                    this.dumpStorage();
                }
            });
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

        dumpStorage: function () {
            this._storage.set(this._key, JSON.stringify(this._unreadSms), {expires: 365});
        },

        updateUnreadMessages: function (messagesFromServer) {
            var stringifyMessagesFromServer = JSON.stringify(messagesFromServer),
                smsChanged = this.smsChanged(stringifyMessagesFromServer);

            if (this._initial) {
                this.updateUnreadSmsFromStorage();
                this._initial = false;
            }

            if (smsChanged) {
                this.handleSmsCountChanged(messagesFromServer);
                this._currentSmsState = stringifyMessagesFromServer;
                this.dumpStorage();
            }
        },

        handleSmsCountChanged: function (messagesFromServer) {
            var context = this,
                imsiTable = pf.modules.imsiTable,
                unreadSmsChangedImsi = [],
                imsiFromServer = {},
                imsi,
                messageServerCount,
                unreadSmsItem,
                unreadCount,
                allCount;
            $.each(messagesFromServer, function (i, serverMessageItem) {
                imsi = serverMessageItem.imsi;
                messageServerCount = serverMessageItem.count;
                if (context._unreadSms.hasOwnProperty(imsi)) {
                    unreadSmsItem = context._unreadSms[imsi];
                    if (imsi === pf.viewmodel.selectedImsi) {
                        unreadSmsItem._a = messageServerCount;
                    }
                    allCount = unreadSmsItem._a;
                    unreadCount = unreadSmsItem._u;
                    unreadSmsItem._a = messageServerCount;
                    imsiFromServer[imsi] = true;
                    if (allCount == messageServerCount) {
                        return false;
                    } else if (messageServerCount > allCount) {
                        unreadSmsItem._u = messageServerCount - allCount + unreadCount;
                        unreadSmsChangedImsi.push(imsi);
                        return false;
                    } else if (messageServerCount < allCount) {
                        unreadSmsItem._u = 0;
                        unreadSmsChangedImsi.push(imsi);
                        return false;
                    }
                } else {
                    context._unreadSms[imsi] = {
                        _u: 0,
                        _a: messageServerCount
                    };
                    imsiFromServer[imsi] = true;
                }
            });

            $.each(unreadSmsChangedImsi, function (i, imsi) {
                imsiTable.updateUnreadSmsCount(imsi, context._unreadSms[imsi]._u);
            });

            $.each(imsiFromServer, function (imsi) {

            });
        },

        updateUnreadSmsFromStorage: function () {
            var imsiTable = pf.modules.imsiTable;

            $.each(this._unreadSms, function (imsi, messagesItem) {
                if (imsi === '_verified') return false;
                imsiTable.updateUnreadSmsCount(imsi, messagesItem._u);
            });
        },

        smsChanged: function (stringifyMessagesFromServer) {
            return stringifyMessagesFromServer !== this._currentSmsState;
        }
    });
}(jQuery, pf));