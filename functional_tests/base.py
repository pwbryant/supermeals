from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpRequest
from selenium import webdriver
import time

class FunctionalTest(StaticLiveServerTestCase):

	def setUp(self):
		self.browser = webdriver.Firefox()

	def tearDown(self):
		self.browser.quit()
	
	def fill_input(self,element_ids,values):
		for i in range(len(element_ids)):
			self.browser.find_element_by_id(element_ids[i]).send_keys(values[i])


	def login_user(self,username,password = False):

		if '' not in [username,password]:
			
			if username == 'guest':
				login_button_id = 'id_as_guest'
			else:
				self.fill_input(['id_username','id_password'],[username,password])
				login_button_id = 'id_login'
		else:
			login_button_id = 'id_login'

		self.browser.find_element_by_id(login_button_id).click()
