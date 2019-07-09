import os

from africastalking.AfricasTalkingGateway import AfricasTalkingGateway, AfricasTalkingGatewayException


class NerdsMicrofinanceGatewayGatewayException(AfricasTalkingGatewayException):
    pass


class NerdsMicrofinanceGateway(AfricasTalkingGateway):
    def __init__(self):
        pass  # override default constructor

    @classmethod
    def init_app(cls, app):
        # this initialises an AfricasTalking Gateway instanse similar to calling
        # africastalking.gateway(username, apikey, environment)
        # this enables us to initialise one gateway to use throughout the app

        cls.username = app.config['AT_USERNAME']
        cls.apiKey = app.config['AT_APIKEY']
        cls.environment = app.config['AT_ENVIRONMENT']
        cls.HTTP_RESPONSE_OK = 200
        cls.HTTP_RESPONSE_CREATED = 201

        # Turn this on if you run into problems. It will print the raw HTTP response from our server
        if os.environ.get('APP_CONFIG') == 'development':
            cls.Debug = True
        else:
            cls.Debug = False


gateway = NerdsMicrofinanceGateway()
