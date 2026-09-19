from django.test import TestCase

from apps.accounts.forms import SignUpForm
from apps.accounts.models import User


class SignUpFormTests(TestCase):
    def test_valid_signup_form(self):
        form = SignUpForm(
            data={
                'email': 'user@example.com',
                'password': 'StrongPassword123!',
                'confirm_password': 'StrongPassword123!',
            }
        )

        self.assertTrue(form.is_valid())

    def test_duplicate_email(self):
        User.objects.create_user(
            email='user@example.com',
            password='StrongPassword123!'
        )

        form = SignUpForm(
            data={
                'email': 'user@example.com',
                'password': 'StrongPassword123!',
                'confirm_password': 'StrongPassword123!',
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_password_mismatch(self):
        form = SignUpForm(
            data={
                'email': 'user@example.com',
                'password': 'StrongPassword123!',
                'confirm_password': 'DifferentPassword123!',
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('confirm_password', form.errors)

    def test_weak_password(self):
        form = SignUpForm(
            data={
                'email': 'user@example.com',
                'password': '123',
                'confirm_password': '123',
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)