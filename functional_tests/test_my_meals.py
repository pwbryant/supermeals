import time
from decimal import Decimal
from datetime import datetime, timedelta

from .base import FunctionalTest
from meals.models import Foods, Servings, Ingredients


class MyMealTests(FunctionalTest):


    def create_meals(self, user):
        first_date = datetime.now()
        second_date = first_date + timedelta(days=1)
        Foods.objects.create(
            name='Ham Sandwich', date=first_date, user=user
        )
        Foods.objects.create(
            name='Pretzels and Cheese', date=second_date, user=user
        )
        Foods.objects.create(
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
        self.assertEqual(most_recent_meal.text, 'Pretzels and Cheese')


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

        self.assertEqual(search_results[0].text, 'Pretzels and Cheese')
        self.assertEqual(len([
            r for r in search_results
            if 'pretzel' in r.text.lower()
            or 'cheese' in r.text.lower()
        ]), 1) # should be one because one 'Pretzel and Cheese' has no user
            
        # He sees that only his saved meals/recipies show up
        # and that all search results contain at least one
        # of his search terms.
        

        self.fail('Finish Test!')

