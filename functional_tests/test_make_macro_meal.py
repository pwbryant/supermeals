from .base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from django.contrib.auth.models import User
from meals.models import Macros,Foods
import time
import numpy as np

class MakeMacroMealTest(FunctionalTest):

    fixtures = ["db.json"]
    
    def get_bar_ratio(self,num_height,denom_height):
        return round(float(num_height) / float(denom_height),2)

    def test_make_macro_meal(self):
        user = self.initialize_test(self.USERNAME,self.PASSWORD)
        # macro = self.create_default_macro(user)
        # self.create_default_meal_templates(user)
        
        # Joe now wants to make a meal that helps him achieve his macros
        # so he clicks on the "Meal Maker" tab
        self.browser.find_element_by_id("meal-maker-tab").click()

        # Joe however, did not set any macros in the my macros tab, but he can 
        # still make a meal.
        #He notices an input to enter the desired calories.
        self.check_element_content("label[for='goal-meal-cals-container']",
                "css","text","How Many Calories?")
        self.check_element_content(
                "goal-meal-cals","id","placeholder","Cals")
       

        #Below he sees a table like area for entering the percentages/grams for each macros	
        macro_div = self.browser.find_element_by_id("goal-meal-macros-container")
        macro_spans = macro_div.find_elements_by_css_selector("label")
        self.assertEqual(macro_spans[0].text,"Percent")
        self.assertEqual(macro_spans[1].text,"Grams")
        self.assertEqual(macro_spans[2].text,"Fat")
        self.assertEqual(macro_spans[3].text,"Carbs")
        self.check_element_content(
                "goal-meal-fat-percent","id","placeholder","%")
        self.check_element_content(
                "goal-meal-fat-g","id","placeholder","g")
        self.check_element_content(
                "goal-meal-carbs-percent","id","placeholder","%")
        self.check_element_content(
                "goal-meal-carbs-g","id","placeholder","g")
        self.check_element_content(
                "goal-meal-protein-percent","id","placeholder","%")
        self.check_element_content(
                "goal-meal-protein-g","id","placeholder","g")

        # Joe enters 500 cals and 34,33,33 % for Fat, Carbs and Protein 
        # respectively and notices that the gram inputs fill in 
        # with 19, 41, 41
        self.fill_input([
            "input[id='goal-meal-fat-percent']",
            "input[id='goal-meal-carbs-percent']",
            "input[id='goal-meal-protein-percent']",
            "input[id='goal-meal-cals']"
            ],
            [34,33,33,500]
        )	
        self.check_element_content("goal-meal-fat-g","id","value","19")
        self.check_element_content("goal-meal-carbs-g","id","value","41")
        self.check_element_content("goal-meal-protein-g","id","value","41")

        # Joe realizes he needs to know his TDEE so he does that and then 
        # comes back where He Notices in the upper left of the tab a 
        # healine showing his TDEE and text input with the label 
        # "How Many Calories?", and the placeholder "cals" and under 
        # that a dropdown with choices of Meal 1,2,3 602 and Meal 4 305.
        macro = self.create_default_macro(user)
        self.create_default_meal_templates(user)
        self.browser.find_element_by_id("meal-maker-tab").click()
        self.check_element_content("tdee","id","text","TDEE: 2111")
        self.check_element_content(
                "label[for='goal-meal-cals-container']","css","text",
                "How Many Calories?")
        self.check_element_content(
                "goal-meal-cals","id","placeholder","Cals")
        set_cals_select = Select(self.browser.find_element_by_id(
            "goal-meal-cals-select"))
        options = set_cals_select.options
        self.assertEqual(options[0].text,"Saved Cals")
        self.assertEqual(options[1].text,"Meal 1,2,3 - 591 cals")
        self.assertEqual(options[2].text,"Meal 4 - 338 cals")

        # Below this input there is an  table like input area with 
        # the macros "Fat"/"Carbs"/"Protein" and their
        # respective percent breakdown.

        table = self.browser.find_element_by_id("goal-meal-macros-container")
        labels = table.find_elements_by_css_selector("label")
        self.assertEqual(labels[0].text,"Percent")
        self.assertEqual(labels[1].text,"Grams")
        self.assertEqual(labels[2].text,"Fat")
        self.assertEqual(labels[3].text,"Carbs")
        self.assertEqual(labels[4].text,"Protein")
        inputs = table.find_elements_by_css_selector("input")
        self.assertEqual(inputs[0].get_attribute("value"),"34")
        self.assertEqual(inputs[1].get_attribute("placeholder"),"-")
        self.assertEqual(inputs[2].get_attribute("value"),"33")
        self.assertEqual(inputs[3].get_attribute("placeholder"),"-")
        self.assertEqual(inputs[4].get_attribute("value"),"33")
        self.assertEqual(inputs[5].get_attribute("placeholder"),"-")
        
        #Joe selects the second option "Meal 4 - 305" and notices that a grams column
        #in the table below fills in.
        set_cals_select = Select(self.browser.find_element_by_id(
            "goal-meal-cals-select"))
        set_cals_select.options[2].click()
        self.assertEqual(inputs[1].get_attribute("value"),"13")
        self.assertEqual(inputs[3].get_attribute("value"),"28")
        self.assertEqual(inputs[5].get_attribute("value"),"28")

        # Joe realized he wants to enter a value not on his saved 
        # tab so he enters 500 into the text input and when he does 
        # so he sees that the dropdown resets to the default position
        cals_input_id = ["input[id='goal-meal-cals']"]
        cals_input = ["500"]
        self.fill_input(cals_input_id,cals_input)	
        self.assertEqual(
                set_cals_select.first_selected_option.text,"Saved Cals")
        
        #He also notices that the grams values chanage as well
        self.assertEqual(inputs[1].get_attribute("value"),"19")
        self.assertEqual(inputs[3].get_attribute("value"),"41")
        self.assertEqual(inputs[5].get_attribute("value"),"41")

        #Joe realizes he actually does want to enter his saved amount
        # so he reslects the 338 cal option and noctices that the text 
        # input clears out. He also changes the Fat and Carbs percents
        # to 30 and 37 % respectively

        set_cals_select.options[2].click()
        self.check_element_content("goal-meal-cals","id","text","")
        macro_input_ids = [
                "input[id='goal-meal-fat-percent']",
                "input[id='goal-meal-carbs-percent']"]
        self.fill_input(macro_input_ids,[],clear=True)	
        macro_inputs = ["30","37"]
        self.fill_input(macro_input_ids,macro_inputs)	
        self.assertEqual(inputs[1].get_attribute("value"),"11")
        self.assertEqual(inputs[3].get_attribute("value"),"31")
        self.assertEqual(inputs[5].get_attribute("value"),"28")

        # To the right of the macro table are a series of four rectangles 
        # labeled "Calories", "Fat", "Carbs", "Protein".
        self.browser.find_element_by_id("create-macro-bars-button").click()
        goal_svg = self.browser.find_element_by_id("goal-macros-svg")
        cal_bar = goal_svg.find_element_by_id("goal-cals-bar")
        fat_bar = goal_svg.find_element_by_id("goal-fat-bar")
        carbs_bar = goal_svg.find_element_by_id("goal-carbs-bar")
        protein_bar = goal_svg.find_element_by_id("goal-protein-bar")
        
        svg_height = self.browser.find_element_by_id(
                "goal-macros-container").size["height"]
        svg_width = self.browser.find_element_by_id(
                "goal-macros-container").size["width"]
        bar_width = (svg_width - (svg_width * .1)) / 4.0	

        print(cal_bar.get_attribute("height"))
        print(svg_height)
        #self.assertTrue(np.isclose(
        #    self.get_bar_ratio(cal_bar.get_attribute("height"),
        #    svg_height),85))
        self.assertTrue(np.isclose(
            float(cal_bar.get_attribute("width")),bar_width)
            ) # all bars set to same width
        self.assertEqual(self.get_bar_ratio(
            fat_bar.get_attribute("height"),
            cal_bar.get_attribute("height")),.30)
        self.assertEqual(self.get_bar_ratio(
            carbs_bar.get_attribute("height"),
            cal_bar.get_attribute("height")),.37)
        self.assertEqual(self.get_bar_ratio(
            protein_bar.get_attribute("height"),
            cal_bar.get_attribute("height")),.33)
        
        # Below which are a series of 0s like 0, 0g, 0g, 0g 
        # for macro amounts.
        labels = self.browser.find_elements_by_tag_name("text")
        self.assertEqual(labels[0].text,"Cals: 0")
        self.assertEqual(labels[1].text,"Fat: 0g")
        self.assertEqual(labels[2].text,"Carbs: 0g")
        self.assertEqual(labels[3].text,"Protein: 0g")

        # Each of the macro rectangles has a standard deviation bar 
        fat_error = self.browser.find_element_by_id(
                "goal-fat-error-bar")
        carbs_error = self.browser.find_element_by_id(
                "goal-carbs-error-bar")
        protein_error = self.browser.find_element_by_id(
                "goal-protein-error-bar")
        
        self.assertEqual(self.get_bar_ratio(
            fat_error.get_attribute("height"),
            cal_bar.get_attribute("height")),.10)
        self.assertEqual(self.get_bar_ratio(
            carbs_error.get_attribute("height"),
            cal_bar.get_attribute("height")),.10)
        self.assertEqual(self.get_bar_ratio(
            protein_error.get_attribute("height"),
            cal_bar.get_attribute("height")),.10)
        
        # To the right of that is a an input with the place holder 
        # "Search for ingredients" with a magnifying glass icon button
        self.check_element_content(
                "meal-maker-food-search-input","id","placeholder",
                "Search For Food")
        
        # All the above only takes up the top of the page, the bottom 
        # half contains a page wide div with the large text 
        # "Add Ingredients using Search"
        self.check_element_content(
                "meal-maker-ingredient-placeholder-text","id","text",
                "Add Ingredients Using Search")
        # Joe is going to attempt to make a salad that will fit his macro 
        # percentages. He starts by entering "600" into the 
        # "How Many Calories?" input box
        cals_input = ["input[id='goal-meal-cals']"]
        cals_input_value = ["600"]
        self.fill_input(cals_input,[],clear=True)	
        self.fill_input(cals_input,cals_input_value)	

        # He starts by typeing "garbonzo beans" in the search bar and 
        # clicks the search icon. And he sees the area below the search 
        # bar fill up with the top 10 results
        self.fill_input(["input[id='meal-maker-food-search-input']"],
                ["garbanzo beans"])	
        self.browser.find_element_by_id(
                "food-search-icon-button").click()
        search_results = self.browser.find_elements_by_class_name(
                "search-result")
        time.sleep(5)
        self.assertEqual(len(search_results),10)

        # Joe clicks on the first result ( on the add + icon )
        # and notices that in the lower left, a series of rectangles
        # appear with the 
        # result text as the header, and "0g" under the bars to the left.
        # The left-most rectangle has a small drag box at the bottom.
        time.sleep(5)
        search_results[0].find_elements_by_class_name("icon")[0].click()
        ing_1_svg = self.browser.find_element_by_id("ingredient-1-svg")
        cal_bar = goal_svg.find_element_by_id("ingredient-1-cals-bar")
        fat_bar = goal_svg.find_element_by_id("ingredient-1-fat-bar")
        carbs_bar = goal_svg.find_element_by_id("ingredient-1-carbs_bar")
        protein_bar = goal_svg.find_element_by_id("ingredient-1-protein-bar")
        self.fail("Finish The Test!")


        #He then searches for "carrots", clicks the "+" button on the first result
        #and notices again, that a series of rectanlges and labels (except title) 
        #like the previous result appear to the right of the previous search result

        #He then adds "bacon" and "lettuce" to the mix as well

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
        #doesn"t really like garbonzo beans, he decides he"s going to replace it.
        #Joe notices an "x" in the upper left of each food, he clicks on it and
        #garbonzo beans disappears 

        #He notices that all foods to the right of "garbonzo beans" slide to the left

        #He also notices that all the meal bars above "garbonzo beans" have slid down.

        #He also notices that the macro amounts have decreased correct amount.

        #He the adds kidney beans, adds 100 cals worth, and then removes bacon.
        #He notices again that all the foods right/above slide over/down, and 
        #and the macro amounts decrease the amount = to the food removed

        #Joe decides he wants a smaller salad, so he changes the cals from 600 to 300
        #and notices that all his macro amounts, and food amounts are cut in half.

        #He then adujst the remaining foods so that all the bars fall within the stdev
        #style bars and then hits the "Save Meal" button below.

        #A modal form pops up, with input box at the top with place holder "Meal Name"
        #Below that is a table summarizing the macros, their amounts, and precentages
        #Below that is bulleted list of the foods and their amounts.

        #Joe enters "Joe Salad" into the meal name input box

        #Below that is a comments box with the place holder "Recipie Notes", where 
        #Joe enters "this salad is best when the kidney beans are smashed a bit, 
        #and with pleny of pepper.

        #Below this is a "Submit" and "Cancel" button, Joe hits "Submit".

        #After he hits "Submit" and a confirmation dialog box replaces the submit and 
        #cancel buttons saying "Meal Saved! View and/or adjust on the My Recipes Tab. 
        #Joe hits the "OK" button and the modal box dissapears

        #He notices that the confirmation box dissapears, and that the Meal Maker tab
        #has returned to its initial state with no added foods.

        #Joe decides he want to make another salad, but one with different macro goals.
        #He hits the "Customize Macros".

        #A modal form pops up with all the macros listed and next to each, an input box
        #with a place holder of their current macros. 

        #He changes the percentages to fat/carbs/protein 50/25/25 and hits the "Apply" 
        #button and the modal disappears.

        #He notices the macros in the summary table have changed to reflect his changes
        #and the meal bars have also changed to reflect the changes.

        #He decides he want to change them again so he clicks the "Customize Macros"
        #button and then once the form comes up, he decides against it, and clicks the
        #"Cancel" button and the modal disappears and nothing has changed.

        #He then searches for and adds kale, cucumbers, ham, and peas. He then adusts
        #their drag bars to fit the target meal and he hits the "Save Meal" button.

        #When the modal comes up, he enters, once again "Joe Salad", enters no
        #Recipe Notes and hits "Submit".  After this, an alert message shows up,
        #above the Submit and Cancel buttons,
        #informing Joe that this Meal Name is already taken, and to enter a new one.

        #Joe enters "Green Salad", and saves the meal,
        #and closes the out after the confirmation message.

        #A week later Joe wants to make the Green salad so he goes to the "My Meals" tab

