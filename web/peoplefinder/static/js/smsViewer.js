(function ($, pf) {
    pf.modules.smsViewer = {};
    $.extend(pf.modules.smsViewer, {

        init: function () {
            this.setDom();
        },

        setDom: function () {
            pf.view.$smsViewer = $('#smsViewer');
        },

        clear: function () {
            pf.view.$smsViewer.find('div.sms').remove();
            this._smsItems = {};
        },

        _smsItems: {},
        addSms: function (imsi, smsItem) {
            var cssClasses = ['sms'],
                $smsItem;

            cssClasses.push(smsItem.type);

            if (!smsItem.sent) {
                cssClasses.push('unsent');
            }

            $smsItem = $('<div id="sms-' + smsItem.id + '" class="' + cssClasses.join(' ') + '">' + smsItem.type + ': ' + smsItem.text + '</div>');
            $smsItem.prependTo(pf.view.$smsViewer);
        }
    });
}(jQuery, pf));