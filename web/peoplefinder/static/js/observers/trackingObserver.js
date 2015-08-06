(function ($, pf, L) {
    pf.modules.trackingObserver = {};
    $.extend(pf.modules.trackingObserver, {

        _circles: null,

        init: function () {
            pf.viewmodel.trackingActive = false;
            this.bindEvents();
        },

        bindEvents: function () {
            var context = this;

            pf.subscriber.subscribe('observer/tracking/toggle', function () {
                pf.viewmodel.trackingActive = !pf.viewmodel.trackingActive;
                if (pf.viewmodel.trackingActive) {
                    pf.modules.circlesLayer.clearAll();
                    context.updateCircles();
                }
            }, this);
        },

        updateCircles: function (timestamp_begin) {
            if (!pf.viewmodel.trackingActive) return false;

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
                url: pf.settings.root_url + '/imsi/' + selectedImsi +'/circles',
                data: params,
                dataType: 'json'
            }).done(function (result) {
                pf.modules.circlesLayer.addCircles(result.circles);
                setTimeout(function () {
                    if (selectedImsi === pf.viewmodel.selectedImsi) {
                        context.updateCircles(context._timestamp_end);
                    }
                }, pf.settings.tracking_timeout);
            });
        }
    });
}(jQuery, pf, L));