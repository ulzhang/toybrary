# -*- coding: utf-8 -*-

from .models import db, Toy, Member, Rental
import csv, sys
import codecs
 
	


#put function to seed data here (this function gets called in data_base_setup.py)
#remember to only run once, and comment out the code in data_base_setup
#if not it will run everytime we start app
def seed_data():
	#parse csv here
	print('data seeded')

	read = codecs.open('./app/customers.csv', 'r', encoding='utf-8')
	reader = csv.reader(read)

	for row in reader:
		user_name = row[1] + ' ' + row[0]
		user_phone_number = row[13]
		if user_phone_number == '':
			user_phone_number = "0000000000"
		else:
			user_phone_number= user_phone_number.replace('-',"")
		a = Member(name=user_name, email=row[15], phone_number= user_phone_number, free_status=False, notes = row[19],membership="current_member")
		print(a.phone_number)
		db.session.add(a)

	#seed in data here can probably loop its
	db.session.commit()
	
