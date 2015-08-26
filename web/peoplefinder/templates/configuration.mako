<%inherit file="_master.mako"/>

<%block name="css">
    % if request.registry.settings['frontend_debug'] and request.registry.settings['frontend_debug'] == 'true':
        <%include file="configuration/_css.mako"/>
    % else:
        <script src="${request.static_url('peoplefinder:static/build/peoplefinder.min.css')}"></script>
    % endif
</%block>

<div id="settings">
    <div class="container">
        <div class="row margin-top-10 margin-bottom-10">
            <div class="col-md-12">
                <h1 class="text-uppercase">Configuration</h1>

                <h2 class="text-uppercase">Downloading tiles</h2>

                <p>Zoom or pan to downloading area on the map and click by <input type="button" class="btn btn-default"
                                                              value="Downloading tiles"/></p>

                <div id="mapDownloading"></div>
            </div>

            <div class="col-md-12">
                <h2 class="text-uppercase">Other settings</h2>

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
                    <button type="submit" class="btn btn-primary">Submit</button>
                </form>

            </div>

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