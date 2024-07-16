# vertex/tests/test_classbooking.py

from unittest.mock import patch
from app import create_app, models
from app.models import db
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

class TestClassBooking:
	"""
	Class for testing class booking system.
	"""
	
	def setup_class(self):
		"""
		Set up the test class. Instantiate app, database...
		"""
		self.app = create_app()
		self.db = db
		self.models = models
		self.app.config['WTF_CSRF_ENABLED'] = False
		self.app.config['TESTING'] = True
		self.client = self.app.test_client()

		with self.app.app_context():
			self.models.reset_database()
			self.models.populate_database()
		
		self.valid_login = {
			"email": "john@doe.com",
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

	def test_classes_runs(self):
		"""
		Test for checking if classes page loads correctly.
		"""
		with self.app.app_context():
			response = self.client.get("/classes")
			assert response.status_code == 200
			
	def test_valid_class_booking_customer(self):
		"""
		Test that a valid class booking is added as intended.
		"""
		with self.app.app_context():

			# Set the current user id to mock a logged in user
			with self.app.test_request_context():
				# Required to login
				self.client.post("/login", follow_redirects=True, data = {
					"email": "john@doe.com",
					"password": "Lemonade!1",
				})

				# Testing the response of the booking view, following all redirects
				response = self.client.get('/classes/4', follow_redirects=True)

				# Check that it redirects successfully and flashes correct message
				assert response.status_code == 200
				booking = models.ClassBookings.query.where(models.ClassBookings.class_id == 4).first()
				user = models.Users.query.where(models.Users.id == 1).first()
				assert booking in user.class_bookings

	def test_invalid_class_booking_customer(self):
		"""
		Test that an invalid class booking is rejected as intended.
		"""
		with self.app.app_context():

			# Set the current user id to mock a logged in user
			with self.app.test_request_context():
				# Required to login
				self.client.post("/login", follow_redirects=True, data = {
					"email": "john@doe.com",
					"password": "Lemonade!1",
				})

				# Testing the response of the booking view, following all redirects
				response = self.client.get('/classes/0', follow_redirects=True)

				# Check that it redirects successfully and flashes correct message
				assert response.status_code == 200
				assert b'No such class exists.' in response.data

	def test_valid_class_booking_employee(self):
		"""
		Test that a valid class booking is added as intended.
		"""
		with self.app.app_context():

			# Set the current user id to mock a logged in user
			with self.app.test_request_context():

				# Required to login
				self.client.post("/employee-login", follow_redirects=True, data = {
					"email": "lily@poole.com",
					"password": "Lemonade!1",
				})

				# Testing the response of the booking view, following all redirects
				response=self.client.post('/classes/2', follow_redirects=True, data={
					"user_class_booked": "john@doe.com"
					})

				# Check that it redirects successfully and flashes correct message
				assert response.status_code == 200
				new_booking = models.ClassBookings.query.where(models.ClassBookings.class_id == 2).first()
				user = models.Users.query.where(models.Users.email == 'john@doe.com').first()
				assert new_booking in user.class_bookings