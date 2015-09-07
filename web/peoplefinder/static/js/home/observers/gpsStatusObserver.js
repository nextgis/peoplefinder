(function ($, pf) {
    pf.modules.gpsStatusObserver = {};
    $.extend(pf.modules.gpsStatusObserver, {

        $gpsStatus: null,
        _currentStatus: null,

        init: function () {
            this.setDOM();
            this.bindEvents();
        },

        setDOM: function () {
            this.$gpsStatus = $('#gpsStatus');
        },

        bindEvents: function () {
            var context = this;
            pf.subscriber.subscribe('observer/gps/status', function (gpsStatus) {
                if (gpsStatus === context._currentStatus) return;

                switch (gpsStatus) {
                    case 'yes':
                        context.$gpsStatus.prop('class', '').html('GPS on').prop('title', 'GPS is on');
                        break;
                    case 'no':
                        context.$gpsStatus.prop('class', 'no').html('GPS off').prop('title', 'GPS is off');
                        break;
                    case 'failed':
                        context.$gpsStatus.prop('class', 'failed').html('GPS unreachable').prop('title', 'GPS is unreachable');
                        break;
                }

                context._currentStatus = gpsStatus;
            }, this);
        }
    });
}(jQuery, pf));