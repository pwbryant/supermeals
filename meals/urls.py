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
	#url(r'^$', views.home_or_login, name='home_or_login'),
	url(r'^login/$', views.to_login, name='to_login'),
	url(r'^logging_in$', views.logging_in, name='logging_in'),
	url(r'^logging_off/$', views.logging_off, name='logging_off'),
	url(r'^sign_up/$', views.sign_up, name='sign_up'),
	url(r'^create_account$', views.create_account, name='create_account'),
	url(r'^get_my_macros/$', views.get_my_macros, name='get_my_macros'),
	url(r'^save_my_macros$', views.save_my_macros_and_meal_templates, name='save_my_macros_and_meal_templates'),
]
	
