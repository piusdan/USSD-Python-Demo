from utils import respond, update_session, make_gateway
from .AfricasTalkingGateway import AfricasTalkingGateway, AfricasTalkingGatewayException
from flask import current_app
from ..models import SessionLevel, User
from .. import db


class LowerLevelMenu:
    """


    """
    def __init__(self, session_id, phone_number):
        """
        initialises the Menu class
        :param user, session_id
        sets the user and session_id to be used by the menus
        """
        self.session_id = session_id
        self.user = User.query.filter_by(phone_number=phone_number).first()
        self.session = SessionLevel.query.filter_by(session_id=self.session_id).first()

    def home(self):
        """
        If user level is zero or zero
        Serves the home menu
        :return: a response object with headers['Content-Type'] = "text/plain" headers
        """

        # upgrade user level and serve home menu
        # TODO background task here
        self.session.promote_level()
        db.session.add(self.session)
        db.session.commit()
        # serve the menu
        menu_text = "CON Welcome to Nerd \
        Microfinance, {} Choose a service.\n".format(
            self.user.name)
        menu_text += " 1. Please call me.\n"
        menu_text += " 2. Deposit Money\n"
        menu_text += " 3. Withdraw Money\n"
        menu_text += " 4. Send Money\n"
        menu_text += " 5. Buy Airtime\n"
        menu_text += " 6. Repay Loan\n"

        # print the response on to the page so that our gateway can read it
        return respond(menu_text)

    def please_call(self):
        # call the user and bridge to a sales person
        menu_text = "END Please wait while we place your call.\n"

        # make a call
        caller = current_app.config["AT_NUMBER"]
        to = self.user.phone_number

        # create a new instance of our awesome gateway
        gateway = AfricasTalkingGateway(
            current_app.config["AT_USERNAME"], current_app.config["AT_APIKEY"])
        try:
            gateway.call(caller, to)
        except AfricasTalkingGateway as e:
            print "Encountered an error when calling: {}".format(str(e))

        # print the response on to the page so that our gateway can read it
        return respond(menu_text)

    def deposit(self):
        # as how much and Launch teh Mpesa Checkout to the user
        menu_text = "CON How much are you depositing?\n"
        menu_text += " 1. 1 Shilling.\n"
        menu_text += " 2. 2 Shillings.\n"
        menu_text += " 3. 3 Shillings.\n"

        # Update sessions to level 9
        update_session(self.session_id, SessionLevel, 9)
        # print the response on to the page so that our gateway can read it
        return respond(menu_text)

    def withdraw(self):
        # Ask how much and Launch B2C to the user
        menu_text = "CON How much are you withdrawing?\n"
        menu_text += " 1. 1 Shilling.\n"
        menu_text += " 2. 2 Shillings.\n"
        menu_text += " 3. 3 Shillings.\n"

        # Update sessions to level 10
        update_session(self.session_id, SessionLevel, 10)

        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    def send_money(self):
        # Send Another User Some Money
        menu_text = "CON You can only send 1 shilling.\n"
        menu_text += " Enter a valid phonenumber (like 0722122122)\n"

        # Update sessions to level 11
        update_session(self.session_id, SessionLevel, 11)
        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    def buy_airtime(self):
        # 9e.Send user airtime
        menu_text = "END Please wait while we load your account.\n"

        # Search DB and the Send Airtime
        recipientStringFormat = [{"phoneNumber": self.user.phone_number, "amount": "KES 5"}]

        # Create an instance of our gateway
        gateway = AfricasTalkingGateway(
            current_app.config["AT_USERNAME"], current_app.config["AT_APIKEY"])
        try:
            menu_text += gateway.sendAirtime(recipientStringFormat)
        except AfricasTalkingGatewayException as e:
            menu_text += str(e)

        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    def pay_loan_menu(self):
        # Ask how much and Launch the Mpesa Checkout to the user
        menu_text = "CON How much are you depositing?\n"
        menu_text += " 4. 1 Shilling.\n"
        menu_text += " 5. 2 Shillings.\n"
        menu_text += " 6. 3 Shillings.\n"

        # Update sessions to level 9
        self.session.promote_level(12)
        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    def default_menu(self):
        # Return user to Main Menu & Demote user's level
        menu_text = "CON You have to choose a service.\n"
        menu_text += "Press 0 to go back to main menu.\n"
        # demote
        self.session.demote_level()
        db.session.add(self.session)
        db.session.commit()
        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    @staticmethod
    def class_menu(session):
        # Return user to Main Menu & Demote user's level
        menu_text = "CON You have to choose a service.\n"
        menu_text += "Press 0 to go back to main menu.\n"
        # demote
        session.demote_level()
        db.session.add(session)
        db.session.commit()
        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

class HighLevelMenu:
    """
    Serves high level callbacks
    """
    def __init__(self, user_response, phone_number, session_id):
        """

        """
        self.phone_number = phone_number
        self.session_id = session_id
        self.user = User.query.filter_by(phone_number=phone_number).first()
        self.session = SessionLevel.query.filter_by(session_id=self.session_id).first()
        self.user_response = user_response


    def c2b_checkout(self):
        # Alert user of incoming Mpesa checkout
        menu_text = "END We have sent the MPESA checkout...\n"
        menu_text += "If you dont have a bonga pin, dial \n"
        menu_text += "Dial dial *126*5*1# to create.\n"

        # Declare params
        gateway = make_gateway()
        product_name = current_app.config["PRODUCT_NAME"]
        currency_code = "KES"
        amount = int(self.user_response)
        metadata = {"sacco": "Nerds", "productId": "321"}

        # pass to gateway
        try:
            menu_text += "transactionId is: %s" % \
                         gateway.initiateMobilePaymentCheckout(
                             product_name,
                             self.phone_number,
                             currency_code,
                             amount,
                             metadata)

        except AfricasTalkingGatewayException as e:
            menu_text += "Received error response: {}".format(str(e))

        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    def default_mpesa_checkout(self):
        menu_text = "END Apologies, something went wrong... \n"
        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    # end level 9


    # level 10
    def b2c_checkout(self):
        if self.user.account > 1:
            # Reduce the balance
            self.user.withdraw(1)
            db.session.add(self.user)
            db.session.commit()

            menu_text = "END We are sending your withdrawal of\n"
            menu_text += " KES {}/- shortly... \n".format(self.user_response)

            # Declare Params
            gateway = make_gateway()
            product_name = current_app.config["PRODUCT_NAME"]
            recipients = [
                {"phoneNumber": self.phone_number,
                 "currencyCode": "KES",
                 "amount": int(self.user_response), "metadata":
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

    def b2c_default(self):
        menu_text = "END Apologies, something went wrong... \n"
        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    # end level 10


    # level 11
    def send_loan(self, ):
        debptor_phone_number = self.user_response
        amount = 1
        # Find and update creditor
        creditorAccount = self.user
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
            code = current_app.config["SMS_CODE"]
            recepients = self.phone_number
            message = "We have sent {}/- to {} \nIf \
            this is a wrong number the transaction will fail\n" \
                      "Your new balance is {} \n\
                      Thank you.\n".format(amount, debptor_phone_number,
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

    def repay_loan(self):
        """
        Pay Loan
        :param session_id, amount:
        :return response object:
        """
        # Alert user of incoming Mpesa checkout
        amount = int(self.user_response)
        menu_text = "END You are repaying {}/-. \
        We have sent the MPESA \
        checkout...\n".format(
            amount)
        menu_text += "If you dont have a bonga pin, dial \n"
        menu_text += "Dial dial *126*5*1# to create.\n"

        # Declare Params
        gateway = make_gateway()
        productName = current_app.config["PRODUCT_NAME"]
        currencyCode = "KES"
        metadata = {"Sacco Repayment": "Nerds", "productId": "321"}

        # pass to gateway
        try:
            transactionId = gateway.initiateMobilePaymentCheckout(
                productName, self.phone_number, currencyCode, amount,
                metadata)
        except AfricasTalkingGatewayException as e:
            print "Received error response: {}".format(str(e))

        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    @staticmethod
    def default_loan_checkout():
        menu_text = "END Apologies, something went wrong... \n"
        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    @staticmethod
    def default_higher_level_response():
        # Request for city again
        menu_text = "END Apologies, something went wrong... \n"

        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

        # end higher level responses


class RegistrationMenu:
    """
    Serves registration callbacks
    """
    def __init__(self, phone_number, session_id, user_response):
        """

        """
        self.session_id = session_id
        self.user = User.query.filter_by(phone_number=phone_number).first()
        self.session = SessionLevel.query.filter_by(session_id=self.session_id).first()
        self.user_response = user_response
        self.phone_number = phone_number

    def get_number(self):
        # insert user's phone number
        new_user = User(phone_number=self.phone_number)
        # TODO background task
        db.session.add(new_user)
        db.session.commit()
        # create a new sessionlevel
        session = SessionLevel(
            session_id=self.session_id, phone_number=self.phone_number)

        # promote the user a higher session level
        session.promote_level(21)
        db.session.add(session)
        db.session.commit()
        menu_text = "CON Please enter your name"

        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    def get_name(self):
        # Request again for name - level has not changed...
        if self.user_response:

            # insert user name into db request for city
            self.user.name =self.user_response

            # graduate user level

            self.session.promote_level(22)
            db.session.add(self.session)
            db.session.add(self.user)
            menu_text = "CON Enter your city"

        else:
            menu_text = "CON Name not supposed to be empty. Please enter your name \n"

        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    def get_city(self):
        if self.user_response:

            # if user response is not an empty string
            # insert user city into db request for city
            self.user.city = self.user_response

            # demote user level to 0
            self.session.demote_level()
            db.session.add(self.session)
            db.session.add(self.user)
            db.session.commit()
            menu_text = "END You have been successfully registered. \n"

        else:

            # if user response is an empty string
            # Request again for city - level has not changed...
            menu_text = "CON City not supposed to be empty. Please enter your city \n"

        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)

    @staticmethod
    def register_default():
        menu_text = "END Apologies something went wrong \n"

        # Print the response onto the page so that our gateway can read it
        return respond(menu_text)
