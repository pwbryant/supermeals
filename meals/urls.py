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
from django.urls import path, re_path
from meals import views
from .views import MyMacros

urlpatterns = [
    re_path(r"^add-food/$", views.add_food, name="add_food"),
    re_path(r"^add-recipe/$", views.render_add_recipe, name="render_add_recipe"),
    re_path(r"^create-account$", views.create_account, name="create_account"),
    re_path(r"^meal-maker/$", views.get_meal_maker_template, name="meal_maker"),
    re_path(r"^my-macros/$", MyMacros.as_view(), name="my_macros"),
    re_path(r"^my-meals/$", views.get_my_meals, name="my_meals"),
    re_path(r"^my-meals-delete$", views.delete_my_meals, name="delete_my_meals"),
    re_path(r"^save-macro-meal$", views.save_macro_meal, name="save_macro_meal"),
    re_path(r"^save-recipe$", views.save_recipe, name="save_recipe"),
    re_path(
        r"^search-foods/(?P<food_owner>user|all)/$",
        views.search_foods,
        name="search_foods",
    ),
    re_path(
        r"^search-my-meals/(?P<meal_or_recipe>meal|recipe)/$",
        views.search_my_meals,
        name="search_my_meals",
    ),
    re_path(r"^sign-up/$", views.sign_up, name="sign_up"),
]
