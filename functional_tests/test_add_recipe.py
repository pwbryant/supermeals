import time
from .base import FunctionalTest
from decimal import Decimal
from selenium.webdriver.support.ui import Select

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

        ingredient_name = self.browser.find_element_by_id(
            f'add-recipe-ingredient-name-{self.carrots.id}'
        ).text

        self.assertEqual(ingredient_name, 'carrots')

        carrot_amt_label = self.browser.find_elements_by_css_selector(
            f'label[for="add-recipe-ingredient-amt-{self.carrots.id}"]'
        )[0].text
        carrot_amt_input = self.browser.find_element_by_id(
            f'add-recipe-ingredient-amt-{self.carrots.id}'
        )
        carrot_units_label = self.browser.find_elements_by_css_selector(
            f'label[for="add-recipe-ingredient-units-{self.carrots.id}"]'
        )[0].text
        carrot_units = Select(self.browser.find_element_by_id(
            f'add-recipe-ingredient-units-{self.carrots.id}'
        ))

        self.assertEqual(carrot_amt_label, 'Amount')
        self.assertEqual(carrot_units_label, 'Units')


        # Joe wants 100g of carrots so he enters 100 into the amount input
        carrot_amt_input.send_keys('100')

        # He then adds the chicken and ice cream
        self.browser.find_element_by_id(
           f'add-recipe-search-result-food-{self.chicken.id}'
        ).click()
        self.browser.find_element_by_id(
           f'add-recipe-search-result-food-{self.ice_cream.id}'
        ).click()

        # Joe decides he does'nt want the ice cream so he clicks on 
        # the x box in the upper right corner and sees the ingredient
        # disappear
        self.browser.find_element_by_id(
           f'add-recipe-ingredient-exit-{self.ice_cream.id}'
        ).click()
        self.assertEqual(
            len(self.browser.find_elements_by_css_selector(
                f'div[id="add-recipe-ingredient-{self.ice_cream.id}-container"]'
            )),0
        )

        # He selects 2 chicken breasts
        chicken_amt_input = self.browser.find_element_by_id(
            f'add-recipe-ingredient-amt-{self.chicken.id}'
        )
        chicken_units = Select(self.browser.find_element_by_id(
            f'add-recipe-ingredient-units-{self.chicken.id}'
        ))

        chicken_amt_input.send_keys('2')
        chicken_units.select_by_visible_text('breast')
        
        self.fail('Finish Test')
        # Joe then sees that there is a grayed out save button below the
        # ingredients, but once he enters the recipe name and description
        # the save button becomes activated.


        # Joe clicks the save button and he sees a success confirmation
        # alert message appear that disappears afte 2 seconds.

        # He also notices all all inputs have been cleared from the page



