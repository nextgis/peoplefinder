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
            this.bindTrackingButtonClick();
        },

        bindTrackingButtonClick: function () {
            pf.view.$trackingButton.on('click', $.proxy(this.trackingButtonClickHandler, this));
        },

        unbindTrackingButtonClick: function () {
            pf.view.$trackingButton.off('click', $.proxy(this.trackingButtonClickHandler, this));
        },

        trackingButtonClickHandler: function () {
            var currentButtonState = this._buttonState;
            pf.view.$trackingButton
                .addClass('wait')
                .text(this._waitButtonText[currentButtonState]);
        }
    });
}(jQuery, pf));