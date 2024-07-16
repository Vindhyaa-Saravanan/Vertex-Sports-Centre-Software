# vertex/app/extensions.py
"""
The extensions module. These are initialised in app.py.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_assets import Environment, Bundle
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
import os
from flask_mail import Mail

bundles = {
	'js_all': Bundle(
		'js/javascript.js',
		output='gen/home.js'),
	
	'css_all': Bundle(
		'css/styles.css',
		output='gen/home.css'),
}

stripe_keys = {
	'secret_key': os.getenv('SECRET_STRIPE_KEY'),
	'publishable_key': os.getenv('PUBLISHABLE_KEY'),
}



db = SQLAlchemy()
assets = Environment()
csrf = CSRFProtect()
login = LoginManager()
mail = Mail()