from django import forms

from .models import Todo


class TodoForm(forms.ModelForm):

    class Meta:
        model = Todo
        fields = [
            'title',
            'label',
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
        }