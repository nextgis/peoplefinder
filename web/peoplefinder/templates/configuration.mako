<%inherit file="_master.mako"/>

<div id="body">
    <div class="container">
        <div class="row margin-top-10 margin-bottom-10">

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