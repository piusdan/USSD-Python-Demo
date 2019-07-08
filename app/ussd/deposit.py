from .base_menu import Menu
from .tasks import makeC2Brequest


class Deposit(Menu):
    def get_amount(self):  # 50
        try:
            amount = int(self.user_response)
        except ValueError as exc:
            return self.home()
        self.session['amount'] = int(self.user_response)
        self.session['level'] = 51
        menu_text = "Deposit Ksh{:.2f} to your Wallet\n".format(self.session.get('amount'))
        menu_text += "1.Confirm\n2.Cancel"
        return self.ussd_proceed(menu_text)

    def confirm(self):  # 51
        amount = self.session.get('amount')
        if self.user_response == "1":
            menu_text = "We are sending you an Mpesa Checkout for deposit of KES{} shortly".format(amount)
            makeC2Brequest.apply_async(
                kwargs={'phone_number': self.user.phone_number, 'amount': amount})
            return self.ussd_end(menu_text)

        if self.user_response == "2":
            menu_text = "Thank you for doing business with us"
            return self.ussd_end(menu_text)

        return self.home()

    def execute(self):
        menu = {
            50: self.get_amount,
            51: self.confirm
        }
        return menu.get(self.level)()
