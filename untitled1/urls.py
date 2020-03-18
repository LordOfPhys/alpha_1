"""untitled1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from game_2 import views
from rest_framework.authtoken import views as rest_framework_views

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^index/$', views.index, name = 'index'),
    url(r'^register/$', views.register, name = 'register'),
    url(r'^get_auth_token/$', rest_framework_views.obtain_auth_token, name='get_auth_token'),
    url(r'^logout/$', views.logout_view, name = 'logout'),
    url(r'^main_view/$', views.main_view, name = 'main_view'),
    url(r'^start_game/$', views.start_game, name = 'start_game'),
]
