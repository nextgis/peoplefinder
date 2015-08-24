(function ($, pf) {
    pf.modules.smsViewer = {};
    $.extend(pf.modules.smsViewer, {

        init: function () {
            this.setDom();
        },

        setDom: function () {
            pf.view.$smsViewer = $('#smsViewer');
        },

        clear: function () {
            pf.view.$smsViewer.find('div.sms').remove();
            this._smsItems = {};
        },

        _smsItems: {},
        addSms: function (imsi, smsItem) {
            var cssClasses = ['sms'],
                isOutgoing = (smsItem.type === 'to'),
                $smsItem;

            cssClasses.push(smsItem.type);

            if (!this._smsItems.hasOwnProperty(smsItem.id)) {
                if (isOutgoing && smsItem.sent === false) { cssClasses.push('unsent'); }
                $smsItem = $('<div id="sms-' + smsItem.id + '" class="' + cssClasses.join(' ') + '">'
                    + smsItem.type + ': ' + smsItem.text + '</div>');
                $smsItem.prependTo(pf.view.$smsViewer);
                this._smsItems[smsItem.id] = !isOutgoing || (isOutgoing && smsItem.sent);
            } else if (!this._smsItems[smsItem.id] && isOutgoing && smsItem.sent) {
                $('#sms-' + smsItem.id).removeClass('unsent');
                this._smsItems[smsItem.id] = true;
            }
        }
    });
}(jQuery, pf));