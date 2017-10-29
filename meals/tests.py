from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string

from meals.views import home_page,meal_lab
from meals.models import User

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
		username, email, password = "Joe Schmoe", "joe@joepass.com", "joepass"
		response = self.client.post('/create_account', data={'username':username, 'email':email,'password':password})
		self.assertEqual(User.objects.count(),1)
		new_user = User.objects.first()
		self.assertEqual(new_user.username,username)
		self.assertEqual(new_user.email,email)
		self.assertEqual(new_user.password,password)
		self.assertEqual(response.content.decode(), '1')


class UserModelTest(TestCase):
	
	def test_saving_and_retrieving_users(self):
		
		user1 = User()
		user1.username = "Joe Schmoe"
		user1.email = "joe@joemail.com"
		user1.password = "joepass"
		user1.save()
		
		user2 = User()
		user2.username = "Jane Doe"
		user2.email = "jane@janemail.com"
		user2.password = "janeRulz"
		user2.save()
		
		saved_users = User.objects.all()
		self.assertEqual(saved_users.count(),2)

		first_saved_user = saved_users[0]
		second_saved_user = saved_users[1]
	
		self.assertEqual(first_saved_user.username,'Joe Schmoe')
		self.assertEqual(first_saved_user.email,'joe@joemail.com')
		self.assertEqual(first_saved_user.password,'joepass')

		self.assertEqual(second_saved_user.username,'Jane Doe')
		self.assertEqual(second_saved_user.email,'jane@janemail.com')
		self.assertEqual(second_saved_user.password,'janeRulz')

