import time
from decimal import Decimal

from .base import FunctionalTest
from meals.models import Foods, Servings, Ingredients


class MyMealTests(FunctionalTest):

    def test_my_meals(self):
        
        user = self.initialize_test(self.USERNAME, self.PASSWORD)

        # Joe wants to lookup a snack he made yesterday so he
        # clicks on the 'My Meals' tab
        self.browser.find_element_by_id('my-meals-tab').click()

        # The first thing he sees is a search bar
        self.check_element_content(
            'my-meals-search', 'id', 'placeholder', 'Search My Meals'
        )

        # Under the search bar he sees a list of his meals, which appear to
        # be ordered by the date he created them
        self.fail('Finish Test!')

