from app.models import db, Toy, Rental, Member
from datetime import datetime

def seed_toys():
	# script-generated toy list
	# follows the below format
	# new_toy1 = Toy(name = 'Quercetti animal links', serial_number = 1)

	# write to db
	# db.session.add_all([new_toy1]) # new toys added to list
	db.session.commit()
	db.session.flush()
	db.session.close()

	return

def seed_customers():
	# Script-generated list of customers
	# follows the below format:
	# new_member1 = Member(name='Sheryl Bonigan', email='sheryl.bonigan@gmail.com', phone='5123346785')

	# Write to db
	# db.session.add_all([new_member1]) # new members added to list
	db.session.commit()
	db.session.flush()
	db.session.close()

	return

def seed_rentals():
	# Script-generated list of rentals
	# follows the format below:
	# mid11 = Member.query.filter(Member.name.contains('Suzie Boneau')).first().id
	# tid11 = Toy.query.filter(Toy.serial_number=='1647').first().id
	# co_date11 = datetime.strptime('1/9/2018', '%m/%d/%Y')
	# d_date11 = datetime.strptime('2/8/2018', '%m/%d/%Y')
	# new_rental11 = Rental(member_fk = mid11, toy_fk = tid11)
	# new_rental11.checkout_date = co_date11
	# new_rental11.due_date = d_date11
	
	# Write to db
	# db.session.add_all([new_rental1]) # new rentals added to list
	db.session.commit()
	db.session.flush()
	db.session.close()

	return
