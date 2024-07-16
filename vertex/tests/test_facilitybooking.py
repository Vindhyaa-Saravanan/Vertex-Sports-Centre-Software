from unittest.mock import patch
from app import create_app, models
from app.models import db
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError
import datetime

class TestFacilityBooking:
    """
    Class for testing facility booking system
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
			
    def test_facilities_runs(self):
        """
        Test for checking if facilities page loads correctly.
        """
        with self.app.app_context():
            response = self.client.get("/facilities")
            assert response.status_code == 200
			
    def test_valid_facility_booking_customer(self):
        """
        Test that a valid facility booking is added as intended.
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
                response = self.client.post('/facility/4', follow_redirects=True, data = {
                    "activity" : "1 hour sessions",
                    "date_chosen": datetime.date(2023, 10, 1),
                    "start_time" : datetime.time(8),
                    "end_time" : datetime.time(9),
                })
           
                # Check that it redirects successfully and flashes correct message
                assert response.status_code == 200
                new_booking = models.FacilityBookings.query.where(models.FacilityBookings.facility_id == 4).first()
                user = models.Users.query.where(models.Users.email == 'john@doe.com').first()
                assert new_booking in user.facility_bookings

    def test_invalid_facility_booking_customer(self):
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
                response = self.client.get('/facility/0', follow_redirects=True)

                # Check that it redirects successfully and flashes correct message
                assert response.status_code == 200
                assert b'No such facility found' in response.data

    def test_valid_facility_booking_employee(self):
        """
        Test that a valid facility booking by an employee is added as intended.
        """
        with self.app.app_context():

            # Set the current user id to mock a logged in user
            with self.app.test_request_context():
                # Required to login
                self.client.post("/login", follow_redirects=True, data = {
                    "email": "lily@poole.com",
                    "password": "Lemonade!1",
                })

                # Testing the response of the booking view, following all redirects
                response = self.client.post('/facility/5', follow_redirects=True, data = {
                    "user_booked" : "john@doe.com",
                    "activity" : "1 hour sessions",
                    "date_chosen": datetime.date(2023, 10, 1),
                    "start_time" : datetime.time(8),
                    "end_time" : datetime.time(9),
                })
           
                # Check that it redirects successfully and flashes correct message
                assert response.status_code == 200
                new_booking = models.FacilityBookings.query.where(models.FacilityBookings.facility_id == 5).first()
                user = models.Users.query.where(models.Users.email == 'john@doe.com').first()
                assert new_booking in user.facility_bookings


