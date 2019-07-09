from flask import make_response


def iso_format(amount):
    return "KES{}".format(amount)


def respond(response):
    response = make_response(response, 200)
    response.headers['Content-Type'] = "text/plain"
    return response
