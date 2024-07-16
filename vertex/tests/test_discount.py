# vertex/tests/test_discount.py

from app import create_app, models
from app.models import db

class TestDiscount:
	"""
	Class for testing discounts.
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
			
	def test_discount_works(self):
		"""
		Test that the default discount is applied as intended.
		"""
		with self.app.app_context():

			# Set the current user id to mock a logged in user
			with self.app.test_request_context():
				# Required to login
				self.client.post("/login", follow_redirects=True, data = {
					"email": "john@doe.com",
					"password": "Lemonade!1",
				})

				# Book two classes
				self.client.get('/classes/4', follow_redirects=True)
				self.client.get('/classes/5', follow_redirects=True)
				
				# Booking the third class
				response = self.client.get('/classes/6', follow_redirects=True)

				# Check that discount amount is displayed correctly
				assert response.status_code == 200
				booked_class = models.Classes.query.where(models.Classes.id == 6).first()
				assert str(int(booked_class.price * 0.35)).encode() in response.data
