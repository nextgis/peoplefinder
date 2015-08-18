(function ($, pf) {
    pf.modules.imsiTracking = {};
    $.extend(pf.modules.imsiTracking, {

        init: function () {
            this.setDom();
            this.bindEvents();
        },

        setDom: function () {
            pf.view.$targetImsi = $('#imsi-input');
            pf.view.$trackingButton = $('#trackingButton');
        },

        _buttonText: [
            'Start Tracking',
            'Stop Tracking'
        ],
        _waitButtonText: [
            'Starting...',
            'Stopping...'
        ],
        _actionUrl: [
            '/tracking/start',
            '/tracking/stop'
        ],
        _buttonCss: [
            'start',
            'stop'
        ],
        _buttonState: 0,

        bindEvents: function () {
            pf.view.$trackingButton.click(this.trackingButtonClickHandler);
        },

        trackingButtonClickHandler: function () {
        }
    });
}(jQuery, pf));