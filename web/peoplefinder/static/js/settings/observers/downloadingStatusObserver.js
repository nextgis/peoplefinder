(function ($, pf) {
    pf.modules.downloadingStatusObserver = {};
    $.extend(pf.modules.downloadingStatusObserver, {
        init: function () {
            this.bindEvents();
        },

        _isActivated: false,
        _currentStatus: 'ready',

        bindEvents: function () {
            pf.subscriber.subscribe('observer/tiles/downloading/status/activate', function () {
                this._isActivated = true;
                this.updateDownloadingStatus();
            }, this);

            pf.subscriber.subscribe('observer/tiles/downloading/status/deactivate', function () {
                this._isActivated = false;
            }, this);
        },

        updateDownloadingStatus: function () {
            if (!this._isActivated) return false;

            $.ajax({
                url: pf.settings.root_url + '/tiles/download/status',
                dataType: 'json'
            }).done($.proxy(function (result) {
                var status = result.status;

                if (status !== this._currentStatus) {
                    this._currentStatus = status;
                    pf.subscriber.publish('/tiles/downloading/status/changed', [status]);
                }

                setTimeout($.proxy(function () {
                    this.updateDownloadingStatus();
                }, this), 10000);
            }, this));
        }
    });
}(jQuery, pf));