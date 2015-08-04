(function ($, pf, L) {
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
                recordsLoaded: function (event, data) {
                    console.log(data);
                },
                sorting: true,
                fields: {
                    imsi: {
                        title: 'IMSI'
                    },
                    last_lur: {
                        title: 'Last LUR (minutes ago)'
                    }
                }
            });
            pf.viewmodel.imsiTable = pf.view.$imsiTable.data('hik-jtable');
            pf.viewmodel.imsiTable.load();
        },

        overwriteJTableMethods: function () {
            pf.viewmodel.imsiTable._showError = function () {
            };
        }
    });
}(jQuery, pf, L));