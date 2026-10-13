
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.todos.models import Todo, TodoItem


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
        self.assertIsNone(todo.scheduled_at)
        self.assertFalse(todo.completed)
        self.assertIsNone(todo.completed_at)

    def test_todo_string_representation(self):
        todo = Todo.objects.create(
            owner=self.user,
            title='Test todo',
        )

        self.assertEqual(str(todo), 'Test todo')

    def test_todo_item_is_created(self):
        todo = Todo.objects.create(
            owner=self.user,
            title='Shopping list',
        )

        item = TodoItem.objects.create(
            todo=todo,
            title='Buy bread',
        )

        self.assertEqual(item.todo, todo)
        self.assertEqual(item.title, 'Buy bread')
        self.assertFalse(item.completed)
        self.assertIsNone(item.completed_at)
        self.assertEqual(todo.items.count(), 1)

    def test_todo_item_string_representation(self):
        todo = Todo.objects.create(
            owner=self.user,
            title='Shopping list',
        )

        item = TodoItem.objects.create(
            todo=todo,
            title='Buy bread',
        )

        self.assertEqual(str(item), 'Buy bread')

    def test_todo_is_completed_when_all_items_are_completed(self):
        todo = Todo.objects.create(
            owner=self.user,
            title='Shopping list',
        )

        first_item = TodoItem.objects.create(
            todo=todo,
            title='Buy meat',
        )

        second_item = TodoItem.objects.create(
            todo=todo,
            title='Buy bread',
        )

        first_item.completed = True
        first_item.save()

        todo.refresh_from_db()
        self.assertFalse(todo.completed)

        second_item.completed = True
        second_item.save()

        todo.refresh_from_db()

        self.assertTrue(todo.completed)
        self.assertIsNotNone(todo.completed_at)

    def test_todo_reopens_when_completed_item_is_reopened(self):
        todo = Todo.objects.create(
            owner=self.user,
            title='Shopping list',
        )

        first_item = TodoItem.objects.create(
            todo=todo,
            title='Buy meat',
            completed=True,
        )

        second_item = TodoItem.objects.create(
            todo=todo,
            title='Buy bread',
            completed=True,
        )

        todo.refresh_from_db()
        self.assertTrue(todo.completed)

        second_item.completed = False
        second_item.save()

        todo.refresh_from_db()

        self.assertFalse(todo.completed)
        self.assertIsNone(todo.completed_at)

    def test_completed_item_gets_completed_at(self):
        todo = Todo.objects.create(
            owner=self.user,
            title='Shopping list',
        )

        item = TodoItem.objects.create(
            todo=todo,
            title='Buy bread',
            completed=True,
        )

        self.assertIsNotNone(item.completed_at)

    def test_reopened_item_clears_completed_at(self):
        todo = Todo.objects.create(
            owner=self.user,
            title='Shopping list',
        )

        item = TodoItem.objects.create(
            todo=todo,
            title='Buy bread',
            completed=True,
        )

        item.completed = False
        item.save()

        item.refresh_from_db()

        self.assertFalse(item.completed)
        self.assertIsNone(item.completed_at)

    def test_deleting_incomplete_item_recalculates_todo_status(self):
        todo = Todo.objects.create(
            owner=self.user,
            title='Shopping list',
        )

        first_item = TodoItem.objects.create(
            todo=todo,
            title='Buy meat',
            completed=True,
        )

        second_item = TodoItem.objects.create(
            todo=todo,
            title='Buy bread',
        )

        todo.refresh_from_db()
        self.assertFalse(todo.completed)

        second_item.delete()

        todo.refresh_from_db()

        self.assertTrue(todo.completed)
        self.assertIsNotNone(todo.completed_at)

    def test_deleting_last_item_preserves_todo_status(self):
        todo = Todo.objects.create(
            owner=self.user,
            title='Shopping list',
        )

        item = TodoItem.objects.create(
            todo=todo,
            title='Buy bread',
        )

        item.delete()

        todo.refresh_from_db()

        self.assertFalse(todo.completed)
        self.assertIsNone(todo.completed_at)

    def test_scheduled_at_can_be_set(self):
        scheduled_at = timezone.now()

        todo = Todo.objects.create(
            owner=self.user,
            title='Shopping list',
            scheduled_at=scheduled_at,
        )

        self.assertEqual(todo.scheduled_at, scheduled_at)
