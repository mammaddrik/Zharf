from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()


class SignUpViewTests(TestCase):
    def test_signup_page_loads(self):
        response = self.client.get(reverse('signup'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')

    def test_authenticated_user_is_redirected_from_signup(self):
        user = User.objects.create_user(
            email='user@example.com',
            password='TestPassword123!'
        )

        self.client.force_login(user)

        response = self.client.get(reverse('signup'))

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

        self.assertEqual(response.status_code, 200)
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

        self.assertEqual(response.status_code, 200)

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

        self.assertEqual(response.status_code, 200)

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
        response = self.client.get(reverse('signin'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signin.html')

    def test_authenticated_user_is_redirected_from_signin(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('signin'))

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

        self.assertEqual(response.status_code, 200)
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

        self.assertEqual(response.status_code, 200)
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

        self.assertEqual(response.status_code, 200)
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

        self.assertEqual(response.status_code, 200)
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