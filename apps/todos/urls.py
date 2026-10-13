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
    path(
        '<uuid:todo_id>/items/create/',
        views.todo_item_create,
        name='todo_item_create',
    ),
    path(
        '<uuid:todo_id>/items/<uuid:item_id>/toggle/',
        views.todo_item_toggle,
        name='todo_item_toggle',
    ),
    path(
        '<uuid:todo_id>/items/<uuid:item_id>/delete/',
        views.todo_item_delete,
        name='todo_item_delete',
    ),
    path(
        '<uuid:todo_id>/items/reorder/',
        views.todo_item_reorder,
        name='todo_item_reorder'
    ),
]