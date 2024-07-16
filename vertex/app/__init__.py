# vertex/app/__init__.py
"""
Main application package.
"""

from flask import Flask, render_template, json
from werkzeug.exceptions import HTTPException
import stripe

from . import public, admin

from .extensions import (
	db, 
	assets, 
	bundles,
	csrf,
	login,
	stripe_keys,
	mail
)

def create_app(extra_options: dict = {}):
	"""
	Create and return an instance of our application.
	"""
	app = Flask(
		__name__,
		static_url_path="/static",
		static_folder="static",
	)

	# Load config from vertex/config.py
	app.config.from_object("config")

	for option in extra_options:
		app.config[option] = extra_options[option]

	register_extensions(app)
	register_blueprints(app)
	register_error_handlers(app)

	return app

def register_extensions(app):
	"""
	Register extensions to our application.
	"""
	db.init_app(app)
	assets.init_app(app)
	assets.register(bundles)
	csrf.init_app(app)
	login.init_app(app)
	mail.init_app(app)
	stripe.api_key = stripe_keys['secret_key']


def register_blueprints(app):
	"""
	Register blueprints to our application.
	"""
	app.register_blueprint(public.views.blueprint)
	app.register_blueprint(admin.views.blueprint)

def register_error_handlers(app):
	
	# Custom error handlers
	# based on ideas from
	# https://flask.palletsprojects.com/en/1.1.x/patterns/errorpages/
	def page_not_found(e):
		"""
		Error handler to show custom error page for 404 error.
		"""
		return render_template('404.html'), 404

	def access_denied(e):
		"""
		Error handler to show custom error page for 401 error.
		"""
		return render_template('401.html'), 401

	def internal_server_error(e):
		"""
		Error handler to show custom error page for 500 error.
		"""
		return render_template('500.html'), 500
	
	# based on ideas from
	# https://flask.palletsprojects.com/en/2.2.x/errorhandling/#generic-exception-handlers
	def handle_exception(e):
		"""
		Generic error handler to show custom error page for Exceptions.
		"""
		# Pass through HTTP errors
		if isinstance(e, HTTPException):
			return e
		
		return render_template("custom_error_page.html", name='Exception', description='UnknownException', error=e), 200
	
	app.register_error_handler(404, page_not_found)
	app.register_error_handler(401, access_denied)

	if "DEBUG" in app.config and app.config["DEBUG"]:
		"""
		If in debug mode, let's not register the custom error handlers in
		order to be able to see and use the handy flask error traceback view.
		"""
		return

	# Otherwise, proceed as normal
	app.register_error_handler(500, internal_server_error)
	app.register_error_handler(Exception, handle_exception)
