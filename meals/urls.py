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
	url(r'^sign-up/$', views.sign_up, name='sign_up'),
	url(r'^create-account$', views.create_account, name='create_account'),
	url(r'^my-macros/$', views.get_my_macros, name='my_macros'),
	url(r'^save-my-macros$', views.save_my_macros, name='save_my_macros'),
	url(r'^meal-maker/$', views.get_meal_maker_template, name='meal_maker'),
	url(r'^search-foods/(?P<food_owner>user|all)/$', views.search_foods, name='search_foods'),
	url(r'^search-my-meals/$', views.search_my_meals, name='search_my_meals'),
	url(r'^save-macro-meal$', views.save_macro_meal, name='save_macro_meal'),
	url(r'^my-meals/$', views.get_my_meals, name='my_meals'),
	url(r'^easy-picks/(?P<pick_type>recent|popular)/$', views.easy_picks, name='easy_picks'),
	url(r'^add-recipe/$', views.add_recipe, name='add_recipe'),
]
	
