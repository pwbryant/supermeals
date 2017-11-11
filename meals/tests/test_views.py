from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login 

# Create your tests here.

class LoginLogoffCreateAccountTest(TestCase):

	def test_anonymous_user_home_redirects_to_login_template(self):
		response = self.client.get('/')
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], 'meals/login/')

	def test_can_login_as_authenticated_user(self):
		username,password = 'joe','joes_password'
		user = User.objects.create_user(username=username,password=password)
		response = self.client.post('/meals/logging_in', data={'username':username, 'password':password})
		
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], '/')

	def test_can_login_as_guest(self):
		guest_username,guest_password = 'guest','321!beware'
		guest_user = User.objects.create_user(username=guest_username,password=guest_password)
		response = self.client.post('/meals/logging_in', data={'username':guest_username, 'password':guest_password})
		
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], '/')


	def test_cant_login_as_unauthenticated_user(self):
		guest_username,guest_password = 'bad_man','bad_password'
		response = self.client.post('/meals/logging_in', data={'username':guest_username, 'password':guest_password})
		
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'login.html')

		expected_error = "Username or Password incorrect"
		self.assertContains(response,expected_error)

	def test_logoff(self):
		guest_username,guest_password = 'joe','crapman'
		guest_user = User.objects.create_user(username=guest_username,password=guest_password)
		response = self.client.post('/meals/logging_in', data={'username':guest_username, 'password':guest_password})

		response = self.client.get('/')
		self.assertTemplateUsed(response, 'home.html')

		response = self.client.post('/meals/logging_off/')
		response = self.client.get('/')
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], 'meals/login/')


	def test_sign_up_button_leads_to_correct_template(self):
		response = self.client.get('/meals/sign_up/')
		self.assertTemplateUsed(response, 'sign_up.html')
	
	def test_can_save_POST_and_create_user_account(self):
		request = HttpRequest()
		username, email, password = "Joe Schmoe", "joe@joepass.com", "joepass"
		response = self.client.post('/meals/create_account', data={'username':username, 'email':email,'password':password})
		self.assertEqual(User.objects.count(),1)
		new_user = User.objects.first()
		self.assertTrue(authenticate(request,username=username,password=password) is not None)

		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], '/')
	
	def test_create_user_account_does_not_allow_blank_inputs(self):

		request = HttpRequest()
		username, email, password = "", "joe@joepass.com", "joepass"
		response = self.client.post('/meals/create_account', data={'username':username, 'email':email,'password':password})
		self.assertEqual(User.objects.count(),0)


	def tests_sign_in_displays_error_for_duplicate_username(self):
		username, email, password = "Joe Schmoe", "joe@joepass.com", "joepass"
		response = self.client.post('/meals/create_account', data={'username':username, 'email':email,'password':password})

		response = self.client.post('/meals/create_account', data={'username':username, 'email':email,'password':password})
		
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'sign_up.html')
		expected_error = "This username is already taken"
		self.assertContains(response,expected_error)
