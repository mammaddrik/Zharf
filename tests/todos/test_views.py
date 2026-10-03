from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.todos.models import Todo


User = get_user_model()


class TodoViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='todo@example.com',
            password='TestPassword123!',
        )

        self.other_user = User.objects.create_user(
            email='other@example.com',
            password='TestPassword123!',
        )

        self.todo = Todo.objects.create(
            owner=self.user,
            title='Test todo',
            label='Work',
        )

    def test_todo_list_requires_login(self):
        response = self.client.get(
            reverse('todo_list')
        )

        self.assertEqual(response.status_code, 302)

    def test_todo_list_shows_user_todos(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('todo_list')
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test todo')
        self.assertContains(response, 'Work')

    def test_todo_create(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('todo_create'),
            {
                'title': 'New todo',
                'label': 'Personal',
            }
        )

        self.assertRedirects(
            response,
            reverse('todo_list')
        )

        self.assertTrue(
            Todo.objects.filter(
                owner=self.user,
                title='New todo',
                label='Personal',
            ).exists()
        )

    def test_todo_create_requires_title(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('todo_create'),
            {
                'title': '',
                'label': 'Personal',
            }
        )

        self.assertRedirects(
            response,
            reverse('todo_list')
        )

        self.assertFalse(
            Todo.objects.filter(
                owner=self.user,
                label='Personal',
            ).exists()
        )

    def test_todo_toggle_completes_todo(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                'todo_toggle',
                kwargs={'todo_id': self.todo.id},
            )
        )

        self.assertRedirects(
            response,
            reverse('todo_list')
        )

        self.todo.refresh_from_db()

        self.assertTrue(self.todo.completed)
        self.assertIsNotNone(self.todo.completed_at)

    def test_todo_toggle_uncompletes_todo(self):
        self.client.force_login(self.user)

        self.todo.completed = True
        self.todo.completed_at = timezone.now()
        self.todo.save()

        response = self.client.post(
            reverse(
                'todo_toggle',
                kwargs={'todo_id': self.todo.id},
            )
        )

        self.assertRedirects(
            response,
            reverse('todo_list')
        )

        self.todo.refresh_from_db()

        self.assertFalse(self.todo.completed)
        self.assertIsNone(self.todo.completed_at)

    def test_todo_delete(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                'todo_delete',
                kwargs={'todo_id': self.todo.id},
            )
        )

        self.assertRedirects(
            response,
            reverse('todo_list')
        )

        self.assertFalse(
            Todo.objects.filter(
                id=self.todo.id
            ).exists()
        )

    def test_user_cannot_toggle_another_users_todo(self):
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse(
                'todo_toggle',
                kwargs={'todo_id': self.todo.id},
            )
        )

        self.assertEqual(response.status_code, 404)

        self.todo.refresh_from_db()

        self.assertFalse(self.todo.completed)

    def test_user_cannot_delete_another_users_todo(self):
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse(
                'todo_delete',
                kwargs={'todo_id': self.todo.id},
            )
        )

        self.assertEqual(response.status_code, 404)

        self.assertTrue(
            Todo.objects.filter(
                id=self.todo.id
            ).exists()
        )

    def test_todo_edit(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                'todo_edit',
                kwargs={'todo_id': self.todo.id},
            ),
            {
                'title': 'Updated todo',
                'label': 'Updated',
            }
        )

        self.assertRedirects(
            response,
            reverse('todo_list')
        )

        self.todo.refresh_from_db()

        self.assertEqual(
            self.todo.title,
            'Updated todo'
        )

        self.assertEqual(
            self.todo.label,
            'Updated'
        )


    def test_todo_edit_page_shows_current_values(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                'todo_edit',
                kwargs={'todo_id': self.todo.id},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test todo')
        self.assertContains(response, 'Work')


    def test_user_cannot_edit_another_users_todo(self):
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse(
                'todo_edit',
                kwargs={'todo_id': self.todo.id},
            ),
            {
                'title': 'Hacked todo',
                'label': 'Hacked',
            }
        )

        self.assertEqual(response.status_code, 404)

        self.todo.refresh_from_db()

        self.assertEqual(
            self.todo.title,
            'Test todo'
        )

        self.assertEqual(
            self.todo.label,
            'Work'
        )