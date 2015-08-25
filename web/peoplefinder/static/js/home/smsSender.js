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
                view = pf.view;
            view.$sendSms.click(function () {
                var smsText = view.$smsSenderMessage.val();
                if (smsText.length > 0) {
                    context.sendSms(pf.viewmodel.selectedImsi, smsText);
                    view.$smsSenderMessage.val('');
                }
            });
        },

        sendSms: function (imsi, text) {
            $.ajax({
                url: pf.settings.root_url + '/imsi/' + imsi + '/message',
                data: text,
                method: 'POST'
            }).done(function () {

            });
        }
    });
}(jQuery, pf));