import time
from .base import FunctionalTest
# from meals.models import Foods, FoodGroup, Servings, Ingredients


class AddIngredientRecipeTest(FunctionalTest):

    def test_add_ingredient_recipe(self):

        self.initialize_test(self.USERNAME, self.PASSWORD)

        # User wants to look up his saved meals because he wants something
        # to eat so hi clicks on the 'Add New Foods/Recipes tab after which
        # he sees an input bar followed by and search icon and  label above
        # reading 'Add New Ingredient'
        self.browser.find_element_by_id("add-new-tab").click()
        self.check_element_content(
            'add-new-headline', 'id', 'text',
            'Add New Ingredients/Recipes')

        self.check_element_content(
            'label[for="add-new-search-1"]', 'css', 'text',
            'Search for Ingredient')

        self.check_element_content(
            'label[for="add-new-search-1"]', 'css', 'text',
            'Search for Ingredient')

        # User wants to make an cheddar omlette so he enters first
        # enters eggs then clicks the search icon.
        self.browser.find_elements_by_class_name('search-button')[0].click()
        self.fail('Finish Test')

