from africastalking.AfricasTalkingGateway import AfricasTalkingGatewayException
from flask import current_app
from app.AfricasTalkingGateway import gateway as africastalkinggateway
from utils import kenya_time, iso_format
from app import celery
from app import celery_logger
from app.models import User
import uuid

@celery.task(ignore_result=True)
def check_balance(user_id):
    user = User.query.get(user_id)
    balance = iso_format(user.account)
    timestamp = kenya_time()
    transaction_cost = 0.00

    message = "{status}. Your Wallet balance was {balance} on {date} at {time} " \
              "Transaction cost {transaction_cost:0.2f}\n".format(balance=balance,
                                                                  status='Confirmed',
                                                                  transaction_cost=transaction_cost,
                                                                  date=timestamp.date().strftime('%d/%m/%y'),
                                                                  time=timestamp.time().strftime('%H:%M %p'))
    try:
        resp = africastalkinggateway.sendMessage(to_=user.phone_number, message_=message)
        celery_logger.warn("Balance message sent to {}".format(user.phone_number))
    except AfricasTalkingGatewayException as exc:
        celery_logger.error("Could not send account balance message to {} "
                            "error {}".format(user.phone_number, exc))


@celery.task(bind=True, ignore_result=True)
def buyAirtime(self, phone_number, amount, account_phoneNumber):
    """
    :param self:
    :param phone_number: phone number to purchase airtime for
    :param amount: airtime worth
    :param account_phoneNumber: phone number linked to account making transaction
    :return:
    """

    user = User.by_phoneNumber(account_phoneNumber)
    celery_logger.warn("{}".format(amount))
    if not isinstance(amount, int):
        celery_logger.error("Invalid format for amount")
    value = iso_format(amount)
    timestamp = kenya_time()  # generate timestamp
    if phone_number.startswith('0'):  # transform phone number to ISO format
        phone_number = "+254" + phone_number[1:]

    if user.account < amount:  # check if user has enough cash
        message = "Failed. There is not enough money in your account to buy airtime worth {amount}. " \
                  "Your Cash Value Wallet balance is {balance}\n".format(amount=value,
                                                                         balance=iso_format(user.account)
                                                                         )
        africastalkinggateway.sendMessage(to_=user.phone_number, message_=message)
        celery_logger.error(message)
        return False
    recepients = [{"phoneNumber": phone_number, "amount": value}]
    try:
        response = africastalkinggateway.sendAirtime(recipients_=recepients)[0]  # get response from AT
        if response['status'] == 'Success':
            user.account -= amount
        else:
            celery_logger.error("Airtime wasn't sent to {}".format(phone_number))
    except AfricasTalkingGatewayException as exc:
        celery_logger.error("Encountered an error while sending airtime: {}".format(exc))
    return True


@celery.task(bind=True, ignore_result=True)
def make_B2Crequest(self, phone_number, amount, reason):
    user = User.by_phoneNumber(phone_number)
    value = iso_format(amount)
    recipients = [
        {"phoneNumber": phone_number,
         "currencyCode": user.address.code.currency_code,
         "amount": amount,
         "reason": reason,
         "metadata": {
             "phone_number": user.phone_number,
             "reason": reason
         }
         }
    ]
    if user.account < amount:
        message = "Failed. There is not enough money in your account to buy withdraw {amount}. " \
                  "Your Cash Value Wallet balance is {balance}\n".format(amount=value,
                                                                         balance=iso_format(user.account)
                                                                         )
        africastalkinggateway.sendMessage(to_=user.phone_number, message_=message)
        celery_logger.error(message)
        return False
    try:
        response = africastalkinggateway.mobilePaymentB2CRequest(productName_=current_app.config["PRODUCT_NAME"],
                                                                 recipients_=recipients)[0]
        # withdrawal request
        transaction_fees = 0.00
        africastalkinggateway.sendMessage(to_=user.phone_number,
                                          message_="Confirmed. "
                                                   "You have withdrwan {amount} from your Wallet to your"
                                                   "Mpesa account."
                                                   "Your new wallet balance is {balance}."
                                                   "Transaction fee is {fees}"
                                                   "".format(amount=value,
                                                             fees=iso_format(transaction_fees),
                                                             balance=iso_format(user.balance)
                                                             )
                                          )


    except AfricasTalkingGatewayException as exc:
        celery_logger.error("B2C request experienced an errorr {}".format(exc))
        raise self.retry(exc=exc, countdown=5)


@celery.task(bind=True, ignore_result=True)
def makeC2Brequest(self, phone_number, amount):
    metadata = {
        "transaction_id": str(uuid.uuid1()),
        "reason": 'Deposit'
    }
    # get user
    user = User.by_phoneNumber(phone_number)
    # get currency code
    currency_code = 'KES'
    timestamp = kenya_time()
    transaction_id = metadata.get('transaction_id')

    try:
        payments = africastalkinggateway.initiateMobilePaymentCheckout(
            productName_=current_app.config['PRODUCT_NAME'],
            currencyCode_=currency_code,
            amount_=amount,
            metadata_=metadata,
            providerChannel_="9142",
            phoneNumber_=phone_number
        )
        user.account += amount
        user.save()
        celery_logger.warn("New transaction id: {} logged".format(transaction_id))
    except AfricasTalkingGatewayException as exc:
        celery_logger.error("Could not complete transaction {exc}".format(exc=exc))