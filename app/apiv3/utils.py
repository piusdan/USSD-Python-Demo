from .AfricasTalkingGateway import AfricasTalkingGateway
from flask import current_app, make_response
from .. import db
from ..models import SessionLevel


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