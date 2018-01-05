from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpRequest
from selenium import webdriver
import time
from meals.models import Macros

class FunctionalTest(StaticLiveServerTestCase):

	USERNAME = 'JoeSchmoe'
	PASSWORD = '123pass123'
	GUEST = 'guest'
	GUESTPASS = '321!beware'

	def setUp(self):
		self.browser = webdriver.Firefox()

	def tearDown(self):
		self.browser.quit()
	
	def fill_input(self,element_ids,values):
		for i in range(len(element_ids)):
			element = self.browser.find_element_by_id(element_ids[i])
			if element.get_attribute('type') == 'text':
				element.send_keys(values[i])

			if element.get_attribute('type') == 'radio':
				element.click()

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

	def check_element_content(self,selector,selector_type,comparison_type, comparison_text,child=None):
	
		if selector_type == 'id':
			element = self.browser.find_element_by_id(selector)
		
		if selector_type == 'css':
			element = self.browser.find_element_by_css_selector(selector)

		if child != None:
			element = element.find_elements_by_tag_name(child)[0]

		if comparison_type == 'text':
			content = element.text
		if comparison_type == 'placeholder':
			content = element.get_attribute('placeholder')
		if comparison_type == 'value':
			content = element.get_attribute('value')

		self.assertEqual(content,comparison_text)

	def initialize_test(self,username,password):

		self.browser.get(self.live_server_url)
		USER = User.objects.create_user(username=username,password=password)
		self.login_user(username,password)

	def create_default_macro(self,username):
		user = User.objects.get(username=username)
		Macros.objects.create(**{
			'user':user,
			'unit_type':'imperial',
			'gender':'m',
			'age':34,
			'height':177.8,
			'weight':95.25,
			'direction':'lose',
			'activity':'light',
			'change_rate':.45359237,
			'protein_percent':33,
			'fat_percent':34
		})
		
