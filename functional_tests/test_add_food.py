import time
from .base import FunctionalTest
from decimal import Decimal
from selenium.webdriver.support.ui import Select


class AddFoodTest(FunctionalTest):

    def test_add_food(self):

        self.initialize_test(self.USERNAME, self.PASSWORD)

        # Joe has some potato chips that he would like to the DB
        # so he goes to the 'Add Food' tabe.
        self.browser.find_elements_by_css_selector("add-food-tab").click()

        # Once he arrives he sees a form with inputs for adding a new food
        name_label = self.browser.find_element_css_selector(
            'label[for="add-food-name"]'
        )
        name_input = self.browser.find_elements_by_css_selector('add-food-name')

        serving_label = self.browser.find_element_css_selector(
            'label[for="add-food-serving"]'
        )
        serving_input = self.browser.find_elements_by_css_selector(
            'add-food-serving'
        )

        cals_label = self.browser.find_element_css_selector(
            'label[for="add-food-cals"]'
        )
        cals_input = self.browser.find_elements_by_css_selector('add-food-cals')

        fat_label = self.browser.find_element_css_selector(
            'label[for="add-food-fat"]'
        )
        fat_input = self.browser.find_elements_by_css_selector('add-food-fat')

        carbs_label = self.browser.find_element_css_selector(
            'label[for="add-food-carbs"]'
        )
        carbs_input = self.browser.find_elements_by_css_selector(
            'add-food-carbs'
        )

        sugar_label = self.browser.find_element_css_selector(
            'label[for="add-food-sugar"]'
        )
        sugar_input = self.browser.find_elements_by_css_selector(
            'add-food-sugar'
        )

        protein_label = self.browser.find_element_css_selector(
            'label[for="add-food-protein"]'
        )
        protein_input = self.browser.find_elements_by_css_selector(
            'add-food-protein'
        )

        save_button = self.browser.find_elements_by_css_selector('add-food-save')
        # Joe enters all the info in the form and clicks the 'Add Food to DB'
        # button after which he sees a 'New Food Successfully Added' message.
        save_button.click()

        self.fail('Finish Test')

        # He notices the form has been cleared.

        # Joe wants to add another food, Hummus, to the DB, but being piss drunk
        # Joe forgets to add any of the info and just clicks save. He notices
        # that error messages pop up under all the form inputs.

        # Joe, still being smashed, proceeds to fill in the form, but has text
        # mixed in with all the number fields. He hits the save button again
        # and now sees different error messages just under the numeric fields





