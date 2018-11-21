import time
from builtins import Exception
from decimal import Decimal

from .base import FunctionalTest
from meals.models import Foods, FoodGroup, Servings, Ingredients


class MakeMacroMealTest(FunctionalTest):


    def test_make_macro_meal(self):

        user = self.initialize_test(self.USERNAME, self.PASSWORD)

        # Joe now wants to make a meal that helps him achieve his macros
        # so he clicks on the "Meal Maker" tab
        self.browser.find_element_by_id("meal-maker-tab").click()

        # Joe however, did not set any macros in the my macros tab, but he can
        # still make a meal.
        #He notices an input to enter the desired calories.
        self.check_element_content(
            "label[for='goal-meal-cals-container']",
            'css', 'text', 'How Many Calories?'
        )
        self.check_element_content(
            'goal-meal-cals', 'id', 'placeholder', 'Cals'
        )

        #Below he sees a table like area for entering the percentages/grams for each macros
        macro_div = self.browser.find_element_by_id("goal-meal-macros-container")
        macro_spans = macro_div.find_elements_by_css_selector("label")
        self.assertEqual(macro_spans[0].text, 'Percent')
        self.assertEqual(macro_spans[1].text, 'Grams')
        self.assertEqual(macro_spans[2].text, 'Fat')
        self.assertEqual(macro_spans[3].text, 'Carbs')
        self.check_element_content(
            'goal-meal-fat-percent', 'id', 'placeholder', '%'
        )
        self.check_element_content(
            'goal-meal-fat-g', 'id', 'placeholder', 'g'
        )
        self.check_element_content(
            'goal-meal-carbs-percent', 'id', 'placeholder', '%')
        self.check_element_content(
            'goal-meal-carbs-g', 'id', 'placeholder', 'g')
        self.check_element_content(
            'goal-meal-protein-percent', 'id', 'placeholder', '%')
        self.check_element_content(
            'goal-meal-protein-g', 'id', 'placeholder', 'g')

        # Joe enters 500 cals and 34,33,33 % for Fat, Carbs and Protein
        # respectively and notices that the gram inputs fill in
        # with 19, 41, 41
        self.fill_input(
            [
                "input[id='goal-meal-fat-percent']",
                "input[id='goal-meal-carbs-percent']",
                "input[id='goal-meal-protein-percent']",
                "input[id='goal-meal-cals']"
            ],
            [34, 33, 33, 500]
        )
        self.check_element_content('goal-meal-fat-g', 'id', 'value', '19')
        self.check_element_content('goal-meal-carbs-g', 'id', 'value', '41')
        self.check_element_content('goal-meal-protein-g', 'id', 'value', '41')

        # Joe realizes he needs to know his TDEE so he does that and then
        # comes back where He Notices in the upper left of the tab a
        # healine showing his TDEE and text input with the label
        # "How Many Calories?", and the placeholder "cals" and under
        # that a dropdown with choices of Meal 1,2,3 602 and Meal 4 305.
        macro = self.create_default_macro(user)

        self.browser.find_element_by_id('meal-maker-tab').click()
        self.check_element_content('tdee', 'id', 'text', 'TDEE: 2166')
        self.check_element_content(
            "label[for='goal-meal-cals-container']", 'css', 'text',
            'How Many Calories?')
        self.check_element_content(
            'goal-meal-cals', 'id', 'placeholder', 'Cals')

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
        self.assertEqual(inputs[1].get_attribute("placeholder"),"g")
        self.assertEqual(inputs[2].get_attribute("value"),"33")
        self.assertEqual(inputs[3].get_attribute("placeholder"),"g")
        self.assertEqual(inputs[4].get_attribute("value"),"33")
        self.assertEqual(inputs[5].get_attribute("placeholder"),"g")

        #Joe selects 500 cals again and notices that a grams column
        #in the table below fills in.
        self.fill_input(["input[id='goal-meal-cals']"], [500])
        self.assertEqual(inputs[1].get_attribute('value'), '19')
        self.assertEqual(inputs[3].get_attribute('value'), '41')
        self.assertEqual(inputs[5].get_attribute('value'), '41')

        # Joe realized he wants to enter a value not on his saved
        # tab so he enters 500 into the text input and when he does
        # so he sees that the dropdown resets to the default position
        cals_input_id = ["input[id='goal-meal-cals']"]
        cals_input = ['338']
        self.fill_input(cals_input_id,[],clear=True)	
        self.fill_input(cals_input_id, cals_input)
        
        #He also notices that the grams values chanage as well
        self.assertEqual(inputs[1].get_attribute('value'), '13')
        self.assertEqual(inputs[3].get_attribute('value'), '28')
        self.assertEqual(inputs[5].get_attribute('value'), '28')

        #Joe realizes he actually does want to enter his saved amount
        # so he reslects the 338 cal option and noctices that the text 
        # input clears out. He also changes the Fat and Carbs percents
        # to 30 and 37 % respectively

        self.check_element_content("goal-meal-cals",'id',"text","")
        macro_input_ids = [
                "input[id='goal-meal-fat-percent']",
                "input[id='goal-meal-carbs-percent']"]
        self.fill_input(macro_input_ids,[],clear=True)	
        macro_inputs = ["30","37"]
        self.fill_input(macro_input_ids,macro_inputs)	
        self.assertEqual(inputs[1].get_attribute("value"),"11")
        self.assertEqual(inputs[3].get_attribute("value"),"31")
        self.assertEqual(inputs[5].get_attribute("value"),"28")
