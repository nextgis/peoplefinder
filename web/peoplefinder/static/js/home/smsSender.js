(function ($, pf) {
    pf.modules.smsSender = {};
    $.extend(pf.modules.smsSender, {

        $smsSenderMessage: null,
        $sendSms: null,

        init: function () {
            this.setDom();
            this.bindEvents();
        },

        setDom: function () {
            this.$smsSenderMessage = $('#smsSenderMessage');
            this.$sendSms = $('#sendSms');
        },

        bindEvents: function () {
            var context = this,
                viemodel = pf.viewmodel,
                view = pf.view;

            this.$sendSms.click(function () {
                var $smsSenderMessage = context.$smsSenderMessage,
                    smsText = $smsSenderMessage.val();
                context.sendSms(viemodel.selectedImsi, smsText);
            });

            this.$smsSenderMessage.keypress(function (e) {
                if (e.which !== 13) return;
                var $smsSenderMessage = context.$smsSenderMessage,
                    smsText = $smsSenderMessage.val();
                context.sendSms(viemodel.selectedImsi, smsText);
            });
        },

        sendSms: function (imsi, text) {
            if (text.length = 0 || !imsi) {
                return false;
            }

            var context = this;
            this.disableControls();

            $.ajax({
                url: pf.settings.root_url + '/imsi/' + imsi + '/message',
                data: text,
                method: 'POST'
            }).done(function (result) {
                if (result.status === 'failed') {
                    alert("You can't send the message at this moment.");
                    context.activateControls();
                } else {
                    context.activateControls();
                    context.$smsSenderMessage.val('');
                }
            }).fail(function () {
                alert("You can't send the message at this moment.");
                context.activateControls();
            });
        },

        disableControls: function () {
            this.$sendSms.prop('disabled', true);
            this.$smsSenderMessage.prop('disabled', true);
        },

        activateControls: function () {
            this.$sendSms.prop('disabled', false);
            this.$smsSenderMessage.prop('disabled', false);
        }
    });
}(jQuery, pf));