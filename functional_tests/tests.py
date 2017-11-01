from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from django.contrib.auth.models import User
import unittest
import time

class NewVistorTest(LiveServerTestCase):

	def setUp(self):
		self.browser = webdriver.Firefox()

	def tearDown(self):
		self.browser.quit()

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

		login_button_text = self.browser.find_element_by_id('id_login').text
		self.assertEqual("Login",login_button_text)

		#Or sign-in as guest,which he does.
		guest_user = User.objects.create_user(username='guest',password='password')
		guest_button = self.browser.find_element_by_id('id_as_guest')
		self.assertEqual("Continue As Guest",guest_button.text)
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

		create_account_button_text = self.browser.find_element_by_id('id_create').text
		self.assertEqual(create_account_button_text,'Create Account')
		cancel_button_text = self.browser.find_element_by_id('id_cancel').text
		self.assertEqual(cancel_button_text,'Cancel')
	
		#Joe but accidently hits the "Cancel" button and is taken back to the main page"
		self.browser.find_element_by_id('id_cancel').click()
		self.browser.find_element_by_id('id_home_headline')

		#Joe clicks the 'Sign up' button again and is take back to the sign up page where he enters
		#"j_bone", "joe@joemail.com", and "joepass" and then goes to hit the 'Create Account' button
		self.browser.find_element_by_id('id_sign_up').click()
		user_name_input = self.browser.find_element_by_id('id_username')
		user_name_input.send_keys('j_bone')
		email_input = self.browser.find_element_by_id('id_email')
		email_input.send_keys('joe@joemail.com')
		password_input = self.browser.find_element_by_id('id_password')
		password_input.send_keys('joepass')
		self.browser.find_element_by_id('id_create').click()
		
		#Joe notices he is back on the main page on the main page
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

		#He decides he wants to login for real so he clicks the login button which takes
		#him to the home login page
		self.browser.find_element_by_id('id_login').click()
		self.browser.find_element_by_id('id_login_headline')

		self.fail('Finish the test!')


	def xtest_can_calculate_and_view_macros(self):
		pass	
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

		#Because Joe is a spaz, he chages his activity level to 'Very Active', and his 
		#calorie deficit to %20. He notices his daily calories and macros change.

		#And because he is an even bigger spaz, he changes his, macro breakdown, first to
		#%50/%25/%25, but then changes his mind, and hits the 'Custom' button, afterwhich, 
		#a pop-up form shows up where upon for each macro there is an input box where he enters
		#a %45/%45/%10 fat/carb/protein break down and hits 'Save'.

		#Once again, he notices the macros on the 'My Macros' tab have changed.

		#He think he wants to change the macros again, so he clicks the 'Custom' button
		#again, but once the form pops up, (and notices all the fields are blank), he decides against it and just hits the 'Cancel' button, after which the form goes away.

	def xtest_make_macro_meal(self):
			
		pass	
		#Joe now wants to make a meal that helps him achieve his macros
		#so he clicks on the 'Meal Maker' tab

		#He Notices in the upper left of the tab a text input with the placeholder 
		#'How Many Calories?'.

		#Below this input there is a table with the macros 'Fat'/'Carbs'/'Protein' and their
		#respective percent breakdown.  

		#Below the table is a 'Customize Macro %' button

		#To the right of the macro table are a series of four rectangles labeled
		#'Calories', 'Fat', 'Carbs', 'Protein', below which are a series of 0s
		#like 0, 0g, 0g, 0g for macro amounts.

		#Each of the macro rectangles has a standard deviation bar covering the macro 
		#percentage range.

		#To the right of that is a an input with the place holder 
		#'Search for ingredients' with a magnifying glass icon button

		#All the above only takes up the top of the page, the bottom half contains a 
		#page wide div with the large text 'Add Ingredients using Search'

		#Joe is going to attempt to make a salad that will fit his macro percentages
		#He starts by entering '600' into the 'How Many Calories?' input box

		#He starts by typeing 'garbonzo beans' in the search bar and hits Enter. 

		#In the area below the search bar several results appear, appearing as
		# the result text, and a + button

		#Joe clicks on the first result
		#and notices that in the lower left, a series of rectangles appear with the 
		#result text as the header, and '0g' under the bars to the left. The left-most
		#rectangle has a small drag box at the bottom.

		#He then searches for 'carrots', clicks the '+' button on the first result
		#and notices again, that a series of rectanlges and labels (except title) 
		#like the previous result appear to the right of the previous search result

		#He then adds 'bacon' and 'lettuce' to the mix as well

		#He then adjusts the dragbar on the bacon cal bar.

		#He notices that as the slider goes up, the above meal bars fill up with
		#the same color as the bacon food bars.

		#He adjusts the lettuce bar and notices that, like the bacon, bar the meal
		#bars fill up with the color of the lettuce bar.

		#He also notices that the bacon bar color in the meal bars is stacked on top
		#of the bacon bars. 

		#He then adjusts the carrots and garbonzo beans, an notices, that the meal bars are stacked in the order that the foods were initially added.

		#Joe is curious how many cals/fat/carbs/prot are in 100g of each food
		#so one by one he drags the bars of each food unil the amount label reaches
		#100g and reads what the cals/far/carbs/prot are on the meal bar.

		#Joe now tries to adjust the foods so that they achieve is target meal goals

		#Joe adds 100cals worth of every food, but after thinking about how much he
		#doesn't really like garbonzo beans, he decides he's going to replace it.
		#Joe notices an 'x' in the upper left of each food, he clicks on it and
		#garbonzo beans disappears 

		#He notices that all foods to the right of 'garbonzo beans' slide to the left

		#He also notices that all the meal bars above 'garbonzo beans' have slid down.

		#He also notices that the macro amounts have decreased correct amount.

		#He the adds kidney beans, adds 100 cals worth, and then removes bacon.
		#He notices again that all the foods right/above slide over/down, and 
		#and the macro amounts decrease the amount = to the food removed

		#Joe decides he wants a smaller salad, so he changes the cals from 600 to 300
		#and notices that all his macro amounts, and food amounts are cut in half.

		#He then adujst the remaining foods so that all the bars fall within the stdev
		#style bars and then hits the 'Save Meal' button below.

		#A modal form pops up, with input box at the top with place holder 'Meal Name'
		#Below that is a table summarizing the macros, their amounts, and precentages
		#Below that is bulleted list of the foods and their amounts.

		#Joe enters 'Joe Salad' into the meal name input box

		#Below that is a comments box with the place holder 'Recipie Notes', where 
		#Joe enters "this salad is best when the kidney beans are smashed a bit, 
		#and with pleny of pepper.

		#Below this is a 'Submit' and 'Cancel' button, Joe hits 'Submit'.

		#After he hits 'Submit' and a confirmation dialog box replaces the submit and 
		#cancel buttons saying "Meal Saved! View and/or adjust on the My Recipes Tab. 
		#Joe hits the 'OK' button and the modal box dissapears

		#He notices that the confirmation box dissapears, and that the Meal Maker tab
		#has returned to its initial state with no added foods.

		#Joe decides he want to make another salad, but one with different macro goals.
		#He hits the 'Customize Macros'.

		#A modal form pops up with all the macros listed and next to each, an input box
		#with a place holder of their current macros. 

		#He changes the percentages to fat/carbs/protein 50/25/25 and hits the 'Apply' 
		#button and the modal disappears.

		#He notices the macros in the summary table have changed to reflect his changes
		#and the meal bars have also changed to reflect the changes.

		#He decides he want to change them again so he clicks the 'Customize Macros'
		#button and then once the form comes up, he decides against it, and clicks the
		#'Cancel' button and the modal disappears and nothing has changed.

		#He then searches for and adds kale, cucumbers, ham, and peas. He then adusts
		#their drag bars to fit the target meal and he hits the 'Save Meal' button.

		#When the modal comes up, he enters, once again 'Joe Salad', enters no
		#Recipe Notes and hits 'Submit'.  After this, an alert message shows up,
		#above the Submit and Cancel buttons,
		#informing Joe that this Meal Name is already taken, and to enter a new one.

		#Joe enters 'Green Salad', and saves the meal,
		#and closes the out after the confirmation message.

		#A week later Joe wants to make the Green salad so he goes to the 'My Meals' tab

	def xtest_view_edit_meal(self):
		pass	
		#On this tab, there is a sidebar list of all meals ordered my most recently made

		#At the top of the list there is a 'Sort-by' with four options: alphabetical, 
		#most recent made, most recent used, most used

		#To the right of the side bar, there is a search input box with magnifying 
		#glass icon, with the place holder 'Search by Meal Name or Ingredients'

		#Since Joe only has two saved meals, he immediately sees 'Green Salad'
		#on the side bar list, right at the top. He bring his pointer over to the name
		# and as he brings his pointer over the name its div highlights a ligh gray

		#He clicks on the name and in the area below the search bar a table appears
		#With the meal name as the header.

		#The table is a macro break down summary with both grams and percentages

		#Below that is and ingredient list with amounts

		#Below that are any Recipe notes.

		#Below the all this is a note describing how any change causes change to all
		#other food and macro values

		#Joe notices that all numeric values, except the percentages, are found in gray
		#input boxes

		#Instead of the 3 hundred calories Joe wants the salad to be 500 cals, so 
		#he enters 500 into the calorie box. As soon as he enters the 5 he notices 
		#than all the other numeric values change as well, and by the time he is
		#finished entering 500, all the macros and food amount correspond to 500 cals

		#Just because joe is a spaz he goes through every changeable value, and doubles it, just to see how the other values change.

		#He then sets the calories back to 500. And notices that there is a button, 
		#that was not there when the cals were at 300, titled 'Save Meal in current 
		#state

		#He hits the button, and where the button was a confirmation message appears
		#saying 'Meal Saved in New State', and then dissapears after 3 seconds.

	def xtest_add_recipe():
		pass	
		
		#Change this to be similar to MFP

		#Joe wants to make some thai dish that has zingo in it so he goes 
		#to the Meal Maker tab and searches for 'zingo'.

		#He gets a 'zingo not found in database, add via "Add Food" tab'

		#Joe goes to the 'Add Food' tab where he sees a form having input fields 
		#with the place holders, 'Food Name', 'Grams per serving', 'Cals per serving',
		#'Grams fat per serving'
		#'Grams per Carbs', 'Grams fiber per serving (optional)', 'Grams sugar per 
		#serving (optional)', 'Grams protein per serving'.With an 'Add food to database'
		#at the bottom. 

		#He enters into the form 'zingo', 100, 89, .3, 23, 2.6, 12, 1.1, and hits the
		#'Add food to database'

		#He recieves a confirmation message, Zingo added to database, which dissapears
		#in three seconds.  

		#He also notices that the form is now blank

		#Joe is a fan of butter and pickles salad and he wants to add it to the database
		#so he goes to the 'Add Recipe' tab. At the top center there is an input box
		#with the place holder 'Recipe Name'

		#Below that there is an input box with the placeholder "Enter Recipe URL" with
		#a 'Get Recipe' button to the right

		#Below the input there is a separating line broken in the middle by 'OR'

		#Below that there is an input box with place holder 'Search for Ingredient'
		#and a 'Search' button to the right. 

		#Below that is a '+' button with 'Add Another Ingredient' to the right

		#Below that are 'Save New Recipe', and 'Cancel' buttons

		# He enters 'Butter Pickle Salad' into the 'Recipe Name' inputbox
		#and he enters 'butter' and hits 'Search' 

		#Below the inputbox the search results are returned. Joe selects the first
		#result

		#In the place of the search results, below the search input box, he sees
		#the meal name, and to the right an input box with place holder 'Qty', and
		#to the right of that a drop down list of units

		#He enters 1 in Qty, and select Tbsp

		#He then clicks the 'Add Another Ingredients' '+' button, and above it appears, #a search box with the place holder 'Search for Ingredient' and a 'Serach' 
		#button to the right

		#He enters 'pickles' and clicks on the first result, and enters 100 and selects
		#'grams' from the drop down menu

		#Joe now clicks the 'Save New Recipe' button, and soon after, where the save 
		#button was, he sees a 'Recipe Saved' confirmation message, which disappears
		#after 3 seconds.

		#Joe also notices that the ingredients and all other form inputs have been cleared.

		#Joe wants to add another, but different butter pickle salad so he enters
		#'Butter Pickle Salad' into the 'Recipe Name' input box, and in addition to the #amounts of butter and pickles, he add 200 grams of chedder cheese

		#Joe hits 'Save New Recipe', and recieves an error message above the 'Save New
		#Recipe button, which has been disabled, notifying him that that Recipe Name
		#has already been taken.

		#Joe changes the Recipe Name to 'Pickel Butter and Cheese salad', and hits the
		#save button again, and gets a succesfull confirmation message.

		#Joe wants to add one more pickle and butter salad so he enters the recipe name
		#'Pickle Butter and Mayo salad' and enters the standard pickle and butter amts
		#but as he gets to mayo, he decides it is gross, so he hits the Cancel button
		#and notices that the ingredients disappear and all the form inputs clear.


