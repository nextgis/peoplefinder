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
        _buttonCss: [
            'start',
            'stop'
        ],
        _buttonState: 0,

        bindEvents: function () {
            var context = this;
            pf.view.$trackingButton.click(function () {
                if (!pf.viewmodel.selectedImsi) return false;
                pf.subscriber.publish('observer/tracking/toggle');
                var newButtonState = context._buttonState === 0 ? 1 : 0;
                pf.view.$trackingButton.val(context._buttonText[newButtonState]);
                pf.view.$trackingButton
                    .removeClass(context._buttonCss[context._buttonState])
                    .addClass(context._buttonCss[newButtonState])
                    .text(context._buttonText[newButtonState]);
                context._buttonState = newButtonState;
            });
        }
    });
}(jQuery, pf));