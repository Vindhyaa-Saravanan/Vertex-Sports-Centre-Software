# vertex/config.py

import os

DEBUG = False

# SQLAlchemy
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_ECHO = False

# CSRF
WTF_CSRF_ENABLED = True

# SECRET KEY
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY PASSWORD SALT FOR EMAIL CONFIRMATION TOKEN
TOKEN_SALT = os.getenv("TOKEN_SALT", default="very-important")

# EMAIL CONFIGURATIONS
MAIL_DEFAULT_SENDER = "noreply@flask.com"
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_DEBUG = False
MAIL_USERNAME = "projectsquad30@gmail.com"
MAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

if bool(os.getenv("FLASK_DEBUG")):
	DEBUG = True
	SQLALCHEMY_ECHO = True