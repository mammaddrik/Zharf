from django.urls import path

from . import views


app_name = 'documents'


urlpatterns = [
    path(
        'collections/',
        views.collection_list,
        name='collection_list'
    ),
    path(
        'collections/create/',
        views.collection_create,
        name='collection_create'
    ),
    path(
        'collections/<uuid:pk>/edit/',
        views.collection_update,
        name='collection_update'
    ),
    path(
        'collections/<uuid:pk>/delete/',
        views.collection_delete,
        name='collection_delete'
    ),
    path(
        '',
        views.document_list,
        name='document_list'
    ),
    path(
        'create/',
        views.document_create,
        name='document_create'
    ),
    path(
        '<uuid:pk>/',
        views.document_detail,
        name='document_detail'
    ),
    path(
        '<uuid:pk>/edit/',
        views.document_update,
        name='document_update'
    ),
    path(
        '<uuid:pk>/delete/',
        views.document_delete,
        name='document_delete'
    ),
    path(
        'workspace/',
        views.workspace,
        name='workspace'
    ),
]