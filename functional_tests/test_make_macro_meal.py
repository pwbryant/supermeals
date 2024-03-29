import time
from builtins import Exception
from decimal import Decimal

from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.select import Select

from .base import FunctionalTest
from meals.models import Foods, FoodGroup, Servings, Ingredients, FoodType


class ElementPresentException(Exception):
    def __init__(self, message):
        self.message = message


class MakeMacroMealTest(FunctionalTest):
    def this_setup(self):

        veg_food_group = FoodGroup.objects.create(name="Veggies", rank=2)
        legume_food_group = FoodGroup.objects.create(name="Legumes", rank=2)
        pork_food_group = FoodGroup.objects.create(name="Meat", rank=3)
        my_meals_food_group = FoodGroup.objects.create(name="My Meals", rank=1)

        FoodType.objects.create(name="meal")

        names = ["Chickpeas", "Carrots", "Bacon", "Lettuce"]
        cals = [1.3800, 0.3500, 4.6800, 0.1600]
        fat = [0.2223, 0.0117, 3.1581, 0.0198]
        carbs = [0.9148, 0.3296, 0.0680, 0.0904]
        sugar = [0.9148, 0.3296, 0.0680, 0.0904]
        protein = [0.2816, 0.0256, 1.3568, 0.0532]

        foods = []
        for i in range(len(names)):
            if names[i] == "Chickpeas":
                fg = legume_food_group
            elif names[i] == "Bacon":
                fg = pork_food_group
            else:
                fg = veg_food_group
            food = Foods.objects.create(
                name=names[i],
                cals_per_gram=cals[i],
                fat_per_gram=fat[i],
                carbs_per_gram=carbs[i],
                sugar_per_gram=sugar[i],
                protein_per_gram=protein[i],
                food_group=fg,
            )
            foods.append(food)

        self.slice_ = Servings.objects.create(
            food=foods[2], grams=Decimal(11.5), quantity=Decimal(1), description="slice"
        )

        duplicate_food = Foods.objects.create(name="duplicate food")

    def get_bar_ratio(self, num_height, denom_height):
        return round(float(num_height) / float(denom_height), 2)

    def move_slider(self, slider_id, ypos):
        slider = self.browser.find_element_by_id(slider_id)
        self.browser.execute_script("arguments[0].scrollIntoView();", slider)
        actions = ActionChains(self.browser)
        actions.drag_and_drop_by_offset(slider, 0, ypos)
        actions.perform()

    def check_food_amt(self, food_id, cals_per_gram, goal_cals):

        svg = self.browser.find_element_by_id("food-{}-cals-svg".format(food_id))
        slider_id = "food-{}-slider".format(food_id)
        self.move_slider(slider_id, svg.size["height"])
        self.move_slider(slider_id, -svg.size["height"])
        food_amt = self.browser.find_element_by_id("food-amt-{}".format(food_id)).text
        if "." not in food_amt:
            food_amt += ".0"  # so it matches with python rounding if no decimal present
        self.assertEqual(food_amt, str(round(goal_cals / cals_per_gram, 2)))
        self.move_slider(slider_id, svg.size["height"])

    def make_sure_absent(self, element_id):
        try:
            self.browser.find_element_by_id(element_id)
            try:
                raise ElementPresentException(
                    "\n\n{} element is present\n".format(element_id)
                )
            except ElementPresentException as error:
                raise

        except NoSuchElementException:
            return True

    def test_make_macro_meal(self):

        self.this_setup()

        user = self.initialize_test(self.USERNAME, self.PASSWORD)
        # self.create_default_meal_templates(user)

        # Joe now wants to make a meal that helps him achieve his macros
        # so he clicks on the "Meal Maker" tab
        self.browser.find_element_by_id("meal-maker-tab").click()

        # Joe enters 500 cals and 34,33,33 % for Fat, Carbs and Protein
        # respectively and notices that the gram inputs fill in
        # with 19, 41, 41
        self.fill_input(
            [
                "input[id='goal-meal-fat-percent']",
                "input[id='goal-meal-carbs-percent']",
                "input[id='goal-meal-protein-percent']",
                "input[id='goal-meal-cals']",
            ],
            [30, 37, 33, 338],
        )

        # To the right of the macro table are a series of four rectangles
        # labeled "Calories", "Fat", "Carbs", "Protein".

        self.browser.find_element_by_id("create-macro-bars-button").click()
        cal_bar = self.browser.find_element_by_id("cals-goal-macro-bar")
        fat_bar = self.browser.find_element_by_id("fat-goal-macro-bar")
        carbs_bar = self.browser.find_element_by_id("carbs-goal-macro-bar")
        protein_bar = self.browser.find_element_by_id("protein-goal-macro-bar")

        bar_container_height = self.browser.find_element_by_id(
            "goal-macros-bar-container"
        ).size["height"]
        bar_container_width = self.browser.find_element_by_id(
            "goal-macros-bar-container"
        ).size["width"]
        bar_width = bar_container_width * 0.2

        self.assertEqual(
            self.get_bar_ratio(fat_bar.size["height"], cal_bar.size["height"]), 0.30
        )
        self.assertEqual(
            self.get_bar_ratio(carbs_bar.size["height"], cal_bar.size["height"]), 0.37
        )
        self.assertEqual(
            self.get_bar_ratio(protein_bar.size["height"], cal_bar.size["height"]), 0.33
        )

        # Below which are a series of 0s like 0, 0g, 0g, 0g
        # for macro amounts.
        labels = self.browser.find_elements_by_css_selector(".macro-label")
        amts = self.browser.find_elements_by_css_selector(".macro-amt")
        units = self.browser.find_elements_by_css_selector(".macro-unit")

        self.assertEqual(labels[0].text, "Cals:")
        self.assertEqual(labels[1].text, "Fat:")
        self.assertEqual(labels[2].text, "Carbs:")
        self.assertEqual(labels[3].text, "Protein:")

        self.assertEqual(
            len(set([amt.text for amt in amts])) == 1 and amts[0].text == "0", True
        )
        self.assertEqual(
            len(set([unit.text for unit in units])) == 1 and units[0].text == "g", True
        )

        # Below the macors bars is a button reading Save Meal
        save_meal_button = self.browser.find_element_by_id("show-modal-button")
        self.assertEqual(save_meal_button.text, "Save Meal")
        self.assertFalse(save_meal_button.is_enabled())

        # All the above only takes up the top of the page, the bottom
        # half contains a page wide div with the large text
        # "Add Ingredients using Search"
        self.check_element_content(
            "meal-maker-food-content-banner",
            "id",
            "text",
            "Add Ingredients Using Search",
        )
        # Joe is going to attempt to make a salad that will fit his macro
        # percentages. He starts by entering "600" into the
        # "How Many Calories?" input box
        cals_input = ["input[id='goal-meal-cals']"]
        cals_input_value = ["600"]
        self.fill_input(cals_input, [], clear=True)
        self.fill_input(cals_input, cals_input_value)

        # He starts by typeing "garbonzo beans" in the search bar and
        # clicks the search icon. And he sees the area below the search
        # bar fill up with the top 10 results
        search_results = self.search_and_results(
            "input[id='meal-maker-search']",
            "meal-maker-search-button",
            "search-result",
            ["chickpeas"],
        )

        # Joe clicks on the first result ( on the add + icon )
        # and notices that in the lower left, a series of rectangles
        # appear with the
        # result text as the header, and "0g" under the bars to the left.
        # The left-most rectangle has a small drag box at the bottom.
        chickpea_id = f'{Foods.objects.get(name="Chickpeas").id}'
        search_results[0].find_elements_by_class_name("icon")[0].click()
        food_container = self.browser.find_element_by_id(
            "food-{}-container".format(chickpea_id)
        )
        food_container.find_element_by_id("food-{}-cals-svg".format(chickpea_id))
        food_container.find_element_by_id("food-{}-fat-svg".format(chickpea_id))
        food_container.find_element_by_id("food-{}-carbs-svg".format(chickpea_id))
        food_container.find_element_by_id("food-{}-protein-svg".format(chickpea_id))
        header = food_container.find_element_by_css_selector(
            ".food-container-header>span"
        ).text
        footer_amt = food_container.find_element_by_id(
            "food-amt-{}".format(chickpea_id)
        ).text
        footer_unit = (
            food_container.find_element_by_id("food-amt-units-{}".format(chickpea_id))
            .find_elements_by_css_selector('option[value="1"]')[0]
            .text
        )
        self.assertEqual(header, "Chickpeas")
        self.assertEqual(footer_amt + footer_unit, "0g")

        # He then searches for "carrots raw", clicks the "+" button on the
        # first result and notices again, that a series of rectanlges and
        # labels (except title) like the previous result appear to the right
        # of the previous search result

        self.fill_input(["input[id='meal-maker-search']"], [], clear=True)
        search_results = self.search_and_results(
            "input[id='meal-maker-search']",
            "meal-maker-search-button",
            "search-result",
            ["carrots"],
        )
        search_results[0].find_elements_by_class_name("icon")[0].click()
        carrot_id = f'{Foods.objects.get(name="Carrots").id}'
        food_container = self.browser.find_element_by_id(
            "food-{}-container".format(carrot_id)
        )
        food_container.find_element_by_id("food-{}-cals-svg".format(carrot_id))
        food_container.find_element_by_id("food-{}-fat-svg".format(carrot_id))
        food_container.find_element_by_id("food-{}-carbs-svg".format(carrot_id))
        food_container.find_element_by_id("food-{}-protein-svg".format(carrot_id))
        header = food_container.find_element_by_css_selector(
            ".food-container-header>span"
        ).text
        footer_amt = food_container.find_element_by_id(
            "food-amt-{}".format(carrot_id)
        ).text
        footer_unit = (
            food_container.find_element_by_id("food-amt-units-{}".format(carrot_id))
            .find_elements_by_css_selector('option[value="1"]')[0]
            .text
        )
        self.assertEqual(header, "Carrots")
        self.assertEqual(footer_amt + footer_unit, "0g")

        # He then adds "bacon" and "lettuce" to the mix as well
        self.fill_input(["input[id='meal-maker-search']"], [], clear=True)
        search_results = self.search_and_results(
            "input[id='meal-maker-search']",
            "meal-maker-search-button",
            "search-result",
            ["bacon"],
        )
        search_results[0].find_elements_by_class_name("icon")[0].click()
        bacon_id = f'{Foods.objects.get(name="Bacon").id}'

        self.fill_input(["input[id='meal-maker-search']"], [], clear=True)
        search_results = self.search_and_results(
            "input[id='meal-maker-search']",
            "meal-maker-search-button",
            "search-result",
            ["lettuce"],
        )
        search_results[0].find_elements_by_class_name("icon")[0].click()

        # He then adjusts the dragbar on the bacon cal bar.
        test_can_move_dist = self.browser.get_window_size()["height"] * -0.13
        self.move_slider("food-{}-slider".format(bacon_id), test_can_move_dist)
        # He notices that as the slider goes up, the above meal bars fill up with
        # the same color as the bacon food bars.
        bacon_cals_bar = self.browser.find_element_by_id(
            "cals-{}-goal-macro-bar".format(bacon_id)
        )
        self.assertEqual(bacon_cals_bar.size["height"] > 0, True)

        # He adjusts the lettuce bar and notices that, like the bacon, bar the
        # meal bars fill up with the color of the lettuce bar.
        lettuce_id = f'{Foods.objects.get(name="Lettuce").id}'
        self.move_slider("food-{}-slider".format(lettuce_id), test_can_move_dist)
        lettuce_cals_bar = self.browser.find_element_by_id(
            "cals-{}-goal-macro-bar".format(lettuce_id)
        )
        self.assertEqual(lettuce_cals_bar.size["height"] > 0, True)

        # He also notices that the bacon bar color in the meal bars is stacked
        # on top of the bacon bars.
        self.assertEqual(
            bacon_cals_bar.location["y"] < lettuce_cals_bar.location["y"], True
        )

        # He then adjusts the carrots and garbonzo beans, an notices, that the
        # meal bars are stacked in the order that the foods were initially added
        self.move_slider("food-{}-slider".format(chickpea_id), test_can_move_dist)
        self.move_slider("food-{}-slider".format(carrot_id), test_can_move_dist)
        chickpea_cals_bar = self.browser.find_element_by_id(
            "cals-{}-goal-macro-bar".format(chickpea_id)
        )
        carrot_cals_bar = self.browser.find_element_by_id(
            "cals-{}-goal-macro-bar".format(carrot_id)
        )

        self.assertEqual(
            chickpea_cals_bar.location["y"]
            < carrot_cals_bar.location["y"]
            < bacon_cals_bar.location["y"]
            < lettuce_cals_bar.location["y"],
            True,
        )
        # Joe is curious how many cals/fat/carbs/prot and grams are at the max
        # capacity of each food so one by one he drags the bars of each food to
        # the max and reads what the cals/far/carbs/prot and grams are.
        goal_cals = 600
        self.check_food_amt(chickpea_id, 1.3800, goal_cals)
        self.check_food_amt(carrot_id, 0.3500, goal_cals)
        self.check_food_amt(bacon_id, 4.68, goal_cals)
        self.check_food_amt(lettuce_id, 0.16, goal_cals)

        # Joe now tries to adjust the foods so that they achieve
        # is target meal goals
        # Joe adds some of every food, but after thinking about how much he
        # doesn"t really like garbonzo beans, he decides he"s going to replace it.
        # Joe notices an "x" in the upper left of each food, he clicks on it and
        # garbonzo beans disappears
        self.browser.find_element_by_id("exit-" + chickpea_id).click()
        self.assertTrue(self.make_sure_absent("exit-" + chickpea_id))

        # self.move_slider('food-{}-slider'.format(chickpea_id), 600)
        # self.move_slider('food-{}-slider'.format(carrot_id), 600)
        # self.move_slider('food-{}-slider'.format(lettuce_id), 600)

        # He also notices that all the meal bars above "garbonzo beans" have slid down.
        # He also notices that the macro amounts have decreased correct amount.
        # He is confused by measuring the amts in grams so he switches the bacon
        # unit to slice
        self.move_slider("food-{}-slider".format(bacon_id), test_can_move_dist)
        bacon_slice = self.browser.find_element_by_id(
            "food-amt-units-{}".format(bacon_id)
        ).find_elements_by_css_selector('option[value="2"]')[0]
        bacon_slice.click()

        # FOR SOME REASON THESE CHECK ARE SQUIRRELY SO I JUST CHECK THE FIRST
        # DIGIT
        # approx_slice_amt = self.browser.find_element_by_id(
        #     'food-amt-{}'.format(bacon_id)
        # ).text[0]
        # self.assertEqual(approx_slice_amt, '6')

        # Joe wants to save this meal so he moves up all the foods
        # clicks on the save button below the
        # goal macro bars, after which he sees a modal form pop up.

        self.move_slider("food-{}-slider".format(carrot_id), test_can_move_dist)
        self.move_slider("food-{}-slider".format(lettuce_id), test_can_move_dist)

        save_modal = self.browser.find_element_by_id("save-macro-meal-modal")

        self.assertFalse(save_modal.is_displayed())

        self.assertTrue(save_meal_button.is_enabled())
        save_meal_button.click()

        self.assertTrue(save_modal.is_displayed())

        self.check_element_content(
            'label[for="macro-meal-name"]', "css", "text", "Meal Name"
        )
        self.check_element_content(
            'label[for="macro-meal-notes"]', "css", "text", "Notes (Optional)"
        )
        self.check_element_content("macro-meal-name", "id", "placeholder", "Meal Name")
        self.check_element_content(
            "macro-meal-notes", "id", "placeholder", "Notes (Optional)"
        )

        # Joe enters 'bacon lettuce carrot mix' as the meal and
        # 'best as a salad'in the notes. He changes his mind though
        # and exits out of the modal by clicking the x in the upper right.

        self.fill_input(
            [
                "input[id='macro-meal-name']",
                "textarea[id='macro-meal-notes']",
            ],
            ["dummy value", "dummy value"],
        )

        self.browser.find_elements_by_css_selector(".close-modal")[0].click()
        self.assertFalse(save_modal.is_displayed())

        # Joe thinks again, and decides to save the meal again.
        # Joe enters 'duplicate name' as the meal name
        # and clicks the save button, after which a duplicate name message
        # shows up in the modal

        save_meal_button.click()
        self.check_element_content("macro-meal-name", "id", "value", "")

        self.fill_input(
            [
                "input[id='macro-meal-name']",
            ],
            ["duplicate food"],
        )

        self.browser.find_element_by_id("save-macro-meal-button").click()

        self.check_element_content(
            "macro-meal-save-status",
            "id",
            "text",
            "Foods with this Name already exists.",
        )

        # Joe switches names and enters 'bacon lettuce carrot mix'
        # as the meal name and he gets a success message. After 3 secs
        # the modal disappears

        self.fill_input(["input[id='macro-meal-name']"], [], clear=True)

        self.fill_input(
            [
                "input[id='macro-meal-name']",
                "textarea[id='macro-meal-notes']",
            ],
            ["bacon lettuce carrot mix", "best as a salad"],
        )

        self.browser.find_element_by_id("save-macro-meal-button").click()
        self.check_element_content(
            "macro-meal-save-status", "id", "text", "Successfully Saved!"
        )

        time.sleep(3)
        self.assertFalse(save_modal.is_displayed())

        # Joe notices that most of the meal tab info except for the macro
        # percent, has been cleared
        self.check_element_content("goal-meal-cals", "id", "value", "")
        self.check_element_content("goal-meal-fat-g", "id", "value", "")
        self.check_element_content("goal-meal-carbs-g", "id", "value", "")
        self.check_element_content("goal-meal-protein-g", "id", "value", "")
        self.check_element_content("meal-maker-search", "id", "value", "")
        self.check_element_content(
            "meal-maker-search-results-container", "id", "innerHTML", ""
        )
        self.check_element_content("goal-macros-bar-content", "id", "innerHTML", "")
        self.check_element_content("goal-macros-bar-footer", "id", "innerHTML", "")
        self.check_element_content("meal-maker-food-content", "id", "innerHTML", "")

        self.check_element_content("macro-meal-name", "id", "value", "")

        self.check_element_content("macro-meal-notes", "id", "value", "")

        self.check_element_content("macro-meal-save-status", "id", "innerHTML", "")
        # Out of curiosity he want to see what the newly saved meals
        # macro bars look like so he searches for the food on the meal
        # maker tab and notices that 'meal' is one of the units

        save_meal_name = "bacon lettuce carrot mix"
        saved_meal = Foods.objects.get(name=save_meal_name)

        self.browser.find_element_by_id("meal-maker-tab").click()
        self.fill_input(
            [
                "input[id='goal-meal-fat-percent']",
                "input[id='goal-meal-carbs-percent']",
                "input[id='goal-meal-protein-percent']",
                "input[id='goal-meal-cals']",
            ],
            [30, 37, 33, 338],
        )
        self.browser.find_element_by_id("create-macro-bars-button").click()

        search_results = self.search_and_results(
            "input[id='meal-maker-search']",
            "meal-maker-search-button",
            "search-result",
            [save_meal_name],
        )

        search_results[0].find_elements_by_class_name("icon")[0].click()
        food_container = self.browser.find_element_by_id(
            "food-{}-container".format(saved_meal.id)
        )
        footer_unit = (
            food_container.find_element_by_id("food-amt-units-{}".format(saved_meal.id))
            .find_elements_by_css_selector('option[value="2"]')[0]
            .text
        )
        self.assertEqual(footer_unit, "meal")
