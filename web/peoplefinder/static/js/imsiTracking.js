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
            var currentButtonState = this._buttonState,
                runActionTracking;

            this.unbindTrackingButtonClick();
            this.$trackingButton
                .addClass('wait')
                .text(this._waitButtonText[currentButtonState]);

            runActionTracking = $.ajax({
                url: pf.settings.root_url + this._actionUrl[currentButtonState],
                dataType: 'json'
            });

            runActionTracking.done($.proxy(this.setNewState, this));
            runActionTracking.fail($.proxy(this.failRunActionTracking, this));
        },

        setNewState: function () {
            var currentButtonState = this._buttonState,
                newButtonState = (currentButtonState === 0 ? 1 : 0);

            this.$trackingButton
                .removeClass('wait ' + this._buttonCss[currentButtonState])
                .addClass(this._buttonCss[newButtonState])
                .text(this._buttonText[newButtonState]);
            this._buttonState = newButtonState;
            this.bindTrackingButtonClick();
        },

        failRunActionTracking: function (jqXHR) {
            this.$trackingButton
                .removeClass('wait')
                .text(this._buttonText[this._buttonState]);
            console.log(jqXHR);
            this.bindTrackingButtonClick();
        }
    });
}(jQuery, pf));