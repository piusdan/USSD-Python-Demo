from flask import g, make_response

from app.apiv2.airtime import Airtime
from app.apiv2.home import LowerLevelMenu
from app.apiv2.register import RegistrationMenu
from app.apiv2.withdraw import WithDrawal
from app.apiv2.deposit import Deposit
from app.models import AnonymousUser
from . import api_v2


@api_v2.route('/', methods=['POST', 'GET'])
def index():
    response = make_response("END connection ok")
    response.headers['Content-Type'] = "text/plain"
    return response


@api_v2.route('/ussd/callback', methods=['POST'])
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
