from .base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class AddRecipeTest(FunctionalTest):

	def test_add_recipe(self):
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


