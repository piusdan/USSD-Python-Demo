import logging
import os

from africastalking.AfricasTalkingGateway import AfricasTalkingGateway, AfricasTalkingGatewayException


class GatewayException(AfricasTalkingGatewayException):
    pass


class ussdAfricasTalkingGateway(AfricasTalkingGateway):
    def __init__(self):
        logging.info("Initialising Africastalking gateway")

    def init_app(self, app):
        # this initialises an AfricasTalking Gateway instanse similar to calling
        # africastalking.gateway(username, apikey, environment)
        # this enables us to initialise one gateway to use throughout the app

        self.username = app.config['AT_USERNAME']
        self.apiKey = app.config['AT_APIKEY']
        self.environment = app.config['AT_ENVIRONMENT']
        self.HTTP_RESPONSE_OK = 200
        self.HTTP_RESPONSE_CREATED = 201

        # Turn this on if you run into problems. It will print the raw HTTP response from our server
        if os.environ.get('APP_CONFIG') == 'development':
            self.Debug = True
        else:
            self.Debug = False

africastalkinggateway = ussdAfricasTalkingGateway()