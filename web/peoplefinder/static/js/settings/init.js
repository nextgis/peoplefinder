pf = {};
pf.view = {};
pf.viewmodel = {};
pf.modules = {};

$(document).ready(function () {
    loadModules();
});

function loadModules() {
    pf.modules.map.init();
}