(function ($, pf) {
    pf.modules.imsiListObserver = {};
    $.extend(pf.modules.imsiListObserver, {

        imsiList: {},

        init: function () {
            this.bindEvents();
        },

        bindEvents: function () {
            var timeout = pf.settings.imsi_list_timeout;
            pf.subscriber.subscribe('observer/imsi/list/activate', function () {
                this.updateIsmiList();
            }, this);
        },

        updateIsmiList: function () {
            var context = this;
            $.ajax({
                url: pf.settings.root_url + '/imsi/list',
                dataType: 'json'
            }).done(function (result) {
                var records = result.Records,
                    imsiTable = pf.viewmodel.imsiTable,
                    imsi;
                $.each(records, function (i, record) {
                    imsi = record.imsi;
                    if (context.imsiList.hasOwnProperty(imsi)) {
                        if (context.imsiList[imsi].last_lur != record.last_lur) {
                            $('#imsi-lur-' + imsi).html(record.last_lur);
                        }
                    } else {
                        context.imsiList[imsi] = record;
                        imsiTable.addRecord({
                            record: record,
                            clientOnly : true
                        });
                    }
                });
                setTimeout(function () {
                    context.updateIsmiList();
                }, pf.settings.imsi_list_timeout);
            });
        }
    });
}(jQuery, pf));