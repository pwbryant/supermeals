import time
from decimal import Decimal
from datetime import datetime, timedelta

from .base import FunctionalTest
from meals.models import Foods, Servings, Ingredients



class MyMealTests(FunctionalTest):


    def create_meals(self, user):

        first_date = datetime.now()
        self.ham_sandwich = Foods.objects.create(
            name='Ham Sandwich', date=first_date, user=user
        )

        second_date = first_date + timedelta(days=1)
        self.pretzels_cheese = Foods.objects.create(
            name='Pretzels and Cheese', date=second_date, user=user
        )

        self.pretzels = Foods.objects.create(
            name='pretzels'
        )

        self.pretzels_srv = Servings.objects.create(
            food=self.pretzels,
            grams=100,
            quantity=1,
            description='bag'
        )

        self.cheese = Foods.objects.create(
            name='cheese'
        )

        self.cheese_srv = Servings.objects.create(
            food=self.cheese,
            grams=10,
            quantity=2,
            description='slice'
        )

        self.pretzels_ing = Ingredients.objects.create(
                main_food=self.pretzels_cheese,
                ingredient=self.pretzels,
                serving=self.pretzels_srv,
                amount=3.5
        )

        self.cheese_ing = Ingredients.objects.create(
                main_food=self.pretzels_cheese,
                ingredient=self.cheese,
                serving=self.cheese_srv,
                amount=2
        )

        self.pretzels_cheese_no_user = Foods.objects.create(
            name='Pretzels and Cheese no user', date=second_date
        )


    def test_my_meals(self):

        user = self.initialize_test(self.USERNAME, self.PASSWORD)
        self.create_meals(user)

        # Joe wants to lookup a snack he made yesterday so he
        # clicks on the 'My Meals' tab
        self.browser.find_element_by_id('my-meals-tab').click()

        # The first thing he sees is a side bar with two radio buttons
        # 'Recent' and 'Popular', with the 'Recent' option checked

        self.check_element_content(
            'label[for="recent"]', 'css', 'text', 'Recent'
        )
        recent_radio = self.browser.find_element_by_id('recent')
        self.assertTrue(recent_radio.is_selected())

        self.check_element_content(
            'label[for="popular"]', 'css', 'text', 'Popular'
        )
        popular_radio = self.browser.find_element_by_id('popular')
        self.assertFalse(popular_radio.is_selected())

        # Below these radio buttons he sees a list of his three meals
        # ordered by most to least recent
        recent_meals = self.browser.find_elements_by_class_name('my-meals-easy-picks-meal')
        most_recent_meal = recent_meals[0]
        self.assertEqual(most_recent_meal.text, self.pretzels_cheese.name)


        # The second thing he sees is a search bar and he searches
        # for a meal he made.
        self.check_element_content(
            'my-meals-search-input', 'id', 'placeholder', 'Search My Meals'
        )

        search_results = self.search_and_results(
            "input[id='my-meals-search-input']",
            'my-meals-search-button',
            'search-result',
            ['pretzels cheese']
        )

        # He sees that only his saved meals/recipies show up
        # and that all search results contain at least one
        # of his search terms.
        # time.sleep(10)
        self.assertEqual(search_results[0].text, self.pretzels_cheese.name)
        self.assertEqual(len([
            r for r in search_results
            if 'pretzel' in r.text.lower()
            or 'cheese' in r.text.lower()
        ]), 1) # should be one because one 'Pretzel and Cheese' has no user
            
        
        # He wants to remember the amounts in his saved meal, so he
        # clicks on the plus icon, and a modal appears listing the meal info

        self.browser.find_element_by_id(
                f'my-meal-result-{self.pretzels_cheese.id}'
        ).click()
        self.check_element_content(
            'my-meals-modal-header', 'id', 'text', self.pretzels_cheese.name
        )

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

        self.fail('Finish Test!')

