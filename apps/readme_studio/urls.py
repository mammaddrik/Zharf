from django.urls import path

from . import views

app_name = 'readme_studio'

urlpatterns = [
    path('', views.index, name='index'),
]