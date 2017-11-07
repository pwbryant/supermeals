from .base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import time


class SignInOutCreateAccountTest(FunctionalTest):

	def fill_input_with_value(element_id,value):
		self.browser.find_element_by_id(element_id).send_keys(value)

	def test_new_user_can_access_as_guest_can_create_account_and_log_in_out(self):
		#Joe wants to find his macros and meals that fit them 
		#so he visits a page he heard of that does just that
		self.browser.get(self.live_server_url)		

		#the  login page title mentions Meal Lab
		self.assertIn('Meal Lab', self.browser.title)

		#He sees the header "Meal Lab"
		header_text = self.browser.find_element_by_id('id_login_headline').text
		self.assertIn('Meal Lab', header_text)

		#He notices he is on a log-in page, where he can sign-in
		#with a user name and password.  
		user_name_input = self.browser.find_element_by_id('id_username')
		self.assertEqual("Username",user_name_input.get_attribute('placeholder'))
		
		password_input = self.browser.find_element_by_id('id_password')
		self.assertEqual("Password",password_input.get_attribute('placeholder'))

		login_button_text = self.browser.find_element_by_id('id_login').get_attribute('value')
		self.assertEqual("Login",login_button_text)

		#Or sign-in as guest,which he does.
		guest_user = User.objects.create_user(username='guest',password='321!beware')
		guest_button = self.browser.find_element_by_id('id_as_guest')
		self.assertEqual("Continue as Guest",guest_button.get_attribute('value'))
		guest_button.click()

		#He is directed to a page with the head line "Meal Lab"
		# and the tabs 'My Macros', 'Meal Maker', 'My Meals', 
		#'Add Recipe', & 'Add Food' and he scrolls through them
		home_headline = self.browser.find_element_by_id('id_home_headline').text
		self.assertEqual('Meal Lab',home_headline)
		tabs = {'my_macros':'My Macros','meal_maker':'Meal Maker','my_meals':'My Meals','add_recipes':'Add Recipes','add_food':'Add Food to Database'}
		[self.assertEqual(tabs[key],self.browser.find_element_by_id('id_' + key + '_tab_label').text) for key in tabs.keys()]

		#He also sees in the upper right 'Login' & 'Sign up' buttons
		login_button_text = self.browser.find_element_by_id('id_login').text
		self.assertEqual(login_button_text,'Login')
		sign_up_button_text = self.browser.find_element_by_id('id_sign_up').text
		self.assertEqual(sign_up_button_text,'Sign up')
		
		#Joe likes what his sees so he decides he wants to create an account so he
		#clicks the 'Sign up' button is taken to a sign up page. 		
		self.browser.find_element_by_id('id_sign_up').click()
		#the sign page title mentions Meal Lab Sign Up
		self.assertIn('Meal Lab Sign Up', self.browser.title)
	
		#He sees a form having 'Username',
		#'Email', and 'Password' inputs, with  "Create Account" and "Cancel" buttons 

		user_name_placeholder = self.browser.find_element_by_id('id_username').get_attribute('placeholder')
		self.assertEqual(user_name_placeholder,'Username')
		email_placeholder = self.browser.find_element_by_id('id_email').get_attribute('placeholder')
		self.assertEqual(email_placeholder,'Email')
		password_placeholder = self.browser.find_element_by_id('id_password').get_attribute('placeholder')
		self.assertEqual(password_placeholder,'Password')

		create_account_button_text = self.browser.find_element_by_id('id_create').get_attribute('value')
		self.assertEqual(create_account_button_text,'Create Account')
		cancel_button_text = self.browser.find_element_by_id('id_cancel').text
		self.assertEqual(cancel_button_text,'Cancel')
	
		#Joe but accidently hits the "Cancel" button and is taken back to the main page"
		self.browser.find_element_by_id('id_cancel').click()
		self.browser.find_element_by_id('id_home_headline')

		#Joe clicks the 'Sign up' button again and is take back to the sign up page where he enters
		#"j_bone", "joe@joemail.com", and "joepass" and then goes to hit the 'Create Account' button
		self.browser.find_element_by_id('id_sign_up').click()
		time.sleep(.25)
		self.fill_input('id_username','j_bone')
		self.fill_input('id_email','joe@joemail.com')
		self.fill_input('id_password','joepass')
		self.browser.find_element_by_id('id_create').click()
		
		#Joe notices he is back on the main page on the main page
		time.sleep(.25)
		self.browser.find_element_by_id('id_home_headline')
		
		#He also notices that the 'Login' button is now a 'Logoff' button 
		logoff_button = self.browser.find_element_by_id('id_logoff')
		self.assertEqual(logoff_button.text,'Logoff')

		#and the 'Sign up' button is gone
		try:
			self.browser.find_element_by_id('id_sign_up')
			assert False
		except AssertionError as e:
			e.args += ('Element should not exist!!!',)
			raise
		except NoSuchElementException as e:
			pass
		
		#Happy that he made an account, Joe hits the 'Logoff' button and finds himself back on the 
		#initial Login page
		logoff_button.click()
		self.browser.find_element_by_id('id_login_headline')
		
		#He logs in as a guest to quickly check something out		
		#guest_user = User.objects.create_user(username='guest',password='password')
		self.browser.find_element_by_id('id_as_guest').click()
		self.browser.find_element_by_id('id_home_headline')

		#He forgets that he already signed up so when he goes to the sign up page and
		#and enters the same username and password, he gets an error message "Username 
		#already taken
		self.browser.find_element_by_id('id_sign_up').click()
		self.fill_input('id_username','j_bone')
		self.fill_input('id_email','joe@joemail.com')
		self.fill_input('id_password','joepass')
		self.browser.find_element_by_id('id_create').click()
		error_message = self.browser.find_element_by_css_selector('.has-error').text
		self.assertEqual(error_message,'This username is already taken')

		#Seeing this he hits the Cancel button
		self.browser.find_element_by_id('id_cancel').click()

		#He decides he wants to login for real so he clicks the login button which takes
		#him to the home login page
		self.browser.find_element_by_id('id_login').click()
		self.browser.find_element_by_id('id_login_headline')

		#He then tries to login
		#but he failed to enter his username and password so when he 
		self.browser.find_element_by_id('id_login').click()

		#hits the 'Login' button he sees and error "Username or Password incorrect"
		error_message = self.browser.find_element_by_css_selector('.has-error').text
		self.assertEqual(error_message,'Username or Password incorrect')

		#So he puts in his info and logs in
		self.fill_input('id_username','j_bone')
		self.fill_input('id_password','joepass')
		self.browser.find_element_by_id('id_login').click()
		self.browser.find_element_by_id('id_home_headline')

		self.fail('finish test')
