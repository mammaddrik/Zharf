from django.urls import path

from . import views


urlpatterns = [
    path(
        '',
        views.workspace,
        name='workspace'
    ),
    path(
        'notes/',
        views.notes,
        name='notes'
    ),
]