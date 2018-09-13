"""supermeals URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from meals import views

urlpatterns = [
	url(r'^sign-up/$', views.sign_up, name='sign-up'),
	url(r'^create-account$', views.create_account, name='create-account'),
	url(r'^get-my-macros/$', views.get_my_macros, name='get-my-macros'),
	url(r'^save-my-macros$', views.save_my_macros, name='save-my-macros'),
	url(r'^meal-maker/$', views.get_meal_maker_template, name='get-meal-maker-template'),
	url(r'^search-foods/$', views.search_foods, name='search-foods'),
	url(r'^save-macro-meal$', views.save_macro_meal, name='save_macro_meal'),
]
	
