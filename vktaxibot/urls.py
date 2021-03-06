"""vktaxibot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from bot import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^index/', views.index, name='index'),
    url(r'^bot/', views.bot, name='bot'),
    url(r'^$', views.index, name='index'),
    url(r'^active_orders/', views.active_orders, name='active_orders'),
    url(r'^completed_orders/', views.completed_orders, name='completed_orders'),
    url(r'^canceled_orders/', views.canceled_orders, name='canceled_orders'),
    #url(r'^complete/(?P<id>\d*)/$', views.complete, name='complete'),
    url(r'^complete/$', views.complete, name='complete'),
    url(r'^cancel/(?P<id>\d*)/$', views.cancel, name='cancel'),
    url(r'^login/', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout,
                          {'next_page': '/'}),
]
