from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.todos.models import Todo


User = get_user_model()


class TodoModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='todo@example.com',
            password='TestPassword123!',
        )

    def test_todo_is_created_with_default_values(self):
        todo = Todo.objects.create(
            owner=self.user,
            title='Test todo',
        )

        self.assertEqual(todo.owner, self.user)
        self.assertEqual(todo.title, 'Test todo')
        self.assertEqual(todo.label, '')
        self.assertFalse(todo.completed)
        self.assertIsNone(todo.completed_at)

    def test_todo_string_representation(self):
        todo = Todo.objects.create(
            owner=self.user,
            title='Test todo',
        )

        self.assertEqual(str(todo), 'Test todo')