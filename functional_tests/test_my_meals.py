import time
from decimal import Decimal
from datetime import datetime, timedelta

from .base import FunctionalTest
from meals.models import Foods, Servings, Ingredients, FoodNotes, FoodType, \
    FoodGroup

from selenium.webdriver.support.select import Select



class MyMealTests(FunctionalTest):


    def create_recipes(self, user):

        recipe_group = FoodGroup.objects.create(
            name='My Recipes'
        )

        if not Foods.objects.filter(name='Ham Sandwich'):
            self.create_meals(user)

        ham_sandwich = Foods.objects.get(name='Ham Sandwich')
        pretzels_cheese = Foods.objects.get(name='Pretzels and Cheese')

        ham_sandwich.name = 'Roasted Broccoli'
        pretzels_cheese.name = 'Denver Omlette'

        ham_sandwich.food_group = recipe_group
        pretzels_cheese.food_group = recipe_group

        tmp_date = ham_sandwich.date
        ham_sandwich.date = pretzels_cheese.date
        pretzels_cheese.date = tmp_date

        self.roasted_broccoli = ham_sandwich
        self.roasted_broccoli.save()

        self.omlette = pretzels_cheese
        self.omlette.save()


    def create_meals(self, user):

        meal_group = FoodGroup.objects.create(
            name='My Meals'
        )
        first_date = datetime.now()
        self.ham_sandwich = Foods.objects.create(
            name='Ham Sandwich', date=first_date, user=user,
            food_group=meal_group
        )

        second_date = first_date + timedelta(days=1)
        self.pretzels_cheese = Foods.objects.create(
            name='Pretzels and Cheese', date=second_date, user=user,
            food_group=meal_group
        )

        self.pretzels = Foods.objects.create(
            name='pretzels',
            cals_per_gram = Decimal(1.04),
            fat_per_gram = Decimal(0.31),
            carbs_per_gram = Decimal(0.54),
            sugar_per_gram = Decimal(0.54),
            protein_per_gram = Decimal(0.16),
        )

        self.pretzels_srv = Servings.objects.create(
            food=self.pretzels,
            grams=Decimal(100),
            quantity=Decimal(1),
            description='bag'
        )

        self.cheese = Foods.objects.create(
            name='cheese',
            cals_per_gram = Decimal(1.04),
            fat_per_gram = Decimal(0.31),
            carbs_per_gram = Decimal(0.54),
            sugar_per_gram = Decimal(0.54),
            protein_per_gram = Decimal(0.16),
        )

        self.cheese_srv = Servings.objects.create(
            food=self.cheese,
            grams=Decimal(10),
            quantity=Decimal(2),
            description='slice'
        )

        self.pretzels_ing = Ingredients.objects.create(
            main_food=self.pretzels_cheese,
            ingredient=self.pretzels,
            serving=self.pretzels_srv,
            amount=Decimal(3.5)
        )

        self.cheese_ing = Ingredients.objects.create(
            main_food=self.pretzels_cheese,
            ingredient=self.cheese,
            serving=self.cheese_srv,
            amount=Decimal(2)
        )
        # Copy for Ham Sandwich, becuase it needs its macros
        Ingredients.objects.create(
            main_food=self.ham_sandwich,
            ingredient=self.pretzels,
            serving=self.pretzels_srv,
            amount=Decimal(3.5)
        )

        Ingredients.objects.create(
            main_food=self.ham_sandwich,
            ingredient=self.cheese,
            serving=self.cheese_srv,
            amount=Decimal(2)
        )

        self.pretzels_cheese_notes = FoodNotes.objects.create(
            notes='Serve piping hot!', food=self.pretzels_cheese
        )

        self.pretzels_cheese_no_user = Foods.objects.create(
            name='Pretzels and Cheese no user', date=second_date
        )

        self.pretzels_cheese.set_macros_per_gram()
        self.pretzels_cheese.save()

        self.ham_sandwich.set_macros_per_gram()
        self.ham_sandwich.save()
        

    def make_macro_profile_str(self, food):

        macro_profile = food.get_macros_profile()

        summary_str = (
            'Percentages may not add up to 100 due to rounding\n'
            f'Cals: ~{round(macro_profile["cals"])}'
        )

        for macro in ['fat', 'carbs', 'protein']:
            summary_str += (
                f' {macro}: ~{round(macro_profile[macro])}g'
                f' (%{round(macro_profile[macro + "_pct"])})'
            )

        return summary_str


    def test_delete_meal(self):

        user = self.initialize_test(self.USERNAME, self.PASSWORD)
        self.create_meals(user)

        # Joe wants to lookup a snack he made yesterday so he
        # clicks on the 'My Meals' tab and select the pretzel and cheese meal
        self.browser.find_element_by_id('my-meals-tab').click()

        delete_meal = self.browser.find_element_by_id(
            f'my-meals-easy-picks-meal-{self.pretzels_cheese.id}'
        )
        delete_meal.click()

        # He sees that on the bottom right of the meal modal a delete button
        # which he clicks.
        delete_button = self.browser.find_element_by_id('my-meals-delete')
        self.assertEqual(delete_button.text, 'Delete This')
        delete_button.click()

        # He sees a dialog pop up asking if he is sure he wants to delete the meal
        # and he clicks 'Ok'
        ok_button = self.browser.find_element_by_id('my-meals-ok-delete')
        ok_button.click()

        # He sees a confirmation message display for 2 seconds
        confirmation = self.browser.find_element_by_id(
            'my-meals-delete-confirmation'
        )
        self.assertEqual(confirmation.text, 'Deletion Complete')
        time.sleep(2)
        ok_button = self.browser.find_element_by_id('my-meals-ok-delete')
        delete_button = self.browser.find_element_by_id('my-meals-delete')
        self.assertFalse(ok_button.is_displayed())
        self.assertFalse(delete_button.is_displayed())

        # He notices that the pretzel cheese meal is missing from the easy pick 
        # area
        search_results = self.browser.find_elements_by_class_name('search-result')
        self.assertEqual(len(search_results), 1)

        
    def test_not_delete_meal(self):

        user = self.initialize_test(self.USERNAME, self.PASSWORD)
        self.create_meals(user)

        # Joe wants to lookup a snack he made yesterday so he
        # clicks on the 'My Meals' tab and select the pretzel and cheese meal
        self.browser.find_element_by_id('my-meals-tab').click()

        self.browser.find_element_by_id(
                f'my-meals-easy-picks-meal-{self.pretzels_cheese.id}'
        ).click()

        # He sees that on the bottom right of the meal modal a delete button
        # which he clicks.
        delete_button = self.browser.find_element_by_id('my-meals-delete')
        delete_button.click()

        # He sees a dialog pop up asking if he is sure he wants to delete the meal
        # and he clicks 'no'
        cancel_button = self.browser.find_element_by_id('my-meals-cancel-delete')
        cancel_button.click()

        # He sees the dialog dissappear with the meal modal remaining in place
        self.assertFalse(cancel_button.is_displayed())
        self.assertTrue(delete_button.is_displayed())


    def test_my_meals(self):

        user = self.initialize_test(self.USERNAME, self.PASSWORD)
        self.create_meals(user)

        # Joe wants to lookup a snack he made yesterday so he
        # clicks on the 'My Meals' tab
        self.browser.find_element_by_id('my-meals-tab').click()

        # The first thing he sees is a side bar with 
        # a drop down contianining 'My Meals' and 'My Recipes' with
        # 'My Recipes' preselected and 

        select = Select(self.browser.find_element_by_id('my-meals-select'))
        selected_option = select.first_selected_option
        self.assertEqual(selected_option.text, 'My Meals')

        # Below these radio buttons he sees a list of his three meals
        # ordered by most to least recent
        select.select_by_visible_text('My Meals')
        recent_meals = self.browser.find_elements_by_class_name('easy-picks-meal')

        most_recent_meal = recent_meals[0]
        self.assertEqual(most_recent_meal.text, self.pretzels_cheese.name)

        # He is intersted in the most recent meal so he clicks on its plus icon
        self.browser.find_element_by_id(
                f'my-meals-easy-picks-meal-{self.pretzels_cheese.id}'
        ).click()

        # He sees a headr
        self.check_element_content(
            'my-meals-modal-header', 'id', 'text', self.pretzels_cheese.name
        )
        
        # a macro breakdown
        self.check_element_content(
            'my-meals-modal-sub-header', 'id', 'text',
            self.make_macro_profile_str(self.pretzels_cheese)
        )

        # a list of ingredients
        ingredients = self.browser.find_elements_by_css_selector(
                'div[class="my-meals-ingredient"]'
        )
        self.assertEqual(len(ingredients), 2)
        pretzels_str = (
                f'{self.pretzels.name}: {self.pretzels_ing.amount}'
                f' {self.pretzels_srv.description}'
        )
        cheese_str = (
                f'{self.cheese.name}: {self.cheese_ing.amount}'
                f' {self.cheese_srv.description}'
        )
        self.assertEqual(ingredients[0].text, pretzels_str)
        self.assertEqual(ingredients[1].text, cheese_str)

        self.browser.find_elements_by_class_name('close-modal')[0].click()
        # The second thing he sees is a search bar and he searches
        # for a meal he made.
        self.check_element_content(
            'my-meals-search', 'id', 'placeholder', 'Search My Meals'
        )

        search_results = self.search_and_results(
            "input[id='my-meals-search']",
            'my-meals-search-button',
            'my-meals-meal',
            ['pretzels cheese']
        )

        # He sees that only his saved meals/recipies show up
        # and that all search results contain at least one
        # of his search terms.
        self.assertEqual(search_results[0].text, self.pretzels_cheese.name)
        self.assertEqual(len([
            r for r in search_results
            if 'pretzel' in r.text.lower()
            or 'cheese' in r.text.lower()
        ]), 1) # should be one because one 'Pretzel and Cheese' has no user
            
        
        # He wants to remember the amounts in his saved meal, so he
        # clicks on the plus icon, and a modal appears listing the meal info

        self.browser.find_element_by_id(
                f'my-meals-my-meals-meal-{self.pretzels_cheese.id}'
        ).click()

        # He sees a headr
        self.check_element_content(
            'my-meals-modal-header', 'id', 'text', self.pretzels_cheese.name
        )
        
        # a macro breakdown
        self.check_element_content(
            'my-meals-modal-sub-header', 'id', 'text',
            self.make_macro_profile_str(self.pretzels_cheese)
        )

        # a list of ingredients
        ingredients = self.browser.find_elements_by_css_selector(
                'div[class="my-meals-ingredient"]'
        )
        self.assertEqual(len(ingredients), 2)
        pretzels_str = (
                f'{self.pretzels.name}: {self.pretzels_ing.amount}'
                f' {self.pretzels_srv.description}'
        )
        cheese_str = (
                f'{self.cheese.name}: {self.cheese_ing.amount}'
                f' {self.cheese_srv.description}'
        )
        self.assertEqual(ingredients[0].text, pretzels_str)
        self.assertEqual(ingredients[1].text, cheese_str)

        # and some notes
        self.check_element_content(
            'my-meals-modal-notes-header', 'id', 'text', 'Notes:'
        )
        self.check_element_content(
           'my-meals-modal-notes-body', 'id', 'text',
            self.pretzels_cheese_notes.notes
        )

        # Joe wants to investigate a recipe of his so he closes the modal
        # and selects 'My Recipes'
        self.create_recipes(user) #changes meal objects to recipe

        self.browser.find_elements_by_class_name('close-modal')[0].click()
        select.select_by_visible_text('My Recipes')
        selected_option = select.first_selected_option
        self.assertEqual(selected_option.text, 'My Recipes')

        # He notices that the easy pick area has been repopulated with recipes
        # rather than meals.
        recent_meals = self.browser.find_elements_by_class_name('easy-picks-meal')
        most_recent_meal = recent_meals[0]
        self.assertEqual(most_recent_meal.text, self.roasted_broccoli.name)


        # He searches for the denver omlette and clicks on the result and
        # sees a modal pop up with Denver omlette info
        self.browser.find_element_by_id('my-meals-search').clear();
        search_results = self.search_and_results(
            "input[id='my-meals-search']",
            'my-meals-search-button',
            'my-meals-meal',
            ['denver omlette']
        )

        self.browser.find_element_by_id(
                f'my-meals-my-meals-meal-{self.omlette.id}'
        ).click()

        # He sees a headr
        self.check_element_content(
            'my-meals-modal-header', 'id', 'text', self.omlette.name
        )
        # a macro breakdown
        self.check_element_content(
            'my-meals-modal-sub-header', 'id', 'text',
            self.make_macro_profile_str(self.omlette)
        )
