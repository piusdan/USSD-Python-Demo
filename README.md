
# Setting Up a USSD Service for MicroFinance Institutions
#### A step-by-step guide

- Setting up the logic for USSD is easy with the [Africa's Talking API](docs.africastalking.com/ussd). This is a guide to how to use the code provided on this [repository](https://github.com/Piusdan/USSD-Python-Demo) to create a USSD that allows users to get registered and then access a menu of the following services:

| USSD APP Features                            |
| --------------------------------------------:| 
| Request to get a call from support           | 
| Deposit Money to user's account              |   
| Withdraw money from users account            |   
| Send money from users account to another     |   
| Repay loan                                   |   
| Buy Airtime                                  |  

## Prerequisites

# INSTALLATION AND GUIDE

1. clone/download the project into the directory of your choice

- First, in the config.py file in your root directory and fill in your Africa's Talking API credentials as below.
    
    AT_APIKEY = [your api key]
    AT_USERNAME = [your username]
    AT_NUMBER = [to test calls, enter a live number]
    SMS_CODE = [your sms code]
    PRODUCT_NAME = [your product name]

# requirements

    Python version 2.* 
    AfricastalkingGateway==1.7
    alembic==0.9.1
    click==6.7
    dominate==2.3.1
    Flask==0.12
    Flask-Bootstrap==3.3.7.1
    Flask-Migrate==2.0.3
    Flask-Script==2.0.5
    Flask-SQLAlchemy==2.2
    Flask-SSLify==0.1.5
    itsdangerous==0.24
    Jinja2==2.9.5
    Mako==1.0.6
    MarkupSafe==1.0
    migrate==0.3.8
    python-editor==1.0.3
    requests==2.13.0
    SQLAlchemy==1.1.6
    visitor==0.1.3
    Werkzeug==0.12.1

-> The project is currently not compatible with future python version

-> Recommendend running the project in a virtual environment


2. Create a virtual environment

          $ makevirtualenv microfinance            # creates a virtual environment
          $ source microfinace/bin/activate        # start the virtual environment

3. Install the project's requirements 

          $ pip install requirements.txt           # download and install project's dependancies

4. Initialise your database

        $ python manage.py runserver             # starts project

5. Run your server

          $ python manage.py runserver             # starts project
          # This command starts your server on https://localhost:5000

- You need to set up on the sandbox and [create](https://sandbox.africastalking.com/ussd/createchannel) a USSD channel that you will use to test by dialing into it via our [simulator](https://simulator.africastalking.com:1517/).

- Assuming that you are doing your development on a localhost, you have to expose your application living in the webroot of your localhost to the internet via a tunneling application like [Ngrok](https://ngrok.com/). Otherwise, if your server has a public IP, you are good to go! Your URL callback for this demo will become:
 http://<your ip address>/MfUSSD/microfinanceUSSD.php

- This application has been developed on an Ubuntu 16.04LTS and lives in the web root at /var/www/html/MfUSSD. Courtesy of Ngrok, the publicly accessible url is: https://49af2317.ngrok.io (instead of http://localhost) which is referenced in the code as well. 
(Create your own which will be different.)

- The webhook or callback to this application therefore becomes: 
https://49af2317.ngrok.io/api/v1.1/ussd/callback. 
To allow the application to talk to the Africa's Talking USSD gateway, this callback URL is placed in the dashboard, [under ussd callbacks here](https://account.africastalking.com/ussd/callback).

- Finally, this application works with a connection to an sqlite database. This is the default database shipped with python, however its recomended switching to a proper database when deploying the application. Also create a session_levels table and a users table. These details are configured in the models.py and this is required in the main application script app/apiv2/views.py

mysql> describe microfinance;

| Field         | Type                         | Null  | Key | Default           | Extra                       |
| ------------- |:----------------------------:| -----:|----:| -----------------:| ---------------------------:|
| id            | int(6)                       |   YES |     | NULL              |                             |
| name          | varchar(30)                  |   YES |     | NULL              |                             |
| phonenumber   | varchar(20)                  |   YES |     | NULL              |                             |
| city          | varchar(30)                  |   YES |     | NULL              |                             |
| validation    | varchar(30)                  |   YES |     | NULL              |                             |
| reg_date      | timestamp                    |   NO  |     | CURRENT_TIMESTAMP | on update CURRENT_TIMESTAMP |

6 rows in set (0.02 sec)

mysql> describe session_levels;

| Field         | Type                         | Null  | Key | Default | Extra |
| ------------- |:----------------------------:| -----:|----:| -------:| -----:|
| session_id    | varchar(50)                  |   YES |     | NULL    |       |
| phonenumber   | varchar(25)                  |   YES |     | NULL    |       |
| level         | tinyint(1)                   |   YES |     | NULL    |       |

3 rows in set (0.02 sec)


## Features on the Services List
This USSD application has the following user journey.

- The user dials the ussd code - something like `*384*303#`

- The application checks if the user is registered or not. If the user is registered, the services menu is served which allows the user to: receive SMS, receive a call with an IVR menu.

- In case the user is not registered, the application prompts the user for their name and city (with validations), before successfully serving the services menu.

## Code walkthrough
This documentation is for the USSD application that lives inhttps://49af2317.ngrok.io/api/v1.1/ussd/callback.

```python
    #1. This code only runs after a post request from AT
    @api_v11.route('/ussd/callback', methods=['POST'])
    def ussd_callback():
        """
        Handles post call back from AT

        :return:
        """
```
Import all the necessary scripts to run this application

```python
    # 2. Import all neccesary modules
    from flask import request, url_for
    from ..models import User, SessionLevel
    from .utils import respond, add_session
    from . import api_v11
    from .menu import LowerLevelMenu, HighLevelMenu, RegistrationMenu
```

Receive the HTTP POST from AT

```python
    # 3. get data from ATs post payload
    session_id = request.values.get("sessionId", None)
    phone_number = request.values.get("phoneNumber", None)
    text = request.values.get("text", "default")
```

The AT USSD gateway keeps chaining the user response. We want to grab the latest input from a string like 1*1*2
```python
    text_array = text.split("*")
    user_response = text_array[len(text_array) - 1]
```

Interactions with the user can be managed using the received sessionId and a level management process that your application implements as follows.

- The USSD session has a set time limit(20-180 secs based on provider) under which the sessionId does not change. Using this sessionId, it is easy to navigate your user across the USSD menus by graduating their level(menu step) so that you dont serve them the same menu or lose track of where the user is. 
- Check the session_levels table for a user with the same phone number as that received in the HTTP POST. If this exists, the user is returning and they therefore have a stored level. Grab that level and serve that user the right menu. Otherwise, serve the user the home menu.
```python
	# 4. Check the level of the user from the DB and retain default level if none is found for this session
	session = SessionLevel.query.filter_by(session_id=session_id).first()
	level = session.level
	if level < 2:
        # Initialise the lower level menu
        menu = LowerLevelMenu(session_id=session_id, phone_number=phone_number)
    elif level <= 12:
        # else initialise higher level menu
        menu = HighLevelMenu(user_response, phone_number, session_id)
    else:
        # Register the user session and set the default level to 0
        add_session(session_id=session_id, phone_number=phone_number)
        # create a lower level menu instance
        menu = LowerLevelMenu(session_id=session_id, phone_number=phone_number)
```

Before serving the menu, check if the incoming phone number request belongs to a registered user(sort of a login). If they are registered, they can access the menu, otherwise, they should first register.
```python
	# 5. Check if the user is in the db
    user = User.query.filter_by(phone_number=phone_number).first()

	# 6. Check if the user is available (yes)->Serve the menu; (no)->Register the user
	if user:
		# 7. Serve the Services Menu
```

If the user is available and all their mandatory fields are complete, then the application switches between their responses to figure out which menu to serve. The first menu is usually a result of receiving a blank text -- the user just dialed in.
```python
    # 7. Serve the Services Menu 
    # if the user is fully registered, level 0 and 1 serve the basic menus, while the rest allow for financial transactions)
    if level < 2:
        menu = LowerLevelMenu( session_id=session_id, phone_number=phone_number)
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
            # check to see if the user actually typed something
            if user_response in menus.keys():
                return menus.get(user_response)()
            # Otherwise demote the session level and serve the default menu
            else:
                    return menus.get("default")()
    
    # We manage other financial services using higher levels (between 9 and 12)
        elif level <= 12:
            menu = HighLevelMenu(user_response, phone_number, session_id)
            # initialise menu dict
            menus = {
                9: {
                        "1": menu.c2b_checkout,
                        "2": menu.c2b_checkout,
                        "3": menu.c2b_checkout,
                        "default": menu.default_mpesa_checkout
                    },
                10: {
                        "1": menu.b2c_checkout,
                        "2": menu.b2c_checkout,
                        "3": menu.b2c_checkout,
                        "default": menu.b2c_default
                    },
                11: {
                        "default": menu.send_loan
                    },
                12:{
                        "4": menu.repay_loan,  # 1
                        "5": menu.repay_loan,  # 2
                        "6": menu.repay_loan,  # 3
                        "default": menu.default_loan_checkout
                    },
                    "default": {
                        "default": menu.default_loan_checkout
                    }
                }
            # check to see if the user typed a valid key
            if user_response in menus[level].keys():
                return menus[level].get(user_response)()
             else:
             # server the default menu
                return menus[level]["default"]()	
```
If the user is not registered, we use the users level - purely to take the user through the registration process. We also enclose the logic in a condition that prevents the user from sending empty responses.
```python
    else:
    # create a menu instance
        menu = RegistrationMenu(
        session_id=session_id, phone_number=phone_number, user_response=user_response)
        # register user
        return menu.get_number()      # adds the user number to the DB and promotes the session level to 20
    
    # the rest of the menu is then handled on level 20-22
    elif level <= 22:
            menu = RegistrationMenu( session_id=session_id, phone_number=phone_number, user_response=user_response)
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

```

## Complexities of Voice.
- The voice service included in this script requires a few juggling acts and probably requires a short review of its own.
When the user requests a to get a call, the following happens.
a) The script at https://49af2317.ngrok.io/api/v1.1/ussd/callback requests the call() method through the Africa's Talking Voice Gateway, passing the number to be called and the caller/dialer Id. The call is made and it comes into the users phone. When they answer isActive becomes 1.

```python
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
        return respond(menu_text)	case "2":
```			        
b) As a result, Africa's Talking gateway check the callback for the voice number in this case +254703554404.
c) The callback is a route on our views.py file whose URL is: https://49af2317.ngrok.io/api/v1.1/voice/callback
d) The instructions are to respond with a text to speech message for the user to enter dtmf digits.

```python
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
```
e) When the user enters the digit - in this case 0, 1 or 2, this digit is submitted to another route also in our views.py file which lives at https://49af2317.ngrok.io/api/v1.1/voice/menu and which switches between the various dtmf digits to make an outgoing call to the right recipient, who will be bridged to speak to the person currently listening to music on hold. We specify this music with the ringtone flag as follows: ringbackTone="url_to/static/media/SautiFinaleMoney.mp3"

```python
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
```

When the agent/person picks up, the conversation can go on.

- That is basically our application! Happy coding!