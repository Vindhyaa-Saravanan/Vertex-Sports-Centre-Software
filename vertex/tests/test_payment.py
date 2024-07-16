# vertex/tests/test_payment.py

import pytest
import datetime
from app import create_app

"""
https://docs.pytest.org/en/7.1.x/how-to/assert.html
"""
'''
class TestPayment:

	#Class for testing payment.html
	
	
	def setup_class(self):

		self.app = create_app()
		self.client = self.app.test_client()
		self.app.config['WTF_CSRF_ENABLED'] = False

	def test_filled_form(self):
		response = self.client.post("/payment", data={
			"name": "John",
			"cardnumber": "7865437846785436",
			"expirymonth": "5",
			"expiryyear": "24",
			"securitycode": "345"
		})
		assert b"payment accepted" in response.data
		
'''