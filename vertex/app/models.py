# vertex/app/models.py

from __future__ import annotations # Must stay at start of file

import datetime

from sqlalchemy import (
	ForeignKey,
	String,
	Boolean,
	Integer,
	select,
)

from sqlalchemy.orm import (
	Mapped,
	mapped_column,
	relationship,
)

from sqlalchemy.dialects.mysql import JSON

from flask_login import UserMixin, login_manager

from typing import List
from sqlalchemy_json import mutable_json_type

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from .extensions import db, login

"""
Cheat sheet on password hashing:
https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

How to use Argon2 (very good password hasher):
https://pypi.org/project/argon2-cffi/
https://argon2-cffi.readthedocs.io/en/stable/api.html
"""

@login.user_loader
def load_user(id):
	return Users.query.where(Users.id == id).first()

ph = PasswordHasher() # Password hasher from Argon2

def reset_database():
	"""
	Reset the database to empty. Useful for testing.
	"""
	db.reflect()
	db.drop_all()
	db.create_all()

def populate_database():
	"""
	Populate the database with some default values. Useful for testing.

	NOTE: Be wary of changing any of the default values. Tests may rely on them.
	"""
	if not db.session.execute(select(Users)).first(): # Only populate if Users is empty
		users = [
			Users("john@doe.com", "Lemonade!1", "John", "Doe", datetime.date(1990, 1, 1), user_type="user", is_member=False), # User
			Users("alice@doe.com", "Lemonade!1", "Alice", "Doe", datetime.date(2000, 5, 12), user_type="user", is_member=False), # User
			Users("rick@jordan.com", "Lemonade!1", "Rick", "Jordan", datetime.date(1990, 1, 1), user_type="manager", is_member=False), # Admin
			Users("lily@poole.com", "Lemonade!1", "Lily", "Poole", datetime.date(1995, 2, 8), user_type="employee", is_member=False), # Non-admin

			# User to test views for a customer who is already a member
			Users(email='member@email.com', password='Member12345', firstname='Member',lastname='User',date_of_birth=datetime.date(1992, 1, 1),user_type='user',is_member=True),
		]

		for u in users:
			db.session.add(u)

		# User to test invalid email confirmation token
		invalidtokenuser = Users(email="invalidtokenuser@email.com", password="invalidtokenuser", firstname="Invalidtoken", lastname="User", date_of_birth=datetime.date(1990, 5, 5), user_type="user", is_member = False)
		invalidtokenuser.is_confirmed = False
		invalidtokenuser.confirmed_on = None

		confirmed_user = Users(email="confirmeduser@email.com", password="confirmeduser", firstname="Confirmed", lastname="User", date_of_birth=datetime.date(1990, 2, 2), user_type="user")
		confirmed_user.is_confirmed = True
		confirmed_user.confirmed_on = datetime.date(2023, 2, 2)

		expired_token_user = Users(email="expiredtokenuser@email.com", password="expiredtokenuser", firstname="Expiredtoken", lastname="User", date_of_birth=datetime.date(1990, 4, 4), user_type="user")
		expired_token_user.is_confirmed = False
		expired_token_user.confirmed_on = None
		
		db.session.add(expired_token_user)
		db.session.add(invalidtokenuser)
		db.session.add(confirmed_user)
	
	if not db.session.execute(select(TeamEvents)).first(): # Only populate if TeamEvents is empty
		team_events = [ 
			# Swimming at 8am for 2 hours every Friday
			TeamEvents("Swimming", datetime.time(8), 2, "Friday"),
			TeamEvents("Swimming", datetime.time(8), 2, "Sunday"),
			TeamEvents("Sports hall", datetime.time(7), 2, "Thursday"),
			TeamEvents("Sports hall", datetime.time(9), 2, "Saturday")
		]

		for t in team_events:
			db.session.add(t)
	
	today = datetime.date.today()
	start_date = today + datetime.timedelta(days=(7 - today.weekday()))

	if not db.session.execute(select(Classes)).first():
		# Add 10 weeks of classes 
		for i in range(0, 10):
			# Number of days to add on from original set of classes
			delta = datetime.timedelta(days=7*i)

			# Pilates every Monday from start_date
			db.session.add(Classes("Pilates", datetime.time(18), 1, start_date + delta, price=25))
			# Aerobics every Tuesday from start_date
			db.session.add(Classes("Aerobics", datetime.time(10), 1, start_date + datetime.timedelta(days=1) + delta, price=20))
			# Aerobics every Thursday from start_date
			db.session.add(Classes("Aerobics", datetime.time(19), 1, start_date + datetime.timedelta(days=3) + delta, price=20))
			# Aerobics every Saturday from start_date
			db.session.add(Classes("Aerobics", datetime.time(10), 1, start_date + datetime.timedelta(days=5) + delta, price=20))
			# Yoga every Friday from start_date
			db.session.add(Classes("Yoga", datetime.time(19), 1, start_date + datetime.timedelta(days=4) + delta, price=10))
			# Yoga every Sunday from start_date
			db.session.add(Classes("Yoga", datetime.time(9), 1, start_date + datetime.timedelta(days=6) + delta, price=10))

	
	if not db.session.execute(select(Facilities)).first(): # Only populate if Facilities is empty
		"""
		Table that sets the initial prices of booking each activity in the facilities.
  
		For each facility:
		"FACILITY NAME": {
			"ACTIVITY NAME": ACTIVITY_PRICE,
		}
		"""
  
		initialPrices = {
			"Swimming pool": {
				"general use": 5,
				"lane swimming": 5,
				"lessons": 5,
				"team events": 5,
			},
			"Fitness room": {
				"general use": 5,
			},
			"Squash court 1": {
				"1 hour sessions": 5,
			},
			"Squash court 2": {
				"1 hour sessions": 5,
			},
			"Sports hall": {
				"1 hour sessions": 5,
				"team events": 5,
			},
			"Climbing wall": {
				"general use": 5,
			},
			"Studio": {
				"exercise classes": 5,
			}
		}
		
		facilities = [
			# Swimming pool with a capacity of 30, open from 8am to 8pm, no sessions
			Facilities("Swimming pool", 30, datetime.time(8), datetime.time(20), activities=initialPrices["Swimming pool"]),
			# Fitness room with a capacity of 35, open for gym opening times, no sessions
			Facilities("Fitness room", 35, activities=initialPrices["Fitness room"]),
			# Squash court 1 with a capacity of 4, open for gym opening times, sessions of an hour
			Facilities("Squash court 1", 4, session_duration = 1, activities=initialPrices["Squash court 1"]),
			Facilities("Squash court 2", 4, session_duration = 1, activities=initialPrices["Squash court 2"]),
			Facilities("Sports hall", 45, session_duration = 1, activities=initialPrices["Sports hall"]),
			Facilities("Climbing wall", 22, datetime.time(10), datetime.time(20), activities=initialPrices["Climbing wall"]),
			Facilities("Studio", 25, activities=initialPrices["Studio"])
		]


		for f in facilities:
			db.session.add(f)

	if not db.session.execute(select(Memberships)).first(): # Only populate if Memberships is empty
		db.session.add(Memberships(name= "The Monthly Membership", price= 35, months=1))
		db.session.add(Memberships(name= "The Annual Membership", price= 300, months=12))

	already_member = Users.query.where(Users.email=='member@email.com').first()
	existing_membership = Memberships.query.first()
	if not db.session.execute(select(ActiveMemberships)).first(): # Only populate if ActiveMemberships is empty
		activememberships = [
			ActiveMemberships(user_id=already_member.id, membership_id= existing_membership.id, member_from=datetime.date(2023, 3, 10),member_till=datetime.date(2024, 3, 10))
		]

		for m in activememberships:
			db.session.add(m)

	if not db.session.execute(select(Discounts)).first(): # Only populate if Discounts is empty
		# Adding discount scheme as specified in the project backlog
		db.session.add(Discounts(name="Three Sessions, 35 off", value=35, session_number=3))

	db.session.commit()
	
'''
	if not db.session.execute(select(ClassBookings)).first(): # Only populate if ClassBookings is empty

		# Populating sample class bookings to show in manager analytics graphs
		db.session.add(ClassBookings(class_id=1, user_id=1))
		db.session.add(ClassBookings(class_id=3, user_id=2))
		db.session.add(ClassBookings(class_id=6, user_id=1))
		db.session.add(ClassBookings(class_id=2, user_id=1))

	if not db.session.execute(select(FacilityBookings)).first(): # Only populate if FacilityBookings is empty

		# Populating sample facility bookings to show in manager analytics graphs
		db.session.add(FacilityBookings(facility_id=1, user_id=1, activity="general use", price=5, date=datetime.date(2023, 3, 26), start=datetime.time(8), end=datetime.time(9)))
		db.session.add(FacilityBookings(facility_id=1, user_id=1, activity="lessons", price=10, date=datetime.date(2023, 3, 27), start=datetime.time(13), end=datetime.time(14)))
		db.session.add(FacilityBookings(facility_id=3, user_id=1, activity="1 hour sessions", price=5, date=datetime.date(2023, 3, 27), start=datetime.time(11), end=datetime.time(12)))
		db.session.add(FacilityBookings(facility_id=3, user_id=1, activity="1 hour sessions", price=5, date=datetime.date(2023, 3, 26), start=datetime.time(8), end=datetime.time(9)))
		db.session.add(FacilityBookings(facility_id=5, user_id=1, activity="team events", price=20, date=datetime.date(2023, 3, 28), start=datetime.time(11), end=datetime.time(12)))
		db.session.add(FacilityBookings(facility_id=5, user_id=1, activity="1 hour sessions", price=10, date=datetime.date(2023, 3, 28), start=datetime.time(15), end=datetime.time(16)))
		db.session.add(FacilityBookings(facility_id=4, user_id=1, activity="1 hour sessions", price=5, date=datetime.date(2023, 3, 27), start=datetime.time(11), end=datetime.time(12)))
'''
	

class Users(UserMixin, db.Model):
	"""
	Table of users, for login and booking tracking.
	NOTE: Passwords should be hashed before storage in the database.
	See: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
	"""
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(primary_key=True)
	email: Mapped[str] = mapped_column(String(100), unique=True)
	password: Mapped[str] = mapped_column(String(97))
	firstname: Mapped[str] = mapped_column(String(50))
	lastname: Mapped[str] = mapped_column(String(50))
	date_of_birth: Mapped[datetime.date] = mapped_column()
	user_type: Mapped[str] = mapped_column(String(10), default="user")
	# Options: "user" --> User type, "employee" --> Employee type, "manager" --> Manager type
	payment_customer_id: Mapped[str] = mapped_column(String(255), nullable=True)
	payment_card_id: Mapped[str] = mapped_column(String(255), nullable=True)

	# To store membership details
	is_member: Mapped[bool] = mapped_column(Boolean, default=False)
	membership: Mapped[List["ActiveMemberships"]] = relationship()

	class_bookings: Mapped[List["ClassBookings"]] = relationship()
	facility_bookings: Mapped[List["FacilityBookings"]] = relationship()

	#  For email verification upon signup
	is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
	confirmed_on: Mapped[datetime.date] = mapped_column(default=None, nullable=True)

	def __init__(self, email: str, password: str, firstname: str, lastname: str, date_of_birth: datetime.date, user_type: str = "user",
		  is_member: bool = False):
		"""
		Initialise a user entry.
		"""
		
		if user_type != "user" and user_type != "employee" and user_type != "manager":
			raise ValueError("user_type must be user, employee, or manager")
		
		if date_of_birth > datetime.datetime.now().date():
			raise ValueError("date of birth cannot be in the future")
		
		self.email = email
		self.password = ph.hash(password) # Hash the password with Argon2 before insertion 
		self.firstname = firstname
		self.lastname = lastname
		self.date_of_birth = date_of_birth
		self.user_type = user_type
		self.is_member = is_member
	
	def verify_password(self, password: str):
		"""
		Verifies if a user's password is correct. Throws argon2.exceptions.VerifyMismatchError
		if password is incorrect. Rehashes the password if need be (will require committing
		to the database after changes made). Returns True if password is correct.
		"""

		try:
			ph.verify(self.password, password) # Throws exception if password is wrong
		except VerifyMismatchError:
			return False

		"""
		When Argon2 parameters change, best practice is to rehash the password when we can. 
		In order to do so, we need the plain-text password. After checking if a password is 
		correct (during login), we check if the password needs rehashing. If it does,
		let's rehash it.
		"""
		if ph.check_needs_rehash(self.password):
			self.password = ph.hash(password) # Will require committing to the database
		
		# Password is correct and rehashed
		return True
	
	def reset_password(self, new_password: str):
		"""
		Resets a users password to a given value. Hashes with argon2id.
		"""
		self.password = ph.hash(new_password)

	def get_dict(self, password: bool = False):
		"""
		Returns a general use dictionary describing the detail. If password is true, the hashed
		password will be included in the dictionary.
		"""
		user = {
			"id": self.id,
			"email": self.email,
			"firstname": self.firstname,
			"lastname": self.lastname,
			"date_of_birth": self.date_of_birth,
			"user_type": self.user_type,
		}
		if password:
			user["password"] = password 
		return user
		

	def __repr__(self):
		"""
		Representation string for a user.
		"""
		return f"<{self.user_type}: ({self.id}) {self.email}>"


class TeamEvents(UserMixin, db.Model):
	"""
	Table of team events. Only changed when a team event is added or removed.
	Day of the week (string), start time and duration are stored.
	"""
	__tablename__ = "teamevents"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(String(20))
	start: Mapped[datetime.time] = mapped_column()
	duration: Mapped[int] = mapped_column()
	day: Mapped[str] = mapped_column(String(10))

	def __init__(self, name: str, start: datetime.time, duration: int, day: str):
		"""
		Initialise a team event entry.
		"""
		self.name = name
		self.start = start
		self.duration = duration
		self.day = day

	def __repr__(self):
		"""
		Representation string for a team event.
		"""
		return f"<Team event: ({self.id}) {self.name} {self.day}>"

class Classes(UserMixin, db.Model):
	"""
	Table of gym classes. Each instance of each class has its own entry.
	Date, time, and duration are all stored separately.
	"""
	__tablename__ = "classes"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[int] = mapped_column(String(20))
	start: Mapped[datetime.time] = mapped_column()
	duration: Mapped[int] = mapped_column()
	date: Mapped[datetime.date] = mapped_column()
	price: Mapped[int] = mapped_column()

	bookings: Mapped[List["ClassBookings"]] = relationship()

	def __init__(self, name: str, start: datetime.time, duration: int, date: datetime.date, price: int):
		"""
		Initialise a class entry.
		"""
		self.name = name
		self.start = start
		self.duration = duration
		self.date = date
		self.price = price

	def get_dict(self):
		"""
		Returns a general use dictionary describing the class.
		"""
		return {
			"id": self.id,
			"name": self.name,
			"start": self.start,
			"duration": self.duration,
			"date": self.date,
			"price": self.price,
			"num_of_bookings": len(self.bookings),
			"bookings": self.bookings,
		}

	def __repr__(self):
		"""
		Representation string for a gym class.
		"""
		return f"<Class: ({self.id}) Name: {self.name}, Date: {self.date}, Price:{self.price}>"

class Facilities(UserMixin, db.Model):
	"""
	Table of gym facilities. Only changed when a facility is added or removed.
	Session duration stored in hours. If zero, the facility does not operate on sessions.
	"""
	__tablename__ = "facilities"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(String(20))
	open: Mapped[datetime.time] = mapped_column(default=datetime.time(8))
	close: Mapped[datetime.time] = mapped_column(default=datetime.time(22))
	capacity: Mapped[int] = mapped_column()
	session_duration: Mapped[int] = mapped_column(default=0)
	activities: Mapped[str] = mapped_column(JSON) # {"general use": 5, "1 hour session": 10}

	def __init__(self, name: str, capacity: int, open: datetime.time = datetime.time(8), close: datetime.time = datetime.time(22), session_duration: int = 0, activities: object = {}):
		"""
		Initialise a facility entry.
		"""
		if close < open:
			raise ValueError("close time cannot be before open time")

		self.name = name
		self.open = open
		self.close = close
		self.capacity = capacity
		self.session_duration = session_duration
		self.activities = activities

	def get_dict(self):
		"""
		Returns a general use dictionary describing the facility.
		"""
		return {
			"id": self.id,
			"name": self.name,
			"open": self.open,
			"close": self.close,
			"capacity": self.capacity,
			"session_duration": self.session_duration,
		}

	def __repr__(self):
		"""
		Representation string for a facility.
		"""
		return f"<Facility: ({self.id}) {self.name}" + (" [sessions]" if self.session_duration > 0 else "") + ">"

class ClassBookings(UserMixin, db.Model):
	"""
	Table of class bookings. Each instance of a user booking into a class is recorded,
	alongside a timestamp.
	"""
	__tablename__ = "classbookings"

	id: Mapped[int] = mapped_column(primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
	class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"))
	timestamp: Mapped[datetime.datetime] = mapped_column()

	def __init__(self, user_id: int, class_id: int):
		"""
		Initialise a class booking entry. Datetime entry is automatic.
		"""
		self.user_id = user_id
		self.class_id = class_id
		self.timestamp = datetime.datetime.now()
	
	def __repr__(self):
		"""
		Representation string for a class booking.
		"""
		return f"<Class booking: ({self.id}) <User:{self.user_id}> <Class:{self.class_id}>>"
	

class FacilityBookings(UserMixin, db.Model):
	"""
	Table of facility bookings. Each instance of a user booking into a facility is recorded,
	alongside a timestamp.
	"""
	__tablename__ = "facilitybookings"

	id: Mapped[int] = mapped_column(primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
	facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"))
	activity: Mapped[int] = mapped_column()
	price: Mapped[int] = mapped_column()
	start: Mapped[datetime.time] = mapped_column()
	end: Mapped[datetime.time] = mapped_column()
	date: Mapped[datetime.date] = mapped_column()
	timestamp: Mapped[datetime.datetime] = mapped_column()

	def __init__(self, user_id: int, facility_id: int, activity: str, price: int, date: datetime.date, start: datetime.time, end: datetime.time):
		"""
		Initialise a facility booking entry. Datetime entry is automatic.
		"""
		self.user_id = user_id
		self.facility_id = facility_id
		self.activity = activity
		self.price = price
		self.date = date
		self.start = start
		self.end = end
		self.timestamp = datetime.datetime.now()
	
	def __repr__(self):
		"""
		Representation string for a facility booking.
		"""
		return f"<Facility booking: ({self.id}) <User:{self.user_id}> <Facility:{self.facility_id}>>"
	
class Memberships(UserMixin, db.Model):
	"""
	Table of membership types. Each type of membership (monthly, annual) has own entry.
	Actual records of active memberships are in table ActiveMemberships.
	"""
	__tablename__ = "memberships"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(String(30))
	price: Mapped[int] = mapped_column(String(10))
	months: Mapped[int] = mapped_column(String(10))

	activememberships: Mapped[List["ActiveMemberships"]] = relationship()

	def __init__(self, name: str, price: int, months: int):
		"""
		Initialise a new type of membership entry.
		"""
		self.name = name
		self.price = price
		self.months = months

	def get_dict(self):
		"""
		Returns a general use dictionary describing the membership class.
		"""
		return {
			"id": self.id,
			"name": self.name,
			"price": self.price,
			"months": self.months,
			"activememberships": len(self.activememberships),
		}

	def __repr__(self):
		"""
		Representation string for a membership type.
		"""
		return f"<Membership: ({self.id}): {self.name}: for {self.months}, price is {self.price}>"
	
class ActiveMemberships(UserMixin, db.Model):
	"""
	Table of records of active memberships bookings.
	"""
	__tablename__ = "activememberships"

	id: Mapped[int] = mapped_column(primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
	membership_id: Mapped[int] = mapped_column(ForeignKey("memberships.id"))
	member_from: Mapped[datetime.date] = mapped_column(default=None, nullable=True)
	member_till: Mapped[datetime.date] = mapped_column(default=None, nullable=True)
	

	def __init__(self, user_id: int, membership_id: int, member_from: datetime.date, member_till: datetime.time):
		"""
		Initialise a membership entry.
		"""
		self.user_id = user_id
		self.membership_id = membership_id
		self.member_from = member_from
		self.member_till = member_till
	
	def __repr__(self):
		"""
		Representation string for a membership.
		"""
		return f"<Active membership: ({self.id}) <User:{self.user_id}> <Membership:{self.membership_id}>>"
	
class Discounts(UserMixin, db.Model):
	"""
	Table for different discount schemes.
	"""
	__tablename__ = "discounts"

	id: Mapped[int] = mapped_column(primary_key=True)

	# Name of discount scheme
	name: Mapped[str] = mapped_column(String(30))

	# Discount percentage, stored as x where x/100 is to be multiplied with the cost
	value: Mapped[int] = mapped_column(default=35)

	# Number of sessions for discount to apply
	session_number: Mapped[int] = mapped_column(default=3)
	

	def __init__(self, name: str, value: int, session_number: int):
		"""
		Initialise a discount entry.
		"""
		self.name = name
		self.value = value
		self.session_number = session_number

	def get_dict(self):
		"""
		Returns a general use dictionary describing the discount class.
		"""
		return {
			"id": self.id,
			"name": self.name,
			"value": self.value,
			"session_number": self.session_number,
		}
	
	def __repr__(self):
		"""
		Representation string for a discount scheme.
		"""
		return f"<Discount scheme {self.id}: {self.value}% off if {self.session_number} sessions booked>"