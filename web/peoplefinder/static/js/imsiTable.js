(function ($, pf) {
    pf.modules.imsiTable = {};
    $.extend(pf.modules.imsiTable, {

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
                    if (pf.viewmodel.trackingActive) return;
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
                            return '<span id="imsi-' + data.record.imsi + '">' + data.record.imsi + '</span>';
                        }
                    },
                    last_lur: {
                        title: 'Last LUR (minutes ago)',
                        display: function (data) {
                            return '<span id="imsi-lur-' + data.record.imsi + '">' + data.record.last_lur + '</span>';
                        }
                    }
                }
            });
            pf.viewmodel.imsiTable = pf.view.$imsiTable.data('hik-jtable');
            pf.subscriber.publish('observer/imsi/list/activate');
        },

        overwriteJTableMethods: function () {
            pf.viewmodel.imsiTable._showError = function () {
            };
        }
    });
}(jQuery, pf));