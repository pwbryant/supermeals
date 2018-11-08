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


        # He checks the 'Popular' button and notices that the meals
        # are ordered my popularity (how often he selects them)
        popular_meals = self.browser.find_elements_by_class_name('my-meals-easy-pick-meal')
        most_popular_meal = popular_meals[0]
        self.assertEqual(most_popular_meal.text, 'Ham Sandwich')

        # The second thing he sees is a search bar
        self.check_element_content(
            'my-meals-search', 'id', 'placeholder', 'Search My Meals'
        )

        # Under the search bar he sees a list of his meals, which appear to
        # be ordered by the date he created them
        self.fail('Finish Test!')

