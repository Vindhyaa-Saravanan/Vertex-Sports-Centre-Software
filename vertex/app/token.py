# vertex/app/public/token.py
# based on ideas from:
# https://www.freecodecamp.org/news/setup-email-verification-in-flask-app/
# https://pythonhosted.org/Flask-Mail/

from itsdangerous import URLSafeTimedSerializer
import config
from app.extensions import mail

def generate_token(email):
    """
    Generates a confirmation token to verify the email address 
    using the URLSafeTimedSerializer class from the itsdangerous package
    """
    serializer = URLSafeTimedSerializer(config.SECRET_KEY)
    return serializer.dumps(email, salt=config.TOKEN_SALT)


def confirm_token(token, expiration=3600):
    """
    Given a token and expiration time, finds email address
    corresponding to the token that is now verified.
    """
    serializer = URLSafeTimedSerializer(config.SECRET_KEY)
    try:
        email = serializer.loads(token, salt=config.TOKEN_SALT, max_age=expiration)
        return email
    except Exception:
        return False