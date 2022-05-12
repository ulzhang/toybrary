"""
Configuration for Flask App
"""

from datetime import date

from flask_sqlalchemy import SQLAlchemy
import atexit
import time



from flask import Flask, url_for, current_app


app = Flask(__name__)


from app.config import configure_app
configure_app(app)

from .models import db, Role, AdminLogin, Toy, Member, Rental, Email

from app.database_setup import init_db
security = init_db(app)

from app.admin_setup import configure_admin
admin = configure_admin(app)

from flask_admin import helpers as admin_helpers


if __name__ == '__main__':
	app.run(use_reloader=False)

# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )


# Importing all necessary API endpoints
from app import routes
