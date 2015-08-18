pf = {};
pf.view = {};
pf.viewmodel = {};
pf.modules = {};

$(document).ready(function () {
    loadModules();
});

function loadModules() {
    pf.modules.imsiListObserver.init();
    pf.modules.selectedImsiObserver.init();
    pf.modules.smsListObserver.init();
    pf.modules.map.init();
    pf.modules.circlesLayer.init(pf.viewmodel.map);
    pf.modules.imsiTable.init();
    pf.modules.smsViewer.init();
    pf.modules.smsSender.init();
    pf.modules.imsiTracking.init();
    pf.modules.circlesObserver.init();
}