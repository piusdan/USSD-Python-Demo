from flask import request, url_for, send_from_directory
from ..models import User, SessionLevel
from .utils import respond, add_session
from . import api_v11
from .menu import LowerLevelMenu, HighLevelMenu, RegistrationMenu


@api_v11.route('/', methods=['POST', 'GET'])
def index():
    return respond("END connection ok")


@api_v11.route('/ussd/callback', methods=['POST'])
def ussd_callback():
    """
    Handles post call back from AT

    :return:
    """

    # GET values from the AT's POST request
    session_id = request.values.get("sessionId", None)
    phone_number = request.values.get("phoneNumber", None)
    text = request.values.get("text", "default")
    text_array = text.split("*")
    user_response = text_array[len(text_array) - 1]

    # 4. Check the level of the user from the DB and retain default level if none is found for this session
    session = SessionLevel.query.filter_by(session_id=session_id).first()
    # 5. Check if the user is in the d
    user = User.query.filter_by(phone_number=phone_number).first()
  	# 6. Check if the user is available (yes)->Serve the menu; (no)->Register the user
    if user:
		# 7. Serve the Services Menu
        if session:
            level = session.level
            # if level is less than 2 serve lower level menus
            if level < 2:
                menu = LowerLevelMenu(
                    session_id=session_id, phone_number=phone_number)
                # initialise menu dict
                menus = {
                    "0": menu.home,
                    "1": menu.please_call,
                    "2": menu.deposit,
                    "3": menu.withdraw,
                    "4": menu.send_money,
                    "5": menu.buy_airtime,
                    "6": menu.pay_loan_menu,
                    "default": menu.default_menu
                }
                # serve menu
                if user_response in menus.keys():
                    return menus.get(user_response)()
                else:
                    return menus.get("default")()

            # if level is between 9 and 12 serve high level response
            elif level <= 12:
                menu = HighLevelMenu(user_response, phone_number, session_id)
                # initialise menu dict
                menus = {
                    9: {
                        # user_response : c2b_checkout(
                        # phone_number= phone_number, amount = int(user_response)
                        # )
                        "1": menu.c2b_checkout,
                        "2": menu.c2b_checkout,
                        "3": menu.c2b_checkout,
                        "default": menu.default_mpesa_checkout
                    },
                    10: {
                        # user_response : b2c_checkout(
                        # phone_number=phone_number, amount=int(user_response)
                        # )
zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz                        "1": menu.b2c_checkout,
                        "2": menu.b2c_checkout,
                        "3": menu.b2c_checkout,
                        "default": menu.b2c_default
                    },
                    11: {
                        # "default": send_loan(session_id=session_id,
                        #                      creditor_phone_number=phone_number,
                        #                      debptor_phone_number=user_response)
                        "default": menu.send_loan
                    },
                    12: {
                        # "4": re_pay_loan(session_id, phone_number, amount)
                        "4": menu.repay_loan,  # 1
                        "5": menu.repay_loan,  # 2
                        "6": menu.repay_loan,  # 3
                        "default": menu.default_loan_checkout
                    },
                    "default": {
                        "default": menu.default_loan_checkout
                    }
                }
                if user_response in menus[level].keys():
                    return menus[level].get(user_response)()
                else:
                    return menus[level]["default"]()
            elif level <= 22:
                menu = RegistrationMenu(
                    session_id=session_id, phone_number=phone_number, user_response=user_response)
                # handle higher level user registration
                menus = {
                    # params = (session_id, phone_number=phone_number)
                    0: menu.get_number,
                    21: menu.get_name,
                    # params = (session_id, phone_number=phone_number,
                    # user_response=user_response)
                    22: menu.get_city,
                    # params = (session_id, phone_number=phone_number,
                    # user_response=user_response)
                    "default": menu.register_default,  # params = (session_id)
                }

                return menus.get(level or "default")()
            else:
                return LowerLevelMenu.class_menu(session)
        else:
            # add a new session level
            add_session(session_id=session_id, phone_number=phone_number)
            # create a menu instance
            menu = LowerLevelMenu(session_id=session_id,
                                  phone_number=phone_number)
            # serve home menu
            return menu.home()

    else:
        # create a menu instance
        menu = RegistrationMenu(
            session_id=session_id, phone_number=phone_number, user_response=user_response)
        # register user
        return menu.get_number()


@api_v11.route('/voice/callback', methods=['POST'])
def voice_callback():
    """
    voice_callback from AT's gateway is handled here

    """
    sessionId = request.get('sessionId')
    isActive = request.get('isActive')

    if isActive == "1":
        callerNumber = request.get('callerNumber')
        # GET values from the AT's POST request
        session_id = request.values.get("sessionId", None)
        isActive = request.values.get('isActive')
        serviceCode = request.values.get("serviceCode", None)
        text = request.values.get("text", "default")
        text_array = text.split("*")
        user_response = text_array[len(text_array) - 1]

        # Compose the response
        menu_text = '<?xml version="1.0" encoding="UTF-8"?>'
        menu_text += '<Response>'
        menu_text += '<GetDigits timeout="30" finishOnKey="#" callbackUrl="https://49af2317.ngrok.io/api/v1.1/voice/callback">'
        menu_text += '<Say>"Thank you for calling. Press 0 to talk to sales, 1 to talk to support or 2 to hear this message again."</Say>'
        menu_text += '</GetDigits>'
        menu_text += '<Say>"Thank you for calling. Good bye!"</Say>'
        menu_text += '</Response>'

        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    else:
        # Read in call details (duration, cost). This flag is set once the call is completed.
        # Note that the gateway does not expect a response in thie case

        duration = request.get('durationInSeconds')
        currencyCode = request.get('currencyCode')
        amount = request.get('amount')

        # You can then store this information in the database for your records


@api_v11.route('/voice/menu')
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
            response += '<Dial phoneNumbers="880.welovenerds@ke.sip.africastalking.com" ringbackTone="{}"/>'.format(url_for('media', path='SautiFinaleMoney.mp3'))
            response += '</Response>'

            # Print the response onto the page so that our gateway can read it
            return respond(response)

        elif (dtmfDigits == "1"):
            # 2c. Compose response - talk to support-
            response = '<?xml version="1.0" encoding="UTF-8"?>'
            response += '<Response>'
            response += '<Say>Please hold while we connect you to Support.</Say>'
            response += '<Dial phoneNumbers="880.welovenerds@ke.sip.africastalking.com" ringbackTone="{}"/>'.format(url_for('media', path='SautiFinaleMoney.mp3'))
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
            response += '<Dial phoneNumbers="880.welovenerds@ke.sip.africastalking.com" ringbackTone="{}"/>'.format(url_for('media', path='SautiFinaleMoney.mp3'))
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

        # 3a. Store the data, write your SQL statements here-

@api_v11.route('/media/<path:path>')
def media(path):
    return send_from_directory('media', path)