from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.users),
    url(r'^/(?P<username>[\w]{1,11})$', views.users),
    url(r'^/(?P<username>[\w]{1,11})/avatar$', views.users_avatar),
]