
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.common.exceptions import NoSuchElementException
from django.contrib.auth.models import User
# from django.contrib.auth import authenticate
import time

from functional_tests.base import FunctionalTest

USERNAME, EMAIL, PASSWORD = 'JoeSchmoe', 'joe@joemail.com', 'Bonepass11'

class FormValidation(FunctionalTest):

    def test_login_form_validation(self):

        # Joe goes to The Meal Lab and finds himself at the login page
        self.browser.get(self.live_server_url)

        # He sees a welcome message
        welcome_msg = self.browser.find_element_by_id('login-welcome').text
        self.assertEqual(
            welcome_msg, 'Macrobatics\nFind portions of foods you love, which support nutritional goals'
        )

        bad_login_message = (
            'Your username and password didn\'t match. Please try again.'
            '\nPlease login to see this page.'
        )

        # Joe goes to login but he failed to enter his username and password
        # so when he
        self.login_user('', '')
        error_message = self.browser.find_element_by_id('login-errors').text
        self.assertEqual(error_message, bad_login_message)

        # Joe goes to sign in but mispells his username and gets an
        # error message, but sees he stays on the page
        self.create_user(USERNAME, EMAIL, PASSWORD)
        self.login_user('j_bo', 'joepass')
        error_message = self.browser.find_element_by_id('login-errors').text
        self.assertEqual(error_message, bad_login_message)
        # He gets it right and is brought to a new page where he then clicks
        # on the logoff button, and is taken back to the login page
        self.login_user(USERNAME, PASSWORD)
        self.browser.find_element_by_id('logoff').click()

        # He sees he's back on the login page (test for Login button)
        self.check_element_content(
            'input[value="Login"]', 'css', 'value',
            'Login'
        )


    def test_sign_up_form_validation(self):

        self.browser.get(self.live_server_url + '/meals/sign-up/')

        # Joe thinks twice about it and goes to hit cancel, but instead hits
        # the Create Account but the page doesn't submit because there arent
        # any fields filled in

        self.browser.find_element_by_id('create').click()
        self.browser.find_element_by_id('id_username') # shows no submit

        # Joe enters a username, but it has a space, which is illegal, so
        # he gets an error message
        bad_user_name_error = (
            'Enter a valid username. This value may contain only letters, '
            'numbers, and @/./+/-/_ characters.'
        )
        signup_selectors = [
            'input[id="id_username"]', 'input[id="id_email"]',
            'input[id="id_password"]'
        ]
        signup_values = ['j bone', EMAIL, PASSWORD]

        self.fill_input(signup_selectors, signup_values)

        self.browser.find_element_by_id('create').click()
        error_message = self.browser.find_elements_by_class_name('errorlist')[0].text
        self.assertEqual(error_message, bad_user_name_error)

        # Finally Joe gets it right and signs up, but later forgets.
        self.browser.find_element_by_id('id_username').clear()
        self.browser.find_element_by_id('id_email').clear()
        self.browser.find_element_by_id('id_password').clear()
        signup_values = [USERNAME, EMAIL, PASSWORD]
        self.fill_input(signup_selectors, signup_values)
        self.browser.find_element_by_id('create').click()

        # Hes signs out
        self.browser.find_element_by_id('logoff').click()

        # Joe forgets that he already signed up so when he goes to the sign up
        # page and and enters the same username and password, he gets an error
        # message "Username already taken
        self.browser.get(self.live_server_url + '/meals/sign-up/')
        duplicate_user_name_error = 'Username taken'
        self.browser.find_element_by_id('id_username').clear()
        self.browser.find_element_by_id('id_email').clear()
        self.browser.find_element_by_id('id_password').clear()
        signup_values = [USERNAME, EMAIL, PASSWORD]
        self.fill_input(signup_selectors, signup_values)
        self.browser.find_element_by_id('create').click()
        error_message = self.browser.find_elements_by_class_name('errorlist')[0].text
        self.assertEqual(error_message, duplicate_user_name_error)

