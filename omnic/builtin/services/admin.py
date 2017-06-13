'''
A read-only admin interface that is useful for monitoring broad server stats
and testing conversions.
'''
from sanic import Blueprint
from sanic import response

TEMPLATE = '''
<!DOCTYPE HTML>
<html lang="en">
<head>
	<meta charset="utf-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>OmniConverter Admin Panel</title>
	<link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css">
	<link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/font-awesome/4.2.0/css/font-awesome.min.css">
	<link rel="stylesheet" href="style.css">
	<link rel="icon" type="image/png" href="favicon.png">
	<script src="http://code.jquery.com/jquery.js"></script>
	<script src="http://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js"></script>
</head>
<body>
	<h1>Hello, world!</h1>
</body>
</html>
'''


class ServiceMeta:
    NAME = 'admin'
    blueprint = Blueprint(NAME)
    config = None
    app = None
    log = None
    enqueue = None


@ServiceMeta.blueprint.get('/')
async def admin_route(request):
    html = TEMPLATE
    return response.html(html)
