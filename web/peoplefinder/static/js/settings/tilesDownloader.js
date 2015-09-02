(function ($, pf, L) {
    pf.modules.tilesDownloader = {};
    $.extend(pf.modules.tilesDownloader, {

        $tilesDownloader: null,
        _state: null,

        init: function () {
            this.setDom();
            this.bindEvents();
            this.setInitialStatus();
        },

        setDom: function () {
            this.$tilesDownloader = $('#tilesDownloader');
        },

        bindEvents: function () {
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
        },

        setInitialStatus: function () {
            $.ajax({
                url: pf.settings.root_url + '/tiles/download/status',
                dataType: 'json',
                type: 'GET'
            }).done($.proxy(function (result) {
                this._state = result.status;
                this.updateDownloadingButton(this._state);
                pf.subscriber.publish('observer/tiles/downloading/status/activate');

            }, this));
        },

        downloadingButtonClickHandler: function () {
            var status = this.$tilesDownloader.data('status') === 'ready' ? 'downloading' : 'ready';
            pf.subscriber.subscribe('observer/tiles/downloading/status/deactivate');
            var status =
                this.toggleDownloadingButton();
        },

        updateDownloadingButton: function (status) {
            if (!status) { return false; }

            switch (status) {
                case 'ready':
                    this.$tilesDownloader.val('Download tiles');
                    break;
                case 'downloading':
                    this.$tilesDownloader.val('Stop downloading');
                    break;
            }

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
                    zoom: [zoom, zoom].join(':')
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
                    pf.subscriber.publish('observer/tiles/downloading/status/activate');
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
                    pf.subscriber.publish('observer/tiles/downloading/status/activate');
                }, this), 2000);
            }, this));
        }
    });
}(jQuery, pf, L));