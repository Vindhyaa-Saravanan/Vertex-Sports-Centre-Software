# vertex/tests/test_models.py

import pytest
from sqlalchemy import select
import datetime

import argon2.exceptions as argon2_exc
import sqlalchemy.exc as sqlalchemy_exc

from app import create_app, models
from app.models import db

"""
https://docs.pytest.org/en/7.1.x/how-to/assert.html
"""

class TestModels:
	"""
	Class for testing models.py - database functionality, integrity...
	"""
	
	def setup_class(self):
		"""
		Set up the test class. Instantiate app, database...
		"""
		self.app = create_app()
		self.db = db
		self.models = models

		# Reset and populate the database to only include test data
		# NOTE: Maybe this shouldn't be in every test class?
		with self.app.app_context():
			self.models.reset_database()
			self.models.populate_database()

		# Create some test objects
		self.valid_user = models.Users("tester3993@gmail.com", "Lemonade!1", "Test", "User", datetime.date(1990, 2, 2))
		self.invalid_user = models.Users("john@doe.com", "Lemonade!1", "Re-used", "Email", datetime.date(2004, 12, 22))

		self.valid_class_booking = models.ClassBookings(user_id=1, class_id=4) # User 1 booking into class 4

		self.valid_facility_booking = models.FacilityBookings(user_id=2, facility_id=1, activity="general use", price=5, date=datetime.date(2023, 2, 2), start=datetime.time(), end=datetime.time())
	
	def teardown_class(self):
		"""
		Deconstruct the test class.
		"""
		# Roll back any un-committed changes to the database and close it
		with self.app.app_context():
			self.db.session.rollback()
			self.db.session.close()
	
	def test_user_query(self):
		"""
		Test a basic table query.
		"""
		with self.app.app_context():
			x = models.Users.query.where(models.Users.id == 1).first()
			assert x.firstname == "John" # Check that first user's first name is John
		
	def test_password_verify(self):
		"""
		Test correct/incorrect password verification.
		"""
		with self.app.app_context():
			x = models.Users.query.where(models.Users.id == 3).first()
			assert x.verify_password("Lemonade!1") # Check that Lemonade!1 is the first employee's password
			assert not x.verify_password("wrongpassword^^3") # Check that an incorrect password doesn't work

	def test_user_insert(self):
		"""
		Test a valid and invalid user insertion.
		"""
		with self.app.app_context():
			# Try a valid user
			self.db.session.add(self.valid_user)
			self.db.session.commit()
			# Try an invalid user - the email is used before in the test entries
			self.db.session.add(self.invalid_user)
			with pytest.raises(sqlalchemy_exc.IntegrityError) as ex:
				self.db.session.commit()
			assert "UNIQUE constraint failed" in str(ex.value)
			self.db.session.rollback()
	
	def test_class_booking(self):
		"""
		Test that a class booking foreign key is working as intended.
		"""
		with self.app.app_context():
			self.db.session.add(self.valid_class_booking)
			self.db.session.commit()
			booking = models.ClassBookings.query.where(models.ClassBookings.class_id == 4, models.ClassBookings.user_id == 1).first()
			user = models.Users.query.where(models.Users.id == 1).first()
			assert booking in user.class_bookings
	
	def test_facility_booking(self):
		"""
		Test that a facility booking foreign key is working as intended.
		"""
		with self.app.app_context():
			self.db.session.add(self.valid_facility_booking)
			self.db.session.commit()
			booking = models.FacilityBookings.query.where(models.FacilityBookings.facility_id == 1, models.FacilityBookings.user_id == 2).first()
			user = models.Users.query.where(models.Users.id == 2).first()
			assert booking in user.facility_bookings