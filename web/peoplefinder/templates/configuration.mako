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

                <p>Pan and zoom to download tiles locally for the area on the map <input id="tilesDownloader"
                                                                                         type="button"
                                                                                         class="btn btn-default"
                                                                                         value="Downloading tiles"/></p>

                <div id="map"></div>
            </div>

            <div class="col-md-12">
                <h2 class="text-uppercase">Other settings</h2>

                <form action="${request.route_url('configuration')}" method="POST">
                    <div class="form-group">
                        <label for="welcome">Welcome message</label>
                        <input type="text" class="form-control" name="welcomeMessage" id="welcomeMessage"
                               value="${welcomeMessage}"/>
                    </div>
                    <div class="form-group">
                        <label for="reply">Reply message</label>
                        <input type="text" class="form-control" name="replyMessage" id="replyMessage"
                               value="${replyMessage}"/>
                    </div>
                    <div class="form-group">
                        <label for="imsiUpdate">IMSI update interval (ms)</label>
                        <input type="number" class="form-control" name="imsiUpdate" id="imsiUpdate"
                               value="${imsiUpdate}"/>
                    </div>
                    <div class="form-group">
                        <label for="smsUpdate">SMS update interval (ms)</label>
                        <input type="number" class="form-control" name="smsUpdate" id="smsUpdate" value="${smsUpdate}"/>
                    </div>
                    <div class="form-group">
                        <label for="silentSms">Silent SMS interval (ms)</label>
                        <input type="number" class="form-control" name="silentSms" id="silentSms" value="${silentSms}"/>
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

    <script>
        pf.settings = {};
        pf.settings.root_url = '${request.application_url}';
    </script>

</%block>
