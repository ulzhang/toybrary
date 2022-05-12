from flask_admin import Admin

from flask_security import current_user, login_required, RoleMixin, Security, \
    SQLAlchemyUserDatastore, UserMixin, utils
from app.application import app 
from app.admin_dashboard import MemberView, ToyView, RentalView
from app.models import db, Member, Toy, Rental

def configure_admin(app):

    admin = Admin(
        app,
        'Liza Admin',
        base_template='my_master.html',
        template_mode='bootstrap3',
    )
    admin.add_view(MemberView(Member, db.session, name="People"))
    admin.add_view(ToyView(Toy, db.session, name="Toys"))
    admin.add_view(RentalView(Rental, db.session, name="Checkin/Checkout"))
    

    return admin