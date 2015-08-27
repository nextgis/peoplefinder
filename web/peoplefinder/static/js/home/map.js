(function ($, pf, L) {
    pf.modules.map = {};
    $.extend(pf.modules.map, {

        init: function () {
            this.setDom();
            this.buildMap();
            this.setInitialView();
            pf.viewmodel.map.tilesSelector._selectTileLayer(true);
        },


        setDom: function () {
            pf.view.$map = $('#map');
        },


        buildMap: function () {
            pf.viewmodel.map = L.map('map');
        },


        setInitialView: function () {
            pf.viewmodel.map.setView([-26.017, 139.219], 4);
        }
    });
}(jQuery, pf, L));