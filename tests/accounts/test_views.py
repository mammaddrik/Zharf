from io import BytesIO

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from PIL import Image

from apps.accounts.models import Profile


User = get_user_model()


class SignUpViewTests(TestCase):

    def test_signup_page_loads(self):
        response = self.client.get(
            reverse('signup')
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            'accounts/signup.html'
        )

    def test_authenticated_user_is_redirected_from_signup(self):
        user = User.objects.create_user(
            email='user@example.com',
            password='TestPassword123!'
        )

        self.client.force_login(user)

        response = self.client.get(
            reverse('signup')
        )

        self.assertRedirects(
            response,
            reverse('home')
        )

    def test_valid_signup_creates_user(self):
        response = self.client.post(
            reverse('signup'),
            {
                'email': 'new@example.com',
                'password': 'StrongPassword123!',
                'confirm_password': 'StrongPassword123!',
            }
        )

        self.assertRedirects(
            response,
            reverse('home')
        )

        self.assertTrue(
            User.objects.filter(
                email='new@example.com'
            ).exists()
        )

    def test_valid_signup_logs_user_in(self):
        response = self.client.post(
            reverse('signup'),
            {
                'email': 'new@example.com',
                'password': 'StrongPassword123!',
                'confirm_password': 'StrongPassword123!',
            }
        )

        self.assertRedirects(
            response,
            reverse('home')
        )

        self.assertTrue(
            response.wsgi_request.user.is_authenticated
        )

    def test_duplicate_email_does_not_create_user(self):
        User.objects.create_user(
            email='user@example.com',
            password='TestPassword123!'
        )

        response = self.client.post(
            reverse('signup'),
            {
                'email': 'user@example.com',
                'password': 'StrongPassword123!',
                'confirm_password': 'StrongPassword123!',
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            User.objects.filter(
                email='user@example.com'
            ).count(),
            1
        )

    def test_password_mismatch_does_not_create_user(self):
        response = self.client.post(
            reverse('signup'),
            {
                'email': 'new@example.com',
                'password': 'StrongPassword123!',
                'confirm_password': 'DifferentPassword123!',
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertFalse(
            User.objects.filter(
                email='new@example.com'
            ).exists()
        )

    def test_weak_password_does_not_create_user(self):
        response = self.client.post(
            reverse('signup'),
            {
                'email': 'new@example.com',
                'password': '123',
                'confirm_password': '123',
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertFalse(
            User.objects.filter(
                email='new@example.com'
            ).exists()
        )

    def test_signup_normalizes_email(self):
        response = self.client.post(
            reverse('signup'),
            {
                'email': ' USER@EXAMPLE.COM ',
                'password': 'StrongPassword123!',
                'confirm_password': 'StrongPassword123!',
            }
        )

        self.assertRedirects(
            response,
            reverse('home')
        )

        self.assertTrue(
            User.objects.filter(
                email='user@example.com'
            ).exists()
        )


class SignInViewTests(TestCase):

    def setUp(self):
        self.email = 'user@example.com'
        self.password = 'TestPassword123!'

        self.user = User.objects.create_user(
            email=self.email,
            password=self.password
        )

    def test_signin_page_loads(self):
        response = self.client.get(
            reverse('signin')
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            'accounts/signin.html'
        )

    def test_authenticated_user_is_redirected_from_signin(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('signin')
        )

        self.assertRedirects(
            response,
            reverse('home')
        )

    def test_valid_signin_logs_user_in(self):
        response = self.client.post(
            reverse('signin'),
            {
                'email': self.email,
                'password': self.password,
            }
        )

        self.assertRedirects(
            response,
            reverse('home')
        )

        self.assertTrue(
            response.wsgi_request.user.is_authenticated
        )

    def test_invalid_password_does_not_sign_in(self):
        response = self.client.post(
            reverse('signin'),
            {
                'email': self.email,
                'password': 'WrongPassword123!',
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertContains(
            response,
            'Invalid email or password.'
        )

        self.assertFalse(
            response.wsgi_request.user.is_authenticated
        )

    def test_unknown_email_does_not_sign_in(self):
        response = self.client.post(
            reverse('signin'),
            {
                'email': 'unknown@example.com',
                'password': self.password,
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertContains(
            response,
            'Invalid email or password.'
        )

        self.assertFalse(
            response.wsgi_request.user.is_authenticated
        )

    def test_inactive_user_does_not_sign_in(self):
        self.user.is_active = False
        self.user.save()

        response = self.client.post(
            reverse('signin'),
            {
                'email': self.email,
                'password': self.password,
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertContains(
            response,
            'Invalid email or password.'
        )

        self.assertFalse(
            response.wsgi_request.user.is_authenticated
        )


class PasswordResetViewTests(TestCase):

    def setUp(self):
        self.email = 'user@example.com'
        self.password = 'TestPassword123!'

        self.user = User.objects.create_user(
            email=self.email,
            password=self.password
        )

    def get_reset_uid(self):
        return urlsafe_base64_encode(
            force_bytes(self.user.pk)
        )

    def test_password_reset_page_loads(self):
        response = self.client.get(
            reverse('password_reset')
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            'accounts/password_reset.html'
        )

    def test_valid_password_reset_submission_redirects_to_done(self):
        response = self.client.post(
            reverse('password_reset'),
            {
                'email': self.email,
            }
        )

        self.assertRedirects(
            response,
            reverse('password_reset_done')
        )

    def test_valid_password_reset_sends_email(self):
        self.client.post(
            reverse('password_reset'),
            {
                'email': self.email,
            }
        )

        self.assertEqual(
            len(mail.outbox),
            1
        )

        self.assertEqual(
            mail.outbox[0].to,
            [self.email]
        )

    def test_unknown_email_does_not_reveal_account(self):
        response = self.client.post(
            reverse('password_reset'),
            {
                'email': 'unknown@example.com',
            }
        )

        self.assertRedirects(
            response,
            reverse('password_reset_done')
        )

        self.assertEqual(
            len(mail.outbox),
            0
        )

    def test_valid_reset_link_redirects_to_set_password(self):
        token = default_token_generator.make_token(
            self.user
        )

        uid = self.get_reset_uid()

        response = self.client.get(
            reverse(
                'password_reset_confirm',
                kwargs={
                    'uidb64': uid,
                    'token': token,
                }
            )
        )

        self.assertRedirects(
            response,
            f'/accounts/reset/{uid}/set-password/'
        )

    def test_invalid_reset_token_is_rejected(self):
        uid = self.get_reset_uid()

        response = self.client.get(
            reverse(
                'password_reset_confirm',
                kwargs={
                    'uidb64': uid,
                    'token': 'invalid-token',
                }
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertContains(
            response,
            'This password reset link is invalid or has expired.'
        )

    def test_valid_reset_changes_password(self):
        token = default_token_generator.make_token(
            self.user
        )

        uid = self.get_reset_uid()

        self.client.get(
            reverse(
                'password_reset_confirm',
                kwargs={
                    'uidb64': uid,
                    'token': token,
                }
            )
        )

        response = self.client.post(
            f'/accounts/reset/{uid}/set-password/',
            {
                'new_password1': 'NewStrongPassword123!',
                'new_password2': 'NewStrongPassword123!',
            }
        )

        self.assertRedirects(
            response,
            reverse('password_reset_complete')
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                'NewStrongPassword123!'
            )
        )

    def test_password_mismatch_does_not_change_password(self):
        token = default_token_generator.make_token(
            self.user
        )

        uid = self.get_reset_uid()

        self.client.get(
            reverse(
                'password_reset_confirm',
                kwargs={
                    'uidb64': uid,
                    'token': token,
                }
            )
        )

        response = self.client.post(
            f'/accounts/reset/{uid}/set-password/',
            {
                'new_password1': 'NewStrongPassword123!',
                'new_password2': 'DifferentPassword123!',
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                self.password
            )
        )

    def test_new_password_can_sign_in(self):
        token = default_token_generator.make_token(
            self.user
        )

        uid = self.get_reset_uid()

        self.client.get(
            reverse(
                'password_reset_confirm',
                kwargs={
                    'uidb64': uid,
                    'token': token,
                }
            )
        )

        self.client.post(
            f'/accounts/reset/{uid}/set-password/',
            {
                'new_password1': 'NewStrongPassword123!',
                'new_password2': 'NewStrongPassword123!',
            }
        )

        response = self.client.post(
            reverse('signin'),
            {
                'email': self.email,
                'password': 'NewStrongPassword123!',
            }
        )

        self.assertRedirects(
            response,
            reverse('home')
        )

    def test_old_password_can_no_longer_sign_in(self):
        token = default_token_generator.make_token(
            self.user
        )

        uid = self.get_reset_uid()

        self.client.get(
            reverse(
                'password_reset_confirm',
                kwargs={
                    'uidb64': uid,
                    'token': token,
                }
            )
        )

        self.client.post(
            f'/accounts/reset/{uid}/set-password/',
            {
                'new_password1': 'NewStrongPassword123!',
                'new_password2': 'NewStrongPassword123!',
            }
        )

        response = self.client.post(
            reverse('signin'),
            {
                'email': self.email,
                'password': self.password,
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertContains(
            response,
            'Invalid email or password.'
        )


class ProfileSetupViewTests(TestCase):

    def setUp(self):
        self.email = 'user@example.com'
        self.password = 'TestPassword123!'

        self.user = User.objects.create_user(
            email=self.email,
            password=self.password
        )

        self.profile = Profile.objects.create(
            user=self.user,
            username='old_username',
            bio='Old bio',
            display_name='Old Name',
            company='Old Company',
            github='https://github.com/old_username'
        )

    def test_anonymous_user_is_redirected_to_signin(self):
        response = self.client.get(
            reverse('profile_setup')
        )

        self.assertRedirects(
            response,
            f"{reverse('signin')}?next={reverse('profile_setup')}"
        )

    def test_authenticated_user_can_access_profile_setup(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('profile_setup')
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertTemplateUsed(
            response,
            'accounts/profile/setup.html'
        )

    def test_profile_setup_loads_existing_profile_data(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('profile_setup')
        )

        form = response.context['form']

        self.assertEqual(
            form.initial['username'],
            'old_username'
        )

        self.assertEqual(
            form.initial['bio'],
            'Old bio'
        )

    def test_valid_profile_setup_updates_profile(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('profile_setup'),
            {
                'username': 'new_username',
                'bio': 'New bio',
            }
        )

        self.assertRedirects(
            response,
            reverse('workspace')
        )

        self.profile.refresh_from_db()

        self.assertEqual(
            self.profile.username,
            'new_username'
        )

        self.assertEqual(
            self.profile.bio,
            'New bio'
        )

    def test_invalid_profile_setup_does_not_update_profile(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('profile_setup'),
            {
                'username': 'ab',
                'bio': 'New bio',
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.profile.refresh_from_db()

        self.assertEqual(
            self.profile.username,
            'old_username'
        )

        self.assertEqual(
            self.profile.bio,
            'Old bio'
        )

    def test_profile_setup_normalizes_username(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('profile_setup'),
            {
                'username': 'New_Username',
                'bio': 'New bio',
            }
        )

        self.assertRedirects(
            response,
            reverse('workspace')
        )

        self.profile.refresh_from_db()

        self.assertEqual(
            self.profile.username,
            'new_username'
        )

    def test_profile_setup_does_not_modify_other_profile_fields(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('profile_setup'),
            {
                'username': 'new_username',
                'bio': 'New bio',
                'display_name': 'New Name',
                'company': 'New Company',
                'github': 'https://github.com/new_username',
            }
        )

        self.assertRedirects(
            response,
            reverse('workspace')
        )

        self.profile.refresh_from_db()

        self.assertEqual(
            self.profile.display_name,
            'Old Name'
        )

        self.assertEqual(
            self.profile.company,
            'Old Company'
        )

        self.assertEqual(
            self.profile.github,
            'https://github.com/old_username'
        )

    def test_profile_setup_uploads_avatar(self):
        self.client.force_login(self.user)

        image = Image.new(
            'RGB',
            (100, 100),
            'white'
        )

        image_file = BytesIO()

        image.save(
            image_file,
            format='JPEG'
        )

        image_file.seek(0)

        avatar = SimpleUploadedFile(
            'avatar.jpg',
            image_file.read(),
            content_type='image/jpeg'
        )

        response = self.client.post(
            reverse('profile_setup'),
            {
                'username': 'new_username',
                'bio': 'New bio',
                'avatar': avatar,
            }
        )

        self.assertRedirects(
            response,
            reverse('workspace')
        )

        self.profile.refresh_from_db()

        self.assertTrue(
            self.profile.avatar
        )

        self.assertTrue(
            self.profile.avatar.name.startswith(
                'profiles/avatars/'
            )
        )