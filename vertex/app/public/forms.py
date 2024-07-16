# vertex/app/public/forms.py

"""
Forms module for the "public" blueprint.
"""

from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, DateField, SelectField, PasswordField
from wtforms.validators import DataRequired, Length, ValidationError, Regexp

# User Login Form
class UserLogin(FlaskForm):
    """
	Form for user to login.
	"""
    email = StringField('email', validators=[DataRequired(), Regexp("^(.+)\@(.+)\.(.+)$", message="Must be a valid email")])
    password = PasswordField('password', validators=[DataRequired()])

# Customer Sign Up Form
class CustomerSignUpForm(FlaskForm):
    """
	Form for user to sign up.
	"""
    email = StringField('Email Address:', validators=[DataRequired(), Regexp("^(.+)\@(.+)\.(.+)$", message="Must be a valid email")])
    first_name = StringField('First Name: ', validators=[DataRequired()])
    last_name = StringField('Last Name: ', validators=[DataRequired()])
    password1 = PasswordField('Enter Password:', validators=[DataRequired()])
    password2 = PasswordField('Re-enter Password:', validators=[DataRequired()])
    date_of_birth = DateField('Date of Birth:', validators=[DataRequired()])

# Form for the card payment system
class paymentForm(FlaskForm):
    """
	Form for user to pay.
	"""
    def validate_int(form, field):
        try:
            int(field.data)
        except ValueError:
            raise ValidationError('must only include digits')

    name = StringField('Name on card: ', validators=[DataRequired()])
    cardnumber = StringField('Card number: ', validators=[DataRequired(), Length(min=16, max=16), validate_int])
    expirymonth = SelectField(' expiry Month:', choices=('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'), validators=[DataRequired()])
    expiryyear = SelectField('expiry year:', choices=('23', '24', '25', '26', '27', '28'), validators=[DataRequired()])
    securitycode = StringField('Security code: ', validators=[DataRequired(), Length(min=3, max=3), validate_int])

# Form for employee to book facility for customer
class confirmationForm(FlaskForm):
    """
	Form for employee to book facility on behalf of customer.
	"""
    user_booked = StringField('User being booked: ')
    activity = SelectField('Activity of Choice:', validators=[DataRequired()])
    date_chosen = DateField('Date of facility booking: ', validators=[DataRequired()])
    start_time = SelectField('Starting time:', validators=[DataRequired()])
    end_time = SelectField('Ending time:', validators=[DataRequired()])
    # activity_duration = SelectField(' Activity of Choice:', validators=[DataRequired()])

# Form for employeee to book class for customer
class employeeForm(FlaskForm):
    """
	Form for employee to book class on behalf of customer.
	"""
    user_class_booked = StringField('User being booked: ', validators=[DataRequired(), Regexp("^(.+)\@(.+)\.(.+)$", message="Must be a valid email")])
