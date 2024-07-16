# vertex/tests/test_display_bookings.py

from unittest.mock import patch
from app import create_app, models
from app.models import db
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

class TestDisplayBooking:
	"""
	Class for testing display booking system.
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
			
	def test_booking_page_works(self):
		"""
		Test that the booking page works.
		"""
		with self.app.app_context():

			# Set the current user id to mock a logged in user
			with self.app.test_request_context():
				# Required to login
				self.client.post("/login", follow_redirects=True, data = {
					"email": "john@doe.com",
					"password": "Lemonade!1",
				})

				response = self.client.get('bookings')
				assert response.status_code == 200