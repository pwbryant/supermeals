from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpRequest
from selenium import webdriver
import time
from decimal import Decimal
from meals.models import Macros, MealTemplate, Servings

class FunctionalTest(StaticLiveServerTestCase):

	USERNAME = "JoeSchmoe"
	PASSWORD = "123pass123"
	GUESTNAME = "guest"
	GUESTPASS = "321!beware"

	def setUp(self):
            self.browser = webdriver.Firefox()
            Servings.objects.create(
                grams=Decimal(1),
                quantity=Decimal(1),
                description='g'
            )


	def tearDown(self):
            self.browser.quit()

	
	def fill_input(self,element_selectors,values,clear=None):
            for i in range(len(element_selectors)):
                element = self.browser.find_element_by_css_selector(
                    element_selectors[i]
                )
                
                if clear:
                        element.clear()
                else:
                    if element.get_attribute('type') in ('text', 'textarea'):
                            element.send_keys(values[i])

                    if element.get_attribute('type') == 'radio':
                            element.click()


	def login_user(self,username,password = False):

            if "" not in [username,password]:
                
                if username == "guest":
                        login_button_id = "guest"
                else:
                    self.fill_input(["input[name='username']","input[name='password']"],[username,password])
                    login_button = "input[value='Login']"
            else:
                login_button = "input[value='Login']"

            self.browser.find_element_by_css_selector(login_button).click()


	def check_element_content(self,selector,selector_type,comparison_type, comparison_text,child=None):
	
            if selector_type == "id":
                element = self.browser.find_element_by_id(selector)
            
            if selector_type == "css":
                    element = self.browser.find_element_by_css_selector(selector)

            if child != None:
                element = element.find_elements_by_tag_name(child)[0]

            if comparison_type == "text":
                    content = element.text
            if comparison_type in ['placeholder', 'value', 'innerHTML']:
                    content = element.get_attribute(comparison_type)

            self.assertEqual(content,comparison_text)


	def initialize_test(self,username,password):
            user = User.objects.create_user(username=username,password=password)
            self.browser.get(self.live_server_url)
            self.login_user(username,password)
            return user
		

	def create_default_macro(self,user):
            macro = Macros.objects.create(**{
                "user":user,
                "unit_type":"imperial",
                "gender":"male",
                "age":35,
                "height":Decimal("177.8"),
                "weight":Decimal("99.79"),
                "direction":"lose",
                "activity":"light",
                "change_rate":Decimal(".45359237"),
                "protein_percent":Decimal("33"),
                "fat_percent":Decimal("34")
            })

            return macro

		
	def create_default_meal_templates(self,user):
            MealTemplate.objects.create(
                user=user,name="meal_0",cals_percent=Decimal("28")
            )
            MealTemplate.objects.create(
                user=user,name="meal_1",cals_percent=Decimal("28")
            )
            MealTemplate.objects.create(
                user=user,name="meal_2",cals_percent=Decimal("28")
            )
            MealTemplate.objects.create(
                user=user,name="meal_3",cals_percent=Decimal("16")
            )
