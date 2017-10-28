from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string

from meals.views import home_page,meal_lab

# Create your tests here.
class HomePageTest(TestCase):

	def test_uses_home_template(self):
		response = self.client.get('/')
		self.assertTemplateUsed(response, 'home.html')


class MealLabPageTest(TestCase):

	def test_uses_meal_lab_template(self):
		response = self.client.get('/meal_lab')
		self.assertTemplateUsed(response, 'meal_lab.html')


class LoginCreateAccontTest(TestCase):

	def test_sign_up_button_leads_to_correct_template(self):
		response = self.client.get('/sign_up')
		self.assertTemplateUsed(response, 'sign_up.html')
	
	def test_can_save_POST_request(self):
		response = self.client.post('/create_account', data={'user_name':'Joe', 'email':'joe@joemail.com','password':'password'})
		self.assertEqual('1',response.content.decode())
