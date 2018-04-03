from flask import Flask, Response
from flask.ext.principal import Principal, Permission, RoleNeed

app = Flask(__name__)

# load the extension
principals = Principal(app)

# Create a permission with a single Need, in this case a RoleNeed.
admin_permission = Permission(RoleNeed('admin'))

# protect a view with a principal for that need
@app.route('/admin')
@admin_permission.require()
def do_admin_index():
    return Response('Only if you are an admin')
    
# this time protect with a context manager
@app.route('/articles')
def do_articles():
    with admin_permission.require():
        return Response('Only if you are admin')