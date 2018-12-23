import time
from .base import FunctionalTest
from decimal import Decimal
from selenium.webdriver.support.ui import Select

from meals.models import FoodGroup, FoodType
from meals.forms import NewFoodForm #for some reason, importing the form
    # gets its food_group attribute populated with all the existing FoodGroups
    # even though at the time of the test those groups don't exist

class AddFoodTest(FunctionalTest):

    def setUp(self):
        super().setUp()
        FoodType.objects.create(name='food')
        FoodGroup.objects.create(name='Snacks', informal_name='Snacks')

    def test_add_food(self):

        self.initialize_test(self.USERNAME, self.PASSWORD)

        # Joe has some potato chips that he would like to the DB
        # so he goes to the 'Add Food' tabe.
        self.browser.find_element_by_id("add-food-tab").click()

        # Once he arrives he sees a form with inputs for adding a new food
        name_label = self.browser.find_elements_by_css_selector(
            'label[for="add-food-name"]'
        )[0].text
        name_input = self.browser.find_element_by_id('add-food-name')
        self.assertEqual(name_label, 'Name:')
        name_input.send_keys('Potato Chips')

        serving_label = self.browser.find_elements_by_css_selector(
            'label[for="add-food-serving"]'
        )[0].text
        serving_input = self.browser.find_element_by_id(
            'add-food-serving'
        )
        self.assertEqual(serving_label, 'Serving:')
        serving_input.send_keys('100')

        cals_label = self.browser.find_elements_by_css_selector(
            'label[for="add-food-cals"]'
        )[0].text
        cals_input = self.browser.find_element_by_id('add-food-cals')
        self.assertEqual(cals_label, 'Cals:')
        cals_input.send_keys('536')

        fat_label = self.browser.find_elements_by_css_selector(
            'label[for="add-food-fat"]'
        )[0].text
        fat_input = self.browser.find_element_by_id('add-food-fat')
        self.assertEqual(fat_label, 'Fat:')
        fat_input.send_keys('35')

        carbs_label = self.browser.find_elements_by_css_selector(
            'label[for="add-food-carbs"]'
        )[0].text
        carbs_input = self.browser.find_element_by_id(
            'add-food-carbs'
        )
        self.assertEqual(carbs_label, 'Carbs:')
        carbs_input.send_keys('53')

        sugar_label = self.browser.find_elements_by_css_selector(
            'label[for="add-food-sugar"]'
        )[0].text
        sugar_input = self.browser.find_element_by_id(
            'add-food-sugar'
        )
        self.assertEqual(sugar_label, 'Sugar:')
        sugar_input.send_keys('0.2')

        protein_label = self.browser.find_elements_by_css_selector(
            'label[for="add-food-protein"]'
        )[0].text
        protein_input = self.browser.find_element_by_id(
            'add-food-protein'
        )
        self.assertEqual(protein_label, 'Protein:')
        protein_input.send_keys('7')

        food_group_label = self.browser.find_elements_by_css_selector(
            'label[for="add-food-food-group"]'
        )[0].text
        food_group_select = Select(self.browser.find_element_by_id(
            'add-food-food-group'
        ))
        self.assertEqual(food_group_label, 'Food Group:')
        food_group_select.select_by_visible_text('Snacks')

        save_button = self.browser.find_element_by_id('add-food-save')
        self.assertEqual(save_button.text, 'Save New Food')
        # Joe enters all the info in the form and clicks the 'Add Food to DB'
        # button after which he sees a 'New Food Successfully Added' message.

        save_button.click()

        status = self.browser.find_element_by_id('add-food-save-status')
        self.assertEqual(status.text, 'Food Saved!')
        time.sleep(4) # wait for status to dissapear
        self.assertEqual(status.text, '')

        # He notices the form has been cleared.

        # Joe wants to add another food, Hummus, to the DB, but being piss drunk
        # Joe forgets to add any of the info and just clicks save. He notices
        # that error messages pop up under all the form inputs.

        # Joe, still being smashed, proceeds to fill in the form, but has text
        # mixed in with all the number fields. He hits the save button again
        # and now sees different error messages just under the numeric fields
