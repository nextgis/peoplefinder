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
                $smsItem,
                html;

            cssClasses.push(smsItem.type);

            if (!this._smsItems.hasOwnProperty(smsItem.id)) {
                if (isOutgoing && smsItem.sent === false) {
                    cssClasses.push('unsent');
                }

                html = '<div id="sms-' + smsItem.id + '" class="' + cssClasses.join(' ') + '">';

                html += (smsItem.type === 'to' ? 'To' : 'From ');

                if (smsItem.type === 'from') {
                    if (smsItem.dest) {
                        html += smsItem.dest;
                    } else if (smsItem.dest === null) {
                        html += 'xx';
                    }
                }

                html += ' (' + smsItem.ts + '):<br/><span>' + smsItem.text + '</span></div>';

                $smsItem = $(html);

                $smsItem.prependTo(pf.view.$smsViewer);

                this._smsItems[smsItem.id] = !isOutgoing || (isOutgoing && smsItem.sent);

            } else if (!this._smsItems[smsItem.id] && isOutgoing && smsItem.sent) {
                $('#sms-' + smsItem.id).removeClass('unsent');
                this._smsItems[smsItem.id] = true;
            }
        }
    });
}(jQuery, pf));