from decimal import Decimal
from django import forms
from meals.models import FoodGroup, FoodNotes, FoodType
from meals.forms import MacroIngredientForm


def make_macro_breakdown_dict_list(macro=None):
    """
    Creates dictionaries to be used for the Macro inputs on the
    meal maker tab.

    Parameters
    ----------
        macro: Macros instance

    Returns
    ----------
    macros_dict_list: list
        list of dictionaries corresponding to each macro
    """

    macros_dict_list = [
        {
            'name':'Fat',
            'percent': 0,
            'data': 0
        },
        {
            'name':'Carbs',
            'percent': 0,
            'data': 0
        },
        {
            'name':'Protein',
            'percent': 0,
            'data': 0
        }
    ]

    if macro:
        fat_pct = macro.fat_percent
        protein_pct = macro.protein_percent

        macros_dict_list[0]['percent'] = round(fat_pct)
        macros_dict_list[0]['data'] = fat_pct

        macros_dict_list[1]['percent'] = 100 - (
            round(fat_pct) + round(protein_pct)
        )
        macros_dict_list[1]['data'] = Decimal(100 - (fat_pct + protein_pct))

        macros_dict_list[2]['percent'] = round(protein_pct)
        macros_dict_list[2]['data'] = protein_pct

    return macros_dict_list


def get_ingredient_count(post_data):
    """get ingredient keys from request

    Separates the ingredient info into a separate dict
    and removes them from request.POST

    Parameters
    ----------
    request: HttpRequest object

    Returns
    -------
    ingredients: int
        count of ingredients in request.POST
    """

    ingredients = len([
        key[-1] for key in post_data if 'ingredient' in key
    ])

    return ingredients


def make_ingredient_formset(request):
    """makes a formset to save multiple ingredients

    A variable number of Ingredients are submitted and a
    formset is used to handled the validation of all them.

    Parameters
    ----------
    request: HttpRequest object
        Hold the POST data

    Returns
    ----------
    ingredient_formset: form.formset instance
        formset for the MacroIngredientForm
    """

    ingredient_count = get_ingredient_count(request.POST)
    # these keys are needed for all formsets
    request.POST['form-TOTAL_FORMS'] = str(ingredient_count)
    request.POST['form-INITIAL_FORMS'] = '0'
    request.POST['form-MAX_NUM_FORMS'] = ''

    ingredient_form_factory = forms.formset_factory(
        MacroIngredientForm, extra=ingredient_count
    )
    ingredient_formset = ingredient_form_factory(request.POST)

    return ingredient_formset


def save_meal_notes_ingredients(user, meal_form, ingredient_formset):
    """saves the validated forms

    Saves the validated forms for Foods, Ingredients, and FoodNotes.

    Parameters
    ----------
    meal_form: MacroMealForm instance
    ingredient_formset: forms.formset
        formset for the MacroIngredientForm

    Returns
    ----------
    None
    """

    new_food = meal_form.save()
    new_food.user = user
    if meal_form.cleaned_data.get('notes'):
        notes = meal_form.cleaned_data.get('notes')
        FoodNotes.objects.create(food=new_food, notes=notes)

    # Add meal food type
    food_type_meal = FoodType.objects.get(name='meal')
    new_food.food_type = food_type_meal

    # Add meal food group
    food_group_meal = FoodGroup.objects.get(name='My Meals')
    new_food.food_group = food_group_meal

    for ing_form in ingredient_formset:
        new_ing = ing_form.save(commit=False)
        new_ing.main_food = new_food
        new_ing.save()

    new_food.set_macros_per_gram()
    new_food.save()
