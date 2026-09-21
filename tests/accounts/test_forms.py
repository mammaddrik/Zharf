from django.test import TestCase

from apps.accounts.forms import (
    ProfileForm,
    ProfileSetupForm,
    SignInForm,
    SignUpForm,
    ZharfPasswordResetForm,
    ZharfSetPasswordForm,
)

from apps.accounts.models import Profile, User

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

class ProfileFormTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='ValidPassword123!'
        )

        self.profile = Profile.objects.create(
            user=self.user,
            username='existing_user'
        )

    def test_valid_profile_form(self):
        form = ProfileForm(
            instance=self.profile,
            data={
                'username': 'new_user',
                'display_name': 'Mammad',
                'bio': 'A short bio.',
                'occupation': 'DevOps Engineer',
                'company': 'Zharf',
                'location': 'Istanbul',
                'website': 'https://example.com',
                'github': 'https://github.com/example',
                'linkedin': 'https://linkedin.com/in/example',
                'instagram': 'https://instagram.com/example',
                'x': 'https://x.com/example',
            }
        )

        self.assertTrue(form.is_valid())

    def test_username_is_normalized(self):
        form = ProfileForm(
            instance=self.profile,
            data={
                'username': '  Mammad_D  ',
            }
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['username'], 'mammad_d')

    def test_username_too_short(self):
        form = ProfileForm(
            instance=self.profile,
            data={
                'username': 'ma',
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_username_too_long(self):
        form = ProfileForm(
            instance=self.profile,
            data={
                'username': 'a' * 31,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_username_with_invalid_characters(self):
        invalid_usernames = [
            'mammad-d',
            'mammad d',
            '@mammad',
        ]

        for username in invalid_usernames:
            form = ProfileForm(
                instance=self.profile,
                data={
                    'username': username,
                }
            )

            self.assertFalse(form.is_valid())
            self.assertIn('username', form.errors)

    def test_duplicate_username(self):
        other_user = User.objects.create_user(
            email='other@example.com',
            password='ValidPassword123!'
        )

        Profile.objects.create(
            user=other_user,
            username='other_user'
        )

        form = ProfileForm(
            instance=self.profile,
            data={
                'username': 'other_user',
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_current_username_is_allowed(self):
        form = ProfileForm(
            instance=self.profile,
            data={
                'username': 'existing_user',
            }
        )

        self.assertTrue(form.is_valid())

    def test_valid_urls(self):
        form = ProfileForm(
            instance=self.profile,
            data={
                'username': 'new_user',
                'website': 'https://example.com',
                'github': 'https://github.com/example',
                'linkedin': 'https://linkedin.com/in/example',
                'instagram': 'https://instagram.com/example',
                'x': 'https://x.com/example',
            }
        )

        self.assertTrue(form.is_valid())

    def test_invalid_url(self):
        form = ProfileForm(
            instance=self.profile,
            data={
                'username': 'new_user',
                'website': 'not-a-url',
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('website', form.errors)

    def test_optional_fields_can_be_empty(self):
        form = ProfileForm(
            instance=self.profile,
            data={
                'username': 'new_user',
            }
        )

        self.assertTrue(form.is_valid())

    def test_avatar_is_optional(self):
        form = ProfileForm(
            instance=self.profile,
            data={
                'username': 'new_user',
            }
        )

        self.assertTrue(form.is_valid())
        self.assertFalse(form.cleaned_data['avatar'])

class ProfileSetupFormTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='setup@example.com',
            password='ValidPassword123!'
        )

        self.profile = Profile.objects.create(
            user=self.user,
            username='setup_user'
        )

    def test_valid_profile_setup_form(self):
        form = ProfileSetupForm(
            instance=self.profile,
            data={
                'username': 'new_user',
                'bio': 'A short bio.',
            }
        )

        self.assertTrue(form.is_valid())

    def test_username_is_normalized(self):
        form = ProfileSetupForm(
            instance=self.profile,
            data={
                'username': '  Mammad_D  ',
            }
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data['username'],
            'mammad_d'
        )

    def test_username_too_short(self):
        form = ProfileSetupForm(
            instance=self.profile,
            data={
                'username': 'ma',
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_username_too_long(self):
        form = ProfileSetupForm(
            instance=self.profile,
            data={
                'username': 'a' * 31,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_username_with_invalid_characters(self):
        invalid_usernames = [
            'mammad-d',
            'mammad d',
            '@mammad',
        ]

        for username in invalid_usernames:
            form = ProfileSetupForm(
                instance=self.profile,
                data={
                    'username': username,
                }
            )

            self.assertFalse(form.is_valid())
            self.assertIn('username', form.errors)

    def test_duplicate_username(self):
        other_user = User.objects.create_user(
            email='other@example.com',
            password='ValidPassword123!'
        )

        Profile.objects.create(
            user=other_user,
            username='other_user'
        )

        form = ProfileSetupForm(
            instance=self.profile,
            data={
                'username': 'other_user',
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_current_username_is_allowed(self):
        form = ProfileSetupForm(
            instance=self.profile,
            data={
                'username': 'setup_user',
            }
        )

        self.assertTrue(form.is_valid())

    def test_optional_fields_can_be_empty(self):
        form = ProfileSetupForm(
            instance=self.profile,
            data={
                'username': 'new_user',
            }
        )

        self.assertTrue(form.is_valid())

    def test_only_setup_fields_are_available(self):
        form = ProfileSetupForm(instance=self.profile)

        self.assertEqual(
            list(form.fields.keys()),
            [
                'avatar',
                'username',
                'bio',
            ]
        )