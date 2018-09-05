import time
from builtins import Exception
from decimal import Decimal

from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.select import Select

from .base import FunctionalTest
from meals.models import Foods, Servings, Ingredients

class ElementPresentException(Exception):

    def __init__(self, message):
        self.message = message

class MakeMacroMealTest(FunctionalTest):

    # fixtures = ["db.json"]

    def this_setup(self):

        names = ['Chickpeas', 'Carrots', 'Bacon', 'Lettuce']
        cals = [1.3800, 0.3500, 4.6800, 0.1600]
        fat = [0.2223, 0.0117, 3.1581, 0.0198]
        carbs = [0.9148, 0.3296, 0.0680, 0.0904]
        protein = [0.2816, 0.0256, 1.3568, 0.0532]
        
        foods = []
        for i in range(len(names)):
            food = Foods.objects.create(
               name=names[i],
               cals_per_gram=cals[i],
               fat_per_gram=fat[i],
               carbs_per_gram=carbs[i],
               protein_per_gram=protein[i],
            )
            foods.append(food)

        # Servings.objects.create(
        #     food=foods[0], grams=Decimal(254), quantity=Decimal(1), description='can'
        # )
        # Servings.objects.create(
        #     food=foods[0], grams=Decimal(152), quantity=Decimal(1), description='cup'
        # )
        # Servings.objects.create(
        #     food=foods[1], grams=Decimal(15), quantity=Decimal(1), description='large'
        # )
        # Servings.objects.create(
        #     food=foods[1], grams=Decimal(10), quantity=Decimal(1), description='medium'
        # )
        # Servings.objects.create(
        #     food=foods[1], grams=Decimal(85), quantity=Decimal(1), description='serving'
        # )
        Servings.objects.create(
            food=foods[2], grams=Decimal(11.5), quantity=Decimal(1), description='slice'
        )
        # Servings.objects.create(
        #     food=foods[3], grams=Decimal(), quantity=Decimal(1), description=''
        # )
        # Servings.objects.create(
        #     food=foods[3], grams=Decimal(), quantity=Decimal(1), description=''
        # )
        # Servings.objects.create(
        #     food=foods[3], grams=Decimal(), quantity=Decimal(1), description=''
        # )


    def get_bar_ratio(self, num_height, denom_height):
        return round(float(num_height) / float(denom_height), 2)

    def search_and_results(self, term_list):
        self.fill_input(
            ["input[id='meal-maker-food-search-input']"],
            term_list
        )
        self.browser.find_element_by_id(
            "food-search-icon-button").click()
        search_results = self.browser.find_elements_by_class_name(
            "search-result")
        return search_results

    def move_slider(self, slider_id, ypos):
        slider = self.browser.find_element_by_id(slider_id)
        self.browser.execute_script('arguments[0].scrollIntoView();', slider)
        actions = ActionChains(self.browser)
        actions.drag_and_drop_by_offset(slider, 0, ypos)
        actions.perform()

    def check_food_amt(self, food_id, cals_per_gram, goal_cals):
        self.move_slider('food-{}-slider'.format(food_id), 600)
        self.move_slider('food-{}-slider'.format(food_id), 1)
        food_amt = self.browser.find_element_by_id(
            'food-amt-{}'.format(food_id)
        ).text
        if '.' not in food_amt:
            food_amt += '.0' # so it matches with python rounding if no decimal present
        self.assertEqual(food_amt, str(round(goal_cals / cals_per_gram, 2)))
        self.move_slider('food-{}-slider'.format(food_id), 600)

    def make_sure_absent(self, element_id):
        try:
            self.browser.find_element_by_id(element_id)
            try:
                raise ElementPresentException('\n\n{} element is present\n'.format(element_id))
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

        # Joe however, did not set any macros in the my macros tab, but he can
        # still make a meal.
        #He notices an input to enter the desired calories.
        self.check_element_content(
            "label[for='goal-meal-cals-container']",
            'css', 'text', 'How Many Calories?'
        )
        self.check_element_content(
            'goal-meal-cals', 'id', 'placeholder', 'Cals'
        )

        #Below he sees a table like area for entering the percentages/grams for each macros
        macro_div = self.browser.find_element_by_id("goal-meal-macros-container")
        macro_spans = macro_div.find_elements_by_css_selector("label")
        self.assertEqual(macro_spans[0].text, 'Percent')
        self.assertEqual(macro_spans[1].text, 'Grams')
        self.assertEqual(macro_spans[2].text, 'Fat')
        self.assertEqual(macro_spans[3].text, 'Carbs')
        self.check_element_content(
            'goal-meal-fat-percent', 'id', 'placeholder', '%'
        )
        self.check_element_content(
            'goal-meal-fat-g', 'id', 'placeholder', 'g'
        )
        self.check_element_content(
            'goal-meal-carbs-percent', 'id', 'placeholder', '%')
        self.check_element_content(
            'goal-meal-carbs-g', 'id', 'placeholder', 'g')
        self.check_element_content(
            'goal-meal-protein-percent', 'id', 'placeholder', '%')
        self.check_element_content(
            'goal-meal-protein-g', 'id', 'placeholder', 'g')

        # Joe enters 500 cals and 34,33,33 % for Fat, Carbs and Protein
        # respectively and notices that the gram inputs fill in
        # with 19, 41, 41
        self.fill_input(
            [
                "input[id='goal-meal-fat-percent']",
                "input[id='goal-meal-carbs-percent']",
                "input[id='goal-meal-protein-percent']",
                "input[id='goal-meal-cals']"
            ],
            [34, 33, 33, 500]
        )
        self.check_element_content('goal-meal-fat-g', 'id', 'value', '19')
        self.check_element_content('goal-meal-carbs-g', 'id', 'value', '41')
        self.check_element_content('goal-meal-protein-g', 'id', 'value', '41')

        # Joe realizes he needs to know his TDEE so he does that and then
        # comes back where He Notices in the upper left of the tab a
        # healine showing his TDEE and text input with the label
        # "How Many Calories?", and the placeholder "cals" and under
        # that a dropdown with choices of Meal 1,2,3 602 and Meal 4 305.
        macro = self.create_default_macro(user)
        self.create_default_meal_templates(user)

        self.browser.find_element_by_id('meal-maker-tab').click()
        self.check_element_content('tdee', 'id', 'text', 'TDEE: 2166')
        self.check_element_content(
            "label[for='goal-meal-cals-container']", 'css', 'text',
            'How Many Calories?')
        self.check_element_content(
            'goal-meal-cals', 'id', 'placeholder', 'Cals')
        set_cals_select = Select(self.browser.find_element_by_id(
            'goal-meal-cals-select'))
        options = set_cals_select.options
        self.assertEqual(options[0].text, 'Saved Cals')
        self.assertEqual(options[1].text, 'Meal 1,2,3 - 607 cals')
        self.assertEqual(options[2].text, 'Meal 4 - 347 cals')

        # Below this input there is an  table like input area with
        # the macros "Fat"/"Carbs"/"Protein" and their
        # respective percent breakdown.

        table = self.browser.find_element_by_id("goal-meal-macros-container")
        labels = table.find_elements_by_css_selector("label")
        self.assertEqual(labels[0].text,"Percent")
        self.assertEqual(labels[1].text,"Grams")
        self.assertEqual(labels[2].text,"Fat")
        self.assertEqual(labels[3].text,"Carbs")
        self.assertEqual(labels[4].text,"Protein")
        inputs = table.find_elements_by_css_selector("input")
        self.assertEqual(inputs[0].get_attribute("value"),"34")
        self.assertEqual(inputs[1].get_attribute("placeholder"),"g")
        self.assertEqual(inputs[2].get_attribute("value"),"33")
        self.assertEqual(inputs[3].get_attribute("placeholder"),"g")
        self.assertEqual(inputs[4].get_attribute("value"),"33")
        self.assertEqual(inputs[5].get_attribute("placeholder"),"g")

        #Joe selects the second option "Meal 4 - 305" and notices that a grams column
        #in the table below fills in.
        set_cals_select = Select(self.browser.find_element_by_id(
            'goal-meal-cals-select'))
        set_cals_select.options[2].click()
        self.assertEqual(inputs[1].get_attribute('value'), '13')
        self.assertEqual(inputs[3].get_attribute('value'), '29')
        self.assertEqual(inputs[5].get_attribute('value'), '29')

        # Joe realized he wants to enter a value not on his saved
        # tab so he enters 500 into the text input and when he does
        # so he sees that the dropdown resets to the default position
        cals_input_id = ["input[id='goal-meal-cals']"]
        cals_input = ['500']
        self.fill_input(cals_input_id, cals_input)
        self.assertEqual(
            set_cals_select.first_selected_option.text, 'Saved Cals')
        
        #He also notices that the grams values chanage as well
        self.assertEqual(inputs[1].get_attribute('value'), '19')
        self.assertEqual(inputs[3].get_attribute('value'), '41')
        self.assertEqual(inputs[5].get_attribute('value'), '41')

        #Joe realizes he actually does want to enter his saved amount
        # so he reslects the 338 cal option and noctices that the text 
        # input clears out. He also changes the Fat and Carbs percents
        # to 30 and 37 % respectively

        set_cals_select.options[2].click()
        self.check_element_content("goal-meal-cals",'id',"text","")
        macro_input_ids = [
                "input[id='goal-meal-fat-percent']",
                "input[id='goal-meal-carbs-percent']"]
        self.fill_input(macro_input_ids,[],clear=True)	
        macro_inputs = ["30","37"]
        self.fill_input(macro_input_ids,macro_inputs)	
        self.assertEqual(inputs[1].get_attribute("value"),"12")
        self.assertEqual(inputs[3].get_attribute("value"),"32")
        self.assertEqual(inputs[5].get_attribute("value"),"29")

        # To the right of the macro table are a series of four rectangles 
        # labeled "Calories", "Fat", "Carbs", "Protein".
        self.browser.find_element_by_id("create-macro-bars-button").click()
        #goal_svg = self.browser.find_element_by_id("goal-macros-svg")
        cal_bar = self.browser.find_element_by_id("cals-goal-macro-bar")
        fat_bar = self.browser.find_element_by_id("fat-goal-macro-bar")
        carbs_bar = self.browser.find_element_by_id("carbs-goal-macro-bar")
        protein_bar = self.browser.find_element_by_id("protein-goal-macro-bar")
        
        bar_container_height = self.browser.find_element_by_id(
                "goal-macros-bar-container").size["height"]
        bar_container_width = self.browser.find_element_by_id(
                "goal-macros-bar-container").size["width"]
        bar_width = bar_container_width * .2

        #self.assertTrue(np.isclose(
        #    self.get_bar_ratio(cal_bar.get_attribute("height"),
        #    svg_height),85))
        self.assertEqual(self.get_bar_ratio(
            fat_bar.size["height"],
            cal_bar.size["height"]),.30)
        self.assertEqual(self.get_bar_ratio(
            carbs_bar.size["height"],
            cal_bar.size["height"]),.37)
        self.assertEqual(self.get_bar_ratio(
            protein_bar.size["height"],
            cal_bar.size["height"]),.33)
        
        # Below which are a series of 0s like 0, 0g, 0g, 0g 
        # for macro amounts.
        labels = self.browser.find_elements_by_css_selector(".macro-label")
        amts = self.browser.find_elements_by_css_selector(".macro-amt")
        units = self.browser.find_elements_by_css_selector(".macro-unit")

        self.assertEqual(labels[0].text, 'Cals:')
        self.assertEqual(labels[1].text, 'Fat:')
        self.assertEqual(labels[2].text, 'Carbs:')
        self.assertEqual(labels[3].text, 'Protein:')

        self.assertEqual(len(set([amt.text for amt in amts])) == 1 and amts[0].text == '0', True)
        self.assertEqual(len(set([
            unit.text for unit in units
        ])) == 1 and units[0].text == 'g', True)

        # Below the macors bars is a button reading Save Meal
        save_meal_button = self.browser.find_element_by_id('show-modal-button')
        self.assertEqual(save_meal_button.text, 'Save Meal')
        self.assertFalse(save_meal_button.is_enabled())

        # To the right of that is a an input with the place holder
        # "Search for ingredients" with a magnifying glass icon button
        self.check_element_content(
            'meal-maker-food-search-input', 'id', 'placeholder',
            'Search For Food')

        # All the above only takes up the top of the page, the bottom
        # half contains a page wide div with the large text
        # "Add Ingredients using Search"
        self.check_element_content(
            'meal-maker-food-header', 'id', 'text',
            'Add Ingredients Using Search')
        # Joe is going to attempt to make a salad that will fit his macro
        # percentages. He starts by entering "600" into the
        # "How Many Calories?" input box
        cals_input = ["input[id='goal-meal-cals']"]
        cals_input_value = ["600"]
        self.fill_input(cals_input,[],clear=True)	
        self.fill_input(cals_input,cals_input_value)	

        # He starts by typeing "garbonzo beans" in the search bar and 
        # clicks the search icon. And he sees the area below the search 
        # bar fill up with the top 10 results
        search_results = self.search_and_results(['chickpeas'])
        #cself.assertEqual(len(search_results),50)

        # Joe clicks on the first result ( on the add + icon )
        # and notices that in the lower left, a series of rectangles
        # appear with the 
        # result text as the header, and "0g" under the bars to the left.
        # The left-most rectangle has a small drag box at the bottom.
        chickpea_id = '1'
        search_results[0].find_elements_by_class_name("icon")[0].click()
        food_container = self.browser.find_element_by_id(
                'food-{}-container'.format(chickpea_id)
        ) 
        food_container.find_element_by_id('food-{}-cals-svg'.format(chickpea_id))
        food_container.find_element_by_id('food-{}-fat-svg'.format(chickpea_id))
        food_container.find_element_by_id('food-{}-carbs-svg'.format(chickpea_id))
        food_container.find_element_by_id('food-{}-protein-svg'.format(chickpea_id))
        header = food_container.find_element_by_css_selector('.food-container-header>span').text
        footer_amt = food_container.find_element_by_id(
                'food-amt-{}'.format(chickpea_id)
        ).text
        footer_unit = food_container.find_element_by_id(
                'food-amt-units-{}'.format(chickpea_id)
        ).find_elements_by_css_selector('option[value="0"]')[0].text
        self.assertEqual(header,'Chickpeas') 
        self.assertEqual(footer_amt + footer_unit,'0g') 


        #He then searches for "carrots raw", clicks the "+" button on the first result
        #and notices again, that a series of rectanlges and labels (except title) 
        #like the previous result appear to the right of the previous search result

        self.fill_input(["input[id='meal-maker-food-search-input']"],[],clear=True)	
        search_results = self.search_and_results(['carrots'])
        search_results[0].find_elements_by_class_name("icon")[0].click()
        carrot_id = '2'
        food_container = self.browser.find_element_by_id(
                'food-{}-container'.format(carrot_id)
        ) 
        food_container.find_element_by_id('food-{}-cals-svg'.format(carrot_id))
        food_container.find_element_by_id('food-{}-fat-svg'.format(carrot_id))
        food_container.find_element_by_id('food-{}-carbs-svg'.format(carrot_id))
        food_container.find_element_by_id('food-{}-protein-svg'.format(carrot_id))
        header = food_container.find_element_by_css_selector('.food-container-header>span').text
        footer_amt = food_container.find_element_by_id(
                'food-amt-{}'.format(carrot_id)
        ).text
        footer_unit = food_container.find_element_by_id(
                'food-amt-units-{}'.format(carrot_id)
        ).find_elements_by_css_selector('option[value="0"]')[0].text
        self.assertEqual(header,'Carrots') 
        self.assertEqual(footer_amt + footer_unit,'0g') 

        #He then adds "bacon" and "lettuce" to the mix as well
        self.fill_input(["input[id='meal-maker-food-search-input']"],[],clear=True)	
        search_results = self.search_and_results(['bacon'])
        search_results[0].find_elements_by_class_name("icon")[0].click()
        bacon_id = '3'

        self.fill_input(["input[id='meal-maker-food-search-input']"],[],clear=True)	
        search_results = self.search_and_results(['lettuce'])
        search_results[0].find_elements_by_class_name("icon")[0].click()

        #He then adjusts the dragbar on the bacon cal bar.
        self.move_slider('food-{}-slider'.format(bacon_id), 500)
        #He notices that as the slider goes up, the above meal bars fill up with
        #the same color as the bacon food bars.
        bacon_cals_bar = self.browser.find_element_by_id(
            'cals-{}-goal-macro-bar'.format(bacon_id)
        )
        self.assertEqual(bacon_cals_bar.size['height'] > 0, True)

        #He adjusts the lettuce bar and notices that, like the bacon, bar the meal
        #bars fill up with the color of the lettuce bar.
        lettuce_id = '4'
        self.move_slider('food-{}-slider'.format(lettuce_id),500)
        lettuce_cals_bar = self.browser.find_element_by_id(
            'cals-{}-goal-macro-bar'.format(lettuce_id)
        )
        self.assertEqual(lettuce_cals_bar.size['height'] > 0, True)

        #He also notices that the bacon bar color in the meal bars is stacked on top
        #of the bacon bars. 
        self.assertEqual(bacon_cals_bar.location['y'] < lettuce_cals_bar.location['y'] , True)

        #He then adjusts the carrots and garbonzo beans, an notices, that the meal bars are stacked in the order that the foods were initially added.

        self.move_slider('food-{}-slider'.format(chickpea_id),500)
        self.move_slider('food-{}-slider'.format(carrot_id),500)
        chickpea_cals_bar = self.browser.find_element_by_id(
            'cals-{}-goal-macro-bar'.format(chickpea_id)
        )
        carrot_cals_bar = self.browser.find_element_by_id(
            'cals-{}-goal-macro-bar'.format(carrot_id)
        )

        self.assertEqual(
                chickpea_cals_bar.location['y'] < carrot_cals_bar.location['y'] < bacon_cals_bar.location['y'] < lettuce_cals_bar.location['y']
                ,True
        )
        #Joe is curious how many cals/fat/carbs/prot and grams are at the max 
        #capacity of each food so one by one he drags the bars of each food to the max 
        #and reads what the cals/far/carbs/prot and grams are.
        goal_cals = 600
        self.check_food_amt(chickpea_id, 1.3800, goal_cals)
        self.check_food_amt(carrot_id, 0.3500, goal_cals)
        self.check_food_amt(bacon_id, 4.68, goal_cals)
        self.check_food_amt(lettuce_id, 0.16, goal_cals)

        #Joe now tries to adjust the foods so that they achieve is target meal goals

        #Joe adds some of every food, but after thinking about how much he
        #doesn"t really like garbonzo beans, he decides he"s going to replace it.
        #Joe notices an "x" in the upper left of each food, he clicks on it and
        #garbonzo beans disappears 
        self.move_slider('food-{}-slider'.format(chickpea_id), 600)
        self.move_slider('food-{}-slider'.format(carrot_id), 600)
        self.move_slider('food-{}-slider'.format(bacon_id), 500) # for below test
        self.move_slider('food-{}-slider'.format(lettuce_id), 600)

        self.browser.find_element_by_id('exit-' + chickpea_id).click()
        self.assertTrue(self.make_sure_absent('exit-' + chickpea_id))

        #He also notices that all the meal bars above "garbonzo beans" have slid down.

        #He also notices that the macro amounts have decreased correct amount.

        # He is confused by measuring the amts in grams so he switches the bacon
        # unit to slice
        bacon_slice = self.browser.find_element_by_id(
            'food-amt-units-{}'.format(bacon_id)
        ).find_elements_by_css_selector('option[value="1"]')[0]

        bacon_slice.click()
        self.check_element_content(
            'food-amt-{}'.format(bacon_id),
            'id', 'text', '6.29'
        )

        # Joe wants to save this meal so he moves up all the foods
        # clicks on the save button below the 
        # goal macro bars, after which he sees a modal form pop up.
        
        self.move_slider('food-{}-slider'.format(carrot_id), 500)
        self.move_slider('food-{}-slider'.format(lettuce_id), 500)
        
        save_modal = self.browser.find_element_by_id('save-macro-meal-modal')
        
        self.assertFalse(save_modal.is_displayed())

        self.assertTrue(save_meal_button.is_enabled())
        save_meal_button.click()
        
        self.assertTrue(save_modal.is_displayed())

        # Joe sees each ingredient listed, the amount, and the unit 
        # Joe saves the meal as 'bacon lettuce carrot mix' by filling in 
        # an input, and clicking the save button, after which a success message
        # shows up in the modal
        self.check_element_content(
            'label[for="macro-meal-name"]',
            'css', 'text', 'Meal Name'
        )
        self.check_element_content(
            'label[for="macro-meal-notes"]',
            'css', 'text', 'Notes (Optional)'
        )
        self.check_element_content(
            'macro-meal-name',
            'id', 'placeholder', 'Meal Name'
        )
        self.check_element_content(
            'macro-meal-notes',
            'id', 'placeholder', 'Notes (Optional)'
        )

        self.fill_input(
            [
                "input[id='macro-meal-name']",
                "textarea[id='macro-meal-notes']",
            ],
            ['bacon lettuce carrot mix', 'best as a salad']
        )

        self.browser.find_element_by_id('save-macro-meal-button').click()

        self.check_element_content(
            'macro-meal-save-status', 'id', 'text',
            'Successfully Saved!')

        time.sleep(3)
        self.assertFalse(save_modal.is_displayed())


        # Joe spaces and hits the saves meal button and tries to save the same meal
        # with the same name 'bacon lettuce carrot mix', but gets an error message

        save_meal_button.click()
        self.fill_input(["input[id='macro-meal-name']"],[], clear=True)
        self.fill_input(
            ["input[id='macro-meal-name']"], ['bacon lettuce carrot mix']
        )
        self.browser.find_element_by_id('save-macro-meal-button').click()

        self.check_element_content(
            'macro-meal-save-status', 'id', 'text',
            'duplicate key value violates unique constraint "meals_foods_name_key"')

        self.fail('Finish The Test!')

        #He then adujst the remaining foods so that all the bars fall within the stdev
        #style bars and then hits the "Save Meal" button below.

        #A modal form pops up, with input box at the top with place holder "Meal Name"
        #Below that is a table summarizing the macros, their amounts, and precentages
        #Below that is bulleted list of the foods and their amounts.

        #Joe enters "Joe Salad" into the meal name input box

        #Below that is a comments box with the place holder "Recipie Notes", where 
        #Joe enters "this salad is best when the kidney beans are smashed a bit, 
        #and with pleny of pepper.

        #Below this is a "Submit" and "Cancel" button, Joe hits "Submit".

        #After he hits "Submit" and a confirmation dialog box replaces the submit and 
        #cancel buttons saying "Meal Saved! View and/or adjust on the My Recipes Tab. 
        #Joe hits the "OK" button and the modal box dissapears

        #He notices that the confirmation box dissapears, and that the Meal Maker tab
        #has returned to its initial state with no added foods.

        #Joe decides he want to make another salad, but one with different macro goals.
        #He hits the "Customize Macros".

        #A modal form pops up with all the macros listed and next to each, an input box
        #with a place holder of their current macros. 

        #He changes the percentages to fat/carbs/protein 50/25/25 and hits the "Apply" 
        #button and the modal disappears.

        #He notices the macros in the summary table have changed to reflect his changes
        #and the meal bars have also changed to reflect the changes.

        #He decides he want to change them again so he clicks the "Customize Macros"
        #button and then once the form comes up, he decides against it, and clicks the
        #"Cancel" button and the modal disappears and nothing has changed.

        #He then searches for and adds kale, cucumbers, ham, and peas. He then adusts
        #their drag bars to fit the target meal and he hits the "Save Meal" button.

        #When the modal comes up, he enters, once again "Joe Salad", enters no
        #Recipe Notes and hits "Submit".  After this, an alert message shows up,
        #above the Submit and Cancel buttons,
        #informing Joe that this Meal Name is already taken, and to enter a new one.

        #Joe enters "Green Salad", and saves the meal,
        #and closes the out after the confirmation message.

        #A week later Joe wants to make the Green salad so he goes to the "My Meals" tab

