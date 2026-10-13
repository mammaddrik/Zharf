
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Todo(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='todos'
    )

    title = models.CharField(
        max_length=300
    )

    label = models.CharField(
        max_length=50,
        blank=True
    )

    scheduled_at = models.DateTimeField(
        null=True,
        blank=True
    )

    completed = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title


class TodoItem(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    todo = models.ForeignKey(
        Todo,
        on_delete=models.CASCADE,
        related_name='items'
    )

    title = models.CharField(
        max_length=300
    )

    completed = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )


    def save(self, *args, **kwargs):
        if self.completed:
            if self.completed_at is None:
                self.completed_at = timezone.now()
        else:
            self.completed_at = None

        update_fields = kwargs.get('update_fields')

        if update_fields is not None:
            update_fields = set(update_fields)
            update_fields.add('completed_at')
            kwargs['update_fields'] = update_fields

        super().save(*args, **kwargs)

        self.sync_todo_status(self.todo)

    def delete(self, *args, **kwargs):
        todo = self.todo
        result = super().delete(*args, **kwargs)
        self.sync_todo_status(todo)
        return result

    @staticmethod
    def sync_todo_status(todo=None):
        if todo is None:
            return

        items = todo.items.all()

        if not items.exists():
            return

        all_completed = not items.filter(
            completed=False
        ).exists()

        if all_completed == todo.completed:
            return

        todo.completed = all_completed
        todo.completed_at = (
            timezone.now() if all_completed else None
        )

        todo.save(
            update_fields=[
                'completed',
                'completed_at',
                'updated_at',
            ]
        )

    def __str__(self):
        return self.title
