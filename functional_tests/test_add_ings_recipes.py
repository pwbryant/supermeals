import time
from .base import FunctionalTest
# from meals.models import Foods, FoodGroup, Servings, Ingredients


class AddIngredientRecipeTest(FunctionalTest):

    def test_add_ingredient_recipe(self):

        self.initialize_test(self.USERNAME, self.PASSWORD)

        self.browser.find_element_by_id("add-new-tab").click()

        self.check_element_content(
            'add-new-headline', 'id', 'text',
            'Add New Ingredient/Recipe')

        self.fail('Finish Test')

