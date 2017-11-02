from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login 

from meals.models import MM_user

# Create your tests here.


class LoginLogoffCreateAccountTest(TestCase):

	def test_anonymous_user_home_redirects_to_login_template(self):
		response = self.client.get('/')
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], '/login')

	def test_can_login_as_authenticated_user(self):
		guest_username,guest_password = 'joe','joes_password'
		guest_user = User.objects.create_user(username=guest_username,password=guest_password)
		response = self.client.post('/logging_in', data={'username':guest_username, 'password':guest_password})
		self.assertEqual(response.content.decode(), '1')
		
		response = self.client.get('/')
		self.assertTemplateUsed(response, 'home.html')

	def test_cant_login_as_unauthenticated_user(self):
		guest_username,guest_password = 'bad_man','bad_password'
		response = self.client.post('/logging_in', data={'username':guest_username, 'password':guest_password})
		self.assertEqual(response.content.decode(), '0')
		
		response = self.client.get('/')
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], '/login')

	def test_logoff(self):
		guest_username,guest_password = 'joe','crapman'
		guest_user = User.objects.create_user(username=guest_username,password=guest_password)
		response = self.client.post('/logging_in', data={'username':guest_username, 'password':guest_password})

		response = self.client.get('/')
		self.assertTemplateUsed(response, 'home.html')

		response = self.client.post('/logging_off')
		response = self.client.get('/')
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], '/login')


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


