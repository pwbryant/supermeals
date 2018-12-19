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

        self.browser.find_element_by_id('my-meals-tab').click()
        self.browser.switch_to_alert().accept()

        # Being a tricky asshole, Joe gets around the front end protections
        # and just types in the url for the content, after which he recieves
        # an error page telling him he cannot nagivate using raw urls
        self.browser.get(f'{self.live_server_url}/meals/my-meals/')
        error = self.browser.find_element_by_id('raw-url-error').text
        self.assertEqual(error, 'You cannot navigate using raw urls')

        # He then clicks on the Home button and returns to the previous screen
        # and then he tries the same thing on the Add Recipe tab
        self.browser.find_element_by_id('home').click()
        self.browser.find_element_by_id('add-recipe-tab').click()

        self.fail('Finish Test')



        # Out of curiosity, he clicks on the tabs and gets an alert dialog
        # telling him he must have an account to use these features

        # He sees that My Macros and Meal Maker tabs are not grayed out
        # so he clicks on My Macros and fills out the form. At the very bottom
        # he sees a grayed out save button, that when he tries to click he
        # gets the same alert as above

        # He then goes to meal maker, makes a little meal but when he goes
        # to save the meal, the button is grayed out and he gets the same
        # alert

