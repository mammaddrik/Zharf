from django import forms
from django.contrib.auth import password_validation

from .models import User


class SignUpForm(forms.ModelForm):
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-input',
                'placeholder': 'Create a password',
                'autocomplete': 'new-password',
            }
        )
    )

    confirm_password = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-input',
                'placeholder': 'Repeat your password',
                'autocomplete': 'new-password',
            }
        )
    )

    class Meta:
        model = User
        fields = ('email', 'password', 'confirm_password')
        widgets = {
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-input',
                    'placeholder': 'you@example.com',
                    'autocomplete': 'email',
                    'inputmode': 'email',
                }
            ),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                'An account with this email already exists.'
            )

        return email

    def clean_password(self):
        password = self.cleaned_data['password']

        password_validation.validate_password(
            password,
            self.instance
        )

        return password

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error(
                'confirm_password',
                'Passwords do not match.'
            )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()

        return user