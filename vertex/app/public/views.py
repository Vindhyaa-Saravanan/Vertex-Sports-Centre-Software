# vertex/app/public/views.py
"""
Views for the "public" blueprint.
"""
import os
import datetime
from .. import models
import stripe
from ..extensions import stripe_keys
import datetime
from dateutil.relativedelta import relativedelta

from flask_login import current_user, login_required
from sqlalchemy.exc import SQLAlchemyError

from flask import (
	Blueprint,
	render_template,
	current_app,
	request,
	flash,
	redirect,
	abort,
	url_for,
	make_response,
)

from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
from xhtml2pdf import pisa

from .forms import (
	UserLogin,
	CustomerSignUpForm,
	employeeForm,
	confirmationForm,
)
from .forms import (
	UserLogin, CustomerSignUpForm, confirmationForm
)


from ..models import (
	Facilities, Classes, Users, ActiveMemberships, db, ClassBookings
)

from flask_login import (
	login_required,
	login_user,
	logout_user,
	current_user
)

import datetime
from dateutil.relativedelta import relativedelta

# For the email confirmation
from app.email import send_email
from app.token import generate_token, confirm_token
from flask import app
from app.models import ClassBookings, Classes
from flask_login import current_user, login_required
from sqlalchemy.exc import SQLAlchemyError
from .forms import CustomerSignUpForm
from ..models import Facilities, Classes, Users, Users, ActiveMemberships

blueprint = Blueprint("public", __name__, static_folder="../static")

# VIEWS FOR THIS BLUEPRINT

@blueprint.route("/", methods=["GET"])
def index():
	"""
	Route to application index page.
	"""
	current_app.logger.info("Loading index.")
	return render_template("index.html", title = "Home | Vertex")

# CUSTOM ERROR TESTING VIEWS
@blueprint.route("/simulate500")
def simulate500():
	"""
	Route to simulate 500 error.
	"""
	abort(500)

@blueprint.route("/simulateException")
def simulateException():
	"""
	Route to simulate Exception error.
	"""
	raise Exception

# USER MANAGEMENT VIEWS

# User login route
@blueprint.route('/login', methods=['GET', 'POST'])
def login():
	"""
	Route to user login page.
	"""
	form = UserLogin()
	if form.validate_on_submit():
		email = form.email.data
		password = form.password.data
		user = models.Users.query.where(models.Users.email == email, models.Users.user_type == "user").first()
		if user:
			if user.verify_password(password):
				flash('Logged in successfully!', category='success')
				login_user(user, remember=False)
				current_app.logger.info("User ID " + str(user.id) + " logged in at " + str(datetime.datetime.now()))
				return redirect(url_for('public.index'))
			else:
				flash('Incorrect password, try again.', category='danger')
				current_app.logger.info("User ID " + str(user.id) + " attempted login unsuccessfully at " + str(datetime.datetime.now()))
		else:
			flash('User account does not exist.', category='danger')
	return render_template("user_login.html", title = "Login | Vertex", user=current_user, form=form)

# Employee login route
@blueprint.route('/employee-login', methods=['GET', 'POST'])
def employeelogin():
	"""
	Route to employee login page.
	"""
	form = UserLogin()
	if form.validate_on_submit():
		email = form.email.data
		password = form.password.data
		user = models.Users.query.where(
			models.Users.email == email, models.Users.user_type == "employee").first()
		if user:
			if user.verify_password(password):
				flash('Logged in successfully!', category='success')
				current_app.logger.info("User ID (Employee) " + str(user.id) + " logged in at " + str(datetime.datetime.now()))
				login_user(user, remember=False)
				return redirect(url_for('public.index'))
			else:
				flash('Incorrect password, try again.', category='danger')
				current_app.logger.info("User ID " + str(user.id) + " attempted login unsuccessfully at " + str(datetime.datetime.now()))
		else:
			flash('User account does not exist.', category='danger')

	return render_template("employee_login.html", title=" Employee Login | Vertex", user=current_user, form=form)

# User logout view
@blueprint.route("/logout", methods=["GET"])
def logout():
	"""
	Route to user logout page.
	"""
	logout_user()
	return redirect(url_for('public.login'))

# Customer signup route
@blueprint.route('/customer-signup', methods=['GET', 'POST'])
def sign_up():
	"""
	Route to user signup page.
	"""
	signup_form = CustomerSignUpForm()
	if signup_form.validate_on_submit():
		email = signup_form.email.data
		first_name = signup_form.first_name.data
		last_name = signup_form.last_name.data
		password1 = signup_form.password1.data
		password2 = signup_form.password2.data
		date_of_birth = signup_form.date_of_birth.data

		user = models.Users.query.where(models.Users.email==email).first()
		if user:
			flash('Email already exists.', category="danger")
		elif len(email) < 10:
			flash('Email must be greater than 10 characters.', category="danger")
		elif len(first_name) < 2:
			flash('First name must be greater than 1 character.', category='error')
		elif len(last_name) < 2:
			flash('First name must be greater than 1 character.', category='error')
		elif password1 != password2:
			flash('Passwords don\'t match.', category="danger")
		elif len(password1) < 8:
			flash('Password must be at least 8 characters.', category='error')
		elif date_of_birth > datetime.date.today()-relativedelta(years=18):
			flash('You should be over the age of 18 .', category='error')
		else:
			#new_user = models.Users(email=email, firstname=first_name, lastname=last_name, password=password1, date_of_birth=date_of_birth, user_type ="user")
			new_user = models.Users(email=email, firstname=first_name, lastname=last_name, password=password1, date_of_birth=date_of_birth, user_type='user')
			db.session.add(new_user)
			current_app.logger.info("New user ID " + str(new_user.id) + " added at " + str(datetime.datetime.now()))
			try:
				db.session.commit()
				current_app.logger.info("Added new user.")

				# based on ideas from:
				# https://www.freecodecamp.org/news/setup-email-verification-in-flask-app/
				# https://pythonhosted.org/Flask-Mail/

				# Generate confirmation token and confirmation url
				token = generate_token(email)
				confirm_url = url_for('public.confirm_email', token=token, _external=True)

				# Render template for confirmation page, pass in url
				email_html_template = render_template('email_template.html', confirm_url=confirm_url)

				# Define parts of email and send the email
				email_subject = 'Vertex Sports | Confirm Email'
				if "PYTEST_CURRENT_TEST" not in os.environ:
					send_email(recipient=new_user.email, subject=email_subject, email_template=email_html_template)
					current_app.logger.info("Sent confirmation email to user ID " + str(new_user.id) + " at " + str(datetime.datetime.now()))
				else:
					current_app.logger.info("Not sending confirmation email, we're testing...")

				login_user(new_user, remember=True)
				current_app.logger.info("Newly created user ID " + str(new_user.id) + " logged in at " + str(datetime.datetime.now()))

				# Tell user that account is created, verification email is sent
				# Then redirect them to index
				flash("Account created! A email to confirm your email address has been sent.", category="success")
				return redirect(url_for('public.unconfirmed'))

			except:
				flash('Error in account creation.', category='error')
				current_app.logger.info("Account not created. Redirecting to signup...")
				return redirect(url_for('public.sign_up'))
	
	return render_template('customer_signup.html', title = "Sign Up | Vertex", form=signup_form)

# EMAIL VERIFICATION RELATED ROUTES

# based on ideas from:
# https://www.freecodecamp.org/news/setup-email-verification-in-flask-app/
# https://pythonhosted.org/Flask-Mail/
@blueprint.route('/unconfirmed')
@login_required
def unconfirmed():
	"""
	Check if user is confirmed or not, and redirect accordingly.
	"""
	# If user is already confirmed and happens to try again
	if current_user.is_confirmed:
		flash('This email address has been already confirmed.', category = 'success')
		current_app.logger.info("User ID " + str(current_user.id) + " is already confirmed. Redirecting to index...")
		return redirect(url_for('public.index'))
	
	return render_template('unconfirmed_email.html', title = "Confirm your Email | Vertex")

# based on ideas from:
# https://www.freecodecamp.org/news/setup-email-verification-in-flask-app/
# https://pythonhosted.org/Flask-Mail/
@blueprint.route('/resend_confirmation')
@login_required
def resend_confirmation():
	"""
	Route to resend a email confirmation token email if user clicks the button.
	"""
	# If user is already confirmed and happens to try again
	if current_user.is_confirmed:
		flash('This email address has been already confirmed.', category = 'success')
		current_app.logger.info("User ID " + str(current_user.id) + " is already confirmed. Redirecting to index...")
		return redirect(url_for('public.index'))
	
	# Else define email and resend
	token = generate_token(current_user.email)
	confirm_url = url_for('public.confirm_email', token=token, _external=True)
	email_html_template = render_template('email_template.html', confirm_url=confirm_url)
	email_subject = 'Vertex Sports | Confirm Email - Resent'
	send_email(recipient=current_user.email, subject=email_subject, email_template=email_html_template)
	
	# Inform user of new email, take to unconfirmed page
	flash('A new confirmation email has been sent to your email address.', category = 'success')
	current_app.logger.info("Email resent to " + str(current_user.id) +  ". Redirecting to unconfirmed...")
	return redirect(url_for('public.unconfirmed'))

# based on ideas from:
# https://www.freecodecamp.org/news/setup-email-verification-in-flask-app/
# https://pythonhosted.org/Flask-Mail/
@blueprint.route('/confirm/<token>')
@login_required
def confirm_email(token):
	"""
	Route for confirming email confirmation token.
	"""
	# If user is already confirmed and happens to try again
	if current_user.is_confirmed:
		flash('This email address has been already confirmed.', category = 'success')
		current_app.logger.info("User ID " + str(current_user.id) + " is already confirmed. Redirecting to index...")
		return redirect(url_for('public.index'))
	
	# Confirm the token is valid and find user
	newly_confirmed_user_email = confirm_token(token)
	newly_confirmed_user = Users.query.filter_by(email=newly_confirmed_user_email).first()
	
	# If the confirmation was valid, and such a user and email exists, record details
	if newly_confirmed_user:
		newly_confirmed_user = Users.query.filter_by(email=newly_confirmed_user_email).first()
		newly_confirmed_user.is_confirmed = True
		newly_confirmed_user.confirmed_on = datetime.date.today()
		db.session.add(newly_confirmed_user)
		db.session.commit()
		flash('You have successfully confirmed your email address.', 'success')
		current_app.logger.info("Email for user ID " + str(current_user.id) + " confirmed successfully. Redirecting to index...")
		return redirect(url_for('public.index'))
	
	# If either token was invalid or expiration time has finished, no valid email will be returned.
	# In that case let user resend email to try again.
	elif not newly_confirmed_user:
		flash('The confirmation link is invalid or has expired.', 'danger')
		current_app.logger.info("User ID " + str(current_user.id) + " attempted to confirm email with expired token. Redirecting to resend confirmation...")
		return redirect(url_for('public.resend_confirmation'))

# PAYMENT VIEWS

@login_required
@blueprint.route("/payment/<int:price>", methods=["GET", "POST"])
def payment(price):
	"""
	Route to payment page.
	"""
	amount = int(str(price) + '00')
	oldamount = amount

	confirm = request.args.get("confirm")

	# Find out how many sessions current user has in the next 2 weeks
	user_sessions = 0

	user_classes = models.ClassBookings.query.where(models.ClassBookings.user_id == current_user.id)
	for item in user_classes:
		user_sessions += 1

	user_facilities = models.FacilityBookings.query.where(models.FacilityBookings.user_id == current_user.id)
	for item in user_facilities:
		user_sessions += 1

	# Get all discounts from discounts table
	all_discounts = models.Discounts.query.where(models.Discounts.session_number <= user_sessions)

	# For each discount in the list, if session_number = no of users sessions, discountvalue/100 * amount
	for discount in all_discounts:
		offamount = discount.value / 100 * amount
		amount = int(amount - offamount)
		price=amount/100
		current_app.logger.info("Discount ID " + str(discount.id) + " applied.")
	
	if current_user.payment_customer_id and current_user.payment_card_id:
		# The user has already paid for something before and has saved payment details


		# Check if the customer has confirmed the paynment
		if not confirm:
			return redirect(url_for("public.confirm_payment", price=price, redirect=request.path))

		# gets the customer and card ids of the already existing customer
		customer_id = current_user.payment_customer_id
		card_id = current_user.payment_card_id

		# Retrieve the customer object from Stripe using the customer ID
		customer = stripe.Customer.retrieve(customer_id)

		# charge the returning customer
		charge = stripe.Charge.create(
			customer=customer.id,
			source=card_id,
			amount=amount,
			currency='gbp',
			description='Flask Charge'
		)

		return render_template('charge.html', title="Charge Portal | Vertex", amount=amount, price=price, discount=(oldamount-amount)*100/oldamount)

	return render_template('payment.html', title="Payment Portal | Vertex", key=stripe_keys['publishable_key'], email=current_user.email, amount=amount, price=price)


@blueprint.route("/charge/<int:amount>", methods=["POST"])
@login_required
def charge(amount):
	"""
	courtesy of https://stripe.com/docs/legacy-checkout/flask?locale=en-GB
	Route to Stripe charging customer.
	"""
	price = amount
	topay = int(str(amount) + '00')
	oldamount = amount

	confirm = request.args.get("confirm")

	# Find out how many sessions current user has in the next 2 weeks
	user_sessions = 0

	user_classes = models.ClassBookings.query.where(models.ClassBookings.user_id == current_user.id)
	for item in user_classes:
		user_sessions += 1

	user_facilities = models.FacilityBookings.query.where(models.FacilityBookings.user_id == current_user.id)
	for item in user_facilities:
		user_sessions += 1

	# Get all discounts from discounts table
	all_discounts = models.Discounts.query.where(models.Discounts.session_number <= user_sessions)

	# For each discount in the list, if session_number = no of users sessions, discountvalue/100 * amount
	for discount in all_discounts:
		offamount = discount.value / 100 * amount
		amount = int(amount - offamount)

	# Query the database for the current user
	user = Users.query.filter_by(id=current_user.id).first()

	# decide if the user has made a payment before or not
	if user.payment_customer_id and user.payment_card_id:
		# The user has already paid for something before and has saved payment details

		# Check if the customer has confirmed the paynment
		if not confirm:
			return redirect(url_for("public.confirm_payment", price=price, redirect=request.path))

		# gets the customer and card ids of the already existing customer
		customer_id = current_user.payment_customer_id
		card_id = current_user.payment_card_id

		# Retrieve the customer object from Stripe using the customer ID
		customer = stripe.Customer.retrieve(customer_id)

		# charge the returning customer
		charge = stripe.Charge.create(
			customer=customer.id,
			source=card_id,
			amount=topay,
			currency='gbp',
			description='Flask Charge'
		)

		current_app.logger.info("User ID " + str(current_user.id) + " payment charged successfully.")

	else:
		# The user has not paid for anything yet

		# creates a new stripe customer
		customer = stripe.Customer.create(
			email=user.email,
			source=request.form['stripeToken']
		)

		# updates the database to add the new customers customer id and card id
		current_user.payment_customer_id = customer.id
		current_user.payment_card_id = customer.default_source
		db.session.commit()

		# charge the newly made customer
		charge = stripe.Charge.create(
			customer=current_user.payment_customer_id,
			source=customer.default_source,
			amount=topay,
			currency='gbp',
			description='Flask Charge'
		)

		current_app.logger.info("User ID " + str(current_user.id) + " payment charged successfully.")

	return render_template('charge.html', title="Charge Portal | Vertex", amount=amount, price=price, discount=(oldamount-amount)*100/oldamount)

@login_required
@blueprint.route("/confirm_payment", methods=["GET"])
def confirm_payment():
	price = request.args.get("price")
	redirect = request.args.get("redirect")

	return render_template("confirm_payment.html", price=price, redirect=redirect)

# PAYMENT FOR MEMBERSHIPS

@login_required
@blueprint.route("/payment_membership/<int:price>", methods=["GET", "POST"])
def payment_membership(price):
	"""
	Route to payment without discount page.
	"""
	amount = int(str(price) + '00')

	confirm = request.args.get("confirm")
	
	if current_user.payment_customer_id and current_user.payment_card_id:
		# The user has already paid for something before and has saved payment details

		# Check if the customer has confirmed the paynment
		if not confirm:
			return redirect(url_for("public.confirm_payment", price=price, redirect=request.path))

		# gets the customer and card ids of the already existing customer
		customer_id = current_user.payment_customer_id
		card_id = current_user.payment_card_id

		# Retrieve the customer object from Stripe using the customer ID
		customer = stripe.Customer.retrieve(customer_id)

		# charge the returning customer
		charge = stripe.Charge.create(
			customer=customer.id,
			source=card_id,
			amount=amount,
			currency='gbp',
			description='Flask Charge'
		)

		#return redirect('/charge/' + str(amount))
		return render_template('charge.html', title="Charge Portal | Vertex", amount=amount, price=price)

	return render_template('payment.html', title="Payment Portal | Vertex", key=stripe_keys['publishable_key'], email=current_user.email, amount=amount, price=price)

# CLASS RELATED VIEWS

@blueprint.route("/classes", methods=["GET"])
def classes():
	"""
	Route to gym classes list page.
	"""
	# Get classes ordered by class id.
	classObj = Classes.query.order_by(Classes.id).all()
	classes = []

	# Get the data from the database.
	for c in classObj:
		if c.date >= datetime.datetime.now().date():
			classes.append(
				{
					"id": c.id,
					"name": c.name,
					"start": c.start,
					"end": datetime.time(c.start.hour + c.duration),
					"duration": c.duration,
					"price":c.price,
					"date": c.date,
				}
			)
	return render_template('classes.html', title = "Gym Classes | Vertex", classes=classes)

@blueprint.route('/classes/<int:class_id>', methods=["GET", "POST"])
def id_class(class_id):
	"""
	Route to booking a class as customer or employee.
	"""
	# check if the user isnt a employee
	if current_user.user_type == "user":
		# Convert class id to int
		int_class_id = int(class_id)
	
		if request.method == 'GET' or request.method == 'GET':
			# Check this is a valid class id
			target = models.Classes.query.where(models.Classes.id == int_class_id).first() 
			
			if not target:
				flash('No such class exists.', category="danger")
				current_app.logger.info("Class ID " + str(class_id) + " not found for booking.")
				return redirect('/classes')
			
			# if target.date < datetime.datetime.now().date():
			# 	flash('Cannot book a past class.', category="danger")
			# 	current_app.logger.info("Class ID " + str(class_id) + " not bookable.")
			# 	return redirect('/classes')
		
			# Create record for this new booking
			class_booking = ClassBookings(user_id=current_user.id, class_id=int_class_id)

			# Try to update database with this booking record and
			# Commit changes of this database session to database
			try:
				db.session.add(class_booking)
				db.session.commit()
		   		# Direct user to class booking payment page on successful booking
				flash('Successfully booked class. Please proceed to payment.', category="success")
				current_app.logger.info("User ID " + str(current_user.id) + " booked class ID " + str(class_id) + " successfully.")
				return redirect('/payment/' + str(target.price))

			# Catching database errors
			except SQLAlchemyError:
				flash('Unable to book class.', category="danger")
				current_app.logger.info("User ID " + str(current_user.id) + " not able to book class ID " + str(class_id) + " due to database error.")
				return redirect('/classes')

	elif current_user.user_type == "employee":
		# The form details
		form = employeeForm()

		classbook = Classes.query.where(Classes.id == class_id).first()

		if classbook:
			class_name = classbook.name

			if form.validate_on_submit():
				user_booked = request.form.get('user_class_booked')
				user = Users.query.where(Users.email == user_booked).first()
				if not user:
					flash(f"No such user: {user_booked}", "error")
					current_app.logger.info("User ID " + str(current_user.id) + " of customer not found when attempting to book class ID " + str(class_id) + " by employee ID " + str(current_user.id) + "on behalf.")
					return redirect('/classes')

				uid = int(user.id)

				# book the class and add to database
				class_booking = ClassBookings(user_id=uid, class_id=class_id)

				try:
					db.session.add(class_booking)
					db.session.commit()
					flash('Booking created!', category='success')
					current_app.logger.info("User ID " + str(current_user.id) + " booked class ID " + str(class_id) + " successfully by employee ID " + str(current_user.id) + "on behalf.")
					return redirect('/payment/' + str(classbook.price))

				except Exception as e:
					flash(f"Error in booking: {e.__repr__()}.", category="danger")
					current_app.logger.info("User ID " + str(current_user.id) + " unable to book class ID " + str(class_id) + " by employee ID " + str(current_user.id) + "on behalf.")
					return redirect("/classes")
		
		return render_template("confirmation_class.html", title=class_name + " Confirmation", class_name=class_name, class_id=class_id, form=form, current_user=current_user)
	
# BOOKINGS RELATED VIEWS

@blueprint.route('/bookings/<int:id>', methods=['POST', 'GET'])
def delete_booking(id):
	"""
	Route to delete a booking.
	"""
	booking_type = request.args.get("booking_type")

	if booking_type == "class":
		booking = models.ClassBookings.query.where(models.ClassBookings.id == id).first()
	elif booking_type == "facility":
		booking = models.FacilityBookings.query.where(models.FacilityBookings.id == id).first()
	
	if not booking:
		flash("No such booking to delete", category="warning")
	else:
		db.session.delete(booking)
		try:
			db.session.commit()
			flash(f"Booking {id} deleted.", category="success")
			current_app.logger.info("Booking ID " + str(id) + " deleted successfully on " + str(datetime.datetime.now()))
			return redirect(url_for("public.bookings"))
		except Exception as e:
			current_app.logger.error(e)
			db.session.rollback()
			flash(f"Deletion failed. Database error {repr(e)}", category="danger")
			current_app.logger.info("Deletion of booking ID " + str(id) + " failed on " + str(datetime.datetime.now()))
	
	return redirect(url_for("public.bookings"))

@blueprint.route("/bookings", methods=["GET"])
def bookings():
	"""
	Route to user's bookings.
	"""
	# Get classes ordered by class id.
	classbookingsObj = current_user.class_bookings
	classes = []
	facilitybookingsObj = current_user.facility_bookings
	facilities = []

	# Get the class data from the database.
	for class_booking in classbookingsObj:
		c = models.Classes.query.where(models.Classes.id == class_booking.class_id).first()
		classes.append(
			{
				"id": class_booking.id,
				"name": c.name,
				"start": c.start,
				"duration": c.duration,
				"price":c.price,
				"date": c.date,
			}
		)

	# Get the facility data from the database.
	for facility_booking in facilitybookingsObj:
		f = models.Facilities.query.where(models.Facilities.id == facility_booking.facility_id).first()

		facilities.append(
			{
				"id": facility_booking.id,
				"name": f.name,
				"activity": facility_booking.activity,
				"start": facility_booking.start,
				"end": facility_booking.end,
				"date": facility_booking.date,
				"price": facility_booking.price
			}
		)
	return render_template('bookings.html', title='Booked Classes', classes=classes, facilities=facilities)

@blueprint.route("/classes/remove/<int:class_booking_id>", methods=["GET"])
@login_required
def remove_class_booking(class_booking_id):
	"""
	Route to remove a class booking.
	"""
	booking = models.ClassBookings.query.where(models.ClassBookings.id == class_booking_id).first()

	if not booking:
		flash("No such class booking", category="error")
		current_app.logger.info("Class booking ID " + str(id) + " not found on " + str(datetime.datetime.now()))
		return redirect(url_for("public.bookings"))
	elif booking.user_id != current_user.id:
		flash("You may only cancel your own class bookings", category="error")
		current_app.logger.info("User ID " + str(current_user.id) + " attempted to delete bookings other than own on " + str(datetime.datetime.now()))
		return redirect(url_for("public.bookings"))
	
	db.session.delete(booking)

	try:
		db.session.commit()
		flash("Cancelled class booking", category="success")
		current_app.logger.info("Class booking ID " + str(id) + " canceled successfully on " + str(datetime.datetime.now()))
		return redirect(url_for("public.bookings"))
	except Exception as e:
		db.session.rollback()
		current_app.logger.info("Class booking ID " + str(id) + " unable to cancel due to database error: " + e)
		flash("Database error: " + e, category="error")
		return redirect(url_for("public.bookings"))


@blueprint.route("/facilities/remove/<int:facility_booking_id>", methods=["POST"])
@login_required
def remove_facility_bookings(facility_booking_id):
	"""
	Route to remove a facility booking.
	"""
	booking = models.FacilityBookings.query.where(models.FacilityBookings.id == facility_booking_id).first()

	if not booking:
		flash("No such facility booking", category="error")
		current_app.logger.info("Class booking ID " + str(facility_booking_id) + " not found on " + str(datetime.datetime.now()))
		return redirect(url_for("public.bookings"))
	elif booking.user_id != current_user.id:
		flash("You may only cancel your own facility bookings", category="error")
		current_app.logger.info("User ID " + str(current_user.id) + " attempted to delete bookings other than own on " + str(datetime.datetime.now()))
		return redirect(url_for("public.bookings"))
	
	db.session.delete(booking)

	try:
		db.session.commit()
		flash("Cancelled facility booking", category="success")
		current_app.logger.info("Facility booking ID " + str(id) + " canceled successfully on " + str(datetime.datetime.now()))
		return redirect(url_for("public.bookings"))
	except Exception as e:
		db.session.rollback()
		current_app.logger.info("Facility booking ID " + str(id) + " unable to cancel due to database error: " + e)
		flash("Database error: " + e, category="error")
		return redirect(url_for("public.bookings"))

# FACILITIES RELATED VIEWS

@blueprint.route("/facilities", methods=["GET"])
def facilities():
	"""
	Route to view all available facilities page.
	"""
	# gets the facilities in alphabetical order
	facilityObjs = Facilities.query.order_by(Facilities.name).all()
	facilities = []

	for f in facilityObjs:  # loops through each member of the facilities database and adds them to a list
		activities = f.activities
		activity_names = []
		activity_prices = []
		for activity_name, price in activities.items():
			activity_names.append(activity_name)
			activity_prices.append(price)
			
		facilities.append({
			"id": f.id,
			"name": f.name,
			"open": f.open,
			"close": f.close,
			"capacity": f.capacity,				
			"activities":activity_names,
			"prices":activity_prices,
			"session duration": f.session_duration
		})
	return render_template('facilities.html', title="Gym Facilities | Vertex", facilities=facilities)


# Facility Confirmation page
@blueprint.route("/facility/<int:facility_id>", methods=["GET", "POST"])
def facility_view(facility_id):
	"""
	Route to facility booking confirmation form page.
	"""
	facility = Facilities.query.where(Facilities.id == facility_id).first()

	# user_booked choices
	userobjs = Users.query.order_by(Users.email).all()

	if facility:
		facility_name = facility.name
		# The form details
		form = confirmationForm()

		# creating dropdown for the activities for the facility
		activity_list = []

		for activity in facility.activities:
			activity_list.append(activity)


		form.activity.choices = activity_list

		# creating dropdowns for starting time
		start_times = []
		for hour in range(facility.open.hour,facility.close.hour):
			for minute in [0, 30]:
				time = datetime.time(hour, minute)
				start_times.append(time)
			
		form.start_time.choices = start_times

		# creating dropdowns for end time
		end_times = []
		for hour in range(facility.open.hour,facility.close.hour + 1):
			for minute in [0, 30]:
				if (((hour == facility.open.hour) and (minute == 0)) \
				or ((hour == facility.close.hour) and (minute == 30))):
					continue
				time = datetime.time(hour, minute)
				end_times.append(time)
		
		form.end_time.choices = end_times

		# collecting information
		if form.validate_on_submit():
			user_booked = request.form.get('user_booked')
			# checking the user isn't an employee
			if current_user.user_type == "user":
				uid = current_user.id
			else:
				user = Users.query.where(Users.email == user_booked).first()
				if not user:
					flash(f"No such user: {user_booked}", "error")
					current_app.logger.info("User " + str(user_booked) + " not found on " + str(datetime.datetime.now()))
					return redirect(url_for('public.facility_view', facility_id=facility_id))
				uid = user.id

			activity = request.form.get('activity')

			date_chosen = request.form.get('date_chosen')
			start_time = request.form.get('start_time')
			end_time = request.form.get('end_time')

			date_chosen = datetime.datetime.strptime(date_chosen, "%Y-%m-%d").date()
			start_time = datetime.datetime.strptime(start_time, "%H:%M:%S").time()
			end_time = datetime.datetime.strptime(end_time, "%H:%M:%S").time()

			start_date = datetime.datetime.combine(date_chosen, start_time)

			# if start_date <= datetime.datetime.now():
			# 	flash("Cannot book in the past", category="danger")
			# 	return redirect(url_for('public.facility_view', facility_id=facility_id))
			
			# testing to see if end is before start
			if end_time < start_time:
				flash("Cannot end before starting activity", category="danger")
				return redirect(url_for('public.facility_view', facility_id=facility_id))

			# create new FacilityBooking object
			facility_booking = models.FacilityBookings(
				facility_id=facility_id, user_id=uid, activity=activity, price=5, date=date_chosen, start=start_time, end=end_time)

			db.session.add(facility_booking)

			try:
				db.session.commit()
				flash('Booking created!', category='success')
				current_app.logger.info("Facility booking for " + str(facility_id) + " created successfully on " + str(datetime.datetime.now()))
				return redirect('/payment/' + str(facility_booking.price))
			except Exception as e:
				flash(f"Error in booking: {e.__repr__()}.", category="danger")
				current_app.logger.info("Facility booking for " + str(facility_id) + " unable to be created on " + str(datetime.datetime.now()))
				return redirect(url_for("public.facility_view", facility_id=facility_id))
	
	else:
		flash(f"No such facility found", category="danger")
		return redirect(url_for("public.facilities"))

	return render_template("confirmation.html", title = facility_name + " Confirmation", facility_name = facility_name, form=form, current_user=current_user)
	
# MEMBERSHIP RELATED VIEWS

@blueprint.route("/my_memberships", methods=["GET"])
@login_required
def my_memberships():
	"""
	Route to page displaying memberships of a user.
	"""
	activemembership = models.ActiveMemberships.query.where(
		models.ActiveMemberships.user_id == current_user.id).first()
	if activemembership != None:
		membership = models.Memberships.query.where(
			models.Memberships.id == activemembership.membership_id).first()
		return render_template('my_memberships.html', title='My Memberships', user=current_user, membership=membership, activemembership=activemembership)
	else:
		return render_template('my_memberships.html', title='My Memberships', user=current_user, activemembership=activemembership)


@blueprint.route("/new_membership", methods=["GET"])
@login_required
def new_membership():
	"""
	Route to page for user to select a new membership.
	"""
	membershipObjs = models.Memberships.query.order_by(
		models.Memberships.name).all()  # gets the facilities in alphabetical order
	memberships = []

	for m in membershipObjs:  # loops through each member of the facilities database and adds them to a list
		memberships.append(
			{
				"id": m.id,
				"name": m.name,
				"price": m.price,
				'months': m.months,
			}
		)
	return render_template('new_membership.html', title='Sign up for a Membership', user=current_user, memberships=memberships)


@blueprint.route("/cancel_membership", methods=["GET"])
@login_required
def cancel_membership():
	"""
	Route to cancel membership of a user.
	"""
	# Find current user to update
	user = models.Users.query.where(models.Users.id == current_user.id).first()
	if not user:
		flash(f"Unable to find user", category="danger")

	if user:
		current_user.is_member = False
		user.is_member = False
		db.session.add(user)

	membership = models.ActiveMemberships.query.where(
		models.ActiveMemberships.user_id == current_user.id).first()

	if not membership:
		flash(f"Unable to find membership", category="danger")

	if membership:
		db.session.delete(membership)

	# Try to update database with this membership record and
	# Commit changes of this database session to database
	try:
		db.session.commit()
		# Direct user to payment page on successful membership
		flash('Successfully canceled your membership', category='success')
		current_app.logger.info("Canceled membership for " + str(current_user.id) + " successfully on " + str(datetime.datetime.now()))
		return redirect('/new_membership')

	# Catching database errors
	except SQLAlchemyError:
		flash('Unable to cancel membership.', category="danger")
		current_app.logger.info("Unable to cancel membership for " + str(current_user.id) + " on " + str(datetime.datetime.now()))
		return redirect('my_memberships')


@blueprint.route('/new_membership/<int:membership_id>', methods=['POST', 'GET'])
def add_membership(membership_id):
	"""
	Route to adding a new member for current_user.
	"""
	# Convert membership id to int
	int_membership_id = int(membership_id)

	if request.method == 'GET':
		# Check this is a valid membership
		valid_membership = models.Memberships.query.where(
			models.Memberships.id == int_membership_id).first()
		if valid_membership == None:
			flash('No such membership exists. Please select a valid membership.')

		# Find current user to update
		user = models.Users.query.where(
			models.Users.id == current_user.id).first()
		if not user:
			flash(f"Unable to find user", "danger")

		if user:
			current_user.is_member = True
			user.is_member = True
			db.session.add(user)

		new_membership = ActiveMemberships(user_id=user.id, membership_id=int_membership_id, member_from=datetime.date.today(
		), member_till=datetime.date.today() + relativedelta(months=int(valid_membership.months)))
		db.session.add(new_membership)

		# Try to update database with this membership record and
		# Commit changes of this database session to database
		try:
			db.session.commit()
			# Direct user to payment page on successful membership
			flash('Successfully added your membership. Please proceed to payment.',category='success')
			current_app.logger.info("Added membership for " + str(current_user.id) + " successfully on " + str(datetime.datetime.now()))
			return redirect('/payment_membership/' + str(valid_membership.price))

		# Catching database errors
		except SQLAlchemyError:
			flash('Unable to add membership.', category="danger")
			current_app.logger.info("Unable to add membership for " + str(current_user.id) + " on " + str(datetime.datetime.now()))
			return redirect('/new_membership')

# OPTIONAL SEARCH FEATURE VIEW

@blueprint.route('/search',methods=["GET"])
def search():
    """
	Route for user to search for page of website.
	"""
    query = request.args.get('query', '')
    view_for_page = '/' + query.lower() 
    return redirect(view_for_page)

# PDF RELATED VIEWS

@blueprint.route('/download/<int:price>/<int:discount>')
def download(price, discount):
    """
	Route to download PDF receipt.
	"""
    # Render the HTML template for the PDF
    html = render_template('receipt_template.html', price=price, discount=discount)

    # Return the PDF as a response
    response = make_response(generate_pdf(html))
    current_app.logger.info("Generated receipt for " + str(current_user.id) + " successfully on " + str(datetime.datetime.now()))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename="receipt.pdf"'
    return response

def generate_pdf(html):
    """
	Function to generate PDF from HTML file.
	"""
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Convert the HTML to PDF using xhtml2pdf
    pisa_status = pisa.CreatePDF(html, dest=pdf_buffer, encoding='utf-8')
    if pisa_status.err:
        raise Exception('Error converting HTML to PDF: %s' % pisa_status.err)

    # Seek to the beginning and return the PDF as a byte string
    pdf_buffer.seek(0)
    pdf = pdf_buffer.read()
    pdf_buffer.close()
    return pdf