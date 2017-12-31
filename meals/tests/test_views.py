from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login 
from decimal import Decimal
from meals.forms import LoginForm, SignUpForm, MakeMacrosForm, DUPLICATE_USERNAME_ERROR, EMPTY_USERNAME_ERROR,EMPTY_PASSWORD_ERROR,INVALID_USERNAME_ERROR,DEFAULT_INVALID_INT_ERROR,EMPTY_WEIGHT_ERROR,EMPTY_HEIGHT_ERROR
from meals.models import Macros,MealTemplate
from meals.views import save_my_macros,save_meal_templates

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

	def test_can_save_POST_and_create_user_account_redirects(self):

		response = self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
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
	SHARED_MACRO_DATA = {'gender':'m','age':'34','activity':'none','direction':'lose','fat_g':'10','fat_percent':'30',
			'protein_g':'10','protein_percent':'30','carbs_g':'10','carbs_percent':'40','meal_0':'287',
				'meal_1':'287','meal_2':'287','meal_3':'285','meal_4':'289','meal_number':'5','tdee':'1435'}
	IMPERIAL_MACRO_DATA = {**SHARED_MACRO_DATA,**{'unit_type':'imperial','i_height_0':'5','i_height_1':'10','i_weight':'210','i_change_rate':'2'}}
	METRIC_MACRO_DATA = {**SHARED_MACRO_DATA,**{'unit_type':'metric','m_height':'5','m_weight':'210','m_change_rate':'2'}}
	
	def setup_user_request_for_post_to_view(self,post_data):
		request = HttpRequest()
		request.POST = post_data
		request.user = User.objects.create_user(username=USERNAME, email=EMAIL,password=PASSWORD)
		return request

	def test_my_macros_url_renders_correct_template(self):
		response = self.client.get('/meals/get_my_macros/')
		self.assertTemplateUsed(response, 'my_macros.html')

	def test_my_macros_template_uses_my_macros_form(self):
		response = self.client.get('/meals/get_my_macros/')
		self.assertIsInstance(response.context['form'], MakeMacrosForm)


	def test_save_my_macros_imperial_macros(self):
		request = self.setup_user_request_for_post_to_view(self.IMPERIAL_MACRO_DATA)
		response = save_my_macros(request)
		saved_macro = Macros.objects.all()
		self.assertEqual(saved_macro.count(),1)		

	def test_save_meal_templates_imperial_macros(self):
		request = self.setup_user_request_for_post_to_view(self.IMPERIAL_MACRO_DATA)
		response = save_meal_templates(request)
		saved_macro = MealTemplate.objects.all()
		self.assertEqual(saved_macro.count(),5)		

	def test_save_my_macros_metric_macros(self):
		request = self.setup_user_request_for_post_to_view(self.METRIC_MACRO_DATA)
		response = save_my_macros(request)
		saved_macro = Macros.objects.all()
		self.assertEqual(saved_macro.count(),1)		

	def test_save_meal_templates_metric_macros(self):
		request = self.setup_user_request_for_post_to_view(self.METRIC_MACRO_DATA)
		response = save_meal_templates(request)
		saved_macro = MealTemplate.objects.all()
		self.assertEqual(saved_macro.count(),5)		
	
	def test_save_my_macro_returns_status_dict_with_status_of_1_if_success(self):
		request = self.setup_user_request_for_post_to_view(self.METRIC_MACRO_DATA)
		response = save_my_macros(request)
		self.assertEqual(response['status'],1)
		self.assertIsInstance(response['form'],MakeMacrosForm)
		self.assertEqual(response['unit_type'],'metric')

	def test_save_meal_templates_returns_status_dict_with_status_of_1_if_success(self):
		request = self.setup_user_request_for_post_to_view(self.METRIC_MACRO_DATA)
		response = save_meal_templates(request)
		self.assertEqual(response['status'],1)

	def test_save_my_macros_and_meal_templates_saves_imperial_macros(self):
		self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
		response=self.client.post('/meals/save_my_macros', data=self.IMPERIAL_MACRO_DATA)
		saved_macro = Macros.objects.all()
		self.assertEqual(saved_macro.count(),1)		
		saved_meal_template = MealTemplate.objects.all()
		self.assertEqual(saved_meal_template.count(),5)		

	def test_save_my_macros_and_meal_templates_saves_imperial_macros(self):
		self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
		response=self.client.post('/meals/save_my_macros', data=self.IMPERIAL_MACRO_DATA)
		self.assertEqual(response.content.decode(),'1')

	def test_save_my_macros_saves_imperial_macros_in_metric(self):
		request = self.setup_user_request_for_post_to_view(self.IMPERIAL_MACRO_DATA)
		save_my_macros(request)
		macro_obj = Macros.objects.first()
		self.assertEqual(macro_obj.height,Decimal('177.80'))
		self.assertEqual(macro_obj.weight,Decimal('95.25'))
		self.assertEqual(macro_obj.change_rate,Decimal('0.91'))

	def test_save_my_macros_saves_metric_macros_in_metric(self):
		request = self.setup_user_request_for_post_to_view(self.METRIC_MACRO_DATA)
		save_my_macros(request)
		macro_obj = Macros.objects.first()
		self.assertEqual(macro_obj.height,Decimal('5.00'))
		self.assertEqual(macro_obj.weight,Decimal('210.00'))
		self.assertEqual(macro_obj.change_rate,Decimal('2.00'))

	def test_save_my_macro_wont_save_duplicate_macro_and_meal_template_but_still_returns_1(self):

		self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
		self.client.post('/meals/save_my_macros', data=self.IMPERIAL_MACRO_DATA)
		response=self.client.post('/meals/save_my_macros', data=self.IMPERIAL_MACRO_DATA)
		saved_macro = Macros.objects.all()
		saved_meal_template = Macros.objects.all()
		self.assertEqual(saved_macro.count(),1)		
		self.assertEqual(saved_meal_template.count(),1)		

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.content.decode(), "1")

	def test_save_my_macro_missing_field_validation_wont_save_macro_and_meal_template(self):	

		self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
		macro_data = self.IMPERIAL_MACRO_DATA.copy()
		macro_data.pop('age')
		response=self.client.post('/meals/save_my_macros', data=macro_data)
		saved_macro = Macros.objects.all()
		saved_meal_template = Macros.objects.all()
		self.assertEqual(saved_macro.count(),0)		
		self.assertEqual(saved_meal_template.count(),0)		


	def test_save_my_macro_validation_error_gets_back_MakeMacrosForm(self):	
		self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
		macro_data = self.IMPERIAL_MACRO_DATA.copy()
		macro_data.pop('age')
		response=self.client.post('/meals/save_my_macros', data=macro_data)
		
		self.assertEqual(response.status_code,200)
		self.assertIsInstance(response.context['form'], MakeMacrosForm)


	def test_save_my_macro_validation_error_render_my_macros_html(self):	
		self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
		macro_data = self.IMPERIAL_MACRO_DATA.copy()
		macro_data.pop('age')
		response=self.client.post('/meals/save_my_macros', data=macro_data)
		
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'my_macros.html')

	def test_save_my_macro_validation_error_shows_up_on_my_macro_html(self):	
		self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
		macro_data = self.IMPERIAL_MACRO_DATA.copy()
		macro_data['age'] = 'str'
		macro_data['i_weight'] = ''
		response=self.client.post('/meals/save_my_macros', data=macro_data)
		self.assertContains(response,DEFAULT_INVALID_INT_ERROR)
		self.assertContains(response,EMPTY_WEIGHT_ERROR)

		macro_data = self.METRIC_MACRO_DATA.copy()
		macro_data['m_height'] = ''
		response=self.client.post('/meals/save_my_macros', data=macro_data)
		self.assertContains(response,EMPTY_HEIGHT_ERROR)


	def test_make_macro_can_save_meal_template(self):
		self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})

		response=self.client.post('/meals/save_my_macros', data=self.METRIC_MACRO_DATA)

	def test_save_my_macro_and_meal_template_retuns_1_upon_successfull_save(self):
		self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})

		response=self.client.post('/meals/save_my_macros', data=self.METRIC_MACRO_DATA)
		self.assertEqual(response.content.decode(),'1')

	def test_save_meal_template_validation_error_render_my_macros_html(self):	
		self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
		macro_data = self.IMPERIAL_MACRO_DATA.copy()
		macro_data.pop('tdee')
		response=self.client.post('/meals/save_my_macros', data=macro_data)
		
		self.assertEqual(response.status_code,200)
		self.assertTemplateUsed(response,'my_macros.html')

	def test_save_meal_template_validation_error_shows_up_on_my_macro_html(self):	
		self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
		macro_data = self.IMPERIAL_MACRO_DATA.copy()
		macro_data.pop('tdee')
		response=self.client.post('/meals/save_my_macros', data=macro_data)
		self.assertContains(response,'TDEE Missing')

	def test_save_meal_template_validation_error_gets_back_MakeMacrosForm(self):	
		self.client.post('/meals/create_account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
		macro_data = self.IMPERIAL_MACRO_DATA.copy()
		macro_data.pop('tdee')
		response=self.client.post('/meals/save_my_macros', data=macro_data)
		
		self.assertIsInstance(response.context['form'], MakeMacrosForm)


