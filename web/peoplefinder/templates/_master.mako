<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>PeopleFinder</title>
    % if request.registry.settings['frontend_debug'] and request.registry.settings['frontend_debug'] == 'true':
        <%include file="_css.mako"/>
    % else:
        <script src="${request.static_url('peoplefinder:static/build/peoplefinder.min.js')}"></script>
    % endif
</head>
<body>
<div id="header">
    <div class="container">
        <nav class="navbar navbar-inner" role="navigation">
            <div class="container-fluid">
                <div class="navbar-header">
                    <a href="#">
                        <span class="logo logo-gray">peolpe</span>
                        <span class="logo logo-orange">finder</span>
                        <small></small>
                    </a>
                </div>
                <div class="navbar-collapse collapse" id="navbar-collapse-1" style="margin-top:20px;">
                    <ul class="nav navbar-nav navbar-right">
                        <li><a href="#"><i class="fa fa-location-arrow"></i></a></li>
                        <li><a href="#"><i class="fa fa-cog"></i></a></li>
                    </ul>
                </div>
            </div>
        </nav>
    </div>
</div>

    ${self.body()}

<div class="footer">
    <div class="container">
        <div class="row">
            <div class="col-md-7">
            </div>
            <div class="col-md-5">
                <div class="pull-right">
                    <a href="home">
                        <span class="logo logo-gray">peolpe</span>
                        <span class="logo logo-orange">finder</span>
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>

    % if request.registry.settings['frontend_debug'] and request.registry.settings['frontend_debug'] == 'true':
        <%include file="_js.mako"/>
    % else:
        <script src="${request.static_url('peoplefinder:static/build/peoplefinder.min.js')}"></script>
    % endif

<script>
    pf.root_url = '${request.application_url}';
</script>

</body>
</html>