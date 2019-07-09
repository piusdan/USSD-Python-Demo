from .base_menu import Menu
from .tasks import make_B2Crequest


class WithDrawal(Menu):
    def get_amount(self):  # 40
        try:
            amount = int(self.user_response)
        except ValueError as exc:
            return self.home()
        self.session['amount'] = int(self.user_response)
        self.session['level'] = 51
        menu_text = "Withdraw Ksh{:.2f} from your Wallet\n".format(self.session.get('amount'))
        menu_text += "1.Confirm\n2.Cancel"
        return self.ussd_proceed(menu_text)

    def confirm(self):  # 41
        amount = self.session.get('amount')
        if self.user_response == "1":
            menu_text = "We are sending your withrawal deposit of KES{} shortly".format(amount)
            make_B2Crequest.apply_async(
                kwargs={'phone_number': self.user.phone_number, 'amount': amount, 'reason': 'Withdraw'})
            return self.ussd_end(menu_text)

        if self.user_response == "2":
            menu_text = "Thank you for doing business with us"
            return self.ussd_end(menu_text)
        return self.home()

    def execute(self):
        menu = {
            40: self.get_amount,
            41: self.confirm
        }
        return menu.get(self.level, self.home)()