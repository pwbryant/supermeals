from .base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
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

		self.assertFalse(self.browser.find_element_by_id('id_gender_1').is_selected())
		self.assertFalse(self.browser.find_element_by_id('id_gender_2').is_selected())
		self.check_element_content('id_age_label','text','Age:')
		self.check_element_content('id_age','placeholder','Age')
		self.check_element_content('id_weight_label','text','Weight:')
		self.check_element_content('id_i_weight','placeholder','lb')
		self.check_element_content('id_height_label','text','Height:')
		self.check_element_content('id_i_height_0','placeholder','ft')
		self.check_element_content('id_i_height_1','placeholder','in')
		self.assertTrue(self.browser.find_element_by_id('id_activity_0').is_selected())
		self.assertFalse(self.browser.find_element_by_id('id_activity_1').is_selected())
		self.assertFalse(self.browser.find_element_by_id('id_activity_2').is_selected())
		self.assertFalse(self.browser.find_element_by_id('id_activity_3').is_selected())
		self.assertFalse(self.browser.find_element_by_id('id_activity_4').is_selected())
		self.assertTrue(self.browser.find_element_by_id('id_direction_0').is_selected())
		self.assertFalse(self.browser.find_element_by_id('id_direction_1').is_selected())
		self.assertFalse(self.browser.find_element_by_id('id_direction_2').is_selected())
		self.check_element_content('id_i_change_rate','placeholder','lb/wk')

		self.check_element_content('id_calc_tdee','text','Calculate')

		#Out of Joe wants to enter his info in metric so he selects the metric radio button
		#and notices that height fields turn into just one input field with 'cm' placeholder, 
		#and the weight and rate of change fields have 'kg' and 'kg/wk' respectively.

		self.browser.find_element_by_id('id_unit_type_1').click()
		self.check_element_content('id_m_weight','placeholder','kg')
		self.check_element_content('id_m_height','placeholder','cm')
		self.check_element_content('id_m_change_rate','placeholder','kg/wk')
	
		#Joe suspects more content will be displayed after he hits Calculates, but as of now he only sees
		#the calc button at the bottom of the form
		is_hidden_div = not self.browser.find_element_by_id('id_choose_macros_form_container').is_displayed()
		self.assertTrue(is_hidden_div)
		isnt_hidden_div = not self.browser.find_element_by_id('id_fat_g').is_displayed()
		self.assertTrue(isnt_hidden_div)

		#Joe enters his info, and hits 'Calculate', but too late he realized he had female selected
		#Below the form, he sees his daily caloric expediture
		macro_form_ids = ['id_unit_type_0','id_gender_2','id_age','id_i_weight','id_i_height_0','id_i_height_1','id_activity_0','id_direction_0','id_i_change_rate']
		macro_form_values = [None,None,'34','210','5','10',None,None,'1']
		self.fill_input(macro_form_ids,macro_form_values)	
		self.browser.find_element_by_id('id_calc_tdee').click()
		self.check_element_content('id_tdee_result','text','2076')
		self.check_element_content('id_change_tdee_result','text','1576')

		#After calculating TDEE, and area for choosing macro percent appers. With inputs for both
		#% and g for each macro, with % Remaing Footer, and a 'Continue' button which is greyed out.

		isnt_hidden_div = self.browser.find_element_by_id('id_choose_macros_form_container').is_displayed()
		self.assertTrue(isnt_hidden_div)
		self.check_element_content('id_protein_percent','placeholder','%')
		self.check_element_content('id_protein_g','placeholder','g')
		self.check_element_content('id_fat_percent','placeholder','%')
		self.check_element_content('id_fat_g','placeholder','g')
		self.check_element_content('id_carbs_percent','placeholder','%')
		self.check_element_content('id_carbs_g','placeholder','g')
		macro_row_headers = self.browser.find_elements_by_class_name('choose_macro_titles')
		self.assertEqual(macro_row_headers[0].text,'%')
		self.assertEqual(macro_row_headers[1].text,'g')
		self.assertEqual(macro_row_headers[2].text,'Protein')
		self.assertEqual(macro_row_headers[3].text,'Fat')
		self.assertEqual(macro_row_headers[4].text,'Carbs')
		self.assertEqual(macro_row_headers[5].text,'% Remaining')
		continue_button = self.browser.find_element_by_id('id_choose_macros_continue_button')
		self.assertFalse(continue_button.is_enabled())

		#Joe switches to Male and hits Calculate again and sees his new TDEE
		self.fill_input(['id_gender_1'],[None])	
		self.browser.find_element_by_id('id_calc_tdee').click()
		self.check_element_content('id_tdee_result','text','2435')
		self.check_element_content('id_change_tdee_result','text','1935')

		#Joe comes wants to see what happens when he selcts the maintain button so he clicks it
		#and sees that the change input box disappears
		self.fill_input(['id_direction_1'],[None])	
		is_hidden_div = not self.browser.find_element_by_id('id_change_rate_form_container').is_displayed()
		self.assertTrue(is_hidden_div)

		#He decides to choose the %50 carb, %30 fat, and %20 protein and notices that
		#after typeing in his percents, the inputs in the 'g' column automatically get filled in
		#and the % remaing is updated
		macro_form_ids = ['id_protein_percent','id_fat_percent','id_carbs_percent']
		macro_form_values = ['20','30','50']
		self.fill_input(macro_form_ids,macro_form_values)	
		self.check_element_content('id_protein_g','value','97')
		self.check_element_content('id_macro_percent_total','text','0')

		#When the % Remaining equals 0, The Continue button becomes ungreyed and so Joe clicks it, and 
		#another section becomes visible which contains a header reading about optionlly breaking up
		#the daily calories, and an input ask prompting the user to enter how many meals/snacks 
		#per day?" Joe enters 5.
		continue_button = self.browser.find_element_by_id('id_choose_macros_continue_button')
		self.assertTrue(continue_button.is_enabled())
		continue_button.click()
		self.check_element_content('id_meal_template_header','text','Break Up Your Daily Calories Into Meals/Snacks (Optional)')
		self.check_element_content('id_meal_template_meals_number_label','text','Number of meals/snacks per day?')
		self.check_element_content('id_calc_macros_meals_number','placeholder','# meals/snacks')
		self.fail('Finish the test!')
		#After entering 5, another section appears where there are 5 inputs labeled Breakfast,Lunch
		#,Dinner, Snack1, Snack2 with the inputs autofilled into five equal caloric chunks of 387.

		#There is a a "Cals Remaining" footer which adds up to 1935. 

		#And a header reading "Customize meal calories (Optional), and a Save button below

		#Joe wants to have two snacks of 200 cals so he changed Snack1 and Snack2 to 200 each
		#and he notices that the total cals changes to 374, and the Save button grays out.
		

		#Joe realizes he wants to make a change to his macro ratio's, so, as per
		#the aforementioned confirmation message, he navigates to the 'My Macros' tab

		#He notices a display that shows his macro stats, such as the percentage 
		#breakdown, his daily activity settings, and his, weight loss/gain rate, and the 
		#macros themselves. Except for the macros, all the other info has the option to change
		#the current settings, with the macro % breakdown having a "Custom" button, in addtion to the preset breakdown radio buttons.
