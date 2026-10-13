
from django import forms
from django.utils import timezone

from .models import Todo, TodoItem


class MultipleTextInputField(forms.Field):
    widget = forms.TextInput

    def to_python(self, value):
        if value is None:
            return []

        if isinstance(value, (list, tuple)):
            values = value
        else:
            values = [value]

        return [
            item.strip()
            for item in values
            if item and item.strip()
        ]


class TodoForm(forms.ModelForm):
    subtasks = MultipleTextInputField(required=False)

    class Meta:
        model = Todo
        fields = [
            'title',
            'label',
            'scheduled_at',
        ]

        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'todo-form-input',
                    'placeholder': 'What needs to be done?',
                    'autocomplete': 'off',
                }
            ),
            'label': forms.TextInput(
                attrs={
                    'class': 'todo-form-input',
                    'placeholder': 'Label',
                    'autocomplete': 'off',
                }
            ),
            'scheduled_at': forms.DateTimeInput(
                attrs={
                    'class': 'todo-form-input',
                    'type': 'text',
                    'placeholder': 'Select date and time',
                    'autocomplete': 'off',
                    'readonly': 'readonly',
                },
                format='%Y-%m-%d %H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['scheduled_at'].input_formats = [
            '%Y-%m-%d %H:%M',
        ]

        self.fields['scheduled_at'].widget.attrs['min'] = (
            timezone.localtime().strftime('%Y-%m-%dT%H:%M')
        )

    def clean_scheduled_at(self):
        scheduled_at = self.cleaned_data.get('scheduled_at')

        if scheduled_at is not None:
            now = timezone.localtime().replace(
                second=0,
                microsecond=0,
            )

            if timezone.is_aware(scheduled_at):
                now = timezone.now().replace(
                    second=0,
                    microsecond=0,
                )

            if scheduled_at <= now:
                raise forms.ValidationError(
                    'Please select a date and time in the future.'
                )

        return scheduled_at


class TodoItemForm(forms.ModelForm):
    class Meta:
        model = TodoItem
        fields = ['title']

        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'todo-form-input',
                    'placeholder': 'Add a subtask...',
                    'autocomplete': 'off',
                }
            ),
        }
