import time
from .base import FunctionalTest
from decimal import Decimal
from selenium.webdriver.support.ui import Select

class GuestTest(FunctionalTest):

    def test_navigate_as_guest(self):


        # Joe is visiting the site for the first time, and since
        # he doesn't want to sign up just yet, he signs in as a guest
        self.initialize_test(self.GUESTNAME, self.GUESTPASS)

        # He sees several tabs across the top of the page, with several
        # My Recipes/Meals, Add New Recipes, and Add New Foods being
        # grayed out
        # Out of curiosity, he clicks on the tabs and gets an alert dialog
        # telling him he must have an account to use these features

        self.browser.find_element_by_id('my-meals-tab').click()
        self.browser.switch_to_alert().accept()

        self.browser.find_element_by_id('add-recipe-tab').click()
        self.browser.switch_to_alert().accept()

        self.browser.find_element_by_id('add-food-tab').click()
        self.browser.switch_to_alert().accept()

        # Being a tricky asshole, Joe gets around the front end protections
        # and just types in the url for the content, after which he recieves
        # an error page telling him he cannot nagivate using raw urls
        raw_url_error = 'You cannot navigate using raw urls'
        self.browser.get(f'{self.live_server_url}/meals/my-meals/')
        error = self.browser.find_element_by_id('raw-url-error').text
        self.assertEqual(error, raw_url_error)

        self.browser.get(f'{self.live_server_url}/meals/add-recipe/')
        error = self.browser.find_element_by_id('raw-url-error').text
        self.assertEqual(error, raw_url_error)

        self.browser.get(f'{self.live_server_url}/meals/add-food/')
        error = self.browser.find_element_by_id('raw-url-error').text
        self.assertEqual(error, raw_url_error)

        self.browser.find_element_by_id('home').click()

        # He is still curious about his TDEE so he goes to the My Macros tab
        # and fills out the TDEE form
        self.browser.find_element_by_id('my-macros-tab').click()

        macro_form_selectors = [
            "input[value='male']",
            "input[name='age']",
            "input[name='weight']", "input[name='height_0']",
            "input[name='height_1']", "input[value='none']",
            "input[value='lose']", "input[name='change_rate']"
        ]
            
        macro_form_values = [None, '34', '210', '5', '10', None, None, '1']
        self.fill_input(macro_form_selectors, macro_form_values)	
        self.browser.find_element_by_id('calc-tdee').click()


        macro_form_selectors = [
            "input[name='fat_percent']", "input[name='carbs_percent']",
            "input[name='protein_percent']"
        ]
        macro_form_values = ['30','50','20']
        self.fill_input(macro_form_selectors,macro_form_values)	

        # After he fills in the form he sees a message indicating that if
        # he wants to save this info, he has to create an account
        save_area = self.browser.find_element_by_id('save-my-macros-guest')
        self.assertEqual(
            save_area.text, 'To Save this info, create an account!!!'
        )

        # He sees that Meal Maker tabs are not grayed out
        # so he clicks on Meal Maker and fills out the form. He sees a Save Meal
        # button, that when he tries to click he gets the same alert as above
        self.browser.find_element_by_id('meal-maker-tab').click()
        self.fill_input(
            [
                "input[id='goal-meal-fat-percent']",
                "input[id='goal-meal-carbs-percent']",
                "input[id='goal-meal-protein-percent']",
                "input[id='goal-meal-cals']"
            ],
            [34, 33, 33, 500]
        )
        self.browser.find_element_by_id('create-macro-bars-button').click()
        save_button = self.browser.find_element_by_id('show-modal-button')
        save_button.click()
        self.browser.switch_to_alert().accept()

