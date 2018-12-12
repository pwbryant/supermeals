import time
from .base import FunctionalTest
from decimal import Decimal
from selenium.webdriver.support.ui import Select

from meals.models import Foods, Servings, Ingredients, FoodNotes, FoodGroup, \
        FoodType


class AddIngredientRecipeTest(FunctionalTest):

    def this_setup(self):


        #create FoodGroups
        self.my_meals_food_group = FoodGroup.objects.create(
            name='My Meals', informal_name='My Meals', informal_rank=1
        )

        self.my_recipe_food_group = FoodGroup.objects.create(
            name='My Recipes', informal_name='My Recipes', informal_rank=2
        )
        self.veg_food_group = FoodGroup.objects.create(
            name='Vegatables', informal_name='Veggies', informal_rank=3
        )

        self.meat_food_group = FoodGroup.objects.create(
            name='Meat', informal_name='Meat', informal_rank=4
        )

        # create recipe FoodType
        self.my_recipe_food_type = FoodType.objects.create(name='recipe')
            
        self.filters = [
            self.my_meals_food_group.informal_name, 
            self.my_recipe_food_group.informal_name, 
            self.veg_food_group.informal_name,
            self.meat_food_group.informal_name
        ]

        # all macro info just copied from one food 
        self.ice_cream = Foods.objects.create(
            name='ice cream', food_group=self.my_meals_food_group,
            cals_per_gram=Decimal(5.9),
            fat_per_gram=Decimal(4.491),
            carbs_per_gram=Decimal(0.8732),
            protein_per_gram=Decimal(0.96)
        )

        self.carrots = Foods.objects.create(
            name='carrots', food_group=self.veg_food_group,
            cals_per_gram=Decimal(5.9),
            fat_per_gram=Decimal(4.491),
            carbs_per_gram=Decimal(0.8732),
            protein_per_gram=Decimal(0.96)
        )

        self.chicken = Foods.objects.create(
            name='chicken', food_group=self.meat_food_group,
            cals_per_gram=Decimal(5.9),
            fat_per_gram=Decimal(4.491),
            carbs_per_gram=Decimal(0.8732),
            protein_per_gram=Decimal(0.96)
        )
        
        # Servings (grams already created in base.py)
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
           f'add-recipe-ingredient-result-{self.carrots.id}'
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
           f'add-recipe-ingredient-result-{self.chicken.id}'
        ).click()
        self.browser.find_element_by_id(
           f'add-recipe-ingredient-result-{self.ice_cream.id}'
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
        
        # Joe then sees that there is a save button below the
        # ingredients so he hits is but gets an error message below
        # the ingredient input that he needs to fill in the recipe name
        save_button = self.browser.find_element_by_id(
            'add-recipe-save-button'
        )
        save_button.click()

        self.check_element_content(
            'add-recipe-name-errors',
            'id', 'text', 'Enter recipe name'
        )
        recipe_name_input = self.browser.find_element_by_id(
            'add-recipe-recipe-name'
        )
        recipe_name_input.send_keys('Carrot Chicken Slurry')


        # Joe accidentally deletes one ingredient ingredients and clicks 
        # the save button again and he gets an alert message
        # saying recipes need more than one ingredient. He alos notics
        # the name error has disappeared
        self.browser.find_element_by_id(
           f'add-recipe-ingredient-exit-{self.carrots.id}'
        ).click()

        save_button.click()

        self.check_element_content(
            'add-recipe-ingredients-container-errors',
            'id', 'text', 'Recipes require more than one ingredient'
        )
        self.check_element_content(
            'add-recipe-name-errors',
            'id', 'text', ''
        )
        # He then adds them back
        self.browser.find_element_by_id(
           f'add-recipe-ingredient-result-{self.carrots.id}'
        ).click()

        carrot_amt_input = self.browser.find_element_by_id(
            f'add-recipe-ingredient-amt-{self.carrots.id}'
        )

        carrot_amt_input.send_keys('100')
        chicken_amt_input.send_keys('2')
        chicken_units.select_by_visible_text('breast')

        # Joe wants to remind himself how to prep this recipe later
        # so he adds some notes in the Notes area
        notes = self.browser.find_element_by_id('add-recipe-notes')
        notes.send_keys('Bake in oven at 100 F for 2000 hours')


        # Joe clicks the save button and he sees the ingredient
        # recipe dissapear and a success confirmation
        # alert message appear that disappears afte 2 seconds.
        save_button.click()

        self.check_element_content(
            'add-recipe-ingredients-container-errors',
            'id', 'text', ''
        )

        self.check_element_content(
            'add-recipe-save-status',
            'id', 'text', 'Recipe Saved'
        )
        
        # He also notices all all inputs have been cleared from the page
        search_results = self.browser.find_elements_by_class_name(
            'add-recipe-search-results'
        )
        self.assertEqual(len(search_results), 0)

        ingredients = self.browser.find_elements_by_class_name(
            'add-recipe-ingredient'
        )
        self.assertEqual(len(ingredients), 0)

        search_input = self.browser.find_element_by_id(
            'add-recipe-search'
        ).get_attribute('value')
        self.assertEqual(search_input, '')

        recipe_name = self.browser.find_element_by_id(
            'add-recipe-recipe-name'
        ).get_attribute('value')
        self.assertEqual(recipe_name, '')

        recipe_notes = self.browser.find_element_by_id(
            'add-recipe-notes'
        ).get_attribute('value')
        self.assertEqual(recipe_notes, '')
