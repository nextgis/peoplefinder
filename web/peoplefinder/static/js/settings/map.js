(function ($, pf, L) {
    pf.modules.map = {};
    $.extend(pf.modules.map, {

        init: function () {
            this.setDom();
            this.buildMap();
            this.addOsmLayer();
        },


        setDom: function () {
            pf.view.$map = $('#mapDownloading');
        },


        buildMap: function () {
            pf.viewmodel.map = L.map('mapDownloading').setView([-26.017, 139.219], 4);
        },


        addOsmLayer: function () {
            L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: 'Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors',
                maxZoom: 18
            }).addTo(pf.viewmodel.map);
        }
    });
}(jQuery, pf, L));