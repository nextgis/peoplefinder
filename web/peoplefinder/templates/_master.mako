<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>PeopleFinder</title>
    <link href="${request.static_url('peoplefinder:static/contrib/bootstrap/css/bootstrap.min.css')}" rel="stylesheet">
    <link href="${request.static_url('peoplefinder:static/contrib/font-awesome/css/font-awesome.min.css')}" rel="stylesheet">

    <%block name="css"/>
</head>
<body>
<div id="header">
    <div class="container">
        <nav class="navbar navbar-inner" role="navigation">
            <div class="container-fluid">
                <div class="navbar-header">
                    <a href="#">
                        <span class="logo logo-gray">people</span>
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
                        <span class="logo logo-gray">people</span>
                        <span class="logo logo-orange">finder</span>
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>

<script src="${request.static_url('peoplefinder:static/contrib/jquery/jquery-1.11.3.min.js')}"></script>
<script src="${request.static_url('peoplefinder:static/contrib/bootstrap/js/bootstrap.min.js')}"></script>
<script src="${request.static_url('peoplefinder:static/contrib/leaflet/leaflet-1.0.0-b1/leaflet-src.js')}"></script>
<script src="${request.static_url('peoplefinder:static/contrib/jquery-ui/jquery-ui.js')}"></script>
<script src="${request.static_url('peoplefinder:static/contrib/jtable/jquery.jtable.js')}"></script>
<script src="${request.static_url('peoplefinder:static/contrib/js-cookie/js.cookie.js')}"></script>

<%block name="scripts"/>

<script>
    pf.settings = {};
    pf.settings.root_url = '${request.application_url}';
    pf.settings.imsi_list_timeout = 3000;
    pf.settings.sms_list_timeout = 3000;
    pf.settings.tracking_timeout = 3000;
</script>
</body>
</html>