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
                actions: {},
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
        },

        overwriteJTableMethods: function () {
            pf.viewmodel.imsiTable._showError = function () {};
        }
    });
}(jQuery, pf, L));