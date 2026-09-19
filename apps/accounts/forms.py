from django import forms
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
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

class SignInForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(
            attrs={
                'class': 'form-input',
                'placeholder': 'you@example.com',
                'autocomplete': 'email',
                'inputmode': 'email',
            }
        )
    )

    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-input',
                'placeholder': 'Enter your password',
                'autocomplete': 'current-password',
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = None

    def clean(self):
        cleaned_data = super().clean()

        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if not email or not password:
            return cleaned_data

        self.user = authenticate(
            email=email.strip().lower(),
            password=password
        )

        if self.user is None:
            raise forms.ValidationError(
                'Invalid email or password.'
            )

        return cleaned_data

class ZharfPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'you@example.com',
            'autocomplete': 'email',
            'inputmode': 'email',
        })

class ZharfSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Create a new password',
            'autocomplete': 'new-password',
        })

        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Repeat your new password',
            'autocomplete': 'new-password',
        })