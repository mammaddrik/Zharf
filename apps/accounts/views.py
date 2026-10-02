from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import (
    ProfileForm,
    ProfileSetupForm,
    SignInForm,
    SignUpForm,
    ZharfPasswordChangeForm,
)


def signup(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()

    return render(
        request,
        'accounts/signup.html',
        {'form': form}
    )


def signin(request):

    if request.user.is_authenticated:
        return redirect('workspace')

    if request.method == 'POST':
        form = SignInForm(request.POST)

        if form.is_valid():
            login(request, form.user)
            return redirect('home')
    else:
        form = SignInForm()

    return render(
        request,
        'accounts/signin.html',
        {'form': form}
    )


@login_required
def profile_setup(request):

    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileSetupForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():
            form.save()
            return redirect('workspace')
    else:
        form = ProfileSetupForm(
            instance=profile
        )

    return render(
        request,
        'accounts/profile/setup.html',
        {'form': form}
    )


@login_required
def profile(request):

    profile = request.user.profile

    profile_form = ProfileForm(
        instance=profile
    )

    password_form = ZharfPasswordChangeForm(
        request.user
    )

    if request.method == 'POST':

        action = request.POST.get('action')

        if action == 'profile':
            profile_form = ProfileForm(
                request.POST,
                request.FILES,
                instance=profile
            )

            if profile_form.is_valid():
                profile_form.save()
                return redirect('profile')

        elif action == 'password':
            password_form = ZharfPasswordChangeForm(
                request.user,
                request.POST
            )

            if password_form.is_valid():
                user = password_form.save()

                login(
                    request,
                    user,
                    backend='django.contrib.auth.backends.ModelBackend'
                )

                return redirect('profile')

    return render(
        request,
        'accounts/profile/profile.html',
        {
            'form': profile_form,
            'password_form': password_form,
        }
    )