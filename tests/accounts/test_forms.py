from django.core.serializers import python
from django.test import TestCase

from apps.accounts.forms import (
    SignInForm,
    SignUpForm,
    ZharfPasswordResetForm,
    ZharfSetPasswordForm,
)

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

class ZharfPasswordResetFormTests(TestCase):

    def test_email_widget_styling(self):
        form = ZharfPasswordResetForm()

        widget = form.fields['email'].widget

        self.assertEqual(widget.attrs['class'], 'form-input')
        self.assertEqual(widget.attrs['placeholder'], 'you@example.com')
        self.assertEqual(widget.attrs['autocomplete'], 'email')
        self.assertEqual(widget.attrs['inputmode'], 'email')

    def test_valid_email(self):
        form = ZharfPasswordResetForm(
            data={
                'email': 'user@example.com',
            }
        )

        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        form = ZharfPasswordResetForm(
            data={
                'email': 'invalid-email',
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

class ZharfSetPasswordFormTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='OldPassword123!'
        )

    def test_password_widget_styling(self):
        form = ZharfSetPasswordForm(user=self.user)

        password_widget = form.fields['new_password1'].widget
        confirmation_widget = form.fields['new_password2'].widget

        self.assertEqual(
            password_widget.attrs['class'],
            'form-input'
        )
        self.assertEqual(
            password_widget.attrs['placeholder'],
            'Create a new password'
        )
        self.assertEqual(
            password_widget.attrs['autocomplete'],
            'new-password'
        )

        self.assertEqual(
            confirmation_widget.attrs['class'],
            'form-input'
        )
        self.assertEqual(
            confirmation_widget.attrs['placeholder'],
            'Repeat your new password'
        )
        self.assertEqual(
            confirmation_widget.attrs['autocomplete'],
            'new-password'
        )

    def test_valid_password(self):
        form = ZharfSetPasswordForm(
            user=self.user,
            data={
                'new_password1': 'NewStrongPassword123!',
                'new_password2': 'NewStrongPassword123!',
            }
        )

        self.assertTrue(form.is_valid())

    def test_password_mismatch(self):
        form = ZharfSetPasswordForm(
            user=self.user,
            data={
                'new_password1': 'NewStrongPassword123!',
                'new_password2': 'DifferentPassword123!',
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('new_password2', form.errors)

    def test_weak_password(self):
        form = ZharfSetPasswordForm(
            user=self.user,
            data={
                'new_password1': '123',
                'new_password2': '123',
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('new_password2', form.errors)