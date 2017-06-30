from flask import Blueprint

api_v11 = Blueprint('api_v11', __name__)

from . import views
