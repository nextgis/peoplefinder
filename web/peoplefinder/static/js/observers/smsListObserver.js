(function ($, pf) {
    pf.modules.smsListObserver = {};
    $.extend(pf.modules.smsListObserver, {
        init: function () {
            this.bindEvents();
        },

        _isActivated: false,
        _timestamp_end: null,

        bindEvents: function () {
            var timeout = pf.settings.imsi_list_timeout;
            pf.subscriber.subscribe('observer/sms/list/activate', function () {
                this._isActivated = true;
                this.updateSmsList();
            }, this);

            pf.subscriber.subscribe('observer/sms/list/deactivate', function () {
                this._isActivated = false;
                pf.modules.smsViewer.clear();
            }, this);
        },

        updateSmsList: function (timestamp_begin) {
            if (!this._isActivated) return false;

            this._timestamp_end = new Date().getTime();

            var context = this,
                selectedImsi = pf.viewmodel.selectedImsi,
                params = {
                    timestamp_end: this._timestamp_end
                };

            if (timestamp_begin) {
                params['timestamp_begin'] = timestamp_begin;
            }

            $.ajax({
                url: pf.settings.root_url + '/imsi/' + selectedImsi +'/messages',
                data: params,
                dataType: 'json'
            }).done(function (result) {
                var sms = result.sms,
                    imsi = result.imsi;
                $.each(sms, function (i, smsItem) {
                    var $smsItem = $('<div class"' + smsItem.type + '">' + smsItem.type + ' ' + imsi + ': ' + smsItem.text + '</div>');
                    $smsItem.appendTo(pf.view.$smsViewer);
                });
                setTimeout(function () {
                    if (selectedImsi === pf.viewmodel.selectedImsi) {
                        context.updateSmsList(context._timestamp_end);
                    }
                }, pf.settings.imsi_list_timeout);
            });
        }
    });
}(jQuery, pf));