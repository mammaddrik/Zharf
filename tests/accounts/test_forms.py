from django.test import TestCase

from apps.accounts.forms import SignUpForm, SignInForm
from apps.accounts.models import User

from django.test import TestCase

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

class SignInFormTests(TestCase):
    def setUp(self):
        self.password = 'ValidPassword123!'

        self.user = User.objects.create_user(
            email='user@example.com',
            password=self.password
        )

    def test_valid_credentials(self):
        form = SignInForm(
            data={
                'email': 'user@example.com',
                'password': self.password,
            }
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.user, self.user)

    def test_invalid_password(self):
        form = SignInForm(
            data={
                'email': 'user@example.com',
                'password': 'WrongPassword123!',
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            'Invalid email or password.',
            form.non_field_errors()
        )

    def test_unknown_email(self):
        form = SignInForm(
            data={
                'email': 'unknown@example.com',
                'password': self.password,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            'Invalid email or password.',
            form.non_field_errors()
        )

    def test_inactive_user(self):
        self.user.is_active = False
        self.user.save(update_fields=['is_active'])

        form = SignInForm(
            data={
                'email': 'user@example.com',
                'password': self.password,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            'Invalid email or password.',
            form.non_field_errors()
        )