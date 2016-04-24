__author__ = 'vAibHav'

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.main, name='main'),
]