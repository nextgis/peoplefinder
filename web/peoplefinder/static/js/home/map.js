(function ($, pf, L) {
    pf.modules.map = {};
    $.extend(pf.modules.map, {

        _map: null,

        init: function () {
            this.setDom();

            this._map = this.buildMap();
            pf.viewmodel.map = this._map;

            this.setInitialView();
            this._map.tilesSelector._selectTileLayer(true);
        },


        setDom: function () {
            pf.view.$map = $('#map');
        },


        buildMap: function () {
            return L.map('map');
        },


        setInitialView: function () {
            this._map.setView([-26.017, 139.219], 4);
        }
    });
}(jQuery, pf, L));