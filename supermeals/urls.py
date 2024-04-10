"""supermeals URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  re_path(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  re_path(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  re_path(r'^blog/', include('blog.urls'))
"""
from django.urls import include, path, re_path
from django.contrib import admin
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from meals import views
from meals import urls as meal_urls

urlpatterns = [
    re_path(r"^$", views.home_or_login, name="home_or_login"),
    re_path(r"^meals/", include(meal_urls)),
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^accounts/", include("django.contrib.auth.urls")),
]
