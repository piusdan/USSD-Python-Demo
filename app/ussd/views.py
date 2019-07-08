from flask import g, make_response, request, url_for

from app.models import AnonymousUser
from . import ussd
from .airtime import Airtime
from .deposit import Deposit
from .home import LowerLevelMenu
from .register import RegistrationMenu
from .utils import respond
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


@ussd.route('/voice/menu')
def voice_menu():
    """
    When the user enters the digit - in this case 0, 1 or 2, this route
    switches between the various dtmf digits to
    make an outgoing call to the right recipient, who will be
    bridged to speak to the person currently listening to music on hold.
    We specify this music with the ringtone flag as follows:
    ringbackTone="url_to/static/media/SautiFinaleMoney.mp3"
    """

    # 1. Receive POST from AT
    isActive = request.get('isActive')
    callerNumber = request.get('callerNumber')
    dtmfDigits = request.get('dtmfDigits')
    sessionId = request.get('sessionId')
    # Check if isActive=1 to act on the call or isActive=='0' to store the
    # result

    if (isActive == '1'):
        # 2a. Switch through the DTMFDigits
        if (dtmfDigits == "0"):
            # Compose response - talk to sales-
            response = '<?xml version="1.0" encoding="UTF-8"?>'
            response += '<Response>'
            response += '<Say>Please hold while we connect you to Sales.</Say>'
            response += '<Dial phoneNumbers="880.welovenerds@ke.sip.africastalking.com" ringbackTone="{}"/>'.format(
                url_for('media', path='SautiFinaleMoney.mp3'))
            response += '</Response>'

            # Print the response onto the page so that our gateway can read it
            return respond(response)

        elif (dtmfDigits == "1"):
            # 2c. Compose response - talk to support-
            response = '<?xml version="1.0" encoding="UTF-8"?>'
            response += '<Response>'
            response += '<Say>Please hold while we connect you to Support.</Say>'
            response += '<Dial phoneNumbers="880.welovenerds@ke.sip.africastalking.com" ringbackTone="{}"/>'.format(
                url_for('media', path='SautiFinaleMoney.mp3'))
            response += '</Response>'

            # Print the response onto the page so that our gateway can read it
            return respond(response)
        elif (dtmfDigits == "2"):
            # 2d. Redirect to the main IVR-
            response = '<?xml version="1.0" encoding="UTF-8"?>'
            response += '<Response>'
            response += '<Redirect>{}</Redirect>'.format(url_for('voice_callback'))
            response += '</Response>'

            # Print the response onto the page so that our gateway can read it
            return respond(response)
        else:
            # 2e. By default talk to support
            response = '<?xml version="1.0" encoding="UTF-8"?>'
            response += '<Response>'
            response += '<Say>Please hold while we connect you to Support.</Say>'
            response += '<Dial phoneNumbers="880.welovenerds@ke.sip.africastalking.com" ringbackTone="{}"/>'.format(
                url_for('media', path='SautiFinaleMoney.mp3'))
            response += '</Response>'

            # Print the response onto the page so that our gateway can read it
            return respond(response)
    else:
        # 3. Store the data from the POST
        durationInSeconds = request.get('durationInSeconds')
        direction = request.get('direction')
        amount = request.get('amount')
        callerNumber = request.get('callerNumber')
        destinationNumber = request.get('destinationNumber')
        sessionId = request.get('sessionId')
        callStartTime = request.get('callStartTime')
        isActive = request.get('isActive')
        currencyCode = request.get('currencyCode')
        status = request.get('status')
