# vertex/tests/test_manager_login.py

import pytest
from sqlalchemy import select
import datetime

import argon2.exceptions as argon2_exc
import sqlalchemy.exc as sqlalchemy_exc

from app import create_app, models, register_extensions
from app.models import db

class TestManager:
	"""
	Class for testing manager login system.
	"""
	
	def setup_class(self):
		"""
		Set up the test class. Instantiate app, database...
		"""
		self.app = create_app({
			"WTF_CSRF_ENABLED": False,
		})
		self.client = self.app.test_client()
		self.db = db
		self.models = models
		
		with self.app.app_context():
			self.models.reset_database()
			self.models.populate_database()

		self.admin_login = {
			"email": "rick@jordan.com",
			"password": "Lemonade!1",
		}
	
	def teardown_class(self):
		"""
		Deconstruct the test class.
		"""
		# Roll back any un-committed changes to the database and close it
		with self.app.app_context():
			self.db.session.rollback()
			self.db.session.close()
	
	def test_manager_login(self):
		"""
		Test that a manager can log in.
		"""
		with self.app.app_context():
			# Login as admin
			response = self.client.post("/admin/login", follow_redirects=True, data = self.admin_login)
			assert response.status_code == 200
			assert b"Logged in as 3" in response.data
	
	def test_view_users(self):
		"""
		Check that we get a list of users.
		"""
		with self.app.app_context():
			# Login as admin first
			self.client.post("/admin/login", follow_redirects=True, data = self.admin_login)

			response = self.client.get("/admin/users")
			assert b"John Doe" in response.data
		
	def test_edit_name(self):
		"""
		Check that we can edit a name properly.
		"""
		with self.app.app_context():
			# Login as admin first
			self.client.post("/admin/login", follow_redirects=True, data = self.admin_login)
			
			response = self.client.post(
				"/admin/edit_name/1", follow_redirects=True,
				data = {
					"new_firstname": "Alex",
					"new_lastname": "Rider",
				}
			)
			assert response.status_code == 200
			user = models.Users.query.where(models.Users.id == 1).first()
			assert user.firstname == "Alex"
			assert user.lastname == "Rider"
	
	def test_delete_user(self):
		"""
		Check that we can delete a user properly.
		"""
		with self.app.app_context():
			# Login as admin first
			self.client.post("/admin/login", follow_redirects=True, data = self.admin_login)
			
			response = self.client.get("/admin/delete_user/1?confirm=True", follow_redirects=True)
			assert response.status_code == 200
			assert b"User 1 deleted" in response.data

			user = models.Users.query.where(models.Users.id == 1).first()
			assert not user
	
	def test_reset_password(self):
		"""
		Check that a manager can reset a user's password to 'default'.
		"""
		with self.app.app_context():
			# Login as admin first
			self.client.post("/admin/login", follow_redirects=True, data = self.admin_login)
			
			response = self.client.get("/admin/reset/2?confirm=True", follow_redirects=True)
			assert response.status_code == 200
			assert b"User 2 password reset" in response.data

			user = models.Users.query.where(models.Users.id == 2).first()
			assert user.verify_password("default")
	
	def test_view_facilities(self):
		"""
		Check that we get a list of facilities.
		"""
		with self.app.app_context():
			# Login as admin first
			self.client.post("/admin/login", follow_redirects=True, data = self.admin_login)

			response = self.client.get("/admin/facilities")
			assert b"Squash court 2" in response.data
	
	def test_edit_facility(self):
		"""
		Check that we can edit a facility properly.
		"""
		with self.app.app_context():
			# Login as admin first
			self.client.post("/admin/login", follow_redirects=True, data = self.admin_login)

			response = self.client.post(
				"admin/edit_facility/1", follow_redirects=True,
				data = {
					"new_name": "Facility 1 name test",
					"new_open": "9:00", # String needed here, not datetime.time object
				}
			)

			assert response.status_code == 200
			facility = models.Facilities.query.where(models.Facilities.id == 1).first()
			assert facility.name == "Facility 1 name test"
			assert facility.open == datetime.time(9)
	
	def test_delete_facility(self):
		"""
		Check that we can delete a facility properly.
		"""
		with self.app.app_context():
			# Login as admin first
			self.client.post("/admin/login", follow_redirects=True, data = self.admin_login)
			
			response = self.client.get("/admin/delete_facility/1?confirm=True", follow_redirects=True)
			assert response.status_code == 200
			assert b"Facility 1 deleted" in response.data

			facility = models.Facilities.query.where(models.Facilities.id == 1).first()
			assert not facility
	
	def test_view_classes(self):
		"""
		Check that we get a list of classes.
		"""
		with self.app.app_context():
			# Login as admin first
			self.client.post("/admin/login", follow_redirects=True, data = self.admin_login)

			response = self.client.get("/admin/classes")
			assert b"Pilates" in response.data
	
	def test_edit_class(self):
		"""
		Check that we can edit a class properly.
		"""
		with self.app.app_context():
			# Login as admin first
			self.client.post("/admin/login", follow_redirects=True, data = self.admin_login)

			response = self.client.post(
				"admin/edit_class/1", follow_redirects=True,
				data = {
					"new_name": "Class 1 name test",
					"new_start": "9:00", # String needed here, not datetime.time object
					"new_date": "2023-01-01",
					"new_price": "10"
				}
			)

			assert response.status_code == 200
			target = models.Classes.query.where(models.Classes.id == 1).first()
			assert target.name == "Class 1 name test"
			assert target.start == datetime.time(9)
			assert target.date == datetime.date(2023, 1, 1)
	
	def test_delete_class(self):
		
		"""
		Check that we can delete a class properly.
		"""
		with self.app.app_context():
			# Login as admin first
			self.client.post("/admin/login", follow_redirects=True, data = self.admin_login)
			
			response = self.client.get("/admin/delete_class/1?confirm=True", follow_redirects=True)
			assert response.status_code == 200
			assert b"Class 1 deleted" in response.data

			target = models.Classes.query.where(models.Classes.id == 1).first()
			assert not target
	
	def test_new_user(self):
		"""
		Check that a manager can create a new user.
		"""
		with self.app.app_context():
			# Login as admin first
			self.client.post("/admin/login", follow_redirects=True, data = self.admin_login)

			good_user_data = {
				"email": "newusertest@testing.com",
				"password": "Lemonade!1",
				"confirm": "Lemonade!1",
				"firstname": "Test",
				"lastname": "User",
				"date_of_birth": datetime.date(2000, 1, 1),
				"user_type": "user"
			}

			good_response = self.client.post(
				"/admin/new_user", follow_redirects=True,
				data = good_user_data
			)
			
			assert good_response.status_code == 200
			assert b"New user created" in good_response.data

			new = models.Users.query.where(models.Users.email == "newusertest@testing.com").first()
			assert new
			for field in good_user_data:
				assert field in ["password", "confirm"] or (getattr(new, field) == good_user_data[field])

			reused_email = self.client.post(
				"/admin/new_user", follow_redirects=True,
				data = {
					"email": "newusertest@testing.com",
					"password": "Lemonade!1",
					"confirm": "Lemonade!1",
					"firstname": "Failed",
					"lastname": "Test",
					"date_of_birth": datetime.date(2000, 1, 1),
					"user_type": "user"
				}
			)

			assert b"email is already in use" in reused_email.data

			password_mismatch = self.client.post(
				"/admin/new_user", follow_redirects=True,
				data = {
					"email": "anothertest@testing.com",
					"password": "Lemonade!1",
					"confirm": "wrongwrong",
					"firstname": "Password",
					"lastname": "Test",
					"date_of_birth": datetime.date(2000, 1, 1),
					"user_type": "user"
				}
			)

			assert b"Passwords must match" in password_mismatch.data
	
	def test_new_facility(self):
		"""
		Check that a manager can create a new facility.
		"""
		with self.app.app_context():
			# Login as admin first
			self.client.post("/admin/login", follow_redirects=True, data = self.admin_login)
		
			good_response = self.client.post(
				"/admin/new_facility", follow_redirects=True,
				data = {
					"name": "Testing room",
					"open": "8:00", # Needs string times
					"close": "22:00",
					"capacity": 4,
					"session_duration": 0,
				}
			)

			assert good_response.status_code == 200
			assert b"New facility created" in good_response.data

			wrong_times = self.client.post(
				"/admin/new_facility", follow_redirects=True,
				data = {
					"name": "Testing room",
					"open": "22:00",
					"close": "8:00",
					"capacity": 4,
					"session_duration": 0,
				}
			)

			assert b"Opening time must be before closing time" in wrong_times.data
	
	def test_new_class(self):
		"""
		Check that a manager can create a new class.
		"""
		with self.app.app_context():
			# Login as admin first
			self.client.post("/admin/login", follow_redirects=True, data = self.admin_login)

			response = self.client.post(
				"/admin/new_class", follow_redirects=True,
				data = {
					"name": "Test class (get it?)",
					"start": "00:00",
					"duration": 24,
					"date": datetime.date(2100, 1, 1),
					"price": "10"
				}
			)

			assert response.status_code == 200
			assert b"New class created" in response.data

			new = models.Classes.query.where(models.Classes.name == "Test class (get it?)").first()
			assert new

	def test_view_memberships(self):
		"""
		Check that we get a list of membership schemes.
		"""
		with self.app.app_context():
			# Login as admin first
			self.client.post("/admin/login", follow_redirects=True, data = self.admin_login)

			response = self.client.get("/admin/memberships")
			assert b"Annual" in response.data

	def test_edit_memberships(self):
		"""
		Check that we can edit a membership properly.
		"""
		with self.app.app_context():
			# Login as admin first
			self.client.post("/admin/login", follow_redirects=True, data = self.admin_login)

			response = self.client.post(
				"admin/edit_membership/1", follow_redirects=True,
				data = {
					"new_name": "Membership 1 name test",
					"new_months": 6,
					"new_price": 175
				}
			)

			assert response.status_code == 200
			target = models.Memberships.query.where(models.Memberships.id == 1).first()
			assert target.name == "Membership 1 name test"
			assert target.months == "6"
			assert target.price == "175"
	
	def test_delete_membership(self):
		
		"""
		Check that we can delete a membership properly.
		"""
		with self.app.app_context():
			# Login as admin first
			self.client.post("/admin/login", follow_redirects=True, data = self.admin_login)
			
			response = self.client.get("/admin/delete_membership/1?confirm=True", follow_redirects=True)
			assert response.status_code == 200
			assert b"Membership scheme 1 deleted" in response.data

			target = models.Memberships.query.where(models.Memberships.id == 1).first()
			assert not target

	def test_new_membership(self):
		"""
		Check that a manager can create a new membership.
		"""
		with self.app.app_context():
			# Login as admin first
			self.client.post("/admin/login", follow_redirects=True, data = self.admin_login)

			response = self.client.post(
				"/admin/new_membership", follow_redirects=True,
				data = {
					"name": "Test membership (get it?)",
					"months": 24,
					"price": 450
				}
			)

			assert response.status_code == 200
			assert b"New membership scheme created" in response.data

			new = models.Memberships.query.where(models.Memberships.name == "Test membership (get it?)").first()
			assert new

	def test_view_discount(self):
		"""
		Check that we get a list of discount schemes.
		"""
		with self.app.app_context():
			# Login as admin first
			self.client.post("/admin/login", follow_redirects=True, data = self.admin_login)

			response = self.client.get("/admin/discount")
			assert b"Discount" in response.data

	def test_edit_discount(self):
		"""
		Check that we can edit a discount properly.
		"""
		with self.app.app_context():
			# Login as admin first
			self.client.post("/admin/login", follow_redirects=True, data = self.admin_login)

			response = self.client.post(
				"admin/edit_discount/1", follow_redirects=True,
				data = {
					"new_name": "Discount 1 edit test",
					"new_value": 45,
					"new_session_number": 4
				}
			)

			assert response.status_code == 200
			target = models.Discounts.query.where(models.Discounts.id == 1).first()
			assert target.name == "Discount 1 edit test"
			assert target.value == 45
			assert target.session_number == 4
	
	def test_delete_discount(self):
		
		"""
		Check that we can delete a discount properly.
		"""
		with self.app.app_context():
			# Login as admin first
			self.client.post("/admin/login", follow_redirects=True, data = self.admin_login)
			
			response = self.client.get("/admin/delete_discount/1?confirm=True", follow_redirects=True)
			assert response.status_code == 200
			assert b"Discount scheme 1 deleted" in response.data

			target = models.Discounts.query.where(models.Discounts.id == 1).first()
			assert not target

	def test_new_discount(self):
		"""
		Check that a manager can create a new discount.
		"""
		with self.app.app_context():
			# Login as admin first
			self.client.post("/admin/login", follow_redirects=True, data = self.admin_login)

			response = self.client.post(
				"/admin/new_discount", follow_redirects=True,
				data = {
					"name": "Test discount (get it?)",
					"value": 60,
					"session_number": 5
				}
			)

			assert response.status_code == 200
			assert b"New discount scheme created" in response.data

			new = models.Discounts.query.where(models.Discounts.name == "Test discount (get it?)").first()
			assert new