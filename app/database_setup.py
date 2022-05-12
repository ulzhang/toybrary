"""
database initialization and setup
"""


def init_db(app):
    """
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    Initializes database and creates the tables
    """
    from app.models import db, Role, AdminLogin, Member, Toy, Rental, Email
    from flask_security import Security, SQLAlchemyUserDatastore
    from flask_migrate import Migrate
    from .seed import seed_toys, seed_customers, seed_rentals

    db.init_app(app)
    app.app_context().push()

    # Initialize the SQLAlchemy data store and Flask-Security
    user_datastore = SQLAlchemyUserDatastore(db, AdminLogin, Role)
    security = Security(app, user_datastore)

    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    # Clear data from table
    # db.session.query(Rental).delete()

    #db.drop_all()    
    db.create_all()
    
    # Seeds in Liza's data, must comment out after single use
    # seed_toys()
    # seed_customers()
    # seed_rentals()

    user_datastore.find_or_create_role(name="superuser")
    if not user_datastore.get_user(app.config['SUPERUSER_ADMIN_EMAIL']):
        user_datastore.create_user(email=app.config['SUPERUSER_ADMIN_EMAIL'], 
                                   password=app.config['SUPERUSER_ADMIN_PASSWORD'],
                                   active=True)
    db.session.commit()

    user_datastore.add_role_to_user(app.config['SUPERUSER_ADMIN_EMAIL'], "superuser")
    db.session.commit()


    return security