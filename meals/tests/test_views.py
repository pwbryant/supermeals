from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login 
from meals.forms import LoginForm, SignUpForm, MakeMacrosForm,ImperialTDEEForm,MetricTDEEForm, DUPLICATE_USERNAME_ERROR, EMPTY_USERNAME_ERROR,EMPTY_PASSWORD_ERROR,INVALID_USERNAME_ERROR
from meals.models import Macros

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
		guest_user = User.objects.create_user(username=GUEST_USERNAME,password=GUEST_PASSWORD)
		response = self.client.post('/meals/logging_in', data={'username':GUEST_USERNAME, 'password':GUEST_PASSWORD})
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], '/')

	def test_login_error_renders_login_page(self):
		response = self.client.post('/meals/logging_in', data={'username':BAD_USERNAME, 'password':BAD_PASSWORD})
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'login.html')

	def test_login_error_login_page_gets_back_login_form(self):
		response = self.client.post('/meals/logging_in', data={'username':BAD_USERNAME, 'password':BAD_PASSWORD})
		self.assertIsInstance(response.context['form'], LoginForm)

	def test_login_error_shows_up_on_login_page(self):
		response = self.client.post('/meals/logging_in', data={'username':BAD_USERNAME, 'password':BAD_PASSWORD})
		expected_error = "Username or Password incorrect"
		self.assertContains(response,expected_error)

	def test_logoff(self):
		guest_user = User.objects.create_user(username=GUEST_USERNAME,password=GUEST_PASSWORD)
		response = self.client.post('/meals/logging_in', data={'username':GUEST_USERNAME, 'password':GUEST_PASSWORD})
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
		response = self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
		self.assertEqual(User.objects.count(),1)
		new_user = User.objects.first()
		self.assertTrue(authenticate(request,username=USERNAME,password=PASSWORD) is not None)

		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], '/')
	
	def test_sign_up_blank_username_validation_error_wont_save_new_user(self):	

		USERNAME = ""
		response = self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
		self.assertEqual(User.objects.count(),0)

	def test_sign_up_duplicate_username_validation_error_wont_save_new_user(self):	

		response = self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
		response = self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
		self.assertEqual(User.objects.count(),1)

	def test_sign_up_bad_username_validation_error_wont_save_new_user(self):	

		USERNAME = "joe blow"
		response = self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
		self.assertEqual(User.objects.count(),0)
	
	def test_sign_up_blank_password_validation_error_wont_save_new_user(self):	

		PASSWORD =  ''
		response = self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
		self.assertEqual(User.objects.count(),0)

	def test_sign_up_validation_error_render_sign_up_html(self):	
		response = self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
		response = self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
		
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'sign_up.html')


	def test_sign_up_duplicate_validation_error_gets_sign_up_form_back(self):	
		username, email, password = USERNAME,EMAIL,PASSWORD
		response = self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
		response = self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
		self.assertIsInstance(response.context['form'], SignUpForm)

	def test_sign_up_duplicate_user_validation_error_message_shows_up_on_sign_up_html(self):	
		response = self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
		response = self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})

		self.assertContains(response,DUPLICATE_USERNAME_ERROR)

	def test_sign_up_bad_username_validation_error_message_shows_up_on_sign_up_html(self):	
		USERNAME = 'Joe Schmoe'
		response = self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
		self.assertContains(response,INVALID_USERNAME_ERROR)
 
	def test_sign_up_missing_password_validation_error_message_shows_up_on_sign_up_html(self):	
		PASSWORD =''
		response = self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
		self.assertContains(response,EMPTY_PASSWORD_ERROR)

class MyMacrosTabTest(TestCase):
	MACRO_DATA = {'unit_type':'imperial','gender':'m','age':'34','height':'70','weight':'210','activity':'none',
			'direction':'lose','change_rate':'23','fat_g':'10','fat_percent':'25','protein_g':'10','protein_percent':'35','carbs_g':'10','carbs_percent':'40'}

	def test_my_macros_url_renders_correct_template(self):
		response = self.client.get('/meals/get_my_macros/')
		self.assertTemplateUsed(response, 'my_macros.html')

	def test_my_macros_template_uses_my_macros_form(self):
		response = self.client.get('/meals/get_my_macros/')
		self.assertIsInstance(response.context['form'], MakeMacrosForm)
		self.assertIsInstance(response.context['i_tdee_form'], ImperialTDEEForm)
		self.assertIsInstance(response.context['m_tdee_form'], MetricTDEEForm)
		
	def test_make_macro_can_save_macros(self):
		self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})

		response=self.client.post('/meals/save_my_macros', data=self.MACRO_DATA)
		saved_macro = Macros.objects.all()
		self.assertEqual(saved_macro.count(),1)		

		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], '/')
	
	def test_save_my_macro_wont_save_duplicate_macro_but_still_redirects(self):

		self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})

		response=self.client.post('/meals/save_my_macros', data=self.MACRO_DATA)
		saved_macro = Macros.objects.all()
		self.assertEqual(saved_macro.count(),1)		

		response=self.client.post('/meals/save_my_macros', data=self.MACRO_DATA)
		saved_macro = Macros.objects.all()
		self.assertEqual(saved_macro.count(),1)		

		self.assertEqual(response.status_code, 302)
		self.assertEqual(response['location'], '/')

	def test_save_my_macro_missing_field_validation_wont_save_macro(self):	

		self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
		macro_data = self.MACRO_DATA.copy()
		macro_data.pop('age')
		response=self.client.post('/meals/save_my_macros', data=macro_data)
		saved_macro = Macros.objects.all()
		self.assertEqual(saved_macro.count(),0)
