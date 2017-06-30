from flask import Blueprint, current_app

api_v1 = Blueprint('api_v1', __name__)

from africastalking.AfricasTalkingGateway import AfricasTalkingGateway

from . import views, errors

# with current_app.app_context():
# if current_app.debug or current_app.testing or current_app.development:
#     gateway = AfricasTalkingGateway(current_app.config["AT_USERNAME"], current_app.config["AT_APIKEY"], "sandbox")
# else:
#     gateway = AfricasTalkingGateway(current_app.config["AT_USERNAME"], current_app.config["AT_APIKEY"])

