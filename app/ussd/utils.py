import datetime
from flask import make_response

def kenya_time():
    return datetime.datetime.utcnow() + datetime.timedelta(hours=3)


def iso_format(amount):
    return "KES{}".format(amount)

def respond(response):
    response = make_response(response, 200)
    response.headers['Content-Type'] = "text/plain"
    return response
