from .base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import time

class FormValidation(FunctionalTest):

	def test_login_form_validation(self):

		self.browser.get(self.live_server_url)		

		#Joe gotes  to login
		#but he failed to enter his username and password so when he 
		
		#He remains on the page !PAUL_NOTE: crispy forms doesn't submit empty forms
		#forms with empty required fields, so there won't be error messages to check
		self.login_user('','')
		self.browser.find_element_by_id('id_username')
		
		#Joe goes to sign in but mispells his username and gets an error message, but sees he
		#stays on the page
		User.objects.create_user(username='j_bone',email='joe@joemail.com',password='joepass')
		self.login_user('j_bo','joepass')
		error_message = self.browser.find_element_by_css_selector('.has-error').text
		self.assertEqual(error_message,'Username or Password incorrect')
		self.browser.find_element_by_id('id_username')


	def test_sign_up_form_validation(self):
	
		#Joe goes to sign up for Meal maker	
		User.objects.create_user(username='j_bone',email='joe@joemail.com',password='joepass')
		self.browser.get(self.live_server_url + '/meals/sign_up/')

		#Joe thinks twice about it and goes to hit cancel, but instead hist the Create Account
		#but the page doesn't submit because there arent any fields filled in
		self.browser.find_element_by_id('id_create').click()
		self.browser.find_element_by_id('id_username')

		#Joe forgets that he already signed up so when he goes to the sign up page and
		#and enters the same username and password, he gets an error message "Username 
		#already taken
		signup_ids,signup_values = ['id_username','id_email','id_password'], ['j_bone','joe@joemail.com','joepass']
		self.fill_input(signup_ids,signup_values)
		self.browser.find_element_by_id('id_create').click()
		error_message = self.browser.find_element_by_css_selector('.has-error').text
		self.assertEqual(error_message,'This username is already taken')
		self.browser.find_element_by_id('id_username')

		#Because the devs have made email requeired, when joe tries to enter with email missing
		#he gets an error
		signup_ids,signup_values = ['id_username','id_password'], ['j_bone','joepass']
		self.fill_input(signup_ids,signup_values)
		self.browser.find_element_by_id('id_create').click()
		error_message = self.browser.find_element_by_css_selector('.has-error').text
		self.assertEqual(error_message,'Email is Missing')
		self.browser.find_element_by_id('id_username')
