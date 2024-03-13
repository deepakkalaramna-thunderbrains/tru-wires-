from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        if user.is_staff and hasattr(user, 'staff'):
            return (
                six.text_type(user.pk) + six.text_type(timestamp) +
                six.text_type(user.staff.signup_confirmation)
            )
        elif hasattr(user, 'client'):
            return (
                six.text_type(user.pk) + six.text_type(timestamp) +
                six.text_type(user.client.signup_confirmation)
            )
        else:
            raise ValueError("User is not a staff or client")
account_activation_token = AccountActivationTokenGenerator()
