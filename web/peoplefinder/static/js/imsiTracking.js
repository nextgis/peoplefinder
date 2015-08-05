(function ($, pf) {
    pf.modules.imsiTracking = {};
    $.extend(pf.modules.imsiTracking, {

        init: function () {
            pf.viewmodel.trackingStateActive = false;
            this.setDom();
        },

        setDom: function () {
            pf.view.$targetImsi = $('#imsi-input');
        }
    });
}(jQuery, pf));