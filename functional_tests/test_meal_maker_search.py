
import time
from builtins import Exception
from decimal import Decimal

from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.select import Select

from .base import FunctionalTest
from meals.models import Foods, FoodGroup, Servings, Ingredients

class ElementPresentException(Exception):

    def __init__(self, message):
        self.message = message

class MakeMacroMealTest(FunctionalTest):

    # fixtures = ["db.json"]

    def this_setup(self):

        veg_food_group = FoodGroup.objects.create(
            name='Vegatables',
            informal_name='Veggies',
            informal_rank=1
        )
        legume_food_group = FoodGroup.objects.create(
            name='Legumes',
            informal_name='Veggies',
            informal_rank=1
        )
        pork_food_group = FoodGroup.objects.create(
            name='Pork',
            informal_name='Meat',
            informal_rank=2
        )

        names = ['Chickpeas', 'Carrots', 'Bacon', 'Lettuce']
        cals = [1.3800, 0.3500, 4.6800, 0.1600]
        fat = [0.2223, 0.0117, 3.1581, 0.0198]
        carbs = [0.9148, 0.3296, 0.0680, 0.0904]
        protein = [0.2816, 0.0256, 1.3568, 0.0532]
        
        foods = []
        for i in range(len(names)):
            if names[i] == 'Chickpeas':
                fg = legume_food_group
            elif names[i] == 'Bacon':
                fg = pork_food_group
            else:
                fg = veg_food_group

            food = Foods.objects.create(
               name=names[i],
               cals_per_gram=cals[i],
               fat_per_gram=fat[i],
               carbs_per_gram=carbs[i],
               protein_per_gram=protein[i],
               food_group = fg
            )
            foods.append(food)

        Servings.objects.create(
            food=foods[2], grams=Decimal(11.5), quantity=Decimal(1), description='slice'
        )
        

    def test_make_macro_meal(self):

        self.this_setup()
        user = self.initialize_test(self.USERNAME, self.PASSWORD)
        # self.create_default_meal_templates(user)

        # Joe now wants to make a meal that helps him achieve his macros
        # so he clicks on the "Meal Maker" tab
        self.browser.find_element_by_id("meal-maker-tab").click()

        # To the right of that is a an input with the place holder
        # "Search for ingredients" with a magnifying glass icon button
        self.check_element_content(
            'meal-maker-food-search-input', 'id', 'placeholder',
            'Search For Food')

        # He sees that the search filter is pre-selected on 'No Filter'
        # But he knows he wants veggies so he select the Veggie option.
        no_filter =  self.browser.find_element_by_id(
            'meal-maker-filter-none'
        )
        veg_filter =  self.browser.find_element_by_id(
            'meal-maker-filter-veggies'
        )
        meat_filter =  self.browser.find_element_by_id(
            'meal-maker-filter-meat'
        )
        # No filter initally checked
        self.assertTrue(no_filter.get_attribute('checked'))

        # Food filters check unselect non filter
        veg_filter.click()
        meat_filter.click()
        self.assertTrue(veg_filter.get_attribute('checked'))
        self.assertTrue(meat_filter.get_attribute('checked'))
        self.assertFalse(no_filter.get_attribute('checked'))
        
        # No filter click clears the others
        no_filter.click()
        self.assertFalse(veg_filter.get_attribute('checked'))
        self.assertFalse(meat_filter.get_attribute('checked'))
        
        # No check boxes at all selects no filter box
        meat_filter.click()
        meat_filter.click()
        self.assertTrue(no_filter.get_attribute('checked'))

        # He starts by typeing "chickpeas carrots lettuce bacon" in
        # the search bar and 
        # clicks the search icon. And he sees the area below the search 
        # bar fill up with those food results
        search_results = self.search_and_results(
            "input[id='meal-maker-food-search-input']",
            'food-search-icon-button',
            'search-result',
            ['chickpeas carrots lettuce bacon']
        )

        self.assertEqual(len(search_results), 4)


        self.fill_input(
            ["input[id='meal-maker-food-search-input']"], [], clear=True
        )
        meat_filter.click()
        search_results = self.search_and_results(
            "input[id='meal-maker-food-search-input']",
            'food-search-icon-button',
            'search-result',
            ['chickpeas carrots lettuce bacon']
        )
        self.assertEqual(search_results[0].text, 'Bacon')
        self.assertEqual(len(search_results), 1)

        self.fail('Finish Test!')
