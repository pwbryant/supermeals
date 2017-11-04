from .base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class ViewAndEditMealTest(FunctionalTest):

	def test_view_edit_meal(self):
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

