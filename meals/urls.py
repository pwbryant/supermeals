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
from meals import views
from .views import MyMacros

urlpatterns = [
    url(r"^add-food/$", views.add_food, name="add_food"),
    url(r"^add-recipe/$", views.render_add_recipe, name="render_add_recipe"),
    url(r"^create-account$", views.create_account, name="create_account"),
    url(r"^meal-maker/$", views.get_meal_maker_template, name="meal_maker"),
    url(r"^my-macros/$", MyMacros.as_view(), name="my_macros"),
    url(r"^my-meals/$", views.get_my_meals, name="my_meals"),
    url(r"^my-meals-delete$", views.delete_my_meals, name="delete_my_meals"),
    url(r"^save-macro-meal$", views.save_macro_meal, name="save_macro_meal"),
    url(r"^save-recipe$", views.save_recipe, name="save_recipe"),
    url(
        r"^search-foods/(?P<food_owner>user|all)/$",
        views.search_foods,
        name="search_foods",
    ),
    url(
        r"^search-my-meals/(?P<meal_or_recipe>meal|recipe)/$",
        views.search_my_meals,
        name="search_my_meals",
    ),
    url(r"^sign-up/$", views.sign_up, name="sign_up"),
]
