import json
from decimal import Decimal
from datetime import datetime, timedelta

from django.test import TestCase
from django.urls import reverse
from django.http import HttpRequest, QueryDict
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.template.loader import render_to_string
from django import forms

from meals.forms import (
    SignUpForm,
    MakeMacrosForm,
    MacroMealForm,
    MacroIngredientForm,
    NewFoodForm,
    NewFoodServingForm,
    DUPLICATE_USERNAME_ERROR,
    EMPTY_USERNAME_ERROR,
    EMPTY_PASSWORD_ERROR,
    INVALID_USERNAME_ERROR,
    DEFAULT_INVALID_INT_ERROR,
    EMPTY_WEIGHT_ERROR,
    EMPTY_HEIGHT_ERROR,
)
from meals.models import (
    Macros,
    Foods,
    FoodGroup,
    Servings,
    Ingredients,
    FoodNotes,
    FoodType,
)
from meals.views import (
    MyMacros,
    get_meal_maker_template,
    make_macro_breakdown_dict_list,
    save_macro_meal,
    search_my_meals,
)
from meals.helpers import get_ingredient_count


# CONTANTS
# ===================================================
USERNAME, EMAIL, PASSWORD = "JoeSchmoe", "joe@joemail.com", "321pass123!"
GUEST_USERNAME, GUEST_PASSWORD = "guest", "321!beware"
BAD_USERNAME, BAD_PASSWORD = "bad", "badpass"


# OTHER CLASSES
# ===================================================
class BaseTestCase(TestCase):
    def log_in_user(self, username, password):
        user = User.objects.create_user(username=username, password=password)
        self.client.post(
            "/accounts/login/", data={"username": username, "password": password}
        )
        return user


# VIEW TESTS
# ===================================================
# Create your tests here.
class NewFoodTest(BaseTestCase):
    def setUp(self):

        self.user = self.log_in_user(USERNAME, PASSWORD)

        self.url = reverse("add_food")
        self.get_response = self.client.get(self.url)

        FoodGroup.objects.create(name="Veggies")
        FoodType.objects.create(name="food")

        self.post = {
            "name": "Broccoli",
            "grams": Decimal(100),
            "quantity": Decimal(1),
            "description": "cup",
            "cals": Decimal(50),
            "fat": Decimal(2),
            "carbs": Decimal(10),
            "sugar": Decimal(5),
            "protein": Decimal(2),
            "food_group": "Veggies",
        }

    def test_add_food_url(self):
        self.assertEqual(self.get_response.status_code, 200)
        self.assertTemplateUsed(self.get_response, "meals/add_food.html")

    def test_add_food_uses_correct_form(self):
        self.assertIsInstance(self.get_response.context["add_food_form"], NewFoodForm)

    def test_add_food_uses_correct_srv_form(self):
        self.assertIsInstance(
            self.get_response.context["add_food_srv_form"], NewFoodServingForm
        )

    def test_add_food_url_renders_correct_template_as_guest(self):
        url = reverse("add_food")
        self.log_in_user("guest", "password")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "meals/bad_raw_url.html")

    def test_add_food_post_saves_food(self):
        NewFoodForm.choices += (
            (
                "Veggies",
                "Veggies",
            ),
        )
        response = json.loads(self.client.post(self.url, self.post).content)
        self.assertEqual(response["status_code"], 201)
        new_foods = Foods.objects.all()
        self.assertEqual(new_foods.count(), 1)

    def test_add_food_post_saves_srv(self):
        response = json.loads(self.client.post(self.url, self.post).content)
        new_food = Foods.objects.get(name=self.post["name"])
        new_srv = Servings.objects.filter(food=new_food)
        self.assertEqual(new_srv.count(), 1)

    def test_add_food_save_sets_user_on_new_food(self):
        response = json.loads(self.client.post(self.url, self.post).content)
        new_food = Foods.objects.all()[0]
        self.assertEqual(new_food.user, self.user)

    def test_add_food_can_handle_bad_post(self):
        self.post["name"] = ""
        response = json.loads(self.client.post(self.url, self.post).content)
        self.assertEqual(response["status_code"], 400)
        new_foods = Foods.objects.all()
        self.assertEqual(new_foods.count(), 0)

    def test_add_food_can_displays_food_form_errors(self):
        self.post["name"] = ""
        response = json.loads(self.client.post(self.url, self.post).content)
        expected_error = "This field is required."
        self.assertTrue(expected_error in response["errors"]["name"])

    def test_add_food_can_displays_srv_form_errors(self):
        self.post["grams"] = "poo"
        response = json.loads(self.client.post(self.url, self.post).content)
        expected_error = "Enter a number."
        self.assertTrue(expected_error in response["errors"]["grams"])

    def test_add_food_can_handle_no_serving(self):
        self.post.pop("quantity")
        self.post.pop("description")
        response = json.loads(self.client.post(self.url, self.post).content)

        new_foods = Foods.objects.filter(name=self.post["name"])
        self.assertEqual(new_foods.count(), 1)


class BaseMakeFoodsTest(BaseTestCase):
    def setUp(self):

        self.user = self.log_in_user(USERNAME, PASSWORD)

        Servings.objects.create(
            food=None, description="g", grams=Decimal(1), quantity=Decimal(1)
        )

        self.my_meals_fg = FoodGroup.objects.create(name="My Meals")
        self.veg_fg = FoodGroup.objects.create(name="Veggies")
        self.meat_fg = FoodGroup.objects.create(name="Meats")

        self.peanut_butter = Foods.objects.create(
            name="Peanut Butter",
            cals_per_gram=Decimal(5.9),
            fat_per_gram=Decimal(4.491),
            carbs_per_gram=Decimal(0.8732),
            sugar_per_gram=Decimal(0.8732),
            protein_per_gram=Decimal(0.96),
        )
        self.peanut_butter_srv = Servings.objects.create(
            food=self.peanut_butter, grams=10, quantity=1, description="tbsp"
        )

        self.bananas = Foods.objects.create(
            name="Bananas",
            cals_per_gram=Decimal(0.89),
            fat_per_gram=Decimal(0.0297),
            carbs_per_gram=Decimal(0.9136),
            sugar_per_gram=Decimal(0.9136),
            protein_per_gram=Decimal(0.0436),
        )
        self.bananas_srv = Servings.objects.create(
            food=self.bananas, grams=100, quantity=1, description="cup"
        )

        self.post = {
            # added long decimals to test that they get rounded
            "name": "Peanut Butter Banana Blitz",
            "notes": "Blend for 5 minutes.",
            "ingredient_0": self.bananas.pk,
            "ingredient_amount_0": "2",
            "ingredient_unit_0": self.bananas_srv.pk,
            "ingredient_1": self.peanut_butter.pk,
            "ingredient_amount_1": "3",
            "ingredient_unit_1": self.peanut_butter_srv.pk,
        }

        # FoodGroup and FoodType creation
        FoodGroup.objects.create(name="My Recipes")
        FoodType.objects.create(name="recipe")


class DeleteRecipeTest(BaseMakeFoodsTest):
    def test_delete_recipe_url(self):
        url = reverse("delete_my_meals")
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 200)

    def test_delete_recipe_withough_meal_returns_status_0(self):
        url = reverse("delete_my_meals")
        response = json.loads(self.client.post(url, {}).content)
        self.assertEqual(response["status"], 0)

    def test_delete_recipe_withough_meal_returns_status_1(self):
        save_url = reverse("save_recipe")
        del_url = reverse("delete_my_meals")

        self.client.post(save_url, self.post)
        main_food = Foods.objects.get(name=self.post["name"])

        response = json.loads(
            self.client.post(del_url, {"meal_id": main_food.id}).content
        )
        self.assertEqual(response["status"], 1)

    def test_delete_recipe_deletes_main_food(self):
        save_url = reverse("save_recipe")
        del_url = reverse("delete_my_meals")

        self.client.post(save_url, self.post)

        main_food = Foods.objects.get(name=self.post["name"])

        self.client.post(del_url, {"meal_id": main_food.id})

        main_food = Foods.objects.filter(name=self.post["name"])
        self.assertEqual(main_food.count(), 0)

    def test_delete_recipe_deletes_ingredients(self):
        save_url = reverse("save_recipe")
        del_url = reverse("delete_my_meals")

        self.client.post(save_url, self.post)

        main_food_id = Foods.objects.get(name=self.post["name"]).id

        self.client.post(del_url, {"meal_id": main_food_id})

        ings = Ingredients.objects.filter(main_food=main_food_id)
        self.assertEqual(ings.count(), 0)

    def test_delete_recipe_deletes_servings(self):
        save_url = reverse("save_recipe")
        del_url = reverse("delete_my_meals")

        self.client.post(save_url, self.post)

        main_food_id = Foods.objects.get(name=self.post["name"]).id

        self.client.post(del_url, {"meal_id": main_food_id})

        servings = Servings.objects.filter(food=main_food_id)
        self.assertEqual(servings.count(), 0)


class AddRecipeTest(BaseMakeFoodsTest):
    def test_add_recipe_url(self):
        url = reverse("render_add_recipe")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "meals/add_recipe.html")

    def test_add_recipe_url_renders_correct_template_as_guest(self):
        url = reverse("render_add_recipe")
        self.log_in_user("guest", "password")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "meals/bad_raw_url.html")

    def test_add_recipe_returns_filters(self):
        url = reverse("render_add_recipe")
        response = self.client.get(url)

        self.assertContains(response, self.my_meals_fg.name)
        self.assertContains(response, self.veg_fg.name)
        self.assertContains(response, self.meat_fg.name)

    def test_save_recipe_new_food_has_user_set(self):
        url = reverse("save_recipe")
        self.client.post(url, self.post)
        new_food = Foods.objects.get(name=self.post["name"])
        self.assertEqual(new_food.user, self.user)

    def test_save_recipe_url_renders_correct_template_as_guest(self):
        url = reverse("save_recipe")
        self.log_in_user("guest", "password")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "meals/bad_raw_url.html")

    def test_save_recipe_returns_success(self):
        url = reverse("save_recipe")
        response = json.loads(self.client.post(url, self.post).content)
        self.assertEqual(response["status"], 201)

    def test_save_recipe_returns_failure_when_errors(self):
        url = reverse("save_recipe")
        # trigger duplicate name error
        self.client.post(url, self.post)
        response = json.loads(self.client.post(url, self.post).content)
        self.assertEqual(response["status"], 400)
        self.assertTrue(response.get("errors"))

    def test_save_recipe_creates_recipe_serving(self):
        url = reverse("save_recipe")
        self.client.post(url, self.post)

        new_food = Foods.objects.get(name=self.post["name"])
        serving = Servings.objects.filter(food=new_food, description="recipe")
        self.assertEqual(serving.count(), 1)


class MyMealsTest(BaseTestCase):
    def setUp(self):
        self.user = self.log_in_user(USERNAME, PASSWORD)

    def create_meals(self, user):

        first_date = datetime.now()
        second_date = first_date - timedelta(days=1)
        third_date = first_date - timedelta(days=2)
        fourth_date = first_date - timedelta(days=3)

        # Food Groups
        meal_group = FoodGroup.objects.create(name="My Meals")
        recipe_group = FoodGroup.objects.create(name="My Recipes")

        self.roasted_broccoli = Foods.objects.create(
            name="Roasted Broccoli",
            user=user,
            cals_per_gram=Decimal(1),
            fat_per_gram=Decimal(1),
            carbs_per_gram=Decimal(1),
            sugar_per_gram=Decimal(1),
            protein_per_gram=Decimal(1),
            food_group=recipe_group,
        )

        self.ham_sandwich = Foods.objects.create(
            name="Ham Sandwich",
            user=user,
            cals_per_gram=Decimal(1),
            fat_per_gram=Decimal(1),
            carbs_per_gram=Decimal(1),
            sugar_per_gram=Decimal(1),
            protein_per_gram=Decimal(1),
            food_group=meal_group,
        )

        self.pretzels_cheese = Foods.objects.create(
            name="Pretzels and Cheese",
            user=user,
            cals_per_gram=Decimal(1),
            fat_per_gram=Decimal(1),
            carbs_per_gram=Decimal(1),
            sugar_per_gram=Decimal(1),
            protein_per_gram=Decimal(1),
            food_group=meal_group,
        )
        self.pretzels_cheese.date = second_date
        self.pretzels_cheese.save()

        self.pretzels = Foods.objects.create(
            name="Pretzels",
            cals_per_gram=Decimal(1),
            fat_per_gram=Decimal(1),
            carbs_per_gram=Decimal(1),
            sugar_per_gram=Decimal(1),
            protein_per_gram=Decimal(1),
        )
        self.pretzels.date = third_date
        self.pretzels.save()

        self.pretzels_srv = Servings.objects.create(
            food=self.pretzels, grams=Decimal(100), quantity=1, description="bag"
        )

        self.cheese = Foods.objects.create(
            name="Cheese",
            cals_per_gram=Decimal(1),
            fat_per_gram=Decimal(1),
            carbs_per_gram=Decimal(1),
            sugar_per_gram=Decimal(1),
            protein_per_gram=Decimal(1),
        )
        self.cheese.date = fourth_date
        self.cheese.save()

        self.cheese_srv = Servings.objects.create(
            food=self.cheese, grams=Decimal(10), quantity=2, description="slice"
        )

        self.pretzels_ing = Ingredients.objects.create(
            main_food=self.pretzels_cheese,
            ingredient=self.pretzels,
            serving=self.pretzels_srv,
            amount=1,
        )

        self.cheese_ing = Ingredients.objects.create(
            main_food=self.pretzels_cheese,
            ingredient=self.cheese,
            serving=self.cheese_srv,
            amount=2,
        )

        Ingredients.objects.create(
            main_food=self.roasted_broccoli,
            ingredient=self.pretzels,
            serving=self.pretzels_srv,
            amount=1,
        )

        Ingredients.objects.create(
            main_food=self.roasted_broccoli,
            ingredient=self.cheese,
            serving=self.cheese_srv,
            amount=2,
        )

        self.pretzels_cheese_notes = FoodNotes.objects.create(
            notes="Serve piping hot!", food=self.pretzels_cheese
        )

    def test_my_meals_url_uses_correct_template(self):
        url = reverse("my_meals")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "meals/my_meals.html")

    def test_my_meals_url_renders_correct_template_as_guest(self):
        url = reverse("my_meals")
        self.log_in_user("guest", "password")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "meals/bad_raw_url.html")

    def test_search_my_meals_url(self):
        url = reverse("search_my_meals", kwargs={"meal_or_recipe": "meal"})
        data = {"search_terms": "Pretzels and Cheese"}
        response = self.client.get(url, data=data)
        self.assertEqual(response.status_code, 200)

    def test_search_my_meals_returns_food(self):
        self.create_meals(self.user)
        url = reverse("search_my_meals", kwargs={"meal_or_recipe": "meal"})
        data = {"search_terms": "Pretzels and Cheese"}
        response = json.loads(self.client.get(url, data=data).content)

        meal_id = list(response["search-results"]["meal_info"].keys())[0]
        results = response["search-results"]["meal_info"][meal_id]

        main_food_name = results[0]["name"]
        self.assertEqual(main_food_name, self.pretzels_cheese.name)

    def test_search_my_meals_returns_food_ingredients(self):
        self.create_meals(self.user)
        url = reverse("search_my_meals", kwargs={"meal_or_recipe": "meal"})
        data = {"search_terms": "Pretzels and Cheese"}
        response = json.loads(self.client.get(url, data=data).content)

        meal_id = list(response["search-results"]["meal_info"].keys())[0]
        results = response["search-results"]["meal_info"][meal_id]

        ingredient1_name = results[0]["main_food__ingredient__name"]
        ingredient2_name = results[1]["main_food__ingredient__name"]

        self.assertEqual(ingredient1_name, self.pretzels.name)
        self.assertEqual(ingredient2_name, self.cheese.name)

    def test_search_my_meals_returns_food_ingredients_and_servings(self):
        self.create_meals(self.user)
        url = reverse("search_my_meals", kwargs={"meal_or_recipe": "meal"})
        data = {"search_terms": "Pretzels and Cheese"}
        response = json.loads(self.client.get(url, data=data).content)

        meal_id = list(response["search-results"]["meal_info"].keys())[0]
        results = response["search-results"]["meal_info"][meal_id]

        serving1_amount = Decimal(results[0]["main_food__amount"])
        serving1_desc = results[0]["main_food__serving__description"]

        serving2_amount = Decimal(results[1]["main_food__amount"])
        serving2_desc = results[1]["main_food__serving__description"]

        self.assertEqual(serving1_amount, self.pretzels_ing.amount)
        self.assertEqual(serving1_desc, self.pretzels_srv.description)

        self.assertEqual(serving2_amount, self.cheese_ing.amount)
        self.assertEqual(serving2_desc, self.cheese_srv.description)

    def test_search_my_meals_returns_food_notes(self):
        self.create_meals(self.user)
        url = reverse("search_my_meals", kwargs={"meal_or_recipe": "meal"})
        data = {"search_terms": "Pretzels and Cheese"}
        response = json.loads(self.client.get(url, data=data).content)

        meal_id = list(response["search-results"]["meal_info"].keys())[0]
        results = response["search-results"]["meal_info"][meal_id]

        main_food_notes = results[0]["notes__notes"]
        self.assertEqual(main_food_notes, self.pretzels_cheese_notes.notes)

    def test_search_my_meals_by_meals_returns_meal(self):
        self.create_meals(self.user)
        url = reverse("search_my_meals", kwargs={"meal_or_recipe": "meal"})
        data = {"search_terms": "Pretzels and Cheese"}
        response = json.loads(self.client.get(url, data=data).content)

        self.assertTrue(len(response["search-results"]["meals"]) > 0)
        self.assertTrue(
            response["search-results"]["meals"][0]["id"] == self.pretzels_cheese.pk
        )

    def test_search_my_meals_by_recipe_does_not_return_meal(self):
        self.create_meals(self.user)
        url = reverse("search_my_meals", kwargs={"meal_or_recipe": "recipe"})
        data = {"search_terms": "Pretzels and Cheese"}
        response = json.loads(self.client.get(url, data=data).content)

        self.assertTrue(len(response["search-results"]["meals"]) == 0)

    def test_search_my_meals_by_recipe_returns_recipe(self):
        self.create_meals(self.user)
        url = reverse("search_my_meals", kwargs={"meal_or_recipe": "recipe"})
        data = {"search_terms": "Roasted Broccoli"}
        response = json.loads(self.client.get(url, data=data).content)

        self.assertTrue(len(response["search-results"]["meals"]) == 1)
        self.assertTrue(
            response["search-results"]["meals"][0]["id"] == self.roasted_broccoli.pk
        )

    def test_search_my_meals_by_meal_does_not_return_recipe(self):
        self.create_meals(self.user)
        url = reverse("search_my_meals", kwargs={"meal_or_recipe": "meal"})
        data = {"search_terms": "Roasted Broccoli"}
        response = json.loads(self.client.get(url, data=data).content)

        self.assertTrue(len(response["search-results"]["meals"]) == 0)


class MacroMealMakerTest(BaseTestCase):
    def setUp(self):

        self.log_in_user(USERNAME, PASSWORD)

        self.food_type_food = FoodType.objects.create(name="food")
        self.food_type_meal = FoodType.objects.create(name="meal")
        self.food_group_meal = FoodGroup.objects.create(name="My Meals")

        self.ingredient1 = Foods.objects.create(
            name="veggie pulled pork",
            cals_per_gram="1.6456",
            fat_per_gram="0.3418",
            carbs_per_gram="0.1519",
            sugar_per_gram="0.1519",
            protein_per_gram="1.1646",
            food_type=self.food_type_food,
        )

        self.srv1 = Servings.objects.create(
            food=self.ingredient1, grams=237, quantity=1, description="bag"
        )

        self.ingredient2 = Foods.objects.create(
            name="bbq sauce",
            cals_per_gram="1.7200",
            fat_per_gram="0.0567",
            carbs_per_gram="1.6308",
            sugar_per_gram="1.6308",
            protein_per_gram="0.0328",
            food_type=self.food_type_food,
        )

        self.srv2 = Servings.objects.create(
            food=self.ingredient2, grams=17, quantity=1, description="tbsp"
        )

        self.ingredient_form_factory = forms.formset_factory(
            MacroIngredientForm, extra=2
        )

        self.food_amt_dict = {
            # added long decimals to test that they get rounded
            "form-TOTAL_FORMS": u"2",
            "form-INITIAL_FORMS": u"0",
            "form-MAX_NUM_FORMS": u"",
            "name": "veggie pulled pork with bbq sauce",
            "notes": "broil in the oven",
            "form-0-ingredient_id": self.ingredient1.pk,
            "form-0-amount": "1",
            "form-0-unit": "bag",
            "form-1-ingredient_id": self.ingredient2.pk,
            "form-1-amount": "4",
            "form-1-unit": "tbsp",
        }

        query_dict = QueryDict("", mutable=True)
        query_dict.update(self.food_amt_dict)
        self.request = HttpRequest()
        self.request.POST = query_dict

    def test_save_macro_meal_url(self):

        url = reverse("save_macro_meal")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_save_macro_meal_returns_1_status(self):
        url = reverse("save_macro_meal")
        response = json.loads(self.client.post(url, data=self.food_amt_dict).content)

        self.assertEqual(response["status"], 1)

    def test_save_macro_meal_saves_ingredients(self):
        url = reverse("save_macro_meal")
        response = json.loads(self.client.post(url, data=self.food_amt_dict).content)

        saved_foods = Foods.objects.filter(name=self.food_amt_dict["name"])
        main_food = saved_foods[0]
        saved_ingredients = Ingredients.objects.filter(main_food=main_food)
        self.assertEqual(saved_ingredients.count(), 2)

    def test_save_macro_meal_saves_notes(self):
        url = reverse("save_macro_meal")
        response = json.loads(self.client.post(url, data=self.food_amt_dict).content)

        saved_foods = Foods.objects.filter(name=self.food_amt_dict["name"])
        main_food = saved_foods[0]

        notes = FoodNotes.objects.filter(food=main_food)
        self.assertEqual(notes.count(), 1)

    def test_save_macro_meal_has_correct_food_group_type(self):
        url = reverse("save_macro_meal")
        response = json.loads(self.client.post(url, data=self.food_amt_dict).content)

        saved_foods = Foods.objects.filter(name=self.food_amt_dict["name"])
        main_food = saved_foods[0]

        self.assertEqual(self.food_type_meal, main_food.food_type)
        self.assertEqual(self.food_group_meal, main_food.food_group)

    def test_save_macro_meal_saves_meal_serving(self):
        url = reverse("save_macro_meal")
        response = json.loads(self.client.post(url, data=self.food_amt_dict).content)

        saved_foods = Foods.objects.filter(name=self.food_amt_dict["name"])
        main_food = saved_foods[0]

        servings = Servings.objects.filter(food=main_food, description="meal")

        self.assertEqual(servings.count(), 1)

    def test_get_ingredient_count(self):

        ingredient_count = get_ingredient_count(self.request.POST)
        self.assertEqual(ingredient_count, 2)


class MealMakerTest(BaseTestCase):
    def setUp(self):

        Servings.objects.create(
            food=None, grams=Decimal(1), description="g", quantity=Decimal(1)
        )

    # fixtures = ['db.json']

    #################################
    ##constants
    #################################
    MACRO_BREAKDOWN = [
        {"name": "Fat", "percent": 34, "data": Decimal("34.00")},
        {"name": "Carbs", "percent": 33, "data": Decimal("33.00")},
        {"name": "Protein", "percent": 33, "data": Decimal("33.00")},
    ]

    MEAL_TEMPLATES = [
        {"value": 527, "text": "Meal 1,2,3 - 527 cals"},
        {"value": 301, "text": "Meal 4 - 301 cals"},
    ]

    #################################
    ##helper functions
    #################################
    def create_foods_for_search(self, user):
        veg_food_group = FoodGroup.objects.create(name="Veggies", rank=1)
        meat_food_group = FoodGroup.objects.create(name="Meat", rank=2)

        Foods.objects.create(
            name="garbanzo beans", user=user, food_group=veg_food_group
        )
        Foods.objects.create(name="lettuce", user=user, food_group=veg_food_group)
        Foods.objects.create(name="garbanzo beans no user", food_group=veg_food_group)
        Foods.objects.create(name="brisket", user=user, food_group=meat_food_group)

        self.all_filters = [
            v["name"] for v in FoodGroup.objects.all().values("name").distinct()
        ]

    def create_default_macro(self, user):
        macro = Macros.objects.create(
            **{
                "user": user,
                "unit_type": "imperial",
                "gender": "male",
                "age": 34,
                "direction": "lose",
                "activity": "light",
                "height": Decimal("177.8"),
                "weight": Decimal("95.25"),
                "change_rate": Decimal(".45359237"),
                "protein_percent": Decimal("33"),
                "fat_percent": Decimal("34"),
            }
        )
        return macro

    #################################
    ##search
    #################################
    # def test_search_food_url_returns_food_dict_with_array_greater_than_0(self):
    #     user = self.log_in_user(USERNAME, PASSWORD)
    #     self.create_foods_for_search(user)
    #     response = self.client.get(
    #         '/meals/search-foods/all/', data={'search_terms':'garbanzo beans'}
    #     )
    #     response_dict = json.loads(response.content.decode())
    #     self.assertTrue(len(response_dict['search-results']) > 0)

    def test_search_food_all_results_contain_at_least_1_search_term(self):
        user = self.log_in_user(USERNAME, PASSWORD)
        self.create_foods_for_search(user)
        search_terms = "garbanzo beans"
        response = self.client.get(
            "/meals/search-foods/all/",
            data={"search_terms": search_terms, "filters[]": ["Veggies"]},
        )
        response_dict = json.loads(response.content.decode())
        results = response_dict["search-results"]
        results_containing_search_terms = len(
            [r for r in results if sum([t in r["name"] for t in search_terms.split()])]
        )
        self.assertTrue(results_containing_search_terms == len(results))

    def test_search_food_user_restrict_only_returns_user_foods(self):
        user = self.log_in_user(USERNAME, PASSWORD)
        self.create_foods_for_search(user)
        search_terms = "garbanzo beans"
        response = self.client.get(
            "/meals/search-foods/user/",
            data={"search_terms": search_terms, "filters[]": ["Veggies"]},
        )
        response_dict = json.loads(response.content.decode())
        results = response_dict["search-results"]
        self.assertTrue(len(results) == 1)

    def test_search_food_filters_based_food_group(self):
        user = self.log_in_user(USERNAME, PASSWORD)
        self.create_foods_for_search(user)
        search_terms = "garbanzo beans brisket"
        response = self.client.get(
            "/meals/search-foods/user/",
            data={"search_terms": search_terms, "filters[]": ["Veggies"]},
        )
        response_dict = json.loads(response.content.decode())
        foods_returned = [d["name"] for d in response_dict["search-results"]]
        self.assertTrue("garbanzo beans" in foods_returned)
        self.assertTrue("brisket" not in foods_returned)
        self.assertTrue(len(foods_returned) == 1)

    def test_search_food_all_filters_returns_all_results(self):
        user = self.log_in_user(USERNAME, PASSWORD)
        self.create_foods_for_search(user)
        search_terms = "garbanzo beans brisket"
        response = self.client.get(
            "/meals/search-foods/user/",
            data={"search_terms": search_terms, "filters[]": self.all_filters},
        )
        response_dict = json.loads(response.content.decode())
        foods_returned = [d["name"] for d in response_dict["search-results"]]
        self.assertTrue("garbanzo beans" in foods_returned)
        self.assertTrue("brisket" in foods_returned)
        self.assertTrue(len(foods_returned) == 2)

    #################################
    ##open tab
    #################################
    def test_meal_maker_url_renders_correct_template(self):
        user = self.log_in_user(USERNAME, PASSWORD)
        self.create_default_macro(user)

        response = self.client.get("/meals/meal-maker/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "meals/meal_maker.html")

    def test_get_meal_maker_context_contains_food_group_names(self):
        user = self.log_in_user(USERNAME, PASSWORD)
        self.create_foods_for_search(user)
        response = self.client.get("/meals/meal-maker/")
        self.assertContains(response, "Veggies")
        self.assertContains(response, "Meat")

    def xtest_make_meal_template_macro_breakdown_dict_returns_list_of_dicts(self):
        user = self.log_in_user(USERNAME, PASSWORD)
        macro = self.create_default_macro(user)
        self.create_default_meal_templates(user)

        expected_result = self.MACRO_BREAKDOWN
        self.assertEqual(make_macro_breakdown_dict_list(macro), expected_result)

    def test_get_meal_maker_template_uses_correct_form(self):

        user = self.log_in_user(USERNAME, PASSWORD)
        response = self.client.get("/meals/meal-maker/")
        self.assertIsInstance(response.context["macro_meal_form"], MacroMealForm)

    def xtest_get_meal_maker_template_no_macro_returns_correct_html(self):

        user = self.log_in_user(USERNAME, PASSWORD)

        request = HttpRequest()
        request.user = user
        response = get_meal_maker_template(request)
        expected_html = render_to_string("meal_maker.html", {})
        self.assertMultiLineEqual(response.content.decode(), expected_html)
        self.assertIn("%", response.content.decode())
        self.assertNotIn("id_goal_meal_cals_select", response.content.decode())

    def xtest_get_meal_maker_template_has_macro_returns_correct_html(self):

        user = self.log_in_user(USERNAME, PASSWORD)
        default_macro = self.create_default_macro(user)
        meal_templates = self.create_default_meal_templates(user)

        request = HttpRequest()
        request.user = user
        response = get_meal_maker_template(request)
        expected_html = render_to_string(
            "meal_maker.html",
            {
                "tdee": 1883,
                "meal_templates": self.MEAL_TEMPLATES,
                "macro_breakdown": self.MACRO_BREAKDOWN,
            },
        )
        self.assertMultiLineEqual(response.content.decode(), expected_html)
        self.assertNotIn("value='34'", response.content.decode())
        self.assertIn("goal-meal-cals-select", response.content.decode())


class LoginLogoffTest(TestCase):
    def test_anonymous_user_home_redirects_to_login_template(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "/accounts/login/?next=/")

    def test_can_login_as_authenticated_user(self):
        username, password = USERNAME, PASSWORD
        user = User.objects.create_user(username=username, password=password)
        response = self.client.post(
            "/accounts/login/", data={"username": username, "password": password}
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "/")

    def test_can_login_as_guest(self):
        guest_user = User.objects.create_user(
            username=GUEST_USERNAME, password=GUEST_PASSWORD
        )
        response = self.client.post(
            "/accounts/login/",
            data={"username": GUEST_USERNAME, "password": GUEST_PASSWORD},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "/")

    def test_login_error_renders_login_page(self):
        response = self.client.post(
            "/accounts/login/",
            data={"username": BAD_USERNAME, "password": BAD_PASSWORD},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")

    def test_login_error_shows_up_on_login_page(self):
        response = self.client.post(
            "/accounts/login/",
            data={"username": BAD_USERNAME, "password": BAD_PASSWORD},
        )
        expected_error = "Your username and password didn't match. Please try again."
        self.assertContains(response, expected_error)

    def test_logoff(self):
        guest_user = User.objects.create_user(
            username=GUEST_USERNAME, password=GUEST_PASSWORD
        )
        response = self.client.post(
            "/accounts/login/",
            data={"username": GUEST_USERNAME, "password": GUEST_PASSWORD},
        )
        response = self.client.get("/")
        self.assertTemplateUsed(response, "meals/base.html")

        response = self.client.get("/accounts/logout/")
        response = self.client.get("/")
        self.assertEqual(response["location"], "/accounts/login/?next=/")


class CreateAccountTest(TestCase):
    def test_sign_up_button_leads_to_correct_template(self):
        response = self.client.get("/meals/sign-up/")
        self.assertTemplateUsed(response, "meals/sign_up.html")

    def test_sign_up_page_uses_sign_up_form(self):
        response = self.client.get("/meals/sign-up/")
        self.assertIsInstance(response.context["form"], SignUpForm)

    def test_can_save_POST_and_create_user_account(self):
        request = HttpRequest()
        response = self.client.post(
            "/meals/create-account",
            data={"username": USERNAME, "email": EMAIL, "password": PASSWORD},
        )
        self.assertEqual(User.objects.count(), 1)
        new_user = User.objects.first()
        self.assertTrue(authenticate(username=USERNAME, password=PASSWORD) is not None)

    def test_can_save_POST_and_create_user_account_redirects(self):
        response = self.client.post(
            "/meals/create-account",
            data={"username": USERNAME, "email": EMAIL, "password": PASSWORD},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], "/")

    def test_sign_up_blank_username_validation_error_wont_save_new_user(self):
        USERNAME = ""
        response = self.client.post(
            "/meals/create-account",
            data={"username": USERNAME, "email": EMAIL, "password": PASSWORD},
        )
        self.assertEqual(User.objects.count(), 0)

    def test_sign_up_duplicate_username_validation_error_wont_save_new_user(self):
        response = self.client.post(
            "/meals/create-account",
            data={"username": USERNAME, "email": EMAIL, "password": PASSWORD},
        )
        response = self.client.post(
            "/meals/create-account",
            data={"username": USERNAME, "email": EMAIL, "password": PASSWORD},
        )
        self.assertEqual(User.objects.count(), 1)

    def test_sign_up_bad_username_validation_error_wont_save_new_user(self):
        USERNAME = "joe blow"
        response = self.client.post(
            "/meals/create-account",
            data={"username": USERNAME, "email": EMAIL, "password": PASSWORD},
        )
        self.assertEqual(User.objects.count(), 0)

    def test_sign_up_blank_password_validation_error_wont_save_new_user(self):
        PASSWORD = ""
        response = self.client.post(
            "/meals/create-account",
            data={"username": USERNAME, "email": EMAIL, "password": PASSWORD},
        )
        self.assertEqual(User.objects.count(), 0)

    def test_sign_up_validation_error_render_sign_up_html(self):
        response = self.client.post(
            "/meals/create-account",
            data={"username": USERNAME, "email": EMAIL, "password": PASSWORD},
        )
        response = self.client.post(
            "/meals/create-account",
            data={"username": USERNAME, "email": EMAIL, "password": PASSWORD},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "meals/sign_up.html")

    def test_sign_up_duplicate_validation_error_gets_sign_up_form_back(self):
        username, email, password = USERNAME, EMAIL, PASSWORD
        response = self.client.post(
            "/meals/create-account",
            data={"username": USERNAME, "email": EMAIL, "password": PASSWORD},
        )
        response = self.client.post(
            "/meals/create-account",
            data={"username": USERNAME, "email": EMAIL, "password": PASSWORD},
        )
        self.assertIsInstance(response.context["form"], SignUpForm)

    def test_sign_up_duplicate_user_validation_error_message_shows_up_on_sign_up_html(
        self,
    ):
        response = self.client.post(
            "/meals/create-account",
            data={"username": USERNAME, "email": EMAIL, "password": PASSWORD},
        )
        response = self.client.post(
            "/meals/create-account",
            data={"username": USERNAME, "email": EMAIL, "password": PASSWORD},
        )
        self.assertContains(response, DUPLICATE_USERNAME_ERROR)

    def test_sign_up_bad_username_validation_error_message_shows_up_on_sign_up_html(
        self,
    ):
        USERNAME = "Joe Schmoe"
        response = self.client.post(
            "/meals/create-account",
            data={"username": USERNAME, "email": EMAIL, "password": PASSWORD},
        )
        self.assertContains(response, INVALID_USERNAME_ERROR)

    def test_sign_up_missing_password_validation_error_message_shows_up_on_sign_up_html(
        self,
    ):
        PASSWORD = ""
        response = self.client.post(
            "/meals/create-account",
            data={"username": USERNAME, "email": EMAIL, "password": PASSWORD},
        )
        self.assertContains(response, EMPTY_PASSWORD_ERROR)


class MyMacrosTabTest(BaseTestCase):
    def setUp(self):

        self.log_in_user(USERNAME, PASSWORD)
        self.url = reverse("my_macros")

    SHARED_MACRO_DATA = {
        "gender": "male",
        "age": "34",
        "activity": "none",
        "direction": "lose",
        "fat-g": "10",
        "fat-pct": "30",
        "protein-g": "10",
        "protein-pct": "30",
        "carbs-g": "10",
        "carbs-pct": "40",
        "meal-0": "287",
        "meal-1": "287",
        "meal-2": "287",
        "meal-3": "285",
        "meal-4": "289",
        "meal-number": "5",
        "tdee": "1435",
    }
    IMPERIAL_MACRO_DATA = {
        **SHARED_MACRO_DATA,
        **{
            "unit-type": "imperial",
            "height-i-ft": "5",
            "height-i-in": "10",
            "weight-i": "210",
            "change-rate-i": "2",
        },
    }
    METRIC_MACRO_DATA = {
        **SHARED_MACRO_DATA,
        **{
            "unit-type": "metric",
            "height-m": "5",
            "weight-m": "210",
            "change-rate-m": "2",
        },
    }

    def setup_user_request_for_post_to_view(self, post_data):
        request = HttpRequest()
        request.POST = post_data
        request.user = User.objects.create_user(
            username=USERNAME, email=EMAIL, password=PASSWORD
        )
        return request

    def test_my_macros_url_renders_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "meals/my_macros.html")


c = """
    def test_my_macros_template_uses_my_macros_form(self):
        response = self.client.get('/meals/get-my-macros/')
        self.assertIsInstance(response.context['form'], MakeMacrosForm)

    def test_save_my_macros_imperial_macros(self):
        request = self.setup_user_request_for_post_to_view(self.IMPERIAL_MACRO_DATA)
        response = save_my_macros(request)
        saved_macro = Macros.objects.all()
        self.assertEqual(saved_macro.count(),1)		


    def test_save_my_macros_metric_macros(self):
        request = self.setup_user_request_for_post_to_view(self.METRIC_MACRO_DATA)
        response = save_my_macros(request)
        saved_macro = Macros.objects.all()
        self.assertEqual(saved_macro.count(),1)		

    def test_save_my_macro_returns_status_dict_with_status_of_1_if_success(self):
        request = self.setup_user_request_for_post_to_view(self.METRIC_MACRO_DATA)
        response = save_my_macros(request)
        self.assertEqual(response['status'],1)
        self.assertIsInstance(response['form'],MakeMacrosForm)
        self.assertEqual(response['unit-type'],'metric')


    def test_save_my_macros_and_meal_templates_saves_imperial_macros(self):
        self.client.post('/meals/create-account', data={'username':USERNAME, 'email':EMAIL,'password':PASSWORD})
        response=self.client.post('/meals/save-my-macros', data=self.IMPERIAL_MACRO_DATA)
        saved_macro = Macros.objects.all()
        self.assertEqual(saved_macro.count(),1)		

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
