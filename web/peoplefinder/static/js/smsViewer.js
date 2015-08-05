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
        }
    });
}(jQuery, pf));