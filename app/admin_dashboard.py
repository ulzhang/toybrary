# Import flask dependencies
import flask_login as login
from flask_security import current_user
from flask_admin.contrib.sqla import ModelView
from flask_admin.actions import action
from flask_admin import Admin, BaseView, expose, AdminIndexView, helpers
from flask_admin.model import typefmt
from flask import flash, render_template, url_for, redirect, request, abort
from flask.ext.admin.babel import gettext, ngettext, lazy_gettext
from jinja2 import Markup
# Import models
from .models import db, Toy, Member, Rental
# Import forms
from datetime import date, timedelta
import datetime
from dateutil.relativedelta import relativedelta
from flask_admin.model import typefmt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import distinct
from sqlalchemy import or_, and_, not_, asc, desc
from flask_wtf import FlaskForm
from flask_admin.actions import action
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from flask_admin.form.widgets import Select2Widget
from flask_admin.form.upload import ImageUploadField
from wtforms import validators
from flask_login import current_user


# Import appplication configs
from app.application import app

# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import sendgrid
import os

# Import appscheduler libraries
import time
from apscheduler.scheduler import Scheduler
import requests 
# Import bug logging
import logging
logging.basicConfig() 

app.config['MAILGUN_KEY'] = 'key-ba10f1319223ba44cd84ed218e43ff2b'
app.config['MAILGUN_DOMAIN'] = 'toybraryaustin.com'

def send_mail(to_address, subject, plaintext):
    from_address = "liza@toybrary.com"
    r = requests.post("https://api.mailgun.net/v2/%s/messages" % app.config['MAILGUN_DOMAIN'],
            auth=("api", app.config['MAILGUN_KEY']),
            data={
                "from": from_address,
                "to": to_address,
                "subject": subject,
                "text": plaintext    
             }
         )
    return r

def send_warning_emails():
    print('warning emails ran')
    query = Rental.query.filter_by(status="checked_out")
    emails_dict = {}
    for rental in query:
        days_to_due = rental.due_date - datetime.datetime.now()
        days_to_due = days_to_due.days
        if days_to_due == 3: 
            if rental.member.email not in emails_dict.keys():
                emails_dict[rental.member.email] = []
            emails_dict[rental.member.email].append(rental.toy)
    print(emails_dict.keys())
    for email in emails_dict.keys():
        to_address = email
        subject = "Toybrary - Warning Toy Due Soon"
        plaintext = "The following toys from Toybrary are due in 3 days: " + str(emails_dict[email])
        send_mail(to_address, subject, plaintext)


def send_late_emails():
    if current_user.is_authenticated:
        print('late emails ran')
        query = Rental.query.filter_by(late=True, status="checked_out")
        emails_dict = {}
        output_string = ''
        #adds associciated rental objects to selected member that needs emailig
        for rental in query:
            rental_email = str(rental.member.email)
            if rental_email not in emails_dict.keys():
                emails_dict[rental_email] = []
            emails_dict[rental_email].append(rental)
            print (emails_dict)
        #goes through all rentals to send email 
        for rental_list in emails_dict.values():
            #this part is to create the body of the email
            output_string = ''
            for rental in rental_list:
                days_overdue = datetime.datetime.now() - rental.due_date
                days_overdue = days_overdue.days
                output_string = str(rental.toy) + " is "
                output_string = output_string + '' + str(days_overdue) + " days overdue"
                plaintext = output_string + "\n" 
            #creates content for emails and sends
            to_address = rental_email
            subject = "Toybrary - Late Toy Due"
            final_plaintext = "The following toys from Toybrary are past due: " + str(plaintext)
            print(final_plaintext)
            send_mail(to_address, subject, final_plaintext)


def warning_scheduler():
    send_warning_emails() 

def late_scheduler():
    send_late_emails()    


sched = Scheduler()
sched.add_interval_job(warning_scheduler, days= 1)
sched.add_cron_job(late_scheduler,day_of_week=1, hour=12)
sched.add_cron_job(late_scheduler,day_of_week=2, hour=12)
sched.add_cron_job(late_scheduler,day_of_week=3, hour=12)
sched.add_cron_job(late_scheduler,day_of_week=4, hour=12)
sched.add_cron_job(late_scheduler,day_of_week=5, hour=12)
sched.start()


'''
FORMATTERS
'''
def date_format(view, value):
    return value.strftime('%m/%d/%Y')
def bool_format(view, value):
    if value:
        return Markup('<span class="glyphicon glyphicon-ok" style="display:block; text-align:center; margin:0 auto;"></span>')
    else:
        return ''
def member_format(view, value):
    return '{} - {}'.format(value.name, value.email)
def string_format(view, value):
    return value.replace('_', ' ')
def phone_format(self, context, model, name):
    return format(int(model.phone_number[:-1]), ',').replace(',', '-') + model.phone_number[-1]
def image_format(self, context, model, name):
    if model.picture:
        return Markup('<img src="/static/images/%s" class="center-block">' % (model.picture))
    return None

MY_DEFAULT_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
MY_DEFAULT_FORMATTERS.update({
        date: date_format,
		bool: bool_format,
		Member: member_format,
        str: string_format,
    })

'''
VALIDATORS
'''
def validate_phone(form, field):
    if len(field.data) != 10:
        raise validators.ValidationError('Please enter a valid 10-digit phone number.')
    try:
        int(field.data)
    except ValueError:
        raise validators.ValidationError('Please enter a valid phone number.')


#serverside end points for the ajax calls from home page 
#changing all durations for number of days late
def change_duration():
    selected_rentals = Rental.query.filter_by(status="checked_out")
    for rental in selected_rentals:
        if rental.late: # if it is late, start updating the duration
            day_gen = (rental.due_date + timedelta(x + 1) for x in range((datetime.datetime.now() - rental.due_date).days))
            new_duration = sum(1 for day in day_gen if (day.weekday() > 0 and day.weekday() < 6)) # only Tues(1) to Sat(5) count
            rental.duration = new_duration
    db.session.commit()
    db.session.close()
    return ""

def change_late():
    selected_rentals = Rental.query.filter_by(status="checked_out")
    for rental in selected_rentals:
        if datetime.datetime.now() > rental.due_date: # is it late?
            rental.late = True
    db.session.commit()
    db.session.close()
    return ""

#serverside endpoint       
@app.route('/update')
def rental_update():
    change_late()
    change_duration()
    return ""

'''
Members
'''
class MemberView(ModelView):

    # LIST VIEW variables
    page_size = 15
    column_searchable_list = ['name', 'email', 'phone_number','notes']
    column_editable_list = ['membership']
    can_export = True
    column_filters = ('free_status', 'membership')
    column_exclude_list = ('rentals')
    column_type_formatters = MY_DEFAULT_FORMATTERS
    column_formatters = {
        'phone_number': phone_format
    }

    # FORM VIEW variables
    form_choices = { 'membership': [ ('current_member', 'Current Member'), ('non_member', 'Non Member'), ('past_member', 'Past Member')] }
    form_args = {
        'email': dict(validators=[validators.Email('Please enter a valid email.'), validators.DataRequired()]),
        'phone_number': dict(validators=[validators.DataRequired(), validate_phone])
    }
    form_excluded_columns = ('rentals')
    
    # DETAILS VIEW variables
    column_details_exclude_list = ('rentals', 'name')

    # WHAT IS THIS???
    column_display_all_relations = True

    # CUSTOM VIEW link
    list_template = '/admin/member_list.html'
    edit_template = '/admin/my_edit.html'
    base_template = "my_master.html"

    # CUSTOM VIEW
    # DETAIL
    @expose('/details/<id>')
    def details_view(self, id, *args):
        model = self.session.query(self.model).get(id)

        # Display
        phone_number = phone_format('', '', model, '')
        data_table = (['Email', 'Phone', 'Membership Type', 'Notes'], {'Email':model.email, 'Phone':phone_number, 'Membership Type':model.membership, 'Notes':model.notes})
        name = model.name
        free = model.free_status

        # Sort
        sort_column = request.args.get('sort') # get which column to sort by
        if sort_column is None:
            sort_column = 0
        else:
            sort_column = int(sort_column)
        sort_order = request.args.get('desc') # get order which to sort by
        if sort_order is None:
            sort_order = 0
        else:
            sort_order = int(sort_order)

        # Rental history for this member
        rentals = db.session.query(Rental).filter(Rental.member_fk==int(id)).order_by(desc(Rental.checkin_date)).limit(10).all()
        co_dates = [rental.checkout_date.strftime("%m/%d/%Y") if rental.checkout_date is not None else "" for rental in rentals]
        ci_dates = [rental.checkin_date.strftime("%m/%d/%Y") if rental.checkin_date is not None else "" for rental in rentals]
        toys = ["{} - {}".format(rental.toy.name, rental.toy.serial_number) for rental in rentals]
        sorted_rentals = self.custom_sort(sort_column=sort_column, sort_order=sort_order, co_dates=co_dates, ci_dates=ci_dates, toys=toys)
        rental_table = (['Checkin Date', 'Checkout Date', 'Toy'], sorted_rentals)

        return self.render('/admin/member_detail.html', model=model, name=name, data_table=data_table, rentals=rental_table, free=free, sort=(sort_column, sort_order))

    # HELPERS
    def custom_sort(self, sort_column, sort_order, **kwargs):
        args = kwargs.keys()
        args = sorted(args, key=str.lower) # Guarantees that dictionary is ordered

        unsort = {} # creates unsorted base
        for arg in args:
            for i in range(0, len(kwargs[arg])):
                if i not in unsort:
                    unsort[i] = [kwargs[arg][i]]
                else:
                    unsort[i].append(kwargs[arg][i])

        sorted_column = sorted(unsort.items(), key=lambda e: e[1][sort_column], reverse=sort_order) # sorts the dictionary on the sort_column

        return sorted_column

    # SECURIY
    def is_accessible(self):
        return login.current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('security.login', next=request.url))

'''
Rentals
'''
class CheckoutForm(FlaskForm):
    # FORM FIELDS
    member = QuerySelectField('Member', query_factory=lambda: Member.query.filter(Member.membership=='current_member'),\
        widget=Select2Widget(), allow_blank=True, get_pk=lambda m: m.id, validators=[validators.DataRequired()])
    toy = QuerySelectMultipleField('Toys', query_factory=lambda: Toy.query.filter(not_(Toy.rentals.any(Rental.checkin_date==None))),\
        widget=Select2Widget(multiple=True), allow_blank=True, get_pk=lambda t: t.id, validators=[validators.DataRequired()])


class RentalView(ModelView):
        
    # LIST VIEW variable
    page_size = 15
    column_labels = { 'duration':'Days Late' }
    column_default_sort = ('checkout_date', True)
    column_default_sort = ('status')
    column_searchable_list = [ Rental.checkout_date, Member.name, Member.email, Toy.name, Toy.serial_number ]
    column_type_formatters = MY_DEFAULT_FORMATTERS
    column_filters = ('late',)
    column_list = ('member', 'toy', 'checkout_date', 'checkin_date', 'due_date', 'late', 'duration', 'status', 'renewal_count')
    can_export = True

    # FORM VIEW variables
    form_columns = ('member', 'toy')
    form_choices = { 'status': [ ('checked_out', 'Checked Out'), ('returned', 'Returned')] }
    form_args = { 'member': dict(validators=[validators.DataRequired()]), 'toy': dict(validators=[validators.DataRequired()]) }
    create_form = CheckoutForm

   



    # CUSTOM ACTIONS
    #adds batch function to check back in a rental/toy
    @action('checkin', 'Check-in', 'Are you sure you want to check in the selected transactions?')
    #function to checkin transactions
    def action_checkin(self, ids):
        try:
            #query for rental selected
            query = Rental.query.filter(Rental.id.in_(ids))
            count = 0
            #change dates and status for check ins
            for transaction in query.all():
                if transaction.status == 'checked_out':
                    transaction.checkin_date = datetime.datetime.now()
                    transaction.status = 'returned'
                    count += 1
            #saves to db
            db.session.commit()
            db.session.close()
            #happy path all were added succesffully
            if query.count() == count:

                flash(ngettext('Transaction was successfully checked in.',
                               '(%(count)s) transactions were checked in.',
                               count,
                               count=count),'success')
            #sad path one or more transaction failed
            else:
                failed = query.count() - count
                #to use was
                if failed == 1:
                    flash(ngettext('Transaction was successfully checked in. (%(failed)s)was not',
                               '(%(count)s) transactions were checked in. %(failed)s was not.',
                               count,
                               count=count, failed=failed),'error')
                #to use were
                else:
                    flash(ngettext('Transaction was successfully checked in. (%(failed)s) were not',
                               '(%(count)s) transactions were checked in. (%(failed)s) were not.',
                               count,
                               count=count, failed=failed),'error')

        #sad path for exception error
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            flash(gettext('Failed to checkin transactions. %(error)s', error=str(ex)), 'error')
    #adds batch function to renew ental/toy
    @action('renew', 'Renew', 'Are you sure you want to renew the selected transactions?')
    #function to checkin transactions
    def action_renew(self, ids):
        try:
            #query for rental selected
            query = Rental.query.filter(Rental.id.in_(ids))
            count = 0
            #change dates and status for check ins
            for renewal in query.all():
                if renewal.status == 'checked_out':
                    renewal.checkout_date = datetime.datetime.now()
                    renewal.due_date = datetime.datetime.now() + relativedelta(months=1)
                    renewal.late = False
                    renewal.renewal_count += 1
                    count += 1
            #saves to db
            db.session.commit()
            db.session.close()
            #happy path all were added succesffully
            if query.count() == count:

                flash(ngettext('Transaction was successfully renewed.',
                               '(%(count)s) transactions were renewed.',
                               count,
                               count=count),'success')
            #sad path one or more transaction failed
            else:
                failed = query.count() - count
                #to use was
                if failed == 1:
                    flash(ngettext('Transaction was successfully renewed. (%(failed)s)was not',
                               '(%(count)s) transactions were renewed. %(failed)s was not.',
                               count,
                               count=count, failed=failed),'error')
                #to use were
                else:
                    flash(ngettext('Transaction was successfully renewed. (%(failed)s) were not',
                               '(%(count)s) transactions were renewed. (%(failed)s) were not.',
                               count,
                               count=count, failed=failed),'error')

        #sad path for exception error
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            flash(gettext('Failed to renew transactions. %(error)s', error=str(ex)), 'error')

    # CUSTOM VIEW link
    list_template = '/admin/rental_list.html'
    edit_template = '/admin/my_edit.html'
    create_template = '/admin/rental_create.html'

    # CUSTOM VIEW
    @expose('/details/<id>')
    def details_view(self, id):
        model = self.session.query(self.model).get(id);

        # Display
        ci_date = ''
        if model.checkin_date is not None:
            ci_date = model.checkin_date.strftime("%m/%d/%Y")
        data_table = (['Checkout Date', 'Checkin Date', 'Duration', 'Due Date', 'Status', 'Renewals'], {'Checkout Date':model.checkout_date.strftime("%m/%d/%Y"), \
            'Checkin Date':ci_date, 'Duration':model.duration, 'Due Date':model.due_date, 'Status':model.status, 'Renewals':model.renewal_count})
        member = model.member
        toy = model.toy
        late = model.late

        return self.render('/admin/rental_detail.html', model=model, data_table=data_table, member=member, toy=toy, late=late)

    # Override checkouts for multiple toys at once
    def create_model(self, form):
        member = form.member.data
        toys = form.toy.data
        emailed_due_date = datetime.datetime.now().date() + relativedelta(months=1)
        subject = "Toybrary Rental"
        plaintext = "This email is to inform that you have rented out the following items from Toybrary: " + str(toys) + "\n" + "They are due on: " + str(emailed_due_date)
        send_mail(member.email,subject, plaintext)
        print(plaintext)
        print(toys)
        for toy in toys:
            rental = Rental(member_fk=member.id, toy_fk=toy.id)
            db.session.add(rental)
            db.session.commit()
        db.session.close()
      
        return form

    # SECURITY
    def is_accessible(self):
        return login.current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('security.login', next=request.url))


'''
Toy
'''
class ToyView(ModelView):
    # LIST VIEW variables
    page_size = 15
    column_searchable_list = ['name', 'description', 'serial_number']
    column_labels = { 'serial_number':'Barcode' }
    can_export = True
    column_auto_select_related = True
    column_exclude_list = ('rentals')
    column_type_formatters = MY_DEFAULT_FORMATTERS
    column_formatters = {
        'picture': image_format
    }
    column_display_all_relations = True

    # FORM VIEW variables
    form_excluded_columns = ('rentals')
    form_extra_fields = {
        'picture': ImageUploadField('Picture', base_path='app/static/images', allow_overwrite=True,\
            max_size=(100, 100, True))
    }

    # DETAILS VIEW variables
    details_exclude_list = ('name', 'rentals')

    # CUSTOM VIEW link
    # details_template = '/admin/toyDetail.html'
    list_template = '/admin/toy_list.html'
    edit_template = '/admin/my_edit.html'

    # CUSTOM VIEW
    # DETAILS
    @expose('/details/<id>')
    def details_view(self, id):
        model = self.session.query(self.model).get(id);

        # Display
        data_table = (['Serial Number', 'Description'], {'Serial Number': model.serial_number, 'Description': model.description})
        name = model.name
        out = False;

        for rental in model.rentals: # Is this toy out?
            if (rental.checkin_date == None):
                out = True;
                break

        # Sort
        sort_column = request.args.get('sort') # get which column to sort by
        if sort_column is None:
            sort_column = 0
        else:
            sort_column = int(sort_column)
        sort_order = request.args.get('desc') # get order which to sort by
        if sort_order is None:
            sort_order = 0
        else:
            sort_order = int(sort_order)

        # Rental history for Toys
        rentals = db.session.query(Rental).filter(Rental.toy_fk==int(id)).order_by(desc(Rental.checkin_date)).limit(10).all()
        co_dates = [rental.checkout_date.strftime("%m/%d/%Y") if rental.checkout_date is not None else "" for rental in rentals]
        ci_dates = [rental.checkin_date.strftime("%m/%d/%Y") if rental.checkin_date is not None else "" for rental in rentals]
        members = ["{} - {}".format(rental.member.name, rental.member.email) for rental in rentals]
        sorted_rentals = self.custom_sort(sort_column=sort_column, sort_order=sort_order, co_dates=co_dates, ci_dates=ci_dates, members=members)
        rental_table = (['Checkin Date', 'Checkout Date', 'Member'], sorted_rentals)

        return self.render('/admin/toy_detail.html', model=model, name=name, data_table=data_table, rentals=rental_table, out=out,\
            sort=(sort_column, sort_order))

    # HELPERS
    def custom_sort(self, sort_column, sort_order, **kwargs):
        args = kwargs.keys()
        args = sorted(args, key=str.lower) # Guarantees that dictionary is ordered

        unsort = {} # creates unsorted base
        for arg in args:
            for i in range(0, len(kwargs[arg])):
                if i not in unsort:
                    unsort[i] = [kwargs[arg][i]]
                else:
                    unsort[i].append(kwargs[arg][i])

        sorted_column = sorted(unsort.items(), key=lambda e: e[1][sort_column], reverse=sort_order) # sorts the dictionary on the sort_column

        return sorted_column

    # SECURITY
    def is_accessible(self):
        return login.current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('security.login', next=request.url))

