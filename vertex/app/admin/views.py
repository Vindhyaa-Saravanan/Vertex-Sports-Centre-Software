# vertex/app/admin/views.py
"""
Views for the "admin" blueprint.
"""
from functools import wraps
import datetime
import io
import os

from flask import (
	Blueprint, 
	render_template,
	flash,
	redirect,
	url_for,
	abort,
	request,
	current_app,
	Response,
	make_response,
	request,
)

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from PIL import Image
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta

from io import BytesIO
from xhtml2pdf import pisa

from flask_login import login_user, current_user, logout_user

from .forms import (
	is_empty,
	EditEmail,
	EditName,
	AdminLogin,
	EditFacility,
	EditClass,
	NewUser,
	NewFacility,
	NewClass,
	EditMembership,
	NewMembership,
	EditDiscount,
	NewDiscount
)

from app import models
from app.models import db

blueprint = Blueprint("admin", __name__, static_folder="../static")

def manager_login_required(func):
	"""
	Custom wrapper function for verifying that a manager is logged in.
	If access is denied, 401 error.

	Used as follows:	
	@manager_login_required
	def some_func():
		print("This will only run if a manager is logged in")
	"""
	@wraps(func)
	def wrapper(*args, **kwargs):
		if not ("LOGIN_DISABLED" in current_app.config):
			if current_user.is_anonymous or current_user.user_type != "manager":
				abort(401) # Exits the function - access denied
		return func(*args, **kwargs)
	return wrapper


@blueprint.route("/admin/", methods=["GET"])
@manager_login_required
def index():
	"""
	Route to manager homepage.
	"""
	if not (current_user.is_authenticated and current_user.user_type == "manager"):
		return redirect(url_for("admin.login"))
	
	id = current_user.id
	manager = current_user.user_type == "manager"
	return render_template("manager_index.html", title="Manager Home | Vertex", id=id, manager=manager)

# Manager login route
@blueprint.route('/admin/login', methods=['GET','POST'])
def login():
	"""
	Route to manager login page.
	"""
	form = AdminLogin()
	if form.validate_on_submit():
		email = form.email.data
		password = form.password.data
		manager = models.Users.query.where(models.Users.email == email, models.Users.user_type == "manager").first()
		if manager:
			if manager.verify_password(password):
				flash('Logged in successfully!', category='success')
				login_user(manager, remember=False)
				current_app.logger.info("Logged in manager having user ID " + str(current_user.id) + " successfully on " + str(datetime.datetime.now()))
				return redirect(url_for('admin.index'))
			else:
				flash('Incorrect password, try again.', category='danger')
				current_app.logger.info("Invalid login attempt for manager access using email " + email + " on " + str(datetime.datetime.now()))
		else:
			flash('Manager account does not exist.', category='danger')

	return render_template("manager_login.html", title="Manager Login | Vertex", user=current_user, form=form)

# Views related to admin user management
@blueprint.route("/admin/users", methods=["GET"])
@manager_login_required
def users():
	"""
	Route to manager view users page.
	"""
	userObjs = models.Users.query.order_by(models.Users.id).all()
	users = []

	for user in userObjs:
		users.append(user.get_dict())
	
	return render_template("manager_users.html", title="User Management - Manager View | Vertex", users=users)

@blueprint.route("/admin/delete_user/<int:id>", methods=["GET"])
@manager_login_required
def delete_user(id):
	"""
	Route for manager to delete a user.
	"""
	confirm = request.args.get("confirm")
	if confirm:
		target = models.Users.query.where(models.Users.id == id).first()
		if not target:
			return render_template("message.html", message="No such user. Redirecting...", redirect=url_for("admin.users"))
		
		if target.id == current_user.id:
			return render_template("message.html", message="Cannot delete user currently logged in. Redirectiong...", redirect=url_for("admin.edit_user", id=id))

		facility_bookings = models.FacilityBookings.query.where(models.FacilityBookings.user_id == id).all()
		for booking in facility_bookings:
			db.session.delete(booking)

		class_bookings = models.ClassBookings.query.where(models.ClassBookings.user_id == id).all()
		for booking in class_bookings:
			db.session.delete(booking)

		db.session.delete(target)
		try:
			db.session.commit()
			flash(f"User {id} deleted.", category="success")
			current_app.logger.info("User ID " + str(id) + " deleted successfully on " + str(datetime.datetime.now()))
			return redirect(url_for("admin.users"))
		except Exception as e:
			current_app.logger.error(e)
			db.session.rollback()
			flash(f"Deletion failed. Database error {repr(e)}", category="danger")
			current_app.logger.info("User ID " + str(id) + " unable to delete on " + str(datetime.datetime.now()))

	return render_template("manager_delete.html", title="Delete User - Manager View | Vertex", target="user", id=id)

@blueprint.route("/admin/reset/<int:id>", methods=["GET"])
def reset_password(id):
	"""
	Route for manager to reset password.
	"""
	confirm = request.args.get("confirm")
	if confirm:
		target = models.Users.query.where(models.Users.id == id).first()
		if not target:
			return render_template("message.html", title="Redirect | Vertex", message="No such user. Redirecting...", redirect=url_for("admin.users"))
		
		target.reset_password("default") # Reset the user's password to 'default'

		try:
			db.session.commit()
			flash(f"User {id} password reset to 'default'.", category="success")
			current_app.logger.info("User ID " + str(id) + " password reset by manager successfully on " + str(datetime.datetime.now()))
			return redirect(url_for("admin.users"))
		except Exception as e:
			current_app.logger.error(e)
			db.session.rollback()
			flash(f"Password reset failed. Database error {repr(e)}", category="danger")
			current_app.logger.info("User ID " + str(id) + " unable to password reset by manager on " + str(datetime.datetime.now()))

	return render_template("manager_reset_password.html", title="Reset Password - Manager View | Vertex", id=id)

@blueprint.route("/admin/edit/<int:id>", methods=["GET"])
@manager_login_required
def edit_user(id):
	"""
	Route for manager to edit user.
	"""
	user = models.Users.query.where(models.Users.id == id).first()
	if not user:
		flash(f"User {id} not found", "danger")
		return redirect(url_for("admin.users"))

	user = user.get_dict()
	edit_email = EditEmail()
	edit_name = EditName()

	return render_template(
		"manager_edit_user.html", 
		title="Edit user " + str(id), 
		user=user, 
		edit_email=edit_email,
		edit_name=edit_name
	)

@blueprint.route("/admin/edit_email/<int:id>", methods=["POST"])
@manager_login_required
def edit_email(id):
	"""
	Route for manager to edit email.
	"""
	user = models.Users.query.where(models.Users.id == id).first()
	if not user:
		flash(f"Edit email error: user {id} not found", "danger")
		current_app.logger.info("User ID " + str(id) + " not found for edit on " + str(datetime.datetime.now()))
		return redirect(url_for("admin.users"))

	edit_email = EditEmail()
	if edit_email.validate_on_submit():
		user.email = edit_email.new_email.data
		db.session.add(user)
		try:
			db.session.commit()
		except Exception as e:
			current_app.logger.error(e)
			db.session.rollback()
			flash(f"DB failed to commit user email: {repr(e)}", "danger")
			current_app.logger.info("User ID " + str(id) + " unable to edit due to database error on " + str(datetime.datetime.now()))
			return redirect(url_for("admin.edit_user", id=id))
		
		flash(f"Edited user {user.id}'s email", "success")
		current_app.logger.info("User ID " + str(id) + " edited email successfully on " + str(datetime.datetime.now()))
		return redirect(url_for("admin.edit_user", id=id))

	return redirect(url_for("admin.edit_user", id=id))

@blueprint.route("/admin/edit_name/<int:id>", methods=["POST"])
@manager_login_required
def edit_name(id):
	"""
	Route for manager to edit name.
	"""
	user = models.Users.query.where(models.Users.id == id).first()
	if not user:
		flash(f"Edit name error: user {id} not found", "danger")
		current_app.logger.info("User ID " + str(id) + " not found for edit on " + str(datetime.datetime.now()))
		return redirect(url_for("admin.users"))

	edit_name = EditName()
	if edit_name.validate_on_submit():
		user.firstname = edit_name.new_firstname.data
		user.lastname = edit_name.new_lastname.data
		db.session.add(user)
		try:
			db.session.commit()
			flash(f"Edited user {user.id}'s name", "success")
			current_app.logger.info("User ID " + str(id) + " name edited successfully on " + str(datetime.datetime.now()))
		except Exception as e:
			current_app.logger.error(e)
			db.session.rollback()
			flash(f"DB failed to commit user name: {repr(e)}", "danger")
			current_app.logger.info("User ID " + str(id) + " unable to edit name due to database error on " + str(datetime.datetime.now()))

	return redirect(url_for("admin.edit_user", id=id))

# Views related to admin facility management
@blueprint.route("/admin/facilities", methods=["GET"])
@manager_login_required
def facilities():
	"""
	Display facility information to the manager.
	"""
	# Query the facility objects from the table
	facilityObjs = models.Facilities.query.order_by(models.Facilities.id).all()

	# Create a list of facility dictionaries
	facilities = [o.get_dict() for o in facilityObjs]

	# Render template
	return render_template("manager_facilities.html", title="Facilities - Manager View | Vertex", facilities=facilities)

@blueprint.route("/admin/edit_facility/<int:id>", methods=["GET", "POST"])
@manager_login_required
def edit_facility(id):
	"""
	Route for manager to edit facility.
	"""
	facility = models.Facilities.query.where(models.Facilities.id == id).first()
	if not facility:
		flash(f"Edit facility error: facility {id} not found", "danger")
		current_app.logger.info("Facility ID " + str(id) + " not found for edit on " + str(datetime.datetime.now()))
		return redirect(url_for("admin.facilities"))

	form = EditFacility()
	if request.method == "POST" and form.validate_on_submit:
		# Check if fields contain data
		# If they don't, defer to default
		changes = []
		for field in ["name", "open", "close", "capacity", "session_duration"]:
			# We use getattr to check if a field is empty in the form
			new_field = getattr(getattr(form, "new_" + field), "data", None)
			if not is_empty(new_field):
				changes.append(field)
				setattr(facility, field, new_field) # facility.field = new_field

		if len(changes) == 0:
			flash("No changes", "info")
		else:
			# Add and commit
			db.session.add(facility)
			try:
				db.session.commit()
				flash(f"Edited facility {id}: " + ", ".join(changes), "success")
				current_app.logger.info("Facility ID " + str(id) + " edited successfully on " + str(datetime.datetime.now()))
			except Exception as e:
				current_app.logger.error(e)
				db.session.rollback()
				flash(f"DB failed to commit facility: {repr(e)}", "danger")
				current_app.logger.info("Facility ID " + str(id) + " unable to edit due to database error on " + str(datetime.datetime.now()))
	
	# Turn facility object into dictionary for easy display
	facility = facility.get_dict()

	return render_template("manager_edit_facility.html", title="Facilities - Manager View | Vertex", form=form, facility=facility)
	
@blueprint.route("/admin/delete_facility/<int:id>")
@manager_login_required
def delete_facility(id):
	"""
	Route for manager to delete facility.
	"""
	confirm = request.args.get("confirm")
	if confirm:
		facility = models.Facilities.query.where(models.Facilities.id == id).first()
		if not facility:
			return render_template("message.html", message="No such facility. Redirecting...", redirect=url_for("admin.facilities"))
		
		facility_bookings = models.FacilityBookings.query.where(models.FacilityBookings.facility_id == id).all()
		for booking in facility_bookings:
			db.session.delete(booking)

		db.session.delete(facility)

		try:
			db.session.commit()
			flash(f"Facility {id} deleted.", category="success")
			current_app.logger.info("Facility ID " + str(id) + " deleted successfully on " + str(datetime.datetime.now()))
			return redirect(url_for("admin.facilities"))
		except Exception as e:
			current_app.logger.error(e)
			db.session.rollback()
			flash(f"Deletion failed. Database error {repr(e)}", category="danger")
			current_app.logger.info("Facility ID " + str(id) + " unable to delete due to database error on " + str(datetime.datetime.now()))

	return render_template("manager_delete.html", title="Facilities - Manager View | Vertex", target="facility", id=id)

# Views related to admin class management
@blueprint.route("/admin/classes", methods=["GET"])
@manager_login_required
def classes():
	"""
	Display class information to the manager.
	"""
	# Query the class objects from the table
	classObjs = models.Classes.query.order_by(models.Classes.id).all()

	# Create a list of facility dictionaries so that we can parse them with Jinja2
	classes = [o.get_dict() for o in classObjs]

	# Render template
	return render_template("manager_classes.html", title="Classes - Manager View | Vertex",classes=classes)

@blueprint.route("/admin/edit_class/<int:id>", methods=["GET", "POST"])
@manager_login_required
def edit_class(id):
	"""
	Route for manager to edit class.
	"""
	target = models.Classes.query.where(models.Classes.id == id).first()
	if not target:
		flash(f"Edit class error: class {id} not found", "danger")
		current_app.logger.info("Class ID " + str(id) + " not found on " + str(datetime.datetime.now()))
		return redirect(url_for("admin.classes"))

	form = EditClass()
	if request.method == "POST" and form.validate_on_submit:
		# Check if fields contain data
		# If they don't, defer to default
		changes = []
		for field in ["name", "start", "duration", "date", "price"]:
			# We use getattr to check if a field is empty in the form
			new_field = getattr(getattr(form, "new_" + field), "data", None)
			if not is_empty(new_field):
				changes.append(field)
				setattr(target, field, new_field) # target.field = new_field

		if len(changes) == 0:
			flash("No changes", "info")
		else:
			# Add and commit
			db.session.add(target)
			try:
				db.session.commit()
				flash(f"Edited class {id}: " + ", ".join(changes), "success")
				current_app.logger.info("Class ID " + str(id) + " edited successfully on " + str(datetime.datetime.now()))
			except Exception as e:
				current_app.logger.error(e)
				db.session.rollback()
				flash(f"DB failed to commit class: {repr(e)}", "danger")
				current_app.logger.info("Class ID " + str(id) + " unable to edit due to database error on " + str(datetime.datetime.now()))
	
	target = target.get_dict()

	return render_template("manager_edit_class.html", title="Classes - Manager View | Vertex", form=form, target=target)

@blueprint.route("/admin/delete_class/<int:id>", methods=["GET"])
@manager_login_required
def delete_class(id):
	"""
	Route for manager to delete class.
	"""
	confirm = request.args.get("confirm")
	if confirm:
		target = models.Classes.query.where(models.Classes.id == id).first()
		if not target:
			return render_template("message.html", message="No such class. Redirecting...", redirect=url_for("admin.classes"))
		
		class_bookings = models.ClassBookings.query.where(models.ClassBookings.class_id == id).all()
		for booking in class_bookings:
			db.session.delete(booking)

		db.session.delete(target)

		try:
			db.session.commit()
			flash(f"Class {id} deleted.", category="success")
			current_app.logger.info("Class ID " + str(id) + " deleted successfully on " + str(datetime.datetime.now()))
			return redirect(url_for("admin.classes"))
		except Exception as e:
			current_app.logger.error(e)
			db.session.rollback()
			flash(f"Deletion failed. Database error {repr(e)}", category="danger")
			current_app.logger.info("Class ID " + str(id) + " unable to delete due to database error successfully on " + str(datetime.datetime.now()))

	return render_template("manager_delete.html", title="Classes - Manager View | Vertex", target="class", id=id)

# Views related to admin membership management
@blueprint.route("/admin/memberships", methods=["GET"])
@manager_login_required
def memberships():
	"""
	Display memberships information to the manager.
	"""
	# Query the class objects from the table
	membershipObjs = models.Memberships.query.order_by(models.Memberships.id).all()

	# Create a list of facility dictionaries so that we can parse them with Jinja2
	memberships = [o.get_dict() for o in membershipObjs]

	# Render template
	return render_template("manager_memberships.html", title="Memberships - Manager View | Vertex", memberships=memberships)

@blueprint.route("/admin/edit_membership/<int:id>", methods=["GET", "POST"])
@manager_login_required
def edit_membership(id):
	"""
	Route for manager to edit memberships.
	"""
	target = models.Memberships.query.where(models.Memberships.id == id).first()
	if not target:
		flash(f"Edit memberships error: memberships {id} not found", "danger")
		return redirect(url_for("admin.memberships"))

	form = EditMembership()
	if request.method == "POST" and form.validate_on_submit:
		# Check if fields contain data
		# If they don't, defer to default
		changes = []
		for field in ["name", "months", "price"]:
			# We use getattr to check if a field is empty in the form
			new_field = getattr(getattr(form, "new_" + field), "data", None)
			if not is_empty(new_field):
				changes.append(field)
				setattr(target, field, new_field) # target.field = new_field

		if len(changes) == 0:
			flash("No changes made to this membership scheme.", "info")
		else:
			# Add and commit
			db.session.add(target)
			try:
				db.session.commit()
				flash(f"Edited membership scheme {id}: " + ", ".join(changes), "success")
				current_app.logger.info("Membership ID " + str(id) + " edited successfully on " + str(datetime.datetime.now()))
			except Exception as e:
				current_app.logger.error(e)
				db.session.rollback()
				flash(f"DB failed to commit membership change: {repr(e)}", "danger")
				current_app.logger.info("Membership ID " + str(id) + " not able to edit due to database error on " + str(datetime.datetime.now()))
	
	target = target.get_dict()

	return render_template("manager_edit_membership.html", title="Edit Memberships - Manager View | Vertex", form=form, target=target)

@blueprint.route("/admin/delete_membership/<int:id>", methods=["GET"])
@manager_login_required
def delete_membership(id):
	"""
	Route for manager to delete membership scheme.
	"""
	confirm = request.args.get("confirm")
	if confirm:
		target = models.Memberships.query.where(models.Memberships.id == id).first()
		if not target:
			return render_template("message.html", message="No such membership. Redirecting...", redirect=url_for("admin.memberships"))
		
		active_memberships = models.ActiveMemberships.query.where(models.ActiveMemberships.membership_id == id).all()
		for membership in active_memberships:
			db.session.delete(membership)

		db.session.delete(target)
		try:
			db.session.commit()
			flash(f"Membership scheme {id} deleted.", category="success")
			current_app.logger.info("Membership ID " + str(id) + " deleted successfully on " + str(datetime.datetime.now()))
			return redirect(url_for("admin.memberships"))
		except Exception as e:
			current_app.logger.error(e)
			db.session.rollback()
			flash(f"Deletion failed. Database error {repr(e)}", category="danger")
			current_app.logger.info("Membership ID " + str(id) + " not able to delete due to database error on " + str(datetime.datetime.now()))

	return render_template("manager_delete.html", title=" Delete Membership - Manager View | Vertex", target="membership", id=id)


# Views related to admin discount management
@blueprint.route("/admin/discount", methods=["GET"])
@manager_login_required
def discount():
	"""
	Display discount information to the manager.
	"""
	# Query the class objects from the table
	discountObjs = models.Discounts.query.order_by(models.Discounts.id).all()

	# Create a list of facility dictionaries so that we can parse them with Jinja2
	discounts = [o.get_dict() for o in discountObjs]

	# Render template
	return render_template("manager_discounts.html", title="Discounts - Manager View | Vertex", discounts=discounts)

@blueprint.route("/admin/edit_discount/<int:id>", methods=["GET", "POST"])
@manager_login_required
def edit_discount(id):
	"""
	Route for manager to edit discount.
	"""
	target = models.Discounts.query.where(models.Discounts.id == id).first()
	if not target:
		flash(f"Edit discount error: discount {id} not found", "danger")
		return redirect(url_for("admin.discount"))

	form = EditDiscount()
	if request.method == "POST" and form.validate_on_submit:
		# Check if fields contain data
		# If they don't, defer to default
		changes = []
		for field in ["name", "value", "session_number"]:
			# We use getattr to check if a field is empty in the form
			new_field = getattr(getattr(form, "new_" + field), "data", None)
			if not is_empty(new_field):
				changes.append(field)
				setattr(target, field, new_field) # target.field = new_field

		if len(changes) == 0:
			flash("No changes made to this discount scheme.", "info")
		else:
			# Add and commit
			db.session.add(target)
			try:
				db.session.commit()
				flash(f"Edited discount scheme {id}: " + ", ".join(changes), "success")
				current_app.logger.info("Discount ID " + str(id) + " successfully edited at " + str(datetime.datetime.now()))
			except Exception as e:
				current_app.logger.error(e)
				db.session.rollback()
				flash(f"DB failed to commit discount change: {repr(e)}", "danger")
				current_app.logger.info("Discount ID " + str(id) + " unable to be edited at " + str(datetime.datetime.now()))
	
	target = target.get_dict()

	return render_template("manager_edit_discount.html", title="Edit Discounts - Manager View | Vertex", form=form, target=target)

@blueprint.route("/admin/delete_discount/<int:id>", methods=["GET"])
@manager_login_required
def delete_discount(id):
	"""
	Route for manager to delete discount.
	"""
	confirm = request.args.get("confirm")
	if confirm:
		target = models.Discounts.query.where(models.Discounts.id == id).first()
		if not target:
			return render_template("message.html", message="No such discount. Redirecting...", redirect=url_for("admin.discount"))
		
		db.session.delete(target)
		try:
			db.session.commit()
			flash(f"Discount scheme {id} deleted.", category="success")
			current_app.logger.info("Discount ID " + str(id) + " deleted at " + str(datetime.datetime.now()))
			return redirect(url_for("admin.discount"))
		except Exception as e:
			current_app.logger.error(e)
			db.session.rollback()
			flash(f"Deletion failed. Database error {repr(e)}", category="danger")
			current_app.logger.info("Discount ID " + str(id) + " unable to be deleted at " + str(datetime.datetime.now()))

	return render_template("manager_delete.html", title=" Delete Discount - Manager View | Vertex", target="discount", id=id)


# Views related to admin adding new things management
@blueprint.route("/admin/new_user", methods=["GET", "POST"])
@manager_login_required
def new_user():
	"""
	Route for manager to add a new user.
	"""
	form = NewUser()
	if request.method == "POST" and form.validate_on_submit:
		if form.password.data != form.confirm.data:
			flash("Passwords must match", "warning")
			return redirect(url_for("admin.new_user"))
			
		try:
			new = models.Users(
				email = form.email.data, 
				password = form.password.data, 
				firstname = form.firstname.data, 
				lastname = form.lastname.data, 
				date_of_birth = form.date_of_birth.data,
				user_type = form.user_type.data
			)
		except ValueError as e:
			flash(e.__str__().capitalize(), "warning")
			return redirect(url_for("admin.new_user"))

		db.session.add(new)

		try:
			db.session.commit()
			flash(f"New user created: ID {new.id}", "success")
			return redirect(url_for("admin.users"))
		except Exception as e:
			db.session.rollback()
			if "UNIQUE constraint failed" in e.__str__() and "users.email" in e.__str__():
				flash("That email is already in use", "warning")
			else:
				current_app.logger.error(f"Database error in new user creation: {repr(e)}")
				flash(f"Database error in user creation: {repr(e)}", "danger")

	return render_template("manager_new_user.html", title="Users - Manager View | Vertex", form=form)

@blueprint.route("/admin/new_facility", methods=["GET", "POST"])
@manager_login_required
def new_facility():
	"""
	Route for manager to add a new facility.
	"""
	form = NewFacility()
	if request.method == "POST" and form.validate_on_submit:
		try:
			new = models.Facilities(
				name = form.name.data,
				open = form.open.data,
				close = form.close.data,
				capacity = form.capacity.data,
				session_duration = form.session_duration.data
			)
		except ValueError as e:
			flash(f"Opening time must be before closing time", "warning")
			return redirect(url_for("admin.new_facility"))
			
		
		db.session.add(new)

		try:
			db.session.commit()
			flash(f"New facility created: ID {new.id}", "success")
			return redirect(url_for("admin.facilities"))
		except Exception as e:
			db.session.rollback()
			current_app.logger.error(f"Database error: {repr(e)}")
			flash(f"Database error: {repr(e)}")

	return render_template("manager_new_facility.html", title="Facilities - Manager View | Vertex", form=form)

@blueprint.route("/admin/new_class", methods=["GET", "POST"])
@manager_login_required
def new_class():
	"""
	Route for manager to add a new class.
	"""
	form = NewClass()
	if request.method == "POST" and form.validate_on_submit:
		new = models.Classes(
			name = form.name.data,
			start = form.start.data,
			duration = form.duration.data,
			date = form.date.data,
			price = form.price.data
		)
		
		db.session.add(new)

		try:
			db.session.commit()
			flash(f"New class created: ID {new.id}", "success")
			return redirect(url_for("admin.classes"))
		except Exception as e:
			db.session.rollback()
			current_app.logger.error(f"Database error: {repr(e)}")
			flash(f"Database error: {repr(e)}")

	return render_template("manager_new_class.html", title="Classes - Manager View | Vertex", form=form)

@blueprint.route("/admin/new_membership", methods=["GET", "POST"])
@manager_login_required
def new_membership():
	"""
	Route for manager to add a new membership scheme.
	"""
	form = NewMembership()
	if request.method == "POST" and form.validate_on_submit:
		new_membership = models.Memberships(
			name = form.name.data,
			months = form.months.data,
			price = form.price.data
		)
		
		db.session.add(new_membership)
		try:
			db.session.commit()
			flash(f"New membership scheme created: ID {new_membership.id}", "success")
			return redirect(url_for("admin.memberships"))
		except Exception as e:
			db.session.rollback()
			current_app.logger.error(f"Database error: {repr(e)}")
			flash(f"Database error: {repr(e)}")

	return render_template("manager_new_membership.html", title="New Membership - Manager View | Vertex", form=form)

@blueprint.route("/admin/new_discount", methods=["GET", "POST"])
@manager_login_required
def new_discount():
	"""
	Route for manager to add a new discount.
	"""
	form = NewDiscount()
	if request.method == "POST" and form.validate_on_submit:
		new_discount = models.Discounts(
			name = form.name.data,
			value = form.value.data,
			session_number = form.session_number.data
		)
		
		db.session.add(new_discount)
		try:
			db.session.commit()
			flash(f"New discount scheme created: ID {new_discount.id}", "success")
			current_app.logger.info("Discount ID " + str(new_discount.id) + " created successfully at " + str(datetime.datetime.now()))
			return redirect(url_for("admin.discount"))
		except Exception as e:
			db.session.rollback()
			current_app.logger.error(f"Database error: {repr(e)}")
			flash(f"Database error: {repr(e)}")
			current_app.logger.info("Discount ID " + str(new_discount.id) + " unable to be created at " + str(datetime.datetime.now()))

	return render_template("manager_new_discount.html", title="New Discount - Manager View | Vertex", form=form)


@blueprint.route("/admin/analytics_facilities", methods=["GET"])
@manager_login_required
def analytics_facilities():
	"""
	Route to manager analytics for facilities page.
	"""
	return render_template("manager_analytics_facilities.html", title="Analytics - Facilites | Vertex")

@blueprint.route("/admin/analytics_classes", methods=["GET"])
@manager_login_required
def analytics_classes():
	"""
	Route to manager analytics for classes page.
	"""
	return render_template("manager_analytics_classes.html", title="Analytics - Classes | Vertex")

@blueprint.route("/admin/analytics_membership", methods=["GET"])
@manager_login_required
def analytics_membership():
	"""
	Route to manager analytics for memberships page.
	"""
	return render_template("manager_analytics_membership.html", title="Analytics - Membership | Vertex")

@blueprint.route("/admin/sales", methods=["GET"])
@manager_login_required
def sales():
	"""
	Route to manager analytics for sales page.
	"""
	return render_template("manager_sales.html", title="Sales - Manager View | Vertex")

@blueprint.route("/plots/<int:plot_id>", methods=["GET"])
@manager_login_required
def plot(plot_id):
	"""
	Route to create and save plots for manager analytics.
	"""
	# Define the start and end dates for the past 7 days
	today = datetime.date.today()
	one_week_ago = today - datetime.timedelta(days=7)
	fig = Figure()
	
	# Define a filepath for the generated images
	fpath = os.path.join('app', 'static', 'gen')

	# Facilities Plots

	# Plot for fitness room throughout day
	if plot_id == 1:
		axis = fig.add_subplot(1, 1, 1)
		langs = [str(datetime.time(i)) + "-" + str(datetime.time(i+1)) for i in range(8, 22)]
		students = np.random.randint(0, 40, size=len(langs))
		axis.bar(langs,students)
		axis.set_xticklabels(axis.get_xticklabels(), rotation=30, ha='right')

	# Plot for climbing wall for past one week
	elif plot_id == 2:
		axis = fig.add_subplot(1, 1, 1)

		# Find all of the bookings for climbing wall
		climbing = models.FacilityBookings.query.where(models.FacilityBookings.facility_id == 6 and models.FacilityBookings.date > one_week_ago).all()

		xs = "general use"
		ys = len(climbing)
		axis.bar(xs, ys)
		fig.savefig(fname=os.path.join(fpath, 'climbingwall.png'))

	# Plot for fitness room for past one week
	elif plot_id == 3:
		axis = fig.add_subplot(1, 1, 1)

		# Find all of the bookings for fitness room
		fitness = models.FacilityBookings.query.where(models.FacilityBookings.facility_id == 2 and models.FacilityBookings.date > one_week_ago).all()

		xs = "general use"
		ys = len(fitness)
		axis.bar(xs, ys)
		fig.savefig(os.path.join(fpath, 'fitnessroom.png'))

	# Plot for sports hall for past one week
	elif plot_id == 4:
		axis = fig.add_subplot(1, 1, 1)

		# find all of the bookings for sports hall general use
		generaluse = models.FacilityBookings.query.where(models.FacilityBookings.facility_id == 5, models.FacilityBookings.activity == "team events", models.FacilityBookings.date > one_week_ago).all()
		
		# find all of the bookings for sports hall one hour sessions
		hoursessions = models.FacilityBookings.query.where(models.FacilityBookings.facility_id == 5, models.FacilityBookings.activity == "1 hour sessions", models.FacilityBookings.date > one_week_ago).all()

		xs = ["general use", "1 hour session"]
		ys = [len(generaluse), len(hoursessions)]
		axis.bar(xs, ys)
		fig.savefig(os.path.join(fpath, 'sportshall.png'))

	# Plot for both squash courts over the last week
	elif plot_id == 5:
		axis = fig.add_subplot(1, 1, 1)

		# find all of the bookings for squash court 1
		court1 = models.FacilityBookings.query.where(models.FacilityBookings.facility_id == 3, models.FacilityBookings.date > one_week_ago).all()
		
		# find all of the bookings for squash court 2
		court2 = models.FacilityBookings.query.where(models.FacilityBookings.facility_id == 4, models.FacilityBookings.date > one_week_ago).all()

		xs = ["Squash Court 1", "Squash Court 2"]
		ys = [len(court1), len(court2)]
		axis.bar(xs, ys)
		fig.savefig(os.path.join(fpath, 'squash.png'))

	# Plot for studio over the last week
	elif plot_id == 6:
		axis = fig.add_subplot(1, 1, 1)

		# Find all of the bookings for the studio general use
		studio = models.FacilityBookings.query.where(models.FacilityBookings.facility_id == 7, models.FacilityBookings.date > one_week_ago).all()
		
		xs = ["General Use"]
		ys = [len(studio)]
		axis.bar(xs, ys)
		fig.savefig(os.path.join(fpath, 'studio.png'))

	# Plot for swimming over the last week
	elif plot_id == 7:
		axis = fig.add_subplot(1, 1, 1)

		# Find all of the bookings for the swimming pool, by various activites
		general_use = models.FacilityBookings.query.where(models.FacilityBookings.facility_id == 1, models.FacilityBookings.activity == "general use", models.FacilityBookings.date > one_week_ago).all()
		lane_swimming = models.FacilityBookings.query.where(models.FacilityBookings.facility_id == 1, models.FacilityBookings.activity == "lane swimming", models.FacilityBookings.date > one_week_ago).all()
		lessons = models.FacilityBookings.query.where(models.FacilityBookings.facility_id == 1, models.FacilityBookings.activity == "lessons", models.FacilityBookings.date > one_week_ago).all()
		team_events = models.FacilityBookings.query.where(models.FacilityBookings.facility_id == 1, models.FacilityBookings.activity == "team events", models.FacilityBookings.date > one_week_ago).all()

		xs = ["General use", "Lane Swimming", "Lessons", "Team Events"]
		ys = [len(general_use), len(lane_swimming),len(lessons),len(team_events)]
		axis.bar(xs, ys)
		fig.savefig(os.path.join(fpath, 'swimming.png'))

	# Classes Plots
	# Plots for all Pilates class bookings in the past week
	elif plot_id == 8:
		axis = fig.add_subplot(1, 1, 1)
		xs=[]
		ys=[]

		# Find all pilates classes
		all_pilates = models.Classes.query.where(models.Classes.name == "Pilates" and models.Classes.date > one_week_ago)
		for pilates_class in all_pilates:
			pilates_bookings = models.ClassBookings.query.where(models.ClassBookings.class_id == pilates_class.id).all()
			xs.append(str(pilates_class.start) + " " + pilates_class.name)
			ys.append(len(pilates_bookings))

		axis.bar(xs, ys)
		fig.savefig(os.path.join(fpath, 'pilates.png'))

	# Plots for all Aerobics class bookings in the past week
	elif plot_id == 9:
		axis = fig.add_subplot(1, 1, 1)
		xs=[]
		ys=[]

		# Find all aerobics classes
		all_aerobics = models.Classes.query.where(models.Classes.name == "Aerobics" and models.Classes.date > one_week_ago)
		for aerobics_class in all_aerobics:
			aerobics_bookings = models.ClassBookings.query.where(models.ClassBookings.class_id == aerobics_class.id).all()
			xs.append(str(aerobics_class.start) + " " + aerobics_class.name)
			ys.append(len(aerobics_bookings))

		axis.bar(xs, ys)
		fig.savefig(os.path.join(fpath, 'aerobics.png'))

	# Plots for all Yoga class bookings in the past week
	elif plot_id == 10:
		axis = fig.add_subplot(1, 1, 1)
		xs=[]
		ys=[]

		# Find all yoga classes
		all_yoga = models.Classes.query.where(models.Classes.name == "Yoga" and models.Classes.date > one_week_ago)
		for yoga_class in all_yoga:
			yoga_bookings = models.ClassBookings.query.where(models.ClassBookings.class_id == yoga_class.id).all()
			xs.append(str(yoga_class.start) + " " + yoga_class.name)
			ys.append(len(yoga_bookings))

		axis.bar(xs, ys)
		fig.savefig(os.path.join(fpath, 'yoga.png'))

	# Membership plot

	elif plot_id == 11:
		axis = fig.add_subplot(1, 1, 1)
		xs=[]
		ys=[]

		# Find number of active memberships for each type of membership
		types_of_memberships = models.Memberships.query.all()
		for membership_type in types_of_memberships:
			active = models.ActiveMemberships.query.where(models.ActiveMemberships.membership_id == membership_type.id).all()
			xs.append(membership_type.name)
			ys.append(len(active))

		axis.bar(xs, ys)
		fig.savefig(os.path.join(fpath, 'membership.png'))

	elif plot_id == 12:
		axis = fig.add_subplot(1, 1, 1)
		xs=[]
		ys=[]

		# Find total price of all active bookings for each type of facility
		swim = models.FacilityBookings.query.where(models.FacilityBookings.facility_id == 1, models.FacilityBookings.date > one_week_ago).all()
		fitroom = models.FacilityBookings.query.where(models.FacilityBookings.facility_id == 2, models.FacilityBookings.date > one_week_ago).all()
		court1 = models.FacilityBookings.query.where(models.FacilityBookings.facility_id == 3, models.FacilityBookings.date > one_week_ago).all()
		court2 = models.FacilityBookings.query.where(models.FacilityBookings.facility_id == 4, models.FacilityBookings.date > one_week_ago).all()
		sporthall = models.FacilityBookings.query.where(models.FacilityBookings.facility_id == 5, models.FacilityBookings.date > one_week_ago).all()
		climbing = models.FacilityBookings.query.where(models.FacilityBookings.facility_id == 6, models.FacilityBookings.date > one_week_ago).all()
		studio = models.FacilityBookings.query.where(models.FacilityBookings.facility_id == 7, models.FacilityBookings.date > one_week_ago).all()
		
		xs = ["SP", "FR", "SC1", "SC2", "SH", "CW", "S"]
		ys = [len(swim)*5, len(fitroom)*5, len(court1)*5, len(court2)*5, len(sporthall)*5, len(climbing)*5, len(studio)*5]
		axis.bar(xs, ys, width=0.3)
		fig.savefig(os.path.join(fpath, 'facility.png'))

	elif plot_id == 13:
		axis = fig.add_subplot(1, 1, 1)
		xs=[]
		ys=[]

		# Find total price of all active bookings for each type of class
		pilates_total = 0
		pilates = models.Classes.query.where(models.Classes.name == "Pilates" and models.Classes.date > one_week_ago)
		for pilates_class in pilates:
			pilates_bookings = models.ClassBookings.query.where(models.ClassBookings.class_id == pilates_class.id).all()
			pilates_total += len(pilates_bookings) * pilates_class.price

		aerobics_total = 0
		aerobics = models.Classes.query.where(models.Classes.name == "Aerobics" and models.Classes.date > one_week_ago)
		for aerobics_class in aerobics:
			aerobics_bookings = models.ClassBookings.query.where(models.ClassBookings.class_id == aerobics_class.id).all()
			aerobics_total += len(aerobics_bookings) * aerobics_class.price

		yoga_total = 0
		yoga = models.Classes.query.where(models.Classes.name == "Yoga" and models.Classes.date > one_week_ago)
		for yoga_class in yoga:
			yoga_bookings = models.ClassBookings.query.where(models.ClassBookings.class_id == yoga_class.id).all()
			yoga_total += len(yoga_bookings) * yoga_class.price

		aerobics = models.FacilityBookings.query.where(models.FacilityBookings.facility_id == 2, models.FacilityBookings.date > one_week_ago).all()
		yoga = models.FacilityBookings.query.where(models.FacilityBookings.facility_id == 3, models.FacilityBookings.date > one_week_ago).all()
		
		xs = ["Pilates", "Aerobics", "Yoga"]
		ys = [pilates_total, aerobics_total, yoga_total]
		axis.bar(xs, ys)
		fig.savefig(os.path.join(fpath, 'class.png'))

	elif plot_id == 14:
		axis = fig.add_subplot(1, 1, 1)
		xs=[]
		ys=[]

		# Find total price of all active bookings for each type of facility
		total_facility_sales = 0
		total_class_sales = 0

		all_facility_bookings = models.FacilityBookings.query.all()
		for facility_booking in all_facility_bookings:
			total_facility_sales += facility_booking.price

		all_classes = models.Classes.query.all()
		for each_class in all_classes:
			total_class_sales += len(each_class.bookings) * each_class.price

		all_team_events = models.TeamEvents.query.all()
		
		xs = ["Facilities", "Classes", "Team Events"]
		ys = [total_facility_sales, total_class_sales, len(all_team_events)*5]
		axis.bar(xs, ys)
		fig.savefig(os.path.join(fpath, 'sales.png'))

	output = io.BytesIO()
	FigureCanvas(fig).print_png(output)

	# Open the image using PIL
	img = Image.open(io.BytesIO(output.getvalue()))

	# Set the maximum width and height for the image
	max_width = 1000
	max_height = 400

	# Get the image size
	width, height = img.size

	# Calculate the new size of the image while preserving its aspect ratio
	if width > max_width:
		ratio = max_width / width
		new_width = max_width
		new_height = int(height * ratio)
	else:
		new_width = width
		new_height = height

	if new_height > max_height:
		ratio = max_height / new_height
		new_height = max_height
		new_width = int(new_width * ratio)

	# Resize the image
	img = img.resize((new_width, new_height), Image.ANTIALIAS)

	# Save the image to a BytesIO object
	output = io.BytesIO()
	img.save(output, format='PNG')
	output.seek(0)

	return Response(output.getvalue(), mimetype='image/png')

@blueprint.route("/admin/logout", methods=["GET"])
def logout():
	"""
	Route for manager to logout.
	"""
	logout_user()
	return render_template("message.html", message="Logged out. Redirecting...", redirect=url_for("admin.login"))

@blueprint.route('/download_sales')
@manager_login_required
def download_sales():
	"""
	Route for manager to download PDF report for sales.
	"""
	html = render_template("manager_sales_report.html")

	# Generate the PDF
	pdf = generate_admin_pdf(html)
	current_app.logger.info("PDF Sales Report generated at " + str(datetime.datetime.now()))

	# Return the PDF as a response
	response = make_response(pdf)
	response.headers['Content-Type'] = 'application/pdf'
	response.headers['Content-Disposition'] = 'attachment; filename="report_sales.pdf"'
	return response

@blueprint.route('/download_facilities')
@manager_login_required
def download_facilities():
	"""
	Route for manager to download PDF report for facilities.
	"""
	html = render_template("manager_facilities_report.html", date_from = datetime.date.today() - relativedelta(weeks=1), date_to = datetime.date.today())

	# Generate the PDF
	pdf = generate_admin_pdf(html)
	current_app.logger.info("PDF Facilities Report generated at " + str(datetime.datetime.now()))

	# Return the PDF as a response
	response = make_response(pdf)
	response.headers['Content-Type'] = 'application/pdf'
	response.headers['Content-Disposition'] = 'attachment; filename="report_facilities.pdf"'
	return response

@blueprint.route('/download_classes')
@manager_login_required
def download_classes():
	"""
	Route for manager to download PDF report for classes.
	"""
	html = render_template("manager_classes_report.html", date_from = datetime.date.today() - relativedelta(weeks=1), date_to = datetime.date.today())

	# Generate the PDF
	pdf = generate_admin_pdf(html)
	current_app.logger.info("PDF Classes Report generated at " + str(datetime.datetime.now()))

	# Return the PDF as a response
	response = make_response(pdf)
	response.headers['Content-Type'] = 'application/pdf'
	response.headers['Content-Disposition'] = 'attachment; filename="report_classes.pdf"'
	return response

@blueprint.route('/download_memberships')
@manager_login_required
def download_memberships():
	"""
	Route for manager to download PDF report for memberships.
	"""
	html = render_template("manager_membership_report.html", graph_url=os.path.join('app','static', 'images', 'membership.png'))

	# Generate the PDF
	pdf = generate_admin_pdf(html)
	current_app.logger.info("PDF Membership Report generated at " + str(datetime.datetime.now()))

	# Return the PDF as a response
	response = make_response(pdf)
	response.headers['Content-Type'] = 'application/pdf'
	response.headers['Content-Disposition'] = 'attachment; filename="report_memberships.pdf"'
	return response

def generate_admin_pdf(html):
	"""
	Function to generate PDF from HTML file.
	"""
	# Create a BytesIO object to hold the PDF data
	pdf_buffer = BytesIO()

	# Create a PDF object using the BytesIO object as its "file."
	pdf = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), pdf_buffer)

	# Check if the PDF generation was successful
	if not pdf.err:
		# Get the value of the BytesIO buffer
		pdf_value = pdf_buffer.getvalue()
		pdf_buffer.close()
		# Return the PDF data as a response
		response = make_response(pdf_value)
		response.headers['Content-Type'] = 'application/pdf'
		response.headers['Content-Disposition'] = 'attachment; filename="report.pdf"'
		return response
	else:
		# Handle the case where PDF generation failed
		pdf_buffer.close()
		current_app.logger.info("PDF Facilities Report generated at " + str(datetime.datetime.now()))
		flash("Error generating PDF: " + str(pdf.err))
