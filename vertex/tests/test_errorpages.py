# vertex/tests/test_classbooking.py

from app import create_app, models
from app.models import db
from werkzeug.exceptions import HTTPException

    
class TestErrorPages:
	"""
	Test Class to test custom error pages loading.
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

	def test_404_error_page(self):
		"""
		Test to check page not found error page.
		"""
		# Trying to load a non existent page
		with self.app.app_context():
			with self.client:
				response = self.client.get('/nonexistent-page')
				assert response.status_code == 404
				assert b"Sorry, this page seems to be taking a rest day. Let's redirect you to a more active one!" in response.data

	def test_401_error_page(self):
		"""
		Test to check access denied error page.
		"""
		# Trying to load the admin homepage without valid manager login
		with self.app.app_context():
			with self.client:
				response = self.client.get('/admin/')
				assert response.status_code == 401
				assert b"Looks like you don't have the necessary credentials to access this page. Time to redirect you to the right page!" in response.data

	def test_500_error_page(self):
		"""
		Test to check internal server error page.
		"""
		# Trying to load 
		if "DEBUG" in self.app.config and self.app.config["DEBUG"]:
			"""
			In debug mode, we preserve the useful built-in flask exception views.
			"""
			return
		
		with self.app.app_context():
			with self.client:
				response = self.client.get('/simulate500')
				assert response.status_code == 500
				assert b'Our server is taking a break, just like you should be! Take this opportunity to grab a water bottle and rehydrate while we work on resolving the issue!' in response.data

	def test_exception_page(self):
		"""
		Test to check internal server error page.
		"""
		# Trying to load 
		if "DEBUG" in self.app.config and self.app.config["DEBUG"]:
			"""
			In debug mode, we preserve the useful built-in flask exception views.
			"""
			return
		
		with self.app.app_context():
			with self.client:
				response = self.client.get('/simulateException')
				assert response.status_code == 200
				assert b'Oops! Something went wrong. In the meantime, you can try refreshing the page or navigating back to the previous page.' in response.data