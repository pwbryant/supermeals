from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login 
from meals.forms import LoginForm, SignUpForm, DUPLICATE_USERNAME_ERROR, EMPTY_USERNAME_ERROR,EMPTY_PASSWORD_ERROR,INVALID_USERNAME_ERROR

# Create your tests here.

USERNAME,EMAIL,PASSWORD = 'JoeSchmoe','joe@joemail.com','321pass123!'
GUEST_USERNAME,GUEST_PASSWORD = 'guest','321!beware'
BAD_USERNAME,BAD_PASSWORD = 'bad','badpass'

class LoginLogoffTest(TestCase):
	
	def test_anonymous_user_home_redirects_to_login_template(self):
		response = self.client.get('/')
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], 'meals/login/')

	def test_login_page_uses_login_form(self):
		response = self.client.get('/meals/login/')
		self.assertIsInstance(response.context['form'], LoginForm)

	def test_can_login_as_authenticated_user(self):
		username,password = USERNAME,PASSWORD
		user = User.objects.create_user(username=username,password=password)
		response = self.client.post('/meals/logging_in', data={'username':username, 'password':password})
		
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], '/')

	def test_can_login_as_guest(self):
		guest_username,guest_password = GUEST_USERNAME,GUEST_PASSWORD
		guest_user = User.objects.create_user(username=guest_username,password=guest_password)
		response = self.client.post('/meals/logging_in', data={'username':guest_username, 'password':guest_password})
		
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], '/')

	def test_login_error_renders_login_page(self):
		bad_username,bad_password = BAD_USERNAME,BAD_PASSWORD
		response = self.client.post('/meals/logging_in', data={'username':bad_username, 'password':bad_password})
		
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'login.html')

	def test_login_error_login_page_gets_back_login_form(self):
		bad_username,bad_password = BAD_USERNAME,BAD_PASSWORD
		response = self.client.post('/meals/logging_in', data={'username':bad_username, 'password':bad_password})
		
		self.assertIsInstance(response.context['form'], LoginForm)

	def test_login_error_shows_up_on_login_page(self):
		bad_username,bad_password = BAD_USERNAME,BAD_PASSWORD
		response = self.client.post('/meals/logging_in', data={'username':bad_username, 'password':bad_password})
		
		expected_error = "Username or Password incorrect"
		self.assertContains(response,expected_error)

	def test_logoff(self):
		guest_username,guest_password = GUEST_USERNAME,GUEST_PASSWORD
		guest_user = User.objects.create_user(username=guest_username,password=guest_password)
		response = self.client.post('/meals/logging_in', data={'username':guest_username, 'password':guest_password})

		response = self.client.get('/')
		self.assertTemplateUsed(response, 'home.html')

		response = self.client.post('/meals/logging_off/')
		response = self.client.get('/')
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], 'meals/login/')




class CreateAccountTest(TestCase):

	def test_sign_up_button_leads_to_correct_template(self):
		response = self.client.get('/meals/sign_up/')
		self.assertTemplateUsed(response, 'sign_up.html')
	
	def test_sign_up_page_uses_sign_up_form(self):
		response = self.client.get('/meals/sign_up/')
		self.assertIsInstance(response.context['form'], SignUpForm)

	def test_can_save_POST_and_create_user_account(self):
		request = HttpRequest()
		username, email, password = USERNAME,EMAIL,PASSWORD
		response = self.client.post('/meals/create_account', data={'username':username, 'email':email,'password':password})
		self.assertEqual(User.objects.count(),1)
		new_user = User.objects.first()
		self.assertTrue(authenticate(request,username=username,password=password) is not None)

		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], '/')
	
	def test_sign_up_blank_username_validation_error_wont_save_new_user(self):	

		username, email, password = "", EMAIL, PASSWORD
		response = self.client.post('/meals/create_account', data={'username':username, 'email':email,'password':password})
		self.assertEqual(User.objects.count(),0)

	def test_sign_up_duplicate_username_validation_error_wont_save_new_user(self):	

		username, email, password = USERNAME, EMAIL, PASSWORD
		response = self.client.post('/meals/create_account', data={'username':username, 'email':email,'password':password})
		response = self.client.post('/meals/create_account', data={'username':username, 'email':email,'password':password})
		response = self.client.post('/meals/create_account', data={'username':username, 'email':email,'password':password})
		self.assertEqual(User.objects.count(),1)

	def test_sign_up_bad_username_validation_error_wont_save_new_user(self):	

		username, email, password = "joe blow", EMAIL, PASSWORD
		response = self.client.post('/meals/create_account', data={'username':username, 'email':email,'password':password})
		self.assertEqual(User.objects.count(),0)
	
	def test_sign_up_blank_password_validation_error_wont_save_new_user(self):	

		username, email, password = USERNAME, EMAIL, ''
		response = self.client.post('/meals/create_account', data={'username':username, 'email':email,'password':password})
		self.assertEqual(User.objects.count(),0)

	def test_sign_up_validation_error_render_sign_up_html(self):	
		username, email, password = USERNAME,EMAIL,PASSWORD
		response = self.client.post('/meals/create_account', data={'username':username, 'email':email,'password':password})
		response = self.client.post('/meals/create_account', data={'username':username, 'email':email,'password':password})
		
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'sign_up.html')


	def test_sign_up_duplicate_validation_error_gets_sign_up_form_back(self):	
		username, email, password = USERNAME,EMAIL,PASSWORD
		response = self.client.post('/meals/create_account', data={'username':username, 'email':email,'password':password})

		response = self.client.post('/meals/create_account', data={'username':username, 'email':email,'password':password})
		self.assertIsInstance(response.context['form'], SignUpForm)

	def test_sign_up_duplicate_user_validation_error_message_shows_up_on_sign_up_html(self):	
		username, email, password = USERNAME,EMAIL,PASSWORD
		response = self.client.post('/meals/create_account', data={'username':username, 'email':email,'password':password})
		response = self.client.post('/meals/create_account', data={'username':username, 'email':email,'password':password})

		self.assertContains(response,DUPLICATE_USERNAME_ERROR)

	def test_sign_up_bad_username_validation_error_message_shows_up_on_sign_up_html(self):	
		username, email, password = 'Joe Schmoe',EMAIL,PASSWORD
		response = self.client.post('/meals/create_account', data={'username':username, 'email':email,'password':password})
		self.assertContains(response,INVALID_USERNAME_ERROR)
 
	def test_sign_up_missing_password_validation_error_message_shows_up_on_sign_up_html(self):	
		username, email, password = USERNAME,EMAIL,''
		response = self.client.post('/meals/create_account', data={'username':username, 'email':email,'password':password})
		self.assertContains(response,EMPTY_PASSWORD_ERROR)
