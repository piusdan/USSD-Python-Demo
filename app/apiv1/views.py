from flask import jsonify, json, current_app, request, make_response
from AfricasTalkingGateway import AfricasTalkingGateway, AfricasTalkingGatewayException
from .. import db
from ..models import User, SessionLevel

from . import api_v1


@api_v1.route('/', methods=['POST', 'GET'])
def index():

    return respond("END connection ok")



@api_v1.route('/ussd/callback', methods=['POST', 'GET'])
def ussd_callback():
    session_id = request.values.get("sessionId", None)
    serviceCode = request.values.get("serviceCode", None)
    phone_number = request.values.get("phoneNumber", None)
    text = request.values.get("text", "default")

    text_array = text.split("*")
    user_response = text_array[len(text_array) - 1]

    lowerUserLevels = {
        "0": home,
        "1": please_call,
        "2": deposit,
        "3": withdraw,
        "4": send_money,
        "5": buy_airtime,

        "6": pay_loan_menu,

        "default": default_menu
    }

    higherLevelResponses = {
        9: {

            # user_response : c2b_checkout(phone_number= phone_number, amount = int(user_response))
            "1": c2b_checkout,
            "2": c2b_checkout,
            "3": c2b_checkout,
            "default": default_mpesa_checkout
        },
        10: {
            # user_response : b2c_checkout(phone_number=phone_number, amount=int(user_response))
            "1": b2c_checkout,
            "2": b2c_checkout,
            "3": b2c_checkout,
            "default": b2c_default
        },
        11: {
            # "default": send_loan(session_id=session_id,
            #                      creditor_phone_number=phone_number,
            #                      debptor_phone_number=user_response)
            "default": send_loan
        },
        12: {
            # "4": re_pay_loan(session_id, phone_number, amount)
            "4": repay_loan,    # 1
            "5": repay_loan,    # 2
            "6": repay_loan,    # 3
            "default": default_loan_checkout
        },
        "default": {
            "default": default_loan_checkout

        }
    }

    register_user = {

        0: get_number,    # params = (session_id, phone_number=phone_number)
        21: get_name,      # params = (session_id, phone_number=phone_number, user_response=user_response)
        22: get_city,      # params = (session_id, phone_number=phone_number, user_response=user_response)
        "default": register_default,    # params = (session_id)

    }

    # get user and if user is not present register user
    user = User.query.filter_by(phone_number=phone_number).first()

    Session = SessionLevel.query.filter_by(
        session_id=session_id).first()
    if user:
        # if session is registered serve appropriate menu else serve the first
        # menu
        if Session:
            level = Session.level
            # if the user has a entered a response serve appropriate menu
            # else serve the default menu
            if user_response:
                # lower menus are handled by session level 1 and 0
                if level < 2:

                    # serve lower reponses
                    return lowerUserLevels[user_response](
                        user=user,
                        session_id=session_id)
                else:

                    # higher menus handled by session levels 9, 10, 11, 12
                    #  else the default higher level menu is served
                    if level == 9:
                        return higherLevelResponses[level].get(
                            user_response or "default")(
                            phone_number=phone_number,
                            amount=int(user_response)
                        )
                    elif level == 10:
                        return higherLevelResponses[level].get(
                            user_response or "default")(
                            phone_number=phone_number,
                            amount=int(user_response)
                        )
                    elif level == 11:
                        return higherLevelResponses[level].get("default")(
                            session_id=session_id,
                            creditor_phone_number=phone_number,
                            debptor_phone_number=user_response
                        )
                    elif level == 12:
                        return higherLevelResponses[level].get(
                            user_response or "default")(
                            phone_number=phone_number,
                            amount=int(user_response)
                        )
                    # continue registration of new user
                    elif level >= 21:
                        if level == 21:
                            return register_user[level](session_id, phone_number=phone_number, user_response=user_response)
                        elif level == 22:
                            return register_user[level](session_id, phone_number=phone_number, user_response=user_response)
                        else:
                            return register_user["default"]()
                    else:
                        return higherLevelResponses["default"].get("default")()

            else:
                return default_menu(user, session_id)
        else:
            # add a new session level

            add_session(session_id=session_id, phone_number=phone_number)
            # serve home menu
            return home(user=user, session_id=session_id)
    else:
        # start user registration proccess
        return register_user[0](session_id, phone_number=phone_number)

# level 1


def home(user, session_id):
    """
    If user level is zero or zero
    Serves the home menu
    :return: a response object with headers['Content-Type'] = "text/plain" headers
    """

    # upgrade user level and serve home menu
    session_level = SessionLevel.query.filter_by(session_id=session_id).first()
    session_level.promote_level()
    db.session.add(session_level)
    db.session.commit()
    # serve the menu
    menu_text = "CON Welcome to Nerd \
    Microfinance, {} Choose a service.\n".format(
        user.name)
    menu_text += " 1. Please call me.\n"
    menu_text += " 2. Deposit Money\n"
    menu_text += " 3. Withdraw Money\n"
    menu_text += " 4. Send Money\n"
    menu_text += " 5. Buy Airtime\n"
    menu_text += " 6. Repay Loan\n"

    # print the response on to the page so that our gateway can read it
    return respond(menu_text)


def please_call(user, session_id=None):
    # call the user and bridge to a sales person
    menu_text = "END Please wait while we place your call.\n"

    # make a call
    caller = "+254703554404"
    recepient = user.phone_number

    # create a new instance of our awesome gateway
    gateway = AfricasTalkingGateway(
        current_app.config["AT_USERNAME"], current_app.config["AT_APIKEY"])
    try:
        gateway.call(caller, recepient)
    except AfricasTalkingGateway as e:
        menu_text = "Encountered an error when calling: {}".format(str(e))

    # print the response on to the page so that our gateway can read it
    return respond(menu_text)


def deposit(session_id, user=None):
    # as how much and Launch teh Mpesa Checkout to the user
    menu_text = "CON How much are you depositing?\n"
    menu_text += " 1. 1 Shilling.\n"
    menu_text += " 2. 2 Shillings.\n"
    menu_text += " 3. 3 Shillings.\n"

    # Update sessions to level 9
    update_session(session_id, SessionLevel, 9)
    # print the response on to the page so that our gateway can read it
    return respond(menu_text)


def withdraw(session_id, user=None):
    # Ask how much and Launch B2C to the user
    menu_text = "CON How much are you withdrawing?\n"
    menu_text += " 1. 1 Shilling.\n"
    menu_text += " 2. 2 Shillings.\n"
    menu_text += " 3. 3 Shillings.\n"

    # Update sessions to level 10
    update_session(session_id, SessionLevel, 10)

    # Print the response onto the page so that our gateway can read it
    return respond(menu_text)


def send_money(session_id, user=None):
    # Send Another User Some Money
    menu_text = "CON You can only send 1 shilling.\n"
    menu_text += " Enter a valid phonenumber (like 0722122122)\n"

    # Update sessions to level 11
    update_session(session_id, SessionLevel, 11)
    # Print the response onto the page so that our gateway can read it
    return respond(menu_text)


def buy_airtime(user, session_id=None):
    # 9e.Send user airtime
    menu_text = "END Please wait while we load your account.\n"

    # Search DB and the Send Airtime

    recipientStringFormat = [{"phoneNumber": user.phone_number, "amount": "KES 5"}]

    # Create an instance of our gateway
    gateway = AfricasTalkingGateway(
        current_app.config["AT_USERNAME"], current_app.config["AT_APIKEY"])
    try:
        menu_text += gateway.sendAirtime(recipientStringFormat)
    except AfricasTalkingGatewayException as e:
        menu_text += str(e)

    # Print the response onto the page so that our gateway can read it
    return respond(menu_text)



def pay_loan_menu(session_id, user):

    # Ask how much and Launch the Mpesa Checkout to the user
    menu_text = "CON How much are you depositing?\n"
    menu_text += " 4. 1 Shilling.\n"
    menu_text += " 5. 2 Shillings.\n"
    menu_text += " 6. 3 Shillings.\n"

    # Update sessions to level 9
    session_level = SessionLevel.query.filter_by(session_id=session_id).first()

    session_level.promote_level(12)

    # Print the response onto the page so that our gateway can read it
    return respond(menu_text)


def default_menu(user, session_id):
    # Return user to Main Menu & Demote user's level
    menu_text = "CON You have to choose a service.\n"
    menu_text += "Press 0 to go back to main menu.\n"
    # demote
    session_level = SessionLevel.query.filter_by(session_id=session_id).first()
    session_level.demote_level()
    db.session.add(session_level)
    db.session.commit()
    # Print the response onto the page so that our gateway can read it
    return respond(menu_text)

# end level 1


# level 9
def c2b_checkout(phone_number, amount):
    # Alert user of incoming Mpesa checkout
    menu_text = "END We have sent the MPESA checkout...\n"
    menu_text += "If you dont have a bonga pin, dial \n"
    menu_text += "Dial dial *126*5*1# to create.\n"

    # Declare params
    gateway = make_gateway()
    product_name = "Nerd Payments"
    currency_code = "KES"
    amount = amount
    metadata = {"sacco": "Nerds", "productId": "321"}

    # pass to gateway
    try:
        menu_text += "transactionId is: %s" % \
            gateway.initiateMobilePaymentCheckout(
                product_name,
                phone_number,
                currency_code,
                amount,
                metadata)

    except AfricasTalkingGatewayException as e:
        menu_text += "Received error response: {}".format(str(e))

    # Print the response onto the page so that our gateway can read it
    return respond(menu_text)


def default_mpesa_checkout():
    menu_text = "END Apologies, something went wrong... \n"
    # Print the response onto the page so that our gateway can read it
    return respond(menu_text)
# end level 9


# level 10
def b2c_checkout(phone_number, amount):
    # Find account
    user = User.query.filter_by(phone_number=phone_number).first()
    if user.account > 1:
        # Reduce the balance
        user.withdraw(1)
        db.session.add(user)
        db.session.commit()

        menu_text = "END We are sending your withdrawal of\n"
        menu_text += " KES {}/- shortly... \n".format(amount)

        # Declare Params

        gateway = make_gateway()

        product_name = "Nerd Payments"
        recipients = [
            {"phoneNumber": phone_number,
             "currencyCode": "KES",

             "amount": amount, "metadata":

                 {
                     "name": "Client",
                     "reason": "Withdrawal"
                 }


             }
        ]
        # Send B2c
        try:
            gateway.mobilePaymentB2CRequest(product_name, recipients)
        except AfricasTalkingGatewayException as e:
            menu_text += "Received error response {}".format(str(e))
    else:
        # Alert user of insufficient funds

        menu_text = "END Sorry, you don't have sufficient\n"

        menu_text += " funds in your account \n"

    return respond(menu_text)


def b2c_default():
    menu_text = "END Apologies, something went wrong... \n"
    # Print the response onto the page so that our gateway can read it
    return respond(menu_text)
# end level 10


# level 11
def send_loan(session_id, debptor_phone_number, creditor_phone_number, amount=1):
    # Find and update creditor
    creditorAccount = User.query.filter_by(
        phone_number=creditor_phone_number).first()
    creditorAccount.withdraw(amount)
    # Send the loan if new account balance is above 0
    if creditorAccount.account > 0:
        menu_text = "END We are sending KES {}/- \n".format(amount)
        menu_text += "to the loanee shortly. \n"
        # get and update Debtor
        debptorAccount = User.query.filter_by(
            phone_number=debptor_phone_number).first()

        if debptorAccount:
            debptorAccount.deposit(amount)
            db.session.add(debptorAccount)
            db.session.add(creditorAccount)

        # SMS New Balance
        code = '20080'
        recepients = creditor_phone_number
        message = "We have sent {}/- to {} If \
        this is a wrong number the transaction will fail" \
            "Your new balance is {} \
            Thank you.".format(amount, creditor_phone_number,
                               creditorAccount.account)
        gateway = make_gateway()
        try:
            gateway.sendMessage(recepients, message, code)
        except AfricasTalkingGatewayException as e:
            print "Encountered an error while sending: {}\n".format(str(e))

        # TODO figure out
        # change user level to 0
        # session_level = SessionLevel.query.filter_by(session_id=session_id).first()
        # session_level.demote_level()
        # db.session.add(session_level)

        # Update DB
        db.session.commit()

        # respond
        menu_text += "CONFIRMED we have sent money to {} \n".format(
            creditorAccount.phone_number)
    else:
        # respond
        menu_text = "END Sorry we could not send the money. \n"
        menu_text += "You dont have enough money. {}\n".format(
            creditorAccount.account)

    # Print the response onto the page so that our gateway can read it
    return respond(menu_text)


def repay_loan(phone_number, amount):

    """
    Pay Loan
    :param session_id, amount:
    :return response object:
    """
    # Alert user of incoming Mpesa checkout
    menu_text = "END You are repaying {}/-. \
    We have sent the MPESA \
    checkout...\n".format(
        amount)
    menu_text += "If you dont have a bonga pin, dial \n"
    menu_text += "Dial dial *126*5*1# to create.\n"

    # Declare Params
    gateway = make_gateway()
    productName = "Nerd Payments"
    currencyCode = "KES"
    amount = amount
    metadata = {"Sacco Repayment": "Nerds", "productId": "321"}

    # pass to gateway
    try:
        transactionId = gateway.initiateMobilePaymentCheckout(
            productName, phone_number, currencyCode, amount,
            metadata)
    except AfricasTalkingGatewayException as e:
        print "Received error response: {}".format(str(e))

    # Print the response onto the page so that our gateway can read it
    return respond(menu_text)


def default_loan_checkout():
    menu_text = "END Apologies, something went wrong... \n"
    # Print the response onto the page so that our gateway can read it
    return respond(menu_text)


def default_higher_level_response():
    # Request for city again
    menu_text = "END Apologies, something went wrong... \n"

    # Print the response onto the page so that our gateway can read it
    return respond(menu_text)

# end higher level responses


def get_number(session_id, phone_number):
    # insert user's phone number
    new_user = User(phone_number=phone_number)
    db.session.add(new_user)

    db.session.commit()

    # create a new sessionlevel
    session_level = SessionLevel(
        session_id=session_id, phone_number=phone_number)

    # promote the user a higher session level

    session_level.promote_level(21)

    db.session.add(session_level)
    db.session.commit()
    menu_text = "CON Please enter your name"

    # Print the response onto the page so that our gateway can read it
    return respond(menu_text)



def get_name(session_id, phone_number, user_response=None):

    # Request again for name - level has not changed...
    if user_response:

        # insert user name into db request for city
        new_user = User.query.filter_by(phone_number=phone_number).first()
        new_user.name = user_response

        # graduate user level
        session_level = SessionLevel.query.filter_by(
            session_id=session_id).first()

        session_level.promote_level(22)

        db.session.add(session_level)
        db.session.add(new_user)
        menu_text = "CON Enter your city"

    else:
        menu_text = "CON Name not supposed to be empty. Please enter your name \n"

    # Print the response onto the page so that our gateway can read it
    return respond(menu_text)


def get_city(session_id, phone_number, user_response):
    if user_response:

        # if user response is not an empty string
        # insert user city into db request for city
        new_user = User.query.filter_by(phone_number=phone_number).first()
        new_user.city = user_response

        # demote user level to 0
        session_level = SessionLevel.query.filter_by(
            session_id=session_id).first()
        session_level.demote_level()
        db.session.add(session_level)
        db.session.add(new_user)
        db.session.commit()
        menu_text = "END You have been successfully registered. \n"

    else:

        # if user response is an empty string
        # Request again for city - level has not changed...
        menu_text = "CON City not supposed to be empty. Please enter your city \n"

    # Print the response onto the page so that our gateway can read it
    return respond(menu_text)


def register_default(session_id):
    menu_text = "END Apologies something went wrong \n"

    # Print the response onto the page so that our gateway can read it
    return respond(menu_text)

# utils


def update_session(session_id, session_level, level):
    session_level = session_level.query.filter_by(
        session_id=session_id).first()
    session_level.promote_level(level)
    db.session.add(session_level)
    db.session.commit()


def respond(menu_text):
    response = make_response(menu_text, 200)
    response.headers['Content-Type'] = "text/plain"
    return response


def make_gateway():
    return AfricasTalkingGateway(
        current_app.config["AT_USERNAME"],
        current_app.config["AT_APIKEY"], "sandbox")



def add_session(session_id, phone_number):
    session = SessionLevel(
        phone_number=phone_number, session_id=session_id)
    db.session.add(session)
    db.session.commit()
    return session

