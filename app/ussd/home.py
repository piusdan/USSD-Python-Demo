from .base_menu import Menu
from .tasks import check_balance


class LowerLevelMenu(Menu):
    """serves the home menu"""
    def deposit(self):  # 1
        menu_text = "Enter amount you wish to deposit?\n"
        self.session['level'] = 50
        return self.ussd_proceed(menu_text)

    def withdraw(self):  # 2
        menu_text = "Enter amount you wish to withdraw?\n"
        self.session['level'] = 40
        return self.ussd_proceed(menu_text)

    def buy_airtime(self):  # level 10
        menu_text = "Buy Airtime\n" \
                    "1. My Number\n" \
                    "2. Another Number\n" \
                    "0. Back"
        self.session['level'] = 10
        return self.ussd_proceed(menu_text)

    def check_balance(self):  # 4
        menu_text = "Please wait as we load your account\nYou will receive an SMS notification shortly"
        # send balance async
        check_balance.apply_async(kwargs={'user_id': self.user.id})
        return self.ussd_end(menu_text)

    def execute(self):
        menus = {
            '1': self.deposit,
            '2': self.withdraw,
            '3': self.buy_airtime,
            '4': self.check_balance
        }
        return menus.get(self.user_response, self.home)()
