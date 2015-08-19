(function ($, pf) {
    pf.modules.selectedImsiObserver = {};
    $.extend(pf.modules.selectedImsiObserver, {

        init: function () {
            pf.viewmodel.selectedImsi = null;
            this.bindEvents();
        },

        bindEvents: function () {
            var vm = pf.viewmodel;
            pf.subscriber.subscribe('imsi/selected/set', function (imsi) {
                vm.selectedImsi = imsi;
                pf.subscriber.publish('observer/sms/list/deactivate');
                pf.subscriber.publish('observer/sms/list/activate');
                pf.subscriber.publish('observer/circles/update');
            });
        }
    });
}(jQuery, pf));