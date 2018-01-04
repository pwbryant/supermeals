from .base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.contrib.auth.models import User
from meals.models import Macros
import time

class MakeMacroMealTest(FunctionalTest):

	def test_make_macro_meal(self):
		USERNAME, PASSWORD = 'JoeSchmoe', '123pass123'
		self.browser.get(self.live_server_url)
		User.objects.create_user(username=USERNAME,password=PASSWORD)
		self.login_user(USERNAME,PASSWORD)
		#Joe now wants to make a meal that helps him achieve his macros
		#so he clicks on the 'Meal Maker' tab
		self.browser.find_element_by_id('id_meal_maker_tab_label').click()
		meal_maker_header = self.browser.find_element_by_id('id_meal_maker_headline').text
		self.assertEqual(meal_maker_header,'Meal Maker')
		#He Notices in the upper left of the tab a text input with the label 
		#'How Many Calories?', and the placeholder 'cals'.
		self.check_element_content('label[for=id_goal_meal_cals]','css','text','How Many Calories?')
		self.check_element_content('id_goal_meal_cals','id','placeholder','2111')
		#Below this input there is a table with the macros 'Fat'/'Carbs'/'Protein' and their
		#respective percent breakdown.  

		table = self.browser.find_element_by_id('id_goal_meal_macros_table')
		cells = table.find_elements_by_tag_name('td')
		self.assertEqual(cells[0].text,'Fat')
		self.assertEqual(cells[1].text,'34')
		self.assertEqual(cells[2].text,'73')
		self.assertEqual(cells[3].text,'Carbs')
		self.assertEqual(cells[4].text,'33')
		self.assertEqual(cells[5].text,'160')
		self.assertEqual(cells[6].text,'Protein')
		self.assertEqual(cells[7].text,'33')
		self.assertEqual(cells[8].text,'160')
		#Macros.objects.create()	
		self.fail('Finish The Test!')

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

