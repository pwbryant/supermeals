from .base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.contrib.auth.models import User
import time

class CalcAndViewMacros(FunctionalTest):

	def check_element_content(self,ID,comparison_type, comparison_text,child=None):
	
		element = self.browser.find_element_by_id(ID)
		if child != None:
			element = element.find_elements_by_tag_name(child)[0]

		if comparison_type == 'text':
			content = element.text
		if comparison_type == 'placeholder':
			content = element.get_attribute('placeholder')
		if comparison_type == 'value':
			content = element.get_attribute('value')

		self.assertEqual(content,comparison_text)

	def test_can_calculate_macros(self):
		USERNAME, PASSWORD = 'JoeSchmoe','123pass123'
		#Joe signs in as guest to calc his macros
		self.browser.get(self.live_server_url)
		User.objects.create_user(username=USERNAME,password=PASSWORD)
		self.login_user(USERNAME,PASSWORD)
		
		#self.browser.find_element_by_id('id_as_guest')
		#Joe, signed in as a guest, got to the Calculate Macros tab and sees the header
		#'Total Daily Energy Expenditure (TDEE)'
		self.browser.find_element_by_id('id_my_macros_tab_label').click()
		time.sleep(5)
		macro_header = self.browser.find_element_by_id('id_my_macros_headline').text
		self.assertEqual(macro_header,'Find Total Daily Energy Expenditure (TDEE)')

		#He also notices that the home page header has disapearred
		home_header_is_displayed = self.browser.find_element_by_id('id_home_headline').is_displayed()
		self.assertFalse(home_header_is_displayed)

		#The form has fields unit type Gender, Age, Sex, Weight, Height, Activity level,
		#options for weight gain,maintain,and loss, and the desired rate of change and a
		#Calculate button. The radio buttons for unit type, gender, activity, and weight change
		#have 'Imperial', 'Male', 'Low Activity', and 'Loss' preselected
		self.assertTrue(self.browser.find_element_by_id('id_unit_type_0').is_selected())
		self.assertFalse(self.browser.find_element_by_id('id_unit_type_1').is_selected())

		self.assertTrue(self.browser.find_element_by_id('id_gender_0').is_selected())
		self.assertFalse(self.browser.find_element_by_id('id_gender_1').is_selected())
		self.check_element_content('id_age_div','text','Age:',child='label')
		self.check_element_content('id_age','placeholder','Age')
		self.check_element_content('id_weight_div','text','Weight:',child='label')
		self.check_element_content('id_weight','placeholder','lbs')
		self.check_element_content('id_height_div','text','Height:',child='label')
		self.check_element_content('id_height_0','placeholder','ft')
		self.check_element_content('id_height_1','placeholder','in')
		self.assertTrue(self.browser.find_element_by_id('id_activity_0').is_selected())
		self.assertFalse(self.browser.find_element_by_id('id_activity_1').is_selected())
		self.assertFalse(self.browser.find_element_by_id('id_activity_2').is_selected())
		self.assertFalse(self.browser.find_element_by_id('id_activity_3').is_selected())
		self.assertFalse(self.browser.find_element_by_id('id_activity_4').is_selected())

		self.assertTrue(self.browser.find_element_by_id('id_direction_0').is_selected())
		self.assertFalse(self.browser.find_element_by_id('id_direction_1').is_selected())
		self.assertFalse(self.browser.find_element_by_id('id_direction_2').is_selected())

		self.check_element_content('id_change_rate','placeholder','lb/wk')

		self.check_element_content('id_calc_tdee','text','Calculate')

		#Out of Joe wants to enter his info in metric so he selects the metric radio button
		#and notices that height fields turn into just one input field with 'cm' placeholder, 
		#and the weight and rate of change fields have 'kg' and 'kg/wk' respectively.

		self.browser.find_element_by_id('id_unit_type_1').click()
		self.check_element_content('id_weight','placeholder','kg')
		self.check_element_content('id_height','placeholder','cm')
		self.check_element_content('id_change_rate','placeholder','kg/wk')
	
		self.fail('Finish the test!')
		#Joe enters his info, and hits 'Calculate'

		#Below the form, he sees his daily caloric expediture

		#Below this he sees a series of radio buttons where he can
		#specify if he want lose/gain/or maintain his weigth, and the corresponding intensity
		#He chooses lose weight at a 20% cal deficit

		#Below this he sees several default marco breakdown's with their 
		#characteristics, as well as custom option
		#He decides to choose the %50 carb, %30 fat, and %20 fat

		#Below this he sees a 'Save My Macros' button, and he clicks it
		#and sees a'Macros Saved -- view/edit on My Macros tab' confirmation message.

		#Joe realizes he wants to make a change to his macro ratio's, so, as per
		#the aforementioned confirmation message, he navigates to the 'My Macros' tab

		#He notices a display that shows his macro stats, such as the percentage 
		#breakdown, his daily activity settings, and his, weight loss/gain rate, and the 
		#macros themselves. Except for the macros, all the other info has the option to change
		#the current settings, with the macro % breakdown having a "Custom" button, in addtion to the preset breakdown radio buttons.
