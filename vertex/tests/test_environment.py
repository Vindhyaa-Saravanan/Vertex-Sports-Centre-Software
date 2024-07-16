# vertex/tests/test_environment.py

import os

class TestEnvironment:
	"""
	Class for testing that the environment has the right variables.
	"""
		
	def test_secret_key(self): 
		assert len(os.getenv("SECRET_KEY")) > 5
	
	def test_email_variables(self):
		assert len(os.getenv("TOKEN_SALT")) > 5
		assert len(os.getenv("EMAIL_PASSWORD")) > 5