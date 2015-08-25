(function ($, pf) {
    pf.modules.smsSender = {};
    $.extend(pf.modules.smsSender, {

        init: function () {
            this.setDom();
            this.bindEvents();
        },

        setDom: function () {
            pf.view.$smsSenderMessage = $('#smsSenderMessage');
            pf.view.$sendSms = $('#sendSms');
        },

        bindEvents: function () {
            var context = this,
                viemodel = pf.viewmodel,
                view = pf.view;

            view.$sendSms.click(function () {
                var $smsSenderMessage = view.$smsSenderMessage,
                    smsText = $smsSenderMessage.val();
                context.sendSms(viemodel.selectedImsi, smsText);
                $smsSenderMessage.val('');
            });

            view.$smsSenderMessage.keypress(function (e) {
                if (e.which !== 13) return;
                var $smsSenderMessage = view.$smsSenderMessage,
                    smsText = $smsSenderMessage.val();
                context.sendSms(viemodel.selectedImsi, smsText);

            });
        },

        sendSms: function (imsi, text) {
            if (text.length = 0 || !imsi) {
                return false;
            }

            $.ajax({
                url: pf.settings.root_url + '/imsi/' + imsi + '/message',
                data: text,
                method: 'POST'
            }).done(function () {
                $smsSenderMessage.val('');
            }, function () {

            });
        }
    });
}(jQuery, pf));