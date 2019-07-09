from .base_menu import Menu
from ..models import User


class RegistrationMenu(Menu):
    """Serves registration callbacks"""

    def get_number(self):
        # insert user's phone number
        self.session["level"] = 21
        menu_text = "Please choose a  username"
        return self.ussd_proceed(menu_text)

    def get_username(self):
        username = self.user_response
        if username or not User.by_username(username):  # check if user entered an option or username exists
            self.user = User.create(username=username, phone_number=self.phone_number)
            self.session["level"] = 0
            # go to home
            return self.home()
        else:  # Request again for name - level has not changed...
            menu_text = "Username is already in use. Please enter your username \n"
            return self.ussd_proceed(menu_text)

    def execute(self):
        if self.session["level"] == 0:
            return self.get_number()
        else:
            return self.get_username()
