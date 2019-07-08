import datetime


def kenya_time():
    return datetime.datetime.utcnow() + datetime.timedelta(hours=3)


def iso_format(amount):
    return "KES{}".format(amount)
