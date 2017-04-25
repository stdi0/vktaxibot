from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^confirmation/', views.confirmation, name='confirmation'),
]
