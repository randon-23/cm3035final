from django.core.exceptions import ValidationError
import re

# Custom validator to ensure that the user's password meets the minimum requirements
# This is used in the User model to ensure that the password meets the minimum requirements
#and is enforced through the AUTH_PASSWORD_VALIDATORS setting in the settings.py file

class UserPasswordValidator:
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(self.get_help_text())
        if not re.search(r'[a-z]', password):
            raise ValidationError(self.get_help_text())
        if not re.search(r'[0-9]', password):
            raise ValidationError(self.get_help_text())
        if not re.search(r'[@#$%^&+=!*]', password):
            raise ValidationError(self.get_help_text())
        
    def get_help_text(self):
        return "Your password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character"