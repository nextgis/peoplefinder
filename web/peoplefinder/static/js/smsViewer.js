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
        },

        addSms: function (imsi, smsItem) {
            var $smsItem = $('<div class="' + smsItem.type + ' sms">' + smsItem.type + ': ' + smsItem.text + '</div>');
            $smsItem.prependTo(pf.view.$smsViewer);
        }
    });
}(jQuery, pf));