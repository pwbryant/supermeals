from .base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class CalcAndViewMacros(FunctionalTest):

	def test_can_calculate_and_view_macros(self):
		pass	
		#self.fail('Finish the test!')
		#self.browser.get('http://localhost:8000')
		#On this a form there is a titled 'Calculate Daily Calories'

		#The form has fields for:
		#Age, Sex, Weight, Height, and a series of radio button specifying 
		#activity level, with a 'Calculate' button on the bottom.

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
