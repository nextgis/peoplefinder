(function ($, pf, L) {
    pf.modules.tilesDownloader = {};
    $.extend(pf.modules.tilesDownloader, {

        $tilesDownloader: null,

        init: function () {
            this.setDom();
            this.bindEvents();
        },

        setDom: function () {
            this.$tilesDownloader = $('#tilesDownloader');
        },

        bindEvents: function () {
            this.$tilesDownloader.click($.proxy(function () {

            }, this));

            pf.subscriber.subscribe('/tiles/downloading/status/changed', function (status) {
                this.updateDownloadingButton(status);
            }, this);
        },

        downloadingButtonClickHandler: function () {
            var status = this.$tilesDownloader.data('status') === 'ready' ? 'downloading' : 'ready';
            pf.subscriber.subscribe('observer/tiles/downloading/status/deactivate');
                var status =
                this.toggleDownloadingButton();
        },

        updateDownloadingButton: function (status) {
            if (!status) {

            }

            switch (status){
                case 'ready':
                    this.$tilesDownloader.text = 'Download tiles';
                    break;
                case 'downloading':
                    this.$tilesDownloader.text = 'Stop downloading';
                    break;
            }

        }
    });
}(jQuery, pf, L));