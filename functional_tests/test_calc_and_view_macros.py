from .base import FunctionalTest
# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
from django.contrib.auth.models import User
import time

class CalcAndViewMacros(FunctionalTest):

    def test_can_calculate_macros(self):
        USERNAME, PASSWORD = 'JoeSchmoe', '123pass123'
        # Joe signs in as guest to calc his macros
        self.browser.get(self.live_server_url)
        User.objects.create_user(username=USERNAME, password=PASSWORD)
        self.login_user(USERNAME, PASSWORD)

        # Joe, signed in as a guest, got to the Calculate Macros tab and sees
        # the header 'Total Daily Energy Expenditure (TDEE)'
        self.browser.find_element_by_id('my-macros-tab').click()
        macro_header = self.browser.find_element_by_id('my-macros-headline').text
        self.assertEqual(
            macro_header, 'Find Total Daily Energy Expenditure (TDEE)'
        )

        # The form has fields unit type Gender, Age, Sex, Weight, Height, Activity
        # level, options for weight gain,maintain,and loss, and the desired rate
        # of change and a Calculate button. The radio buttons for unit type,
        # gender, activity, and weight change #have 'Imperial', 'Male',
        # 'Low Activity', and 'Loss' preselected
        self.check_element_content(
            'label[for="unit-input-container"]', 'css', 'text',
            'Unit Type'
        )
        imperial_unit_select = self.browser.find_element_by_css_selector(
            'input[name="unit_type"][value="imperial"]'
        )
        self.assertTrue(imperial_unit_select.is_selected())

        metric_unit_select = self.browser.find_element_by_css_selector(
            'input[name="unit_type"][value="metric"]'
        )
        self.assertFalse(metric_unit_select.is_selected())

        self.check_element_content(
            'label[for="gender-inputs"]', 'css', 'text', 'Physical Traits'
        )
        male_select = self.browser.find_element_by_css_selector(
            "input[name='gender'][value='male']"
        )
        female_select = self.browser.find_element_by_css_selector(
            "input[name='gender'][value='female']"
        )
        self.assertFalse(male_select.is_selected())
        self.assertFalse(female_select.is_selected())

        self.check_element_content('age-input', 'id', 'text', 'Age', 'label')
        self.check_element_content(
            'age-input', 'id', 'placeholder', 'Age', 'input'
        )
        self.check_element_content(
            'weight-input', 'id', 'text', 'Weight', 'label'
        )
        self.check_element_content(
            'weight-input', 'id', 'placeholder', 'lbs', 'input'
        )

        self.check_element_content(
            'height-input', 'id', 'text', 'Height', 'label'
        )
        self.check_element_content(
            "input[placeholder='ft']", 'css', 'placeholder', 'ft'
        )
        self.check_element_content(
            "input[placeholder='in']", 'css', 'placeholder', 'in'
        )
        self.check_element_content(
            "input[type='radio'][value='none']", 'css', 'value', 'none'
        )

        activty_label = (
            "Activity Level (Don't get hung up on these. When in doubt, "
            "be conservative)"
        )
        self.check_element_content(
            'label[for="activity-inputs"]', 'css', 'text', activty_label
        )
        none_activity = self.browser.find_elements_by_css_selector(
            "input[type='radio'][value='none']"
        )[0]
        light_activity = self.browser.find_elements_by_css_selector(
            "input[type='radio'][value='none']"
        )[0]
        medium_activity = self.browser.find_elements_by_css_selector(
            "input[type='radio'][value='medium']"
        )[0]
        high_activity = self.browser.find_elements_by_css_selector(
            "input[type='radio'][value='high']"
        )[0]
        very_high_activity = self.browser.find_elements_by_css_selector(
            "input[type='radio'][value='very high']"
        )[0]
        self.assertFalse(none_activity.is_selected())
        self.assertFalse(light_activity.is_selected())
        self.assertFalse(medium_activity.is_selected())
        self.assertFalse(high_activity.is_selected())
        self.assertFalse(very_high_activity.is_selected())

        self.check_element_content(
            'label[for="direction-inputs"]', 'css', 'text', 'Weight Change'
        )
        lose_select = self.browser.find_elements_by_css_selector(
            "input[type='radio'][value='lose']"
        )[0]
        maintain_select = self.browser.find_elements_by_css_selector(
            "input[type='radio'][value='maintain']"
        )[0]
        gain_select = self.browser.find_elements_by_css_selector(
            "input[type='radio'][value='gain']"
        )[0]
        self.assertTrue(lose_select.is_selected())
        self.assertFalse(maintain_select.is_selected())
        self.assertFalse(gain_select.is_selected())

        self.check_element_content(
            'change-rate-input', 'id', 'text', 'Rate of Change', 'label'
        )
        self.check_element_content(
            'my-macros-change-rate', 'id', 'placeholder', 'lbs/wk'
        )
        self.check_element_content('calc-tdee', 'id', 'text', 'Calculate')

        # Out of Joe wants to enter his info in metric so he selects the metrict
        # radio button and notices that height fields turn into just one input
        # field with 'cm' placeholder, and the weight and rate of change fields
        # have 'kg' and 'kg/wk' respectively.
        self.browser.find_element_by_css_selector(
            "input[name='unit_type'][value='metric']"
        ).click()
        self.check_element_content(
            "input[name='weight']", 'css', 'placeholder', 'kgs'
        )
        self.check_element_content(
            "input[name='height_0']", 'css', 'placeholder', 'cm'
        )
        self.check_element_content(
            "input[name='change_rate']", 'css', 'placeholder', 'kgs/wk'
        )

        # Joe suspects more content will be displayed after he hits Calculates,
        # but as of now he only sees the calc button at the bottom of the form
        macros_form = self.browser.find_element_by_id(
            'choose-macros-container'
        )
        self.assertTrue(
            macros_form.location['x'] < -9000
            and macros_form.location['y'] < -9000
        )

        # Joe changes back to imperial units and enters his info, and hits
        # 'Calculate', but too late he realized he had female selected. Below
        # the form, he sees his daily caloric expediture
        self.browser.find_element_by_css_selector("input[value='imperial']").click()
        macro_form_selectors = [
            "input[value='imperial']", "input[value='female']",
            "input[name='age']",
            "input[name='weight']", "input[name='height_0']",
            "input[name='height_1']", "input[value='none']",
            "input[value='lose']", "input[name='change_rate']"
        ]
        macro_form_values = [None, None, '34', '210', '5', '10', None, None, '1']
        self.fill_input(macro_form_selectors, macro_form_values)
        self.browser.find_element_by_id('calc-tdee').click()

        self.check_element_content(
            'tdee-result', 'id', 'text', 'Maintenance: 2079 Cals'
        )
        self.check_element_content(
            'change-tdee-result', 'id', 'text', 'Change: 1579 Cals'
        )

        # After calculating TDEE, and area for choosing macro percent appers.
        # With inputs for both  % and g for each macro, with % Remaing Footer,t

        macros_form = self.browser.find_element_by_id(
            'choose-macros-container'
        )
        self.assertTrue(
            macros_form.location['x'] > 0 and macros_form.location['y'] > 0
        )
        self.check_element_content(
            "input[name='fat_percent']", 'css', 'placeholder', '%'
        )
        self.check_element_content(
            "input[name='fat_g']", 'css', 'placeholder', 'g'
        )
        self.check_element_content(
            "input[name='carbs_percent']", 'css', 'placeholder', '%'
        )
        self.check_element_content(
            "input[name='carbs_g']", 'css', 'placeholder', 'g'
        )
        self.check_element_content(
            "input[name='protein_percent']", 'css', 'placeholder', '%'
        )
        self.check_element_content(
            "input[name='protein_g']", 'css', 'placeholder', 'g'
        )
        choose_macro_form = self.browser.find_element_by_id('choose-macros')
        macro_row_headers = choose_macro_form.find_elements_by_css_selector('span')
        self.assertEqual(macro_row_headers[1].text, '%')
        self.assertEqual(macro_row_headers[2].text, 'g')
        macro_row_labels = choose_macro_form.find_elements_by_css_selector('label')
        self.assertEqual(macro_row_labels[0].text, 'Fat')
        self.assertEqual(macro_row_labels[1].text, 'Carbs')
        self.assertEqual(macro_row_labels[2].text, 'Protein')
        self.assertEqual(macro_row_labels[3].text, 'Pct. Left')

        save_button = self.browser.find_element_by_id('save-my-macros-button')
        self.assertFalse(save_button.is_enabled())

        #Joe switches to Male and hits Calculate again and sees his new TDEE
        self.fill_input(["input[value='male']"], [None])
        self.browser.find_element_by_id('calc-tdee').click()
        self.check_element_content(
            'tdee-result', 'id', 'text', 'Maintenance: 2279 Cals'
        )
        self.check_element_content(
            'change-tdee-result', 'id', 'text', 'Change: 1779 Cals'
        )

        # Joe comes wants to see what happens when he selcts the maintain
        # button so he clicks it and sees that the change input box disappears
        self.fill_input(["input[value='maintain']"], [None])
        change_rate_input = self.browser.find_element_by_id(
            'my-macros-change-rate'
        )
        self.assertTrue(
            change_rate_input.location['x'] < -9000
            and change_rate_input.location['y'] < -9000
        )

        # He decides to choose the %50 carb, %30 fat, and %20 protein and
        # notices that after typeing in his percents, the inputs in the 'g'
        # column automatically get filled in and the % remaing is updated
        macro_form_selectors = [
            "input[name='fat_percent']", "input[name='carbs_percent']",
            "input[name='protein_percent']"
        ]
        macro_form_values = ['30', '50', '20']
        self.fill_input(macro_form_selectors, macro_form_values)
        self.check_element_content("input[name='protein_g']", 'css', 'value', '89')
        self.check_element_content('choose-macros-total', 'id', 'text', '0')

        # When the % Remaining equals 0, The Continue button becomes ungreyed
        # and so Joe clicks it, and another section becomes visible which
        # contains a header reading about optionlly breaking up the daily
        # calories, and an input ask prompting the user to enter how many
        # meals/snacks per day?' And a 'Set Calories' button which is disabled.

        self.assertTrue(save_button.is_enabled())
        save_button.click()
        successful_post_message = self.browser.find_element_by_id(
            'my-macros-successful-save'
        ).text
        self.assertEqual(
            successful_post_message,
            'Macros Successfully Saved! Now Go Make a Meal!'
        )
