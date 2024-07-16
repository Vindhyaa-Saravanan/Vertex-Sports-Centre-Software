# vertex/tests/test_user_login.py

from sqlalchemy import select

from flask_login import current_user

import argon2.exceptions as argon2_exc
import sqlalchemy.exc as sqlalchemy_exc

from app import create_app, models, register_extensions
from app.models import db

class TestUserLogin:
	"""
	Class for testing user login system.
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
	
	def teardown_class(self):
		"""
		Deconstruct the test class.
		"""
		# Roll back any un-committed changes to the database and close it
		with self.app.app_context():
			self.db.session.rollback()
			self.db.session.close()
	
	def test_user_login(self):
		"""
		Test that a user can log in.
		"""
		with self.app.app_context():
			with self.client:
				response = self.client.post("/login", follow_redirects=True, data = {
					"email": "john@doe.com",
					"password": "Lemonade!1",
				})
				assert response.status_code == 200
				assert current_user.is_authenticated