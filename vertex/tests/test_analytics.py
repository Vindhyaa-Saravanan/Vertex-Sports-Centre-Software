# vertex/tests/test_analytics.py

from app import create_app, models
from app.models import db

class TestAnalytics:
	"""
	Class for testing analytics page.
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
	
	def test_facilities_analytics(self):
		"""
		Test for checking if facilities analytics page loads successfullly.
		"""
		with self.app.app_context():
			with self.client:
				# Login as admin
				response = self.client.post("/admin/login", follow_redirects=True, data = self.admin_login)
				assert response.status_code == 200
				assert b"Logged in as 3" in response.data
		
				response = self.client.get("/admin/analytics_facilities")
				assert response.status_code == 200
				
	def test_classes_analytics(self):
		"""
		Test for checking if classes analytics page loads successfullly.
		"""
		with self.app.app_context():
			with self.client:
				# Login as admin
				response = self.client.post("/admin/login", follow_redirects=True, data = self.admin_login)
				assert response.status_code == 200
				assert b"Logged in as 3" in response.data
		
				response = self.client.get("/admin/analytics_classes")
				assert response.status_code == 200

	def test_membership_analytics(self):
		"""
		Test for checking if membership analytics page loads successfullly.
		"""
		with self.app.app_context():
			with self.client:
				# Login as admin
				response = self.client.post("/admin/login", follow_redirects=True, data = self.admin_login)
				assert response.status_code == 200
				assert b"Logged in as 3" in response.data
		
				response = self.client.get("/admin/analytics_membership")
				assert response.status_code == 200