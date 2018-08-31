import json
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.http import HttpRequest, QueryDict
from django.contrib.auth.models import User

from meals.forms import SignUpForm, MakeMacrosForm, MacroMealForm, \
    DUPLICATE_USERNAME_ERROR, EMPTY_USERNAME_ERROR, EMPTY_PASSWORD_ERROR, \
    INVALID_USERNAME_ERROR, DEFAULT_INVALID_INT_ERROR, EMPTY_WEIGHT_ERROR, \
    EMPTY_HEIGHT_ERROR
from meals.models import Macros, MealTemplate, Foods, Servings, Ingredients
from meals.views import save_my_macros, save_meal_templates, \
    get_meal_maker_template, make_meal_template_unique_cal_dict_list, \
    make_macro_breakdown_dict_list, save_macro_meal
from meals.helpers import get_ingredient_count, save_meal
# Create your tests here.

USERNAME, EMAIL, PASSWORD = 'JoeSchmoe', 'joe@joemail.com', '321pass123!'
GUEST_USERNAME, GUEST_PASSWORD = 'guest', '321!beware'
BAD_USERNAME, BAD_PASSWORD = 'bad', 'badpass'

class MacroMealMakerTest(TestCase):

    def setUp(self):
        
        ing1 = Foods.objects.create(
            name='veggie pork',
            cals_per_gram=Decimal(1.6456),
            fat_per_gram=Decimal(.3418),
            carbs_per_gram=Decimal(.1519),
            protein_per_gram=Decimal(1.1646)
        )

        ing2 = Foods.objects.create(
            name='bbq',
            cals_per_gram=Decimal(1.72),
            fat_per_gram=Decimal(.0567),
            carbs_per_gram=Decimal(1.6308),
            protein_per_gram=Decimal(.0328)
        )


        servings1 = Servings.objects.create(
            description='bag',
            grams=Decimal(237),
            quantity=Decimal(1),
            food=ing1
        )

        servings1 = Servings.objects.create(
            description='tbsp',
            grams=Decimal(67),
            quantity=Decimal(4),
            food=ing2
        )

        self.food_amt_dict = {
            'name': 'veggie_pulled_pork_with_bbq_sauce',
            'cals_per_gram': '1.6622',
            'fat_per_gram': '0.2782',
            'carbs_per_gram': '0.4816',
            'protein_per_gram': '0.9123',
            'ingredient_id_0': f'{ing1.id}',
            'ingredient_amt_0': '1',
            'ingredient_unit_0': 'bag',
            'ingredient_id_1': f'{ing2.id}',
            'ingredient_amt_1': '4',
            'ingredient_unit_1': 'tbsp'
        }
       
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.food_amt_dict)
        self.request = HttpRequest()
        self.request.POST = query_dict


    def test_save_macro_meal_url(self):

        url = reverse('save_macro_meal')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


    def test_save_macro_meal_saves_meal(self):

        meal_name = self.food_amt_dict['name']

        url = reverse('save_macro_meal')
        response = json.loads(
            self.client.post(url, data=self.food_amt_dict).content
        )

        self.assertEqual(response['status'], 1)


    def test_get_ingredient_count(self):

        ingredient_count = get_ingredient_count(self.request.POST)
        self.assertEqual(ingredient_count, 2)


    def test_save_meal(self):

        meal_name = self.food_amt_dict['name']

        save_meal(self.food_amt_dict)

        foods = Foods.objects.filter(name=meal_name)
        self.assertEqual(foods.count(), 1)

        ingredients = Ingredients.objects.filter(main_food=foods[0])
        self.assertEqual(ingredients.count(), 2)


c = """
class MealMakerTest(TestCase):
    
    fixtures = ['db.json']

    #################################
    ##constants
    #################################
    MACRO_BREAKDOWN = [
            {
                    'name':'Fat',
                    'percent':34,
                    'data':Decimal('34.00')
            },{
                    'name':'Carbs',
                    'percent':33,
                    'data':Decimal('33.00')
            },
            {
                    'name':'Protein',
                    'percent':33,
                    'data':Decimal('33.00')
            }
    ]

    MEAL_TEMPLATES = [{
                            'value':527,
                            'text':'Meal 1,2,3 - 527 cals'
                    },{
                            'value':301,
                            'text':'Meal 4 - 301 cals'
                    }]

    #################################
    ##helper functions
    #################################
    def create_default_macro(self,user):
            macro = Macros.objects.create(**{
                    'user':user,
                    'unit_type':'imperial',
                    'gender':'male',
                    'age':34,
                    'direction':'lose',
                    'activity':'light',
                    'height':Decimal('177.8'),
                    'weight':Decimal('95.25'),
                    'change_rate':Decimal('.45359237'),
                    'protein_percent':Decimal('33'),
                    'fat_percent':Decimal('34')
            })
            return macro
            
    def create_default_meal_templates(self,user):
        meal_template1 = MealTemplate.objects.create(user=user,name='meal_0',cals_percent=Decimal('28'))
        meal_template2 = MealTemplate.objects.create(user=user,name='meal_1',cals_percent=Decimal('28'))
        meal_template3 = MealTemplate.objects.create(user=user,name='meal_2',cals_percent=Decimal('28'))
        meal_template4 = MealTemplate.objects.create(user=user,name='meal_3',cals_percent=Decimal('16'))
        return(meal_template1,meal_template2,meal_template3,meal_template4)

    def log_in_user(self,USERNAME,PASSWORD):
        user = User.objects.create_user(username=USERNAME,password=PASSWORD)
        self.client.post('/accounts/login/', data={'username':USERNAME, 'password':PASSWORD})
        return user

    #################################
    ##search
    #################################
    def test_search_food_url_returns_food_dict_with_array_greater_than_0(self):
        user = self.log_in_user(USERNAME,PASSWORD)
        response = self.client.get('/meals/search-foods/',data={'search_terms':'garbonzo beans'})
        response_dict = json.loads(response.content.decode())
        self.assertTrue(len(response_dict['search_results']) > 0)
    
    #################################
    ##open tab
    #################################
    def test_meal_maker_url_renders_correct_template(self):
        user = self.log_in_user(USERNAME,PASSWORD)
        self.create_default_macro(user)

        response = self.client.get('/meals/meal-maker/')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'meal_maker.html')

    def test_make_meal_template_unique_cal_dict_list_returns_list_of_dicts(self):
        user = self.log_in_user(USERNAME,PASSWORD)
        macro = self.create_default_macro(user)
        self.create_default_meal_templates(user)

        expected_result = self.MEAL_TEMPLATES
        self.assertEqual(make_meal_template_unique_cal_dict_list(user,macro.calc_tdee()),expected_result)

    def test_make_meal_template_macro_breakdown_dict_returns_list_of_dicts(self):
        user = self.log_in_user(USERNAME,PASSWORD)
        macro = self.create_default_macro(user)
        self.create_default_meal_templates(user)
        
        expected_result = self.MACRO_BREAKDOWN 
        self.assertEqual(make_macro_breakdown_dict_list(macro),expected_result)

    def test_get_meal_maker_template_uses_correct_form(self):

        user = self.log_in_user(USERNAME, PASSWORD)
        response = self.client.get('/meals/meal-maker/')
        self.assertIsInstance(response.context['macro_meal_form'], MacroMealForm)

    def test_get_meal_maker_template_no_macro_returns_correct_html(self):
            
        user = self.log_in_user(USERNAME,PASSWORD)

        request = HttpRequest()
        request.user = user
        response = get_meal_maker_template(request)
        expected_html = render_to_string('meal_maker.html',{})
        self.assertMultiLineEqual(response.content.decode(),expected_html)
        self.assertIn('%',response.content.decode())
        self.assertNotIn('id_goal_meal_cals_select',response.content.decode())
            
    def test_get_meal_maker_template_has_macro_returns_correct_html(self):
            
        user = self.log_in_user(USERNAME,PASSWORD)
        default_macro = self.create_default_macro(user)
        meal_templates = self.create_default_meal_templates(user)
        
        request = HttpRequest()
        request.user = user
        response = get_meal_maker_template(request)
        expected_html = render_to_string('meal_maker.html',{
                'tdee':1883,
                'meal_templates':self.MEAL_TEMPLATES,
                'macro_breakdown':self.MACRO_BREAKDOWN
        })
        self.assertMultiLineEqual(response.content.decode(),expected_html)
        self.assertNotIn("value='34'",response.content.decode())
        self.assertIn('goal-meal-cals-select',response.content.decode())


class LoginLogoffTest(TestCase):
    
    def test_anonymous_user_home_redirects_to_login_template(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/accounts/login/')

    def test_can_login_as_authenticated_user(self):
        username,password = USERNAME,PASSWORD
        user = User.objects.create_user(username=username,password=password)
        response = self.client.post('/accounts/login/', data={'username':username, 'password':password})
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')

    def test_can_login_as_guest(self):
        guest_user = User.objects.create_user(username=GUEST_USERNAME,password=GUEST_PASSWORD)
        response = self.client.post('/accounts/login/', data={'username':GUEST_USERNAME, 'password':GUEST_PASSWORD})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')

    def test_login_error_renders_login_page(self):
        response = self.client.post('/accounts/login/', data={'username':BAD_USERNAME, 'password':BAD_PASSWORD})
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'registration/login.html')

    def test_login_error_shows_up_on_login_page(self):
        response = self.client.post('/accounts/login/', data={'username':BAD_USERNAME, 'password':BAD_PASSWORD})
        expected_error = "Your username and password didn't match. Please try again."
        self.assertContains(response,expected_error)

    def test_logoff(self):
        guest_user = User.objects.create_user(username=GUEST_USERNAME,password=GUEST_PASSWORD)
        response = self.client.post('/accounts/login/', data={'username':GUEST_USERNAME, 'password':GUEST_PASSWORD})
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'base.html')

        response = self.client.post('/accounts/logout/')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/accounts/login/')


class CreateAccountTest(TestCase):

    def test_sign_up_button_leads_to_correct_template(self):
        response = self.client.get('/meals/sign-up/')
        self.assertTemplateUsed(response, 'sign_up.html')
    
    def test_sign_up_page_uses_sign_up_form(self):
        response = self.client.get('/meals/sign-up/')
        self.assertIsInstance(response.context['form'], SignUpForm)

    def test_can_save_POST_and_create_user_account(self):
        request = HttpRequest()
        response = self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        self.assertEqual(User.objects.count(),1)
        new_user = User.objects.first()
        self.assertTrue(authenticate(request,username=USERNAME,password=PASSWORD) is not None)

    def test_can_save_POST_and_create_user_account_redirects(self):
        response = self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], '/')
    
    def test_sign_up_blank_username_validation_error_wont_save_new_user(self):	
        USERNAME = ""
        response = self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        self.assertEqual(User.objects.count(),0)

    def test_sign_up_duplicate_username_validation_error_wont_save_new_user(self):	
        response = self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        response = self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        self.assertEqual(User.objects.count(),1)

    def test_sign_up_bad_username_validation_error_wont_save_new_user(self):	
        USERNAME = "joe blow"
        response = self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        self.assertEqual(User.objects.count(),0)
    
    def test_sign_up_blank_password_validation_error_wont_save_new_user(self):	
        PASSWORD =  ''
        response = self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        self.assertEqual(User.objects.count(),0)

    def test_sign_up_validation_error_render_sign_up_html(self):	
        response = self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        response = self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'sign_up.html')

    def test_sign_up_duplicate_validation_error_gets_sign_up_form_back(self):	
        username, email, password = USERNAME,EMAIL,PASSWORD
        response = self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        response = self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        self.assertIsInstance(response.context['form'], SignUpForm)

    def test_sign_up_duplicate_user_validation_error_message_shows_up_on_sign_up_html(self):	
        response = self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        response = self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        self.assertContains(response,DUPLICATE_USERNAME_ERROR)

    def test_sign_up_bad_username_validation_error_message_shows_up_on_sign_up_html(self):	
        USERNAME = 'Joe Schmoe'
        response = self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        self.assertContains(response,INVALID_USERNAME_ERROR)

    def test_sign_up_missing_password_validation_error_message_shows_up_on_sign_up_html(self):	
        PASSWORD =''
        response = self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        self.assertContains(response,EMPTY_PASSWORD_ERROR)


class MyMacrosTabTest(TestCase):

    SHARED_MACRO_DATA = {'gender':'male','age':'34','activity':'none','direction':'lose','fat-g':'10','fat-pct':'30',
                    'protein-g':'10','protein-pct':'30','carbs-g':'10','carbs-pct':'40','meal-0':'287',
                            'meal-1':'287','meal-2':'287','meal-3':'285','meal-4':'289','meal-number':'5','tdee':'1435'}
    IMPERIAL_MACRO_DATA = {**SHARED_MACRO_DATA,**{'unit-type':'imperial','height-i-ft':'5','height-i-in':'10','weight-i':'210','change-rate-i':'2'}}
    METRIC_MACRO_DATA = {**SHARED_MACRO_DATA,**{'unit-type':'metric','height-m':'5','weight-m':'210','change-rate-m':'2'}}
    
    def setup_user_request_for_post_to_view(self,post_data):
        request = HttpRequest()
        request.POST = post_data
        request.user = User.objects.create_user(username=USERNAME, email=EMAIL,password=PASSWORD)
        return request

    def test_my_macros_url_renders_correct_template(self):
        response = self.client.get('/meals/get-my-macros/')
        self.assertTemplateUsed(response, 'my_macros.html')

    def test_my_macros_template_uses_my_macros_form(self):
        response = self.client.get('/meals/get-my-macros/')
        self.assertIsInstance(response.context['form'], MakeMacrosForm)

    def test_save_my_macros_imperial_macros(self):
        request = self.setup_user_request_for_post_to_view(self.IMPERIAL_MACRO_DATA)
        response = save_my_macros(request)
        saved_macro = Macros.objects.all()
        self.assertEqual(saved_macro.count(),1)		

    def test_save_meal_templates_imperial_macros(self):
        request = self.setup_user_request_for_post_to_view(self.IMPERIAL_MACRO_DATA)
        response = save_meal_templates(request)
        saved_macro = MealTemplate.objects.all()
        self.assertEqual(saved_macro.count(),5)		

    def test_save_my_macros_metric_macros(self):
        request = self.setup_user_request_for_post_to_view(self.METRIC_MACRO_DATA)
        response = save_my_macros(request)
        saved_macro = Macros.objects.all()
        self.assertEqual(saved_macro.count(),1)		

    def test_save_meal_templates_metric_macros(self):
        request = self.setup_user_request_for_post_to_view(self.METRIC_MACRO_DATA)
        response = save_meal_templates(request)
        saved_macro = MealTemplate.objects.all()
        self.assertEqual(saved_macro.count(),5)		
    
    def test_save_my_macro_returns_status_dict_with_status_of_1_if_success(self):
        request = self.setup_user_request_for_post_to_view(self.METRIC_MACRO_DATA)
        response = save_my_macros(request)
        self.assertEqual(response['status'],1)
        self.assertIsInstance(response['form'],MakeMacrosForm)
        self.assertEqual(response['unit-type'],'metric')

    def test_save_meal_templates_returns_status_dict_with_status_of_1_if_success(self):
            request = self.setup_user_request_for_post_to_view(self.METRIC_MACRO_DATA)
            response = save_meal_templates(request)
            self.assertEqual(response['status'],1)

    def test_save_my_macros_and_meal_templates_saves_imperial_macros(self):
        self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        response=self.client.post('/meals/save-my-macros', data=self.IMPERIAL_MACRO_DATA)
        saved_macro = Macros.objects.all()
        self.assertEqual(saved_macro.count(),1)		
        saved_meal_template = MealTemplate.objects.all()
        self.assertEqual(saved_meal_template.count(),5)		

    def test_save_my_macros_and_meal_templates_saves_imperial_macros(self):
        self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        response=self.client.post('/meals/save-my-macros', data=self.IMPERIAL_MACRO_DATA)
        self.assertEqual(response.content.decode(),'1')

    def test_save_my_macros_saves_imperial_macros_in_metric(self):
        request = self.setup_user_request_for_post_to_view(self.IMPERIAL_MACRO_DATA)
        save_my_macros(request)
        macro_obj = Macros.objects.first()
        self.assertEqual(macro_obj.height,Decimal('177.80'))
        self.assertEqual(macro_obj.weight,Decimal('95.25'))
        self.assertEqual(macro_obj.change_rate,Decimal('0.90718474'))

    def test_save_my_macros_saves_metric_macros_in_metric(self):
        request = self.setup_user_request_for_post_to_view(self.METRIC_MACRO_DATA)
        save_my_macros(request)
        macro_obj = Macros.objects.first()
        self.assertEqual(macro_obj.height,Decimal('5.00'))
        self.assertEqual(macro_obj.weight,Decimal('210.00'))
        self.assertEqual(macro_obj.change_rate,Decimal('2.00'))

    def test_save_my_macro_wont_save_duplicate_macro_and_meal_template_but_still_returns_1(self):
        self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        self.client.post('/meals/save-my-macros', data=self.IMPERIAL_MACRO_DATA)
        response=self.client.post('/meals/save-my-macros', data=self.IMPERIAL_MACRO_DATA)
        saved_macro = Macros.objects.all()
        saved_meal_template = Macros.objects.all()
        self.assertEqual(saved_macro.count(),1)		
        self.assertEqual(saved_meal_template.count(),1)		

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "1")

    def test_save_my_macro_missing_field_validation_wont_save_macro_and_meal_template(self):	
        self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        macro_data = self.IMPERIAL_MACRO_DATA.copy()
        macro_data.pop('age')
        response=self.client.post('/meals/save-my-macros', data=macro_data)
        saved_macro = Macros.objects.all()
        saved_meal_template = Macros.objects.all()
        self.assertEqual(saved_macro.count(),0)		
        self.assertEqual(saved_meal_template.count(),0)		


    def test_save_my_macro_validation_error_gets_back_MakeMacrosForm(self):	
        self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        macro_data = self.IMPERIAL_MACRO_DATA.copy()
        macro_data.pop('age')
        response=self.client.post('/meals/save-my-macros', data=macro_data)
        
        self.assertEqual(response.status_code,200)
        self.assertIsInstance(response.context['form'], MakeMacrosForm)

    def test_save_my_macro_validation_error_render_my_macros_html(self):	
        self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        macro_data = self.IMPERIAL_MACRO_DATA.copy()
        macro_data.pop('age')
        response=self.client.post('/meals/save-my-macros', data=macro_data)
        
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'my_macros.html')

    def test_save_my_macro_validation_error_shows_up_on_my_macro_html(self):	
        self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        macro_data = self.IMPERIAL_MACRO_DATA.copy()
        macro_data['age'] = 'str'
        macro_data['weight-i'] = ''
        response=self.client.post('/meals/save-my-macros', data=macro_data)
        self.assertContains(response,DEFAULT_INVALID_INT_ERROR)
        self.assertContains(response,EMPTY_WEIGHT_ERROR)

        macro_data = self.METRIC_MACRO_DATA.copy()
        macro_data['height-m'] = ''
        response=self.client.post('/meals/save-my-macros', data=macro_data)
        self.assertContains(response,EMPTY_HEIGHT_ERROR)

    def test_make_macro_can_save_meal_template(self):
        self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        response=self.client.post('/meals/save-my-macros', data=self.METRIC_MACRO_DATA)

    def test_save_my_macro_and_meal_template_retuns_1_upon_successfull_save(self):
        self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        response=self.client.post('/meals/save-my-macros', data=self.METRIC_MACRO_DATA)
        self.assertEqual(response.content.decode(),'1')

    def test_save_meal_template_validation_error_render_my_macros_html(self):	
        self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        macro_data = self.IMPERIAL_MACRO_DATA.copy()
        macro_data.pop('tdee')
        response=self.client.post('/meals/save-my-macros', data=macro_data)
        
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'my_macros.html')

    def test_save_meal_template_validation_error_shows_up_on_my_macro_html(self):	
        self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        macro_data = self.IMPERIAL_MACRO_DATA.copy()
        macro_data.pop('tdee')
        response=self.client.post('/meals/save-my-macros', data=macro_data)
        self.assertContains(response,'TDEE Missing')

    def test_save_meal_template_validation_error_gets_back_MakeMacrosForm(self):	
        self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        macro_data = self.IMPERIAL_MACRO_DATA.copy()
        macro_data.pop('tdee')
        response=self.client.post('/meals/save-my-macros', data=macro_data)
        
        self.assertIsInstance(response.context['form'], MakeMacrosForm)

"""
