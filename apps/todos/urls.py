from django.urls import path

from . import views


urlpatterns = [
    path(
        '',
        views.todo_list,
        name='todo_list',
    ),
    path(
        'create/',
        views.todo_create,
        name='todo_create',
    ),
    path(
        '<uuid:todo_id>/edit/',
        views.todo_edit,
        name='todo_edit',
    ),
    path(
        '<uuid:todo_id>/toggle/',
        views.todo_toggle,
        name='todo_toggle',
    ),
    path(
        '<uuid:todo_id>/delete/',
        views.todo_delete,
        name='todo_delete',
    ),
]