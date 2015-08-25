<%inherit file="_master.mako"/>

<div id="settings">
    <div class="container">
        <div class="row margin-top-10 margin-bottom-10">
            <h1 class="text-uppercase">Configuration</h1>
            <form>
                <div class="form-group">
                    <label for="welcome">Welcome message</label>
                    <input type="text" class="form-control" id="welcome">
                </div>
                <div class="form-group">
                    <label for="imsiUpdate">IMSI update interval</label>
                    <input type="number" class="form-control" id="imsiUpdate">
                </div>
                <div class="form-group">
                    <label for="smsUpdate">SMS update interval</label>
                    <input type="number" class="form-control" id="smsUpdate">
                </div>
                <div class="form-group">
                    <label for="silentSms">Silent SMS interval</label>
                    <input type="number" class="form-control" id="silentSms">
                </div>
                <button type="submit" class="btn btn-default">Submit</button>
            </form>
        </div>
    </div>
</div>

<%block name="scripts">
    % if request.registry.settings['frontend_debug'] and request.registry.settings['frontend_debug'] == 'true':
        <%include file="configuration/_js.mako"/>
    % else:
        <script src="${request.static_url('peoplefinder:static/build/peoplefinder.min.js')}"></script>
    % endif
</%block>