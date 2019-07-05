from flask import Blueprint

ussd = Blueprint('ussd', __name__)

from . import views, decorators
