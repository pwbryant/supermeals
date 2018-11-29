import time
from .base import FunctionalTest

from meals.models import Foods, Servings, Ingredients, FoodNotes, FoodGroup


class AddIngredientRecipeTest(FunctionalTest):

    def this_setup(self):

        self.meat_food_group = FoodGroup.objects.create(
            name='Meat', informal_name='Meat'
        )

        self.veg_food_group = FoodGroup.objects.create(
            name='Vegatables', informal_name='Veggies'
        )
            
        self.filters = [
            self.meat_food_group.informal_name, 
            self.veg_food_group.informal_name
        ]
        

    def test_add_ingredient_recipe(self):

        self.initialize_test(self.USERNAME, self.PASSWORD)
        self.this_setup()

        # User wants to look up his saved meals because he wants something
        # to eat so hi clicks on the 'Add New Foods/Recipes tab after which
        # he sees a side bar with all the search filters, the 'No Filter'
        # checkbox already being selected
        self.browser.find_element_by_id("add-recipe-tab").click()
        self.check_element_content(
            'label[for="add-recipe-filters"]', 'css', 'text',
            'Search Filters')

        filters = [
            e.get_attribute('value') for e in
            self.browser.find_elements_by_class_name('filter')
        ]
        filters.sort()
        self.assertEqual(filters, self.filters)

        self.fail('Finish Test')
