from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string

from meals.views import home_page

# Create your tests here.
class HomePageTest(TestCase):

	def test_uses_home_template(self):
		found = resolve('/')
		self.assertTemplateUsed(response, 'home.html')
