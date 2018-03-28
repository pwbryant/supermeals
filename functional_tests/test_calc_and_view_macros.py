from .base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.contrib.auth.models import User
import time

class CalcAndViewMacros(FunctionalTest):

    def test_can_calculate_macros(self):
        USERNAME, PASSWORD = "JoeSchmoe","123pass123"
        #Joe signs in as guest to calc his macros
        self.browser.get(self.live_server_url)
        User.objects.create_user(username=USERNAME,password=PASSWORD)
        self.login_user(USERNAME,PASSWORD)

        #self.browser.find_element_by_id("id_as_guest")
        #Joe, signed in as a guest, got to the Calculate Macros tab and sees the header
        #"Total Daily Energy Expenditure (TDEE)"
        self.browser.find_element_by_id("my-macros-tab").click()
        macro_header = self.browser.find_element_by_id("my-macros-headline").text
        self.assertEqual(macro_header,"Find Total Daily Energy Expenditure (TDEE)")

        #The form has fields unit type Gender, Age, Sex, Weight, Height, Activity level,
        #options for weight gain,maintain,and loss, and the desired rate of change and a
        #Calculate button. The radio buttons for unit type, gender, activity, and weight change
        #have "Imperial", "Male", "Low Activity", and "Loss" preselected
        self.check_element_content("unit-type","id","text","Unit Type","div")
        self.assertTrue(self.browser.find_element_by_css_selector("input[name='unit-type'][value='imperial']").is_selected())
        self.assertFalse(self.browser.find_element_by_css_selector("input[name='unit-type'][value='metric']").is_selected())


        self.check_element_content("traits","id","text","Physical Traits","div")
        self.assertFalse(self.browser.find_element_by_css_selector("input[name='gender'][value='male']").is_selected())
        self.assertFalse(self.browser.find_element_by_css_selector("input[name='gender'][value='female']").is_selected())
        self.check_element_content("age-input","id","text","Age:","label")
        self.check_element_content("age-input","id","placeholder","Age","input")
        self.check_element_content("weight-input","id","text","Weight:","label")
        self.check_element_content("weight-input","id","placeholder","Weight(lb)","input")

        self.check_element_content("height-input","id","text","Height:","label")
        self.check_element_content("input[placeholder='ft']","css","placeholder","ft")
        self.check_element_content("input[placeholder='in']","css","placeholder","in")

        self.check_element_content("input[type='radio'][value='none']","css","value","none")

        self.check_element_content("activity","id","text","Activity Level","div")
        self.assertFalse(self.browser.find_elements_by_css_selector("input[type='radio'][value='none']")[0].is_selected())
        self.assertFalse(self.browser.find_elements_by_css_selector("input[type='radio'][value='light']")[0].is_selected())
        self.assertFalse(self.browser.find_elements_by_css_selector("input[type='radio'][value='medium']")[0].is_selected())
        self.assertFalse(self.browser.find_elements_by_css_selector("input[type='radio'][value='high']")[0].is_selected())
        self.assertFalse(self.browser.find_elements_by_css_selector("input[type='radio'][value='very high']")[0].is_selected())

        self.check_element_content("weight-change","id","text","Weight Change","div")
        self.assertTrue(self.browser.find_elements_by_css_selector("input[type='radio'][value='lose']")[0].is_selected())
        self.assertFalse(self.browser.find_elements_by_css_selector("input[type='radio'][value='maintain']")[0].is_selected())
        self.assertFalse(self.browser.find_elements_by_css_selector("input[type='radio'][value='gain']")[0].is_selected())


        self.check_element_content("change-rate-input","id","text","Rate of Change","label")
        self.check_element_content("change-rate-i","id","placeholder","lb/wk")

        self.check_element_content("calc-tdee","id","text","Calculate")

        #Out of Joe wants to enter his info in metric so he selects the metric radio button
        #and notices that height fields turn into just one input field with "cm" placeholder, 
        #and the weight and rate of change fields have "kg" and "kg/wk" respectively.

        self.browser.find_element_by_css_selector("input[name='unit-type'][value='metric']").click()
        self.check_element_content("input[name='weight-m']","css","placeholder","kg")
        self.check_element_content("input[name='height-m']","css","placeholder","cm")
        self.check_element_content("input[name='change-rate-m']","css","placeholder","kg/wk")

        #Joe suspects more content will be displayed after he hits Calculates, but as of now he only sees
        #the calc button at the bottom of the form
        macros_form = self.browser.find_element_by_id("choose-macros-form-container")
        self.assertTrue(macros_form.location['x'] < -9000 and macros_form.location['y'] < -9000) 

        #Joe changes back to imperial units and enters his info, and hits "Calculate", but too late he realized he had
        #female selected. Below the form, he sees his daily caloric expediture
        self.browser.find_element_by_css_selector("input[value='imperial']").click()
        macro_form_selectors = ["input[value='imperial']","input[value='female']","input[name='age']","input[name='weight-i']",
            "input[name='height-i-ft']","input[name='height-i-in']","input[value='none']","input[value='lose']",
            "input[name='change-rate-i']"]
        macro_form_values = [None,None,"34","210","5","10",None,None,"1"]
        self.fill_input(macro_form_selectors,macro_form_values)	
        self.browser.find_element_by_id("calc-tdee").click()
        self.check_element_content("tdee-result","id","text","Maintenance: 2079 Cals")
        self.check_element_content("change-tdee-result","id","text","Change: 1579 Cals")

        #After calculating TDEE, and area for choosing macro percent appers. With inputs for both
        #% and g for each macro, with % Remaing Footer, and a "Continue" button which is greyed out.
        #macros_form = self.browser.find_element_by_id("choose-macros-form-container")
        self.assertTrue(macros_form.location['x'] > 0 and macros_form.location['y'] > 0) 

        self.check_element_content("input[name='fat-pct']","css","placeholder","%")
        self.check_element_content("input[name='fat-g']","css","placeholder","g")
        self.check_element_content("input[name='carbs-pct']","css","placeholder","%")
        self.check_element_content("input[name='carbs-g']","css","placeholder","g")
        self.check_element_content("input[name='protein-pct']","css","placeholder","%")
        self.check_element_content("input[name='protein-g']","css","placeholder","g")
        choose_macro_form = self.browser.find_element_by_id("choose-macros-form")
        macro_row_headers = choose_macro_form.find_elements_by_css_selector("span")
        self.assertEqual(macro_row_headers[1].text,"%")
        self.assertEqual(macro_row_headers[2].text,"g")
        macro_row_labels = choose_macro_form.find_elements_by_css_selector("label")
        self.assertEqual(macro_row_labels[0].text,"Fat")
        self.assertEqual(macro_row_labels[1].text,"Carbs")
        self.assertEqual(macro_row_labels[2].text,"Protein")
        self.assertEqual(macro_row_labels[3].text,"% Left")
        continue_button = self.browser.find_element_by_id("choose-macros-continue-button")
        self.assertFalse(continue_button.is_enabled())

        #Joe switches to Male and hits Calculate again and sees his new TDEE
        self.fill_input(["input[value='male']"],[None])	
        self.browser.find_element_by_id("calc-tdee").click()
        self.check_element_content("tdee-result","id","text","Maintenance: 2279 Cals")
        self.check_element_content("change-tdee-result","id","text","Change: 1779 Cals")

        #Joe comes wants to see what happens when he selcts the maintain button so he clicks it
        #and sees that the change input box disappears
        self.fill_input(["input[value='maintain']"],[None])	
        change_rate_input = self.browser.find_element_by_id("change-rate-input")
        self.assertTrue(change_rate_input.location['x'] < -9000 and change_rate_input.location['y'] < -9000) 

        #He decides to choose the %50 carb, %30 fat, and %20 protein and notices that
        #after typeing in his percents, the inputs in the "g" column automatically get filled in
        #and the % remaing is updated
        macro_form_selectors = ["input[name='fat-pct']","input[name='carbs-pct']","input[name='protein-pct']"]
        macro_form_values = ["30","50","20"]
        self.fill_input(macro_form_selectors,macro_form_values)	
        self.check_element_content("input[name='protein-g']","css","value","89")
        self.check_element_content("choose-macros-total","id","text","0")

        #When the % Remaining equals 0, The Continue button becomes ungreyed and so Joe clicks it, and 
        #another section becomes visible which contains a header reading about optionlly breaking up
        #the daily calories, and an input ask prompting the user to enter how many meals/snacks 
        #per day?" And a "Set Calories" button which is disabled. 
        continue_button = self.browser.find_element_by_id("choose-macros-continue-button")
        self.assertTrue(continue_button.is_enabled())
        continue_button.click()
        self.check_element_content("#meal-template-meals-number-form-container .content-box__header","css","text","Break Up Your Daily Calories Into Meals/Snacks")
        self.check_element_content("#meal-template-meals-number-form-container .input__label","css","text","Number of meals/snacks per day?")
        self.check_element_content("input[name='meal-number']","css","placeholder","# meals/snacks")

        set_cals_button = self.browser.find_element_by_id("meal-template-set-cals-continue-button")
        self.assertEqual(set_cals_button.text,"Continue")
        self.assertFalse(set_cals_button.is_enabled())
        #Joe enters 5, and clicks the Set Calories which becomes enabled once the the input is entered.
        #Another section appears where there are 5 inputs labeled meal/snack 1 - 5
        #with the inputs autofilled into five equal caloric chunks of 387.
        self.fill_input(["input[name='meal-number']"],["5"])	
        self.assertTrue(set_cals_button.is_enabled())

        empty_div = self.browser.find_element_by_id("meal-template-set-meal-cals-form-container").text
        self.assertEqual(empty_div,"")
        set_cals_button.click()
        set_meal_cals_table = self.browser.find_element_by_id("meal-template-set-meal-cals-form-container")
        table_labels = set_meal_cals_table.find_elements_by_tag_name("label")
        self.assertEqual(table_labels[0].text,"Meal 1")
        self.assertEqual(table_labels[1].text,"Meal 2")
        self.assertEqual(table_labels[2].text,"Meal 3")
        self.assertEqual(table_labels[3].text,"Meal 4")
        self.assertEqual(table_labels[4].text,"Meal 5")
        self.assertEqual(table_labels[5].text,"Remaining Cals")
        meal_0_input = set_meal_cals_table.find_element_by_css_selector("input[name=meal-0]")
        auto_filled_tdee_split_value = meal_0_input.get_attribute("value")
        self.assertEqual(auto_filled_tdee_split_value,"355.8")


        #Joe wants to have one meal of 200 cals so he changes Meal 1 to 200
        #and he notices that the Remaining Cals changes to 187, and the Save button grays out.
        meal_0_input.clear()
        meal_0_input.send_keys(200)
        remaining_cals_span = self.browser.find_element_by_id("meal-template-set-cals-total")
        remaining_cals = remaining_cals_span.text
        self.assertEqual(remaining_cals,"155.8")

        save_macros_button = self.browser.find_element_by_id("save-my-macros-button")
        self.assertEqual(save_macros_button.text,"Save Macro Info")
        self.assertFalse(save_macros_button.is_enabled())

        #Joe returns the meal 1 to 387 and when the save button is enabled he clicks it and soon gets a 
        #"Macros Sucessfully Saved" Alert message below the save button
        meal_0_input.clear()
        meal_0_input.send_keys("355.8")
        self.assertTrue(save_macros_button.is_enabled())
        save_macros_button.click()
        successful_post_message = self.browser.find_element_by_id("my-macros-successful-save").text
        self.assertEqual(successful_post_message,"Macros Successfully Saved! Now Go Make a Meal!")
