from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def workspace(request):
    return render(
        request,
        'workspace/workspace.html'
    )