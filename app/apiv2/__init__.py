from flask import Blueprint

api_v2 = Blueprint('api_v2', __name__)

from . import views, decorators
