(function ($, pf) {
    pf.modules.imsiTable = {};
    $.extend(pf.modules.imsiTable, {

        _imsiTable: null,
        _imsiList: {},

        init: function () {
            this.setDom();
            this.buildTable();
            this.overwriteJTableMethods();

        },

        setDom: function () {
            pf.view.$imsiTable = $('#imsiTable');
        },

        buildTable: function () {
            pf.view.$imsiTable.jtable({
                actions: {
                    listAction: pf.settings.root_url + '/imsi/list'
                },
                ajaxSettings: {
                    type: 'GET',
                    dataType: 'json'
                },
                selectionChanged: function (event, data) {
                    var $selectedRows = $(this).jtable('selectedRows'),
                        imsiSelected;
                    if ($selectedRows.length > 0) {
                        imsiSelected = $selectedRows.find('span').attr('id').split('-')[1];
                        pf.subscriber.publish('imsi/selected/set', [imsiSelected]);
                    }
                },
                selecting: true,
                multiselect: false,
                fields: {
                    imsi: {
                        title: 'IMSI',
                        list: true,
                        display: function (data) {
                            return '<span id="imsi-' + data.record.imsi + '">' + data.record.imsi +
                                '</span><span class="unread-sms" id="imsi-sms-' + data.record.imsi + '"></span>';
                        }
                    },
                    last_lur: {
                        title: 'Last activity',
                        display: function (data) {
                            return '<span id="imsi-lur-' + data.record.imsi + '">' + data.record.last_lur + '</span>';
                        }
                    }
                }
            });
            this._imsiTable = pf.view.$imsiTable.data('hik-jtable');
            pf.subscriber.publish('observer/imsi/list/activate');
        },

        overwriteJTableMethods: function () {
            this._imsiTable._showError = function () {
            };
        },

        updateTable: function (ismiListFromServer) {
            this._updateImsiRows(ismiListFromServer.Records);
            this._updateUnreadMessages(ismiListFromServer.Messages);
        },

        _updateImsiRows: function (records) {
            var context = this,
                imsi;

            $.each(records, function (i, record) {
                imsi = record.imsi;
                if (context._imsiList.hasOwnProperty(imsi)) {
                    if (context._imsiList[imsi].last_lur != record.last_lur) {
                        $('#imsi-lur-' + imsi).html(record.last_lur);
                    }
                } else {
                    context._imsiList[imsi] = record;
                    context._imsiTable.addRecord({
                        record: record,
                        clientOnly: true
                    });
                }
            });
        },

        updateUnreadSmsCount: function (imsi, unreadSmsCount) {
            var unreadSmsText = unreadSmsCount > 0 ? '+ ' + unreadSmsCount + ' sms' : '';
            $('#imsi-sms-' + imsi).text(unreadSmsText);
        },

        _updateUnreadMessages: function (messages) {
            pf.modules.unreadSmsStorage.updateUnreadMessages(messages);
        }
    });
}(jQuery, pf));