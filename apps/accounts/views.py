from django.contrib.auth import login

from django.shortcuts import redirect, render

from .forms import SignInForm, SignUpForm


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
        return redirect('home')

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