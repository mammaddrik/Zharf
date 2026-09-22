from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProfileSetupForm, SignInForm, SignUpForm


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