# vertex/tests/test_email_confirmation.py
# based on ideas from:
# https://www.freecodecamp.org/news/setup-email-verification-in-flask-app/
# https://pythonhosted.org/Flask-Mail/

from unittest.mock import patch
from app import create_app, models
from app.models import db
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError
import os

# For the email confirmation
from app.email import send_email
from app.token import generate_token, confirm_token
import datetime

class TestEmailConfirmationToken:
	"""
	Class for testing email confirmation feature.
	"""
	# SETUP AND TEARDOWN
	
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
			
	def teardown_class(self):
		"""
		Deconstruct the test class.
		"""
		# Roll back any un-committed changes to the database and close it
		with self.app.app_context():
			self.db.session.rollback()
			self.db.session.close()

	def test_already_confirmed_user(self):
		"""
		Testing whether email confirmation redirects an already confirmed user.
		"""
		with self.app.app_context():
			with self.client:
				self.client.get("/logout", follow_redirects=True)
				self.client.post("/login", follow_redirects=True, data = {
					"email": "confirmeduser@email.com",
					"password": "confirmeduser",
				})
				assert current_user.is_authenticated
				
				token = generate_token('confirmeduser@email.com')
				test_token_response = self.client.get('/confirm/'+token, follow_redirects=True)
				assert b'This email address has been already confirmed.' in test_token_response.data
	
	def test_confirm_valid_token(self):
		"""
		Testing whether email confirmation works for a valid token.
		"""
		with self.app.app_context():
			with self.client:

				# Sign up a new unconfirmed user and follow all redirects
				self.client.get('/logout', follow_redirects=True)
				signup_response = self.client.post('/customer-signup', 
				       data=dict(email='unconfirmeduser@email.com', first_name='Unconfirmed', last_name='User', password1='unconfirmeduser', password2='unconfirmeduser', date_of_birth=datetime.date(1990, 3, 3)), 
					   follow_redirects=True)
				assert b'Account created! A email to confirm your email address has been sent.' in signup_response.data

				# Generate token and simulate the user clicking on the button in the email
				token = generate_token('unconfirmeduser@email.com')
				test_token_response = self.client.get('/confirm/'+token, follow_redirects=True)
				assert test_token_response.status_code == 200

				# Check if confirmation records have been updated
				newly_confirmed_user = models.Users.query.filter_by(email='unconfirmeduser@email.com').first()
				assert newly_confirmed_user.confirmed_on == datetime.date.today()
				assert newly_confirmed_user.is_confirmed == True

	def test_confirm_invalid_token(self):
		"""
		Testing whether email confirmation rejects an invalid token.
		"""
		with self.app.app_context():
			with self.client:
				self.client.post("/login", follow_redirects=True, data = {
					"email": "invalidtokenuser@email.com",
					"password": "invalidtokenuser",
				})
				assert current_user.is_authenticated

				# Test with a token generated using the wrong email to ensure invalid token
				token = generate_token('wrongemail@email.com')
				test_token_response = self.client.get('/confirm/'+str(token), follow_redirects=True)
				assert test_token_response.status_code == 200

	def test_confirm_expired_token(self):
		"""
		Testing whether email confirmation rejects an expired token.
		"""
		with self.app.app_context():
			with self.client:
				self.client.get("/logout", follow_redirects=True)
				self.client.post("/login", follow_redirects=True, data = {
					"email": "expiredtokenuser@email.com",
					"password": "expiredtokenuser",
				})
				assert current_user.is_authenticated
				
				# Test with expiration time of -1, guaranteeing no token can be considered as valid
				token = generate_token('expiredtokenuser@email.com')
				assert confirm_token(token, -1) == False