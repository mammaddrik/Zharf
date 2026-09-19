from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class SignUpViewTests(TestCase):
    def test_signup_page_returns_200(self):
        response = self.client.get(reverse('signup'))

        self.assertEqual(response.status_code, 200)

    def test_signup_page_uses_correct_template(self):
        response = self.client.get(reverse('signup'))

        self.assertTemplateUsed(response, 'accounts/signup.html')

    def test_authenticated_user_is_redirected_from_signup(self):
        User.objects.create_user(
            email='user@example.com',
            password='StrongPassword123!'
        )

        self.client.login(
            email='user@example.com',
            password='StrongPassword123!'
        )

        response = self.client.get(reverse('signup'))

        self.assertRedirects(response, reverse('home'))

    def test_valid_signup_creates_user(self):
        response = self.client.post(
            reverse('signup'),
            data={
                'email': 'user@example.com',
                'password': 'StrongPassword123!',
                'confirm_password': 'StrongPassword123!',
            }
        )

        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(
            User.objects.filter(email='user@example.com').exists()
        )

    def test_valid_signup_logs_user_in(self):
        response = self.client.post(
            reverse('signup'),
            data={
                'email': 'user@example.com',
                'password': 'StrongPassword123!',
                'confirm_password': 'StrongPassword123!',
            }
        )

        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_valid_signup_redirects_to_home(self):
        response = self.client.post(
            reverse('signup'),
            data={
                'email': 'user@example.com',
                'password': 'StrongPassword123!',
                'confirm_password': 'StrongPassword123!',
            }
        )

        self.assertRedirects(response, reverse('home'))

    def test_invalid_signup_does_not_create_user(self):
        response = self.client.post(
            reverse('signup'),
            data={
                'email': 'user@example.com',
                'password': 'StrongPassword123!',
                'confirm_password': 'DifferentPassword123!',
            }
        )

        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_duplicate_email_does_not_create_user(self):
        User.objects.create_user(
            email='user@example.com',
            password='StrongPassword123!'
        )

        response = self.client.post(
            reverse('signup'),
            data={
                'email': 'user@example.com',
                'password': 'AnotherStrongPassword123!',
                'confirm_password': 'AnotherStrongPassword123!',
            }
        )

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 200)