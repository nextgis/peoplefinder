(function ($, pf) {
    pf.modules.imsiListObserver = {};
    $.extend(pf.modules.imsiListObserver, {

        init: function () {
            this.bindEvents();
        },

        bindEvents: function () {
            pf.subscriber.subscribe('observer/imsi/list/activate', function () {
                this.updateIsmiList();
            }, this);
        },

        updateIsmiList: function () {
            var context = this;
            $.ajax({
                url: pf.settings.root_url + '/imsi/list',
                dataType: 'json'
            }).done(function (result) {
                pf.modules.imsiTable.updateTable(result);
                setTimeout(function () {
                    context.updateIsmiList();
                }, pf.settings.imsi_list_timeout);
            });
        }
    });
}(jQuery, pf));