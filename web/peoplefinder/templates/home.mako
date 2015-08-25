<%inherit file="_master.mako"/>

<%block name="css">
    % if request.registry.settings['frontend_debug'] and request.registry.settings['frontend_debug'] == 'true':
        <%include file="home/_css.mako"/>
    % else:
        <script src="${request.static_url('peoplefinder:static/build/peoplefinder.min.css')}"></script>
    % endif
</%block>

<div id="body">
    <div class="container">
        <div class="row margin-top-10 margin-bottom-10">
            <div class="col-md-8">
                <div id="map"></div>
            </div>
            <div id="rightPanel" class="col-md-4">
                <div class="row">
                    <span class="text-uppercase sub-header">Tracking</span>
                    <div class="inner-row">
                        <a class="btn btn-primary start" id="trackingButton" href="javascript:void(0)" role="button">Start Tracking</a>
                        <a class="btn btn-link btn-xs" href="javascript:void(0)" role="button">Clear Results</a>
                    </div>
                </div>
                <div class="row">
                    <span class="text-uppercase sub-header">Registered Mobile IMSI</span>

                    <div id="imsiTable"></div>
                </div>
                <div class="row">
                    <span class="text-uppercase sub-header">SMS Comms</span>
                    <div id="smsViewer" class="form-control input-sm no-sms">
##                        <div class="no-sms">No SMS history for {IMSI}</div>
                    </div>

                    <div class="inner-row">
                        <div class="input-group">
                            <input type="text" id="smsSenderMessage" maxlength="160" class="form-control"
                                   placeholder="SMS Message"/>
                            <span class="input-group-btn">
                                <button type="button" id="sendSms" class="btn btn-default">
                                    <i class="fa fa-send"></i>
                                </button>
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<%block name="scripts">
    % if request.registry.settings['frontend_debug'] and request.registry.settings['frontend_debug'] == 'true':
<%include file="home/_js.mako"/>
    % else:
<script src="${request.static_url('peoplefinder:static/build/peoplefinder.min.js')}"></script>
    % endif
</%block>