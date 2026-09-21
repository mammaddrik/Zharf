from django.contrib.auth import views as auth_views
from django.urls import path

from . import forms
from . import views


urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),

    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            form_class=forms.ZharfPasswordResetForm,
            template_name='accounts/password_reset.html',
            success_url='/accounts/password-reset/done/',
        ),
        name='password_reset',
    ),

    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_sent.html',
        ),
        name='password_reset_done',
    ),

    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            form_class=forms.ZharfSetPasswordForm,
            template_name='accounts/password_reset_confirm.html',
        ),
        name='password_reset_confirm',
    ),

    path(
        'reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),

    path(
        'profile/setup/',
        views.profile_setup,
        name='profile_setup',
    ),
]