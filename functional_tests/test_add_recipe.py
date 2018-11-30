import time
from .base import FunctionalTest
from decimal import Decimal

from meals.models import Foods, Servings, Ingredients, FoodNotes, FoodGroup


class AddIngredientRecipeTest(FunctionalTest):

    def this_setup(self):


        self.my_meals_food_group = FoodGroup.objects.create(
            name='My Meals', informal_name='My Meals', informal_rank=1
        )

        self.veg_food_group = FoodGroup.objects.create(
            name='Vegatables', informal_name='Veggies', informal_rank=2
        )

        self.meat_food_group = FoodGroup.objects.create(
            name='Meat', informal_name='Meat', informal_rank=3
        )
            
        self.filters = [
            self.my_meals_food_group.informal_name, 
            self.veg_food_group.informal_name,
            self.meat_food_group.informal_name
        ]

        self.ice_cream = Foods.objects.create(
            name='ice cream', food_group=self.my_meals_food_group
        )

        self.carrots = Foods.objects.create(
            name='carrots', food_group=self.veg_food_group
        )

        self.chicken = Foods.objects.create(
            name='chicken', food_group=self.meat_food_group
        )

        
        # Servings
        self.srv_gram = Servings.objects.create(
            grams=Decimal(1),
            quantity=Decimal(1), description='g'
        )
        self.scoop = Servings.objects.create(
            food=self.ice_cream, grams=Decimal(10),
            quantity=Decimal(1), description='scoop'
        )
        self.stick = Servings.objects.create(
            food=self.carrots, grams=Decimal(5),
            quantity=Decimal(1), description='stick'
        )
        self.breast = Servings.objects.create(
            food=self.chicken, grams=Decimal(20),
            quantity=Decimal(1), description='breast'
        )


    def test_add_ingredient_recipe(self):

        self.initialize_test(self.USERNAME, self.PASSWORD)
        self.this_setup()

        # Joe wants to look up his saved meals because he wants something
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
        self.assertEqual(filters, self.filters)
        
        no_filter = self.browser.find_element_by_id('add-recipe-filter-none')

        self.assertTrue(no_filter.get_attribute('checked'))

        # Joe wants to add a recipe he saw in the New York Times: 
        # carrot and chicken ice cream so he searched for those foods
        # and sees all the ingredients showup
        search_terms = ['carrots chicken ice cream']
        search_results = self.setup_and_run_search(
            search_terms, [no_filter], 'add-recipe'
        )
        self.assertEqual(len(search_results), 3)

        # He clicks on the add button of the carrot result, and he
        # sees the food show up on the right side of the page,
        # accompanied by an input for the amount followed by a dropdown
        # with units.
        self.browser.find_element_by_id(
           f'add-recipe-search-result-food-{self.carrots.id}'
        ).click()

        added_food_name = self.browser.find_element_by_id(
            f'add-recipe-ingredient-{self.carrots.id}'
        ).text

        self.assertEqual(added_food_name, 'carrots')

        self.fail('Finish Test')
