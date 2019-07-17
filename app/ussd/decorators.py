import json
from functools import wraps
import uuid

from flask import g, request

from . import ussd
from .. import redis
from ..models import User, AnonymousUser


def validate_ussd_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        """Get user trying to access to USSD session and the session id and adds them to the g request variable"""
        # get user response
        text = request.values.get("text", "default")
        text_array = text.split("*")
        # get phone number
        phone_number = request.values.get("phoneNumber")
        # get session id
        session_id = request.values.get("sessionId") or str(uuid.uuid4())
        # get user
        user = User.by_phoneNumber(phone_number) or AnonymousUser()
        # get session
        session = redis.get(session_id)
        if session is None:
            session = {"level": 0, "session_id": session_id}
            redis.set(session_id, json.dumps(session))
        else:
            session = json.loads(session.decode())
        # add user, response and session to the request variable g
        g.user_response = text_array[len(text_array) - 1]
        g.session = session
        g.current_user = user
        g.phone_number = phone_number
        g.session_id = session_id
        return func(*args, **kwargs)

    return wrapper


@ussd.before_app_request
@validate_ussd_user
def before_request():
    pass
