from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^/(?P<username>[\w]{1,11})$', views.topics),
]