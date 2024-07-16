# vertex/tests/test_classbooking.py

from app import create_app, models
from app.models import db
from flask_login import current_user
import datetime

class TestMembership:
	"""
	Class for testing membership system.
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
			
	def teardown_class(self):
		"""
		Deconstruct the test class.
		"""
		# Roll back any un-committed changes to the database and close it
		with self.app.app_context():
			self.db.session.rollback()
			self.db.session.close()
	
	def test_new_membership_page(self):
		"""
		Test for checking if new membership page loads successfullly.
		"""
		with self.app.app_context():
			with self.client:
				# Required to login
				self.client.post("/login", follow_redirects=True, data = {
					"email": "john@doe.com",
					"password": "Lemonade!1",
				})
				assert current_user.is_authenticated
				response = self.client.get("/new_membership")
				assert response.status_code == 200

	def test_my_memberships_page(self):
		"""
		Test for checking if my memberships page loads correctly.
		"""
		with self.app.app_context():
			with self.client:
				# Required to login
				self.client.post("/login", follow_redirects=True, data = {
					"email": "john@doe.com",
					"password": "Lemonade!1",
				})
				assert current_user.is_authenticated

				response = self.client.get("/my_memberships")
				assert response.status_code == 200

	def test_new_valid_membership(self):
		"""
		Test for checking if a new valid membership can be added successfully.
		"""
		with self.app.app_context():
			with self.client:
				# Required to login
				self.client.post("/login", follow_redirects=True, data = {
					"email": "john@doe.com",
					"password": "Lemonade!1",
				})
				assert current_user.is_authenticated

				# Testing adding a new valid membership
				valid_response = self.client.get('/new_membership/1', follow_redirects=True)
				assert valid_response.status_code == 200
				assert b'Successfully added your membership. Please proceed to payment.' in valid_response.data

				new_member = models.Users.query.where(models.Users.id == current_user.id).first()
				new_membership = models.ActiveMemberships.query.where(models.ActiveMemberships.user_id == current_user.id).first()
				assert new_member.is_member
				assert new_membership
				assert new_membership.member_from == datetime.date.today()
				

	def test_cancel_membership(self):
		"""
		Test for checking if a membership can be cancelled successfully.
		"""
		with self.app.app_context():
			with self.client:

				# Required to login
				self.client.post('/login', follow_redirects=True, data = {
					'email': 'member@email.com',
					'password': 'Member12345',
				})
				assert current_user.is_authenticated

				# Testing adding a new valid membership
				cancel_response = self.client.get('/cancel_membership', follow_redirects=True)
				assert cancel_response.status_code == 200
				assert b'Successfully canceled your membership' in cancel_response.data
				canceled_member = models.Users.query.where(models.Users.id == current_user.id).first()
				canceled_membership = models.ActiveMemberships.query.where(models.ActiveMemberships.user_id == current_user.id).first()
				assert canceled_member.is_member == False
				assert canceled_membership == None
				