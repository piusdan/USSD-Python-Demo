from flask import g, make_response

from app.models import AnonymousUser
from . import ussd
from .airtime import Airtime
from .deposit import Deposit
from .home import LowerLevelMenu
from .register import RegistrationMenu
from .withdraw import WithDrawal


@ussd.route('/', methods=['POST', 'GET'])
def index():
    response = make_response("END connection ok")
    response.headers['Content-Type'] = "text/plain"
    return response


@ussd.route('/ussd/callback', methods=['POST'])
def ussd_callback():
    """Handles post call back from AT"""
    session_id = g.session_id
    user = g.current_user
    session = g.session
    user_response = g.user_response
    if isinstance(user, AnonymousUser):
        # register user
        menu = RegistrationMenu(session_id=session_id, session=session, phone_number=g.phone_number,
                                user_response=user_response, user=user)
        return menu.execute()
    level = session.get('level')
    print("level {}".format(level))
    if level < 2:
        menu = LowerLevelMenu(session_id=session_id, session=session, phone_number=g.phone_number,
                              user_response=user_response, user=user)
        return menu.execute()

    if level >= 50:
        menu = Deposit(session_id=session_id, session=session, phone_number=g.phone_number,
                       user_response=user_response, user=user, level=level)
        return menu.execute()

    if level >= 40:
        menu = WithDrawal(session_id=session_id, session=session, phone_number=g.phone_number,
                          user_response=user_response, user=user, level=level)
        return menu.execute()

    if level >= 10:
        menu = Airtime(session_id=session_id, session=session, phone_number=g.phone_number, user_response=user_response,
                       user=user, level=level)
        return menu.execute()

    response = make_response("END nothing here", 200)
    response.headers['Content-Type'] = "text/plain"
    return response
