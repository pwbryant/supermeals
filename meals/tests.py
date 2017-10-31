from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from meals.models import MM_user

# Create your tests here.


class LoginCreateAccountTest(TestCase):

	def test_anonymous_user_home_redirects_to_login_template(self):
		response = self.client.get('/')
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], '/login')


	def test_can_login_as_authenticated_user(self):
		guest_username,guest_password = 'guest','password'
		
		guest_user = User.objects.create_user(username=guest_username,password=guest_password)
		response = self.client.post('/logging_in', data={'username':guest_username, 'password':guest_password})
		self.assertEqual(response.content.decode(), '1')
		
		response = self.client.get('/')
		self.assertTemplateUsed(response, 'home.html')

	def test_cant_login_as_unauthenticated_user(self):
		guest_username,guest_password = 'guest','password'
		response = self.client.post('/logging_in', data={'username':guest_username, 'password':guest_password})
		self.assertEqual(response.content.decode(), '0')
		
		response = self.client.get('/')
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], '/login')


	def test_sign_up_button_leads_to_correct_template(self):
		response = self.client.get('/sign_up')
		self.assertTemplateUsed(response, 'sign_up.html')
	
	def test_can_save_POST_request(self):
		username, email, password = "Joe Schmoe", "joe@joepass.com", "joepass"
		response = self.client.post('/create_account', data={'username':username, 'email':email,'password':password})
		self.assertEqual(MM_user.objects.count(),1)
		new_user = MM_user.objects.first()
		self.assertEqual(new_user.username,username)
		self.assertEqual(new_user.email,email)
		self.assertEqual(new_user.password,password)
		self.assertEqual(response.content.decode(), '1')


class UserModelTest(TestCase):
	
	def test_saving_and_retrieving_users(self):
		
		user1 = MM_user()
		user1.username = "Joe Schmoe"
		user1.email = "joe@joemail.com"
		user1.password = "joepass"
		user1.save()
		
		user2 = MM_user()
		user2.username = "Jane Doe"
		user2.email = "jane@janemail.com"
		user2.password = "janeRulz"
		user2.save()
		
		saved_users = MM_user.objects.all()
		self.assertEqual(saved_users.count(),2)

		first_saved_user = saved_users[0]
		second_saved_user = saved_users[1]
	
		self.assertEqual(first_saved_user.username,'Joe Schmoe')
		self.assertEqual(first_saved_user.email,'joe@joemail.com')
		self.assertEqual(first_saved_user.password,'joepass')

		self.assertEqual(second_saved_user.username,'Jane Doe')
		self.assertEqual(second_saved_user.email,'jane@janemail.com')
		self.assertEqual(second_saved_user.password,'janeRulz')

