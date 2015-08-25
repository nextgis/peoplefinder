(function ($, pf, L) {
    pf.modules.circlesLayer = {};
    $.extend(pf.modules.circlesLayer, {
        _circlesGroupLayer: null,
        _centersGroupLayer: null,
        _lastCirclesArray: [],
        _lastCirclesCount: 3,
        _circlesStyles: {
            old: {
                color: '#637D3E',
                weight: 1,
                opacity: 1,
                fillOpacity: 0
            },
            last: {
                color: '#FF1900',
                weight: 1,
                opacity: 1,
                fillOpacity: 0
            }
        },

        init: function (map) {
            this._circlesGroupLayer = L.featureGroup();
            map.addLayer(this._circlesGroupLayer);
            this._centersGroupLayer = L.featureGroup();
            map.addLayer(this._centersGroupLayer);

        },

        addCircles: function (circles) {
            var context = this,
                countCircles = circles.length,
                i = countCircles,
                lastCirclesIndex = this._lastCirclesCount,
                circle,
                geoCircle,
                style,
                marker;

            if (countCircles === 0) return false;

            while (i !== 0) {
                i--;
                circle = circles[i];

                style = lastCirclesIndex > 0 ? this._circlesStyles.last : this._circlesStyles.old;
                geoCircle = L.circle(circle.center, circle.radius, style);

                if (lastCirclesIndex > 0) {
                    this.pushLastCircle(geoCircle);
                }
                lastCirclesIndex--;

                context._circlesGroupLayer.addLayer(geoCircle);
            }

            $.each(circles, function (i, circle) {
                geoCircle = L.circle(circle.center, circle.radius, {
                    color: '#637D3E',
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0
                });
                context._circlesGroupLayer.addLayer(geoCircle);
            });

            this._centersGroupLayer.clearLayers();
            marker = L.marker(circles[countCircles - 1].center);
            this._centersGroupLayer.addLayer(marker);

            this.bringToFrontLastCircles();

            pf.viewmodel.map.fitBounds(this._circlesGroupLayer.getBounds());
        },

        pushLastCircle: function (geoCircle) {
            var countLastCircles = this._lastCirclesArray.length,
                isLastCirclesFull = countLastCircles === this._lastCirclesCount;

            if (isLastCirclesFull) {
                this._lastCirclesArray[0].setStyle(this._circlesStyles.old);
                this._lastCirclesArray.shift();
            }

            this._lastCirclesArray.push(geoCircle);
        },

        bringToFrontLastCircles: function () {
            $.each(this._lastCirclesArray, function (i, geoCircles) {
                geoCircles.bringToFront();
            });
        },

        clearAll: function () {
            this._centersGroupLayer.clearLayers();
            this._circlesGroupLayer.clearLayers();
            this._lastCirclesArray = [];
        }
    });
}(jQuery, pf, L));