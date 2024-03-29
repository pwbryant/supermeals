from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
from decimal import Decimal
import os
from datetime import datetime

# import socket
# from django.test import TestCase

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpRequest

from meals.models import Macros, Servings
from supermeals.settings import DATABASES as dbs


class FunctionalTest(StaticLiveServerTestCase):

    USERNAME = "JoeSchmoe"
    PASSWORD = "123pass123"
    GUESTNAME = "guest"
    GUESTPASS = "password"

    host = "web"
    port = 8888

    def setUp(self):

        browser = os.environ.get("BROWSER", "Firefox")
        self.browser = webdriver.Remote(
            command_executor="http://hub:4444/wd/hub",
            desired_capabilities=DesiredCapabilities.FIREFOX,
        )

        self.browser.implicitly_wait(10)

        Servings.objects.create(grams=Decimal(1), quantity=Decimal(1), description="g")

    def tearDown(self):
        self.browser.quit()
        super().tearDown()

    def search_and_results(self, input_selector, button_id, result_class, term_list):

        self.fill_input([input_selector], term_list)
        self.browser.find_element_by_id(button_id).click()
        search_results = self.browser.find_elements_by_class_name(result_class)

        return search_results

    def setup_and_run_search(self, terms, filters, tab_name):

        input_id = f"{tab_name}-search"
        self.fill_input([f"input[id='{input_id}']"], [], clear=True)

        for filter_ in filters:
            filter_.click()

        return self.search_and_results(
            f"input[id='{input_id}']",
            f"{input_id}-button",
            f"{tab_name}-search-result",
            terms,
        )

    def fill_input(self, element_selectors, values, clear=None):
        for i in range(len(element_selectors)):
            element = self.browser.find_element_by_css_selector(element_selectors[i])

            if clear:
                element.clear()
            else:
                if element.get_attribute("type") in ("text", "textarea"):
                    element.send_keys(values[i])

                if element.get_attribute("type") == "radio":
                    element.click()

    def login_user(self, username, password=False):

        if "" not in [username, password]:

            if username == "guest":
                select_login_button = "input[value='Login As Guest']"
            else:
                self.fill_input(
                    ["input[name='username']", "input[name='password']"],
                    [username, password],
                )
                select_login_button = "input[value='Login']"
        else:
            select_login_button = "input[value='Login']"

        login_button = self.browser.find_element_by_css_selector(select_login_button)
        login_button.click()

    def check_element_content(
        self, selector, selector_type, comparison_type, comparison_text, child=None
    ):

        if selector_type == "id":
            element = self.browser.find_element_by_id(selector)

        if selector_type == "css":
            element = self.browser.find_element_by_css_selector(selector)

        if child != None:
            element = element.find_elements_by_tag_name(child)[0]

        if comparison_type == "text":
            content = element.text
        if comparison_type in ["placeholder", "value", "innerHTML"]:
            content = element.get_attribute(comparison_type)

        self.assertEqual(content, comparison_text)

    def initialize_test(self, username, password):
        user = User.objects.create_user(username=username, password=password)
        self.browser.get(self.live_server_url)
        self.login_user(username, password)
        return user

    def create_default_macro(self, user):
        macro = Macros.objects.create(
            **{
                "user": user,
                "unit_type": "imperial",
                "gender": "male",
                "age": 35,
                "height": Decimal("177.8"),
                "weight": Decimal("99.79"),
                "direction": "lose",
                "activity": "light",
                "change_rate": Decimal(".45359237"),
                "protein_percent": Decimal("33"),
                "fat_percent": Decimal("34"),
            }
        )

        return macro

    def create_user(self, username, email, password):
        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        return user
