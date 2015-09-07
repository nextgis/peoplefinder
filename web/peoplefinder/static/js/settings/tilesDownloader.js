(function ($, pf, L) {
    pf.modules.tilesDownloader = {};
    $.extend(pf.modules.tilesDownloader, {

        $tilesDownloader: null,
        _state: null, // values: 'downloading', 'ready'

        init: function () {
            this.setDom();
            this.bindEvents();
            this.setInitialStatus();
        },

        setDom: function () {
            this.$tilesDownloader = $('#tilesDownloader');
        },

        bindEvents: function () {
            var context = this;

            this.$tilesDownloader.click($.proxy(function () {
                if (this._state === 'ready') {
                    this.startDownload();
                } else if (this._state === 'downloading') {
                    this.stopDownload();
                }
            }, this));

            pf.subscriber.subscribe('/tiles/downloading/status/changed', function (status) {
                this.updateDownloadingButton(status);
            }, this);

            pf.viewmodel.map.on('zoomend', function () {
                context._updateDisabledButton(this);
            });
        },

        _updateDisabledButton: function (map) {
            var newZoom = map.getZoom();
            if (newZoom < 10 && this._state === 'ready') {
                this.$tilesDownloader.prop('disabled', true);
            } else {
                this.$tilesDownloader.prop('disabled', false);
            }
        },

        setInitialStatus: function () {
            $.ajax({
                url: pf.settings.root_url + '/tiles/download/status',
                dataType: 'json',
                type: 'GET'
            }).done($.proxy(function (result) {
                this.updateDownloadingButton(result.status);
                pf.subscriber.publish('observer/tiles/downloading/status/activate');
                this._updateDisabledButton(pf.viewmodel.map);
            }, this));
        },

        updateDownloadingButton: function (status) {
            if (!status || status === this._state) {
                return false;
            }

            this._state = status;
            switch (status) {
                case 'ready':
                    this.$tilesDownloader.val('Download tiles');
                    this.$tilesDownloader.prop('class', 'btn btn-success');
                    break;
                case 'downloading':
                    this.$tilesDownloader.val('Stop downloading');
                    this.$tilesDownloader.prop('class', 'btn btn-danger');
                    break;
            }

            this._updateDisabledButton(pf.viewmodel.map);
        },

        startDownload: function () {
            var map = pf.viewmodel.map,
                bounds = map.getBounds(),
                zoom = map.getZoom(),
                params = {
                    bounds: [
                        bounds._southWest.lng,
                        bounds._southWest.lat,
                        bounds._northEast.lng,
                        bounds._northEast.lat].join(','),
                    zoom: [zoom, 18].join(':')
                };

            pf.subscriber.publish('observer/tiles/downloading/status/deactivate');
            this.$tilesDownloader.val('Starting...');
            this.$tilesDownloader.prop('disabled', true);

            $.ajax({
                url: pf.settings.root_url + '/tiles/download/start',
                dataType: 'json',
                type: 'POST',
                data: params
            }).done($.proxy(function () {
                setTimeout($.proxy(function () {
                    this._state = 'downloading';
                    this.$tilesDownloader.val('Stop downloading');
                    this.$tilesDownloader.prop('disabled', false);
                    this.$tilesDownloader.prop('class', 'btn btn-danger');
                    pf.subscriber.publish('observer/tiles/downloading/status/activate');
                    this._updateDisabledButton(pf.viewmodel.map);
                }, this), 2000);
            }, this));
        },


        stopDownload: function () {
            pf.subscriber.publish('observer/tiles/downloading/status/deactivate');
            this.$tilesDownloader.val('Stopping...');
            this.$tilesDownloader.prop('disabled', true);

            $.ajax({
                url: pf.settings.root_url + '/tiles/download/stop',
                dataType: 'json',
                type: 'GET'
            }).done($.proxy(function () {
                setTimeout($.proxy(function () {
                    this._state = 'ready';
                    this.$tilesDownloader.val('Download tiles');
                    this.$tilesDownloader.prop('disabled', false);
                    this.$tilesDownloader.prop('class', 'btn btn-success');
                    pf.subscriber.publish('observer/tiles/downloading/status/activate');
                    this._updateDisabledButton(pf.viewmodel.map);
                }, this), 2000);
            }, this));
        }
    });
}(jQuery, pf, L));