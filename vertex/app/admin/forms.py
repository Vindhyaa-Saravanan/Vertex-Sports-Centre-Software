# vertex/app/admin/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, DateField, EmailField, SelectField
from wtforms.fields import TimeField
from wtforms.validators import InputRequired, Regexp, EqualTo

def is_empty(data):
    return data in [None, '', []]

class AdminLogin(FlaskForm):
    """
    Form to allow managers to login.
    """
    email = StringField('email', validators=[
        InputRequired(), 
        Regexp("^(.+)\@(.+)\.(.+)$", message="Must be a valid email")]
    )
    password = PasswordField('password', validators=[InputRequired()])

class EditEmail(FlaskForm):
    """
    Form to allow managers to edit a user's email.
    """
    new_email = StringField('new_email', validators=[InputRequired()])

class EditName(FlaskForm):
    """
    Form to allow managers to edit a user's name.
    """
    new_firstname = StringField('new_firstname', validators=[InputRequired()])
    new_lastname = StringField("new_lastname", validators=[InputRequired()])

class EditFacility(FlaskForm):
    """
    Form to allow managers to edit a facility.
    """
    new_name = StringField("new_name") # We will not specify DataRequired - we will defer to the default
    new_open = TimeField("new_open") # if the user doesn't give us a value
    new_close = TimeField("new_close")
    new_capacity = IntegerField("new_capacity")
    new_session_duration = IntegerField("new_session_duration")

class EditClass(FlaskForm):
    """
    Form to allow managers to edit a class.
    """
    new_name = StringField("new_name") # Same reason for no DataRequired as EditFacility
    new_start = TimeField("new_start")
    new_duration = IntegerField("new_duration")
    new_date = DateField("new_date")
    new_price = IntegerField("new_price")

class EditMembership(FlaskForm):
    """
    Form to allow managers to edit a membership scheme.
    """
    new_name = StringField("new_name") # Same reason for no DataRequired as EditFacility
    new_months = IntegerField("new_months")
    new_price = IntegerField("new_price")

class EditDiscount(FlaskForm):
    """
    Form to allow managers to edit a discount scheme.
    """
    new_name = StringField("new_name") # Same reason for no DataRequired as EditFacility
    new_value = IntegerField("new_value")
    new_session_number = IntegerField("new_session_number")

class NewUser(FlaskForm):
    """
    Form to allow managers to create a new user of any type.
    """
    email = EmailField("email", validators=[InputRequired()])
    password = PasswordField("password", validators=[InputRequired()])
    confirm = PasswordField("password", validators=[
        InputRequired(),
        EqualTo("password", "Passwords must match")
    ])
    firstname = StringField("firstname", validators=[InputRequired()])
    lastname = StringField("lastname", validators=[InputRequired()])
    date_of_birth = DateField("date_of_birth", validators=[InputRequired()])
    user_type = SelectField("user_type", choices=["user", "employee", "manager"], validators=[InputRequired()])

class NewFacility(FlaskForm):
    """
    Form to allow managers to create a new facility.
    """
    name = StringField("name", validators=[InputRequired()])
    open = TimeField("open", validators=[InputRequired()])
    close = TimeField("close", validators=[InputRequired()])
    capacity = IntegerField("capacity", validators=[InputRequired()])
    session_duration = IntegerField("session_duration", validators=[InputRequired()])

class NewClass(FlaskForm):
    """
    Form to allow managers to create a new class.
    """
    name = StringField("name", validators=[InputRequired()])
    start = TimeField("start", validators=[InputRequired()])
    duration = IntegerField("duration", validators=[InputRequired()])
    date = DateField("date", validators=[InputRequired()])
    price = IntegerField("price", validators=[InputRequired()])

class NewMembership(FlaskForm):
    """
    Form to allow managers to create a new membership.
    """
    name = StringField("name", validators=[InputRequired()])
    months = IntegerField("duration in months", validators=[InputRequired()])
    price = IntegerField("date", validators=[InputRequired()])

class NewDiscount(FlaskForm):
    """
    Form to allow managers to create a new discount scheme.
    """
    name = StringField("name", validators=[InputRequired()])
    value = IntegerField("value", validators=[InputRequired()])
    session_number = IntegerField("session_number", validators=[InputRequired()])
