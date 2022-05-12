"""
Models for database
"""

from flask_security import current_user, login_required, RoleMixin, Security, \
    SQLAlchemyUserDatastore, UserMixin, utils
from flask_sqlalchemy import SQLAlchemy
import datetime
from dateutil.relativedelta import relativedelta

from app.application import app
from datetime import date

db = SQLAlchemy()


roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('admins.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('roles.id'))
)


class AdminLogin(db.Model, UserMixin):
    """
    Admin accounts with different permissions
    """
    __tablename__ = 'admins'

    # Metadata
    id = db.Column(db.Integer(), primary_key=True)
    
    #flask admin + security metadata
    active = db.Column(db.Boolean())
    email = db.Column(db.Text(), unique=True)
    password = db.Column(db.Text())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('AdminLogin'))

    def __init__(self, **data):
        # Metadata
        self.active = data.get('active', False)

        # Application data
        self.email = data.get('email','')
        self.password = data.get('password','')


    def __repr__(self):
    	return '<{}>'.format(self.email)


    def get_id(self):
        return self.id

    def has_role(self, role):
        for my_role in self.roles:
            if (my_role.name == role):
                return True
        return False

class Role(db.Model, RoleMixin):
    """
    Role table to hold different permission levels that admins can have
    """
    __tablename__ = 'roles'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.Text())

    def __init__(self, **data):
        self.name = data.get('name','')

    def __repr__(self):
        return '<{}>'.format(self.name)

#class for memeber
class Member(db.Model): 
    #table name in db
    __tablename__ = 'members'
    #primary key attribute
    id = db.Column(db.Integer(), primary_key=True)

    name = db.Column(db.Text(), nullable=False)
    email = db.Column(db.Text(), unique=True, nullable=False)
    notes = db.Column(db.Text(), nullable = True)
    phone_number = db.Column(db.Text(), nullable= True)
    free_status = db.Column(db.Boolean(), nullable = False)
    membership = db.Column(db.Text(), nullable = False)
    #navi 
    rentals = db.relationship('Rental',backref = db.backref('member'), cascade="all,delete")
    #init
    def __init__(self,**data):
        self.name = data.get('name','')
        self.email = data.get('email','')
        self.notes = data.get('notes', '')
        self.phone_number= data.get('phone_number', '')
        self.free_status= data.get('free_status', '')
        self.membership = data.get('membership', '')


        #represent
    def __repr__(self):
        return '{} - {}'.format(self.name, self.email)

   
#class for toys -> to hold inventory 
class Toy(db.Model):
    #table name in db
    __tablename__ = 'toys'
    #attributees
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.TEXT(), nullable=False)
    serial_number = db.Column(db.Text(), nullable=False)
    description = db.Column(db.Text(), nullable=True)
    picture = db.Column(db.Text(), nullable = True)
    #FK
    rentals = db.relationship('Rental',backref = db.backref('toy'))
    
    #init func
    def __init__(self, **data):
        self.name = data.get('name','')
        self.serial_number = data.get('serial_number', '')
        self.description = data.get('description', '')
        self.picture =  data.get('picture', '')

    #str representation
    def __repr__(self):
        return '{} - {}'.format(self.name, self.serial_number)

#class to keep track of when emails were last sent 
class Email(db.Model):
    __tablename__ = 'emails'
    id = db.Column(db.Integer(), primary_key=True)
    last_email = db.Column(db.DateTime(), nullable = False)

#class fro rentals

class Rental(db.Model):
    #table name in db
    __tablename__ = 'rentals'
    #attributes
    id = db.Column(db.Integer(), primary_key=True)
    checkout_date = db.Column(db.DateTime(), nullable=False)
    checkin_date = db.Column(db.DateTime(), nullable= True)
    duration = db.Column(db.Integer(), nullable = False)
    due_date = db.Column(db.DateTime(), nullable = False)
    late = db.Column(db.Boolean(), nullable = False)
    status = db.Column(db.Text(), nullable = False)
    renewal_count = db.Column(db.Integer(), nullable = False)


    member_fk = db.Column(db.ForeignKey("members.id"))
    toy_fk = db.Column(db.ForeignKey("toys.id"))

    
    #intialized 
    def __init__(self, **data):
        self.checkout_date = datetime.datetime.now()
        self.duration = 0
        self.member_fk = data.get('member_fk', '')
        self.toy_fk = data.get('toy_fk', '')
        self.late = False
        self.status = "checked_out"
        self.due_date = datetime.datetime.now() + relativedelta(months=1)
        self.renewal_count = 0


    #string to repre
    def __repr__(self):
    
        return '{} - {} - {}'.format(self.member.name, self.toy.name, self.checkin_date)
       



