(function ($, pf) {
    pf.modules.imsiTracking = {};
    $.extend(pf.modules.imsiTracking, {

        init: function () {
            this.setDom();
            this.bindEvents();
        },

        $trackingButton: null,
        setDom: function () {
            this.$trackingButton = $('#trackingButton');
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
            this.$trackingButton.on('click', $.proxy(this.trackingButtonClickHandler, this));
        },

        unbindTrackingButtonClick: function () {
            this.$trackingButton.off('click', $.proxy(this.trackingButtonClickHandler, this));
        },

        trackingButtonClickHandler: function () {
            var currentButtonState = this._buttonState;
            this.$trackingButton
                .addClass('wait')
                .text(this._waitButtonText[currentButtonState]);
        }
    });
}(jQuery, pf));