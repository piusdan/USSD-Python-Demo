# from utils import respond, update_session, make_gateway
# from .AfricasTalkingGateway import AfricasTalkingGateway, AfricasTalkingGatewayException
# from flask import current_app, g, copy_current_request_context
# from ..models import SessionLevel, User
# from .. import db
# import gevent
# from .. import celery
#
#
# class HighLevelMenu:
#     """
#     Serves high level callbacks
#     """
#     def __init__(self, user_response, phone_number, session_id):
#         """
#
#         """
#         self.phone_number = phone_number
#         self.session_id = session_id
#         self.user = User.query.filter_by(phone_number=phone_number).first()
#         self.session = SessionLevel.query.filter_by(session_id=self.session_id).first()
#         self.user_response = user_response
#
#
#     def c2b_checkout(self):
#         # Alert user of incoming Mpesa checkout
#         menu_text = "END We are sending you the MPESA checkout in a moment...\n"
#         menu_text += "If you dont have a bonga pin, dial \n"
#         menu_text += "Dial dial *126*5*1# to create.\n"
#         gateway = make_gateway()
#         product_name = current_app.config["PRODUCT_NAME"]
#         currency_code = "KES"
#         amount = int(self.user_response)
#         metadata = {"sacco": "Nerds", "productId": "321"}
#         api_key = current_app.config["AT_APIKEY"]
#         user_name = current_app.config["AT_USERNAME"]
#         payload = {"phone_number": self.phone_number, "product_name":product_name, "metadat":metadata, "amount":amount,"currency_code": currency_code, "metadata":metadata, "api_key":api_key, "user_name":user_name}
#         async_checkoutc2b.apply_async(args=[payload], countdown=10)
#
#         return respond(menu_text)
#
#
#     def default_mpesa_checkout(self):
#         menu_text = "END Apologies, something went wrong... \n"
#         # Print the response onto the page so that our gateway can read it
#         return respond(menu_text)
#
#     # end level 9
#
#
#     # level 10
#     def b2c_checkout(self):
#         if self.user.account > 1:
#             # Reduce the balance
#             self.user.withdraw(1)
#             db.session.add(self.user)
#             db.session.commit()
#
#             menu_text = "END We are sending your withdrawal of\n"
#             menu_text += " KES {}/- shortly... \n".format(self.user_response)
#
#             # Declare Params
#             gateway = make_gateway()
#
#             product_name = current_app.config["PRODUCT_NAME"]
#
#             recipients = [
#                 {"phoneNumber": self.phone_number,
#                  "currencyCode": "KES",
#                  "amount": int(self.user_response), "metadata":
#                      {
#                          "name": "Client",
#                          "reason": "Withdrawal"
#                      }
#                  }
#             ]
#             # Send B2c
#             try:
#                 gateway.mobilePaymentB2CRequest(product_name, recipients)
#             except AfricasTalkingGatewayException as e:
#                 print "Received error response {}".format(str(e))
#         else:
#             # Alert user of insufficient funds
#             menu_text = "END Sorry, you don't have sufficient\n"
#             menu_text += " funds in your account \n"
#
#         return respond(menu_text)
#
#     def b2c_default(self):
#         menu_text = "END Apologies, something went wrong... \n"
#         # Print the response onto the page so that our gateway can read it
#         return respond(menu_text)
#
#     # end level 10
#
#
#     # level 11
#     def send_loan(self, ):
#         debptor_phone_number = self.user_response
#         amount = 1
#         # Find and update creditor
#         creditorAccount = self.user
#         creditorAccount.withdraw(amount)
#         # Send the loan if new account balance is above 0
#         if creditorAccount.account > 0:
#             menu_text = "END We are sending KES {}/- \n".format(amount)
#             menu_text += "to the loanee shortly. \n"
#             # get and update Debtor
#             debptorAccount = User.query.filter_by(
#                 phone_number=debptor_phone_number).first()
#
#             if debptorAccount:
#                 debptorAccount.deposit(amount)
#                 db.session.add(debptorAccount)
#                 db.session.add(creditorAccount)
#
#             # SMS New Balance
#
#             code = current_app.config["SMS_CODE"]
#             recepients = self.phone_number
#             message = "We have sent {}/- to {} \nIf \
#             this is a wrong number the transaction will fail\n" \
#                       "Your new balance is {} \n\
#                       Thank you.\n".format(amount, debptor_phone_number, creditorAccount.account)
#             gateway = make_gateway()
#             try:
#                 gateway.sendMessage(recepients, message, code)
#             except AfricasTalkingGatewayException as e:
#                 print "Encountered an error while sending: {}\n".format(str(e))
#
#             # TODO figure out
#             # change user level to 0
#             # session_level = SessionLevel.query.filter_by(session_id=session_id).first()
#             # session_level.demote_level()
#             # db.session.add(session_level)
#
#             # Update DB
#             db.session.commit()
#
#             # respond
#             menu_text += "CONFIRMED we have sent money to {} \n".format(
#                 creditorAccount.phone_number)
#         else:
#             # respond
#             menu_text = "END Sorry we could not send the money. \n"
#             menu_text += "You dont have enough money. {}\n".format(
#                 creditorAccount.account)
#
#         # Print the response onto the page so that our gateway can read it
#         return respond(menu_text)
#
#     def repay_loan(self):
#         """
#         Pay Loan
#         :param session_id, amount:
#         :return response object:
#         """
#         # Alert user of incoming Mpesa checkout
#         amount = int(self.user_response)
#         menu_text = "END You are repaying {}/-. \
#         We have sent the MPESA \
#         checkout...\n".format(
#             amount)
#         menu_text += "If you dont have a bonga pin, dial \n"
#         menu_text += "Dial dial *126*5*1# to create.\n"
#
#         # Declare Params
#         gateway = make_gateway()
#
#         productName = current_app.config["PRODUCT_NAME"]
#
#         currencyCode = "KES"
#         metadata = {"Sacco Repayment": "Nerds", "productId": "321"}
#
#         # pass to gateway
#         try:
#             transactionId = gateway.initiateMobilePaymentCheckout(
#                 productName, self.phone_number, currencyCode, amount,
#                 metadata)
#         except AfricasTalkingGatewayException as e:
#             print "Received error response: {}".format(str(e))
#
#         # Print the response onto the page so that our gateway can read it
#         return respond(menu_text)
#
#     @staticmethod
#     def default_loan_checkout():
#         menu_text = "END Apologies, something went wrong... \n"
#         # Print the response onto the page so that our gateway can read it
#         return respond(menu_text)
#
#     @staticmethod
#     def default_higher_level_response():
#         # Request for city again
#         menu_text = "END Apologies, something went wrong... \n"
#
#         # Print the response onto the page so that our gateway can read it
#         return respond(menu_text)
#
#         # end higher level responses
#
#
#
#
# @celery.task(bind=True, default_retry_delay=30 * 60)
# def async_checkoutc2b(self, payload):
#     gateway = make_gateway(api_key=payload.get("api_key"), user_name=payload.get("user_name"))
#     # pass to gateway
#     try:
#         transaction_id = gateway.initiateMobilePaymentCheckout(productName_=payload["product_name"], amount_=payload["amount"], metadata_=payload["metadata"],
#                                           phoneNumber_=payload['phone_number'], currencyCode_=payload["currency_code"])
#         print "Transaction id is: " + transaction_id
#     except Exception as exc:
#         raise self.retry(exc=exc, countdown=5)
