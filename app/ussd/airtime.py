from .base_menu import Menu
from .tasks import buyAirtime


class Airtime(Menu):
    def get_phone_number(self):  # 10
        if self.user_response == '1':
            self.session["phone_number"] = self.phone_number
            menu_text = "Buy Airtime\nPlease Enter Amount(Ksh)"
            self.session['level'] = 12
            return self.ussd_proceed(menu_text)
        if self.user_response == '2':
            menu_text = "Buy Airtime\nPlease enter phone number as (+2547XXXXXXXX)"
            self.session['level'] = 11
            return self.ussd_proceed(menu_text)
        return self.home()

    def another_number(self):  # 11
        if not self.user_response.startswith("+"):
            menu_text = "Buy Airtime\nPlease enter a valid phone number as (+2547XXXXXXXX)"
            return self.ussd_proceed(menu_text)
        self.session['phone_number'] = self.phone_number
        menu_text = "Buy Airtime\nPlease Enter Amount(Ksh)"
        self.session['level'] = 12
        return self.ussd_proceed(menu_text)

    def get_amount(self, amount=None):  # level 12
        if int(self.user_response) < 5 and amount is None:
            menu_text = "Buy Airtime\nYou can only buy airtime above Ksh 5.00. Please enter amount"
            return self.ussd_proceed(menu_text)
        if amount is None:
            self.session['amount'] = int(self.user_response)
        self.session['level'] = 13
        menu_text = "Purchase Ksh{:.2f} worth of airtime for {}\n".format(self.session.get('amount'),
                                                                          self.session.get("phone_number"))
        menu_text += "1.Confirm\n2.Cancel"
        return self.ussd_proceed(menu_text)

    def confirm(self):  # 13
        if self.user_response == "1":
            menu_text = "Please wait as we load your account."
            buyAirtime.apply_async(
                kwargs={'phone_number': self.session['phone_number'], 'amount': self.session['amount'],
                        'account_phoneNumber': self.user.phone_number})
            return self.ussd_end(menu_text)
        if self.user_response == "2":
            menu_text = "Thank you for doing business with us"
            return self.ussd_end(menu_text)
        return self.get_amount(amount=True)

    def execute(self):
        level = self.session.get('level')
        menu = {
            10: self.get_phone_number,
            11: self.another_number,
            12: self.get_amount,
            13: self.confirm
        }
        return menu.get(level, self.home)()
