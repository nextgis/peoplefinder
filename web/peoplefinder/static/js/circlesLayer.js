(function ($, pf, L) {
    pf.modules.circlesLayer = {};
    $.extend(pf.modules.circlesLayer, {
        _circlesGroupLayer: null,
        _centersGroupLayer: null,

        init: function (map) {
            this._circlesGroupLayer = L.featureGroup();
            map.addLayer(this._circlesGroupLayer);
            this._centersGroupLayer = L.featureGroup();
            map.addLayer(this._centersGroupLayer);

        },

        addCircles: function (circles) {
            var context = this,
                countCircles = circles.length,
                geoCircle,
                marker;

            $.each(circles, function (i, circle) {
                geoCircle = L.circle(circle.center, circle.radius, {
                    color: '#637D3E',
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0
                });
                context._circlesGroupLayer.addLayer(geoCircle);
            });

            if (countCircles > 0) {
                this._centersGroupLayer.clearLayers();
                marker = L.marker(circles[countCircles - 1].center);
                this._centersGroupLayer.addLayer(marker);
            }
        },

        clearAll: function () {
            this._centersGroupLayer.clearLayers();
            this._circlesGroupLayer.clearLayers();
        }
    });
}(jQuery, pf, L));