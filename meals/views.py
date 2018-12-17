from decimal import Decimal
import json
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.db.utils import IntegrityError
from django.db import transaction
from django.core.serializers.json import DjangoJSONEncoder

from meals.forms import SignUpForm, MakeMacrosForm, MacroMealForm, \
        MacroIngredientForm, MealRecipeForm, NewFoodForm
from meals.models import Macros, Foods, FoodGroup, Ingredients, Servings, \
        FoodNotes, FoodType
from meals.helpers import make_ingredient_formset, \
        save_meal_notes_ingredients


# Constants
KG_TO_LB = .45359237
IN_TO_CM = .3937
TEMPLATES_DIR = 'meals/'

BAD_REQUEST = 400
OK = 200

# Create your views here.
def home_or_login(request):

    if request.user.is_authenticated():
        return render(request, TEMPLATES_DIR + 'base.html')

    return redirect('login')


def sign_up(request):
    return render(
        request, TEMPLATES_DIR + 'sign_up.html', {'form': SignUpForm()}
    )


def create_account(request):

    username = request.POST.get('username', '')
    email = request.POST.get('email', '')
    password = request.POST.get('password', '')
    form = SignUpForm(data=request.POST)
    if form.is_valid():
        user = User()
        user.username = username
        user.email = email
        user.set_password(password)
        user.save()
        login(request, user)
        return redirect('/')

    return render(request, 'sign_up.html', {"form":form})


def get_my_macros(request):
    form = MakeMacrosForm(unit_type='imperial')
    return render(request, TEMPLATES_DIR + 'my_macros.html', {
        'form':form
    })


def save_my_macros(request):
    """saves new Macro

    Save new Macro model object

    Parameters
    ----------
    request: HttpRequest instance

    Returns
    ----------
    context: dict
        dict with status, form, and unit-type upon
        success or failure

    """

    macro_form = MakeMacrosForm(request.POST)
    context = {}
    if macro_form.is_valid():
        Macros.objects.filter(user=request.user).delete()
        macro_form.instance.user = request.user
        macro_form.save()
        context['status_code'] = OK 

        return JsonResponse(context)

    context['status_code'] = BAD_REQUEST
    context['errors'] = macro_form.errors
    return JsonResponse(context)



def make_macro_breakdown_dict_list(macro):
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

    fat_pct = macro.fat_percent
    protein_pct = macro.protein_percent


    macros_dict_list = [
        {
            'name':'Fat',
            'percent':round(fat_pct),
            'data':fat_pct
        },
        {
            'name':'Carbs',
            'percent':100 - (round(fat_pct) + round(protein_pct)),
            'data':Decimal(100 - (fat_pct + protein_pct))
        },
        {
            'name':'Protein',
            'percent':round(protein_pct),
            'data':protein_pct
        }
    ]

    return macros_dict_list 


def get_meal_maker_template(request):
    """passes saved info to meal_maker tab

    Get saved Macros and MealTemplates to pass to meal_maker.html.

    Parameters
    ----------
    request: HttpRequest instance

    Returns
    ----------
    render: render instance
        renders meal_maker.html with info from MyMacros tab
        such as tdee, MealTemplate info, and the Macros breakdown
    """

    macro_set = Macros.objects.filter(user = request.user)
    form = MacroMealForm()
    if macro_set:
        macro = macro_set[0]
        tdee = macro.calc_tdee()

        macro_breakdown_dict_list = make_macro_breakdown_dict_list(macro)
        context = {
            'tdee':round(tdee),
            'macro_breakdown':macro_breakdown_dict_list,
            'macro_meal_form': form
        }
    else:
        context = {'macro_meal_form': form}

    # informal name to use in input id, and to use in label
    context['filters'] = [
        {
            'id_name': fg['informal_name'].lower().replace(' ', '-'),
            'informal_name': fg['informal_name']
        } for fg in
        FoodGroup.objects.all().values('informal_name').distinct()
    ]
    return render(request, TEMPLATES_DIR + 'meal_maker.html', context)


def save_macro_meal(request):
    """saves the models associated with a 'macro meal'

    Takes two forms and saves the info to make a 'macro meal'
    which is compromised of Foods, Ingredients, and FoodNotes
    models

    Parameters
    ----------
    request: HttpRequest instance

    Returns
    ----------
    context: dict
        holds success/failure status, and any errors
    """
    request.POST._mutable = True

    meal_form = MacroMealForm(request.POST)
    ingredient_formset = make_ingredient_formset(request)

    context = {'status': 0, 'errors': ''}
    if meal_form.is_valid() and ingredient_formset.is_valid():
        save_meal_notes_ingredients(request.user, meal_form, ingredient_formset)
        context['status'] = 1

    else:
        context['status'] = 0
        meal_error_dict = dict([
            (k, [e for e in v]) for k, v in meal_form.errors.items()
        ])
        context['errors'] = json.dumps(meal_error_dict)
        # ingredient_error_dict = [
        #     [k for k in ingredient_formset.errors]
        # ]
        # context['errors'] += ingredient_formset.errors

    return JsonResponse(context)


def get_my_meals(request):

    return render(request, TEMPLATES_DIR + 'my_meals.html')


def search_foods(request, food_owner):
    """search db

    Seach usda foods db based on 'search_terms' key, submitted by user.

    Parameters
    ----------
    request: HttpRequest object
    food_owner: str
        Can be 'all' | 'user'. 'user' constrains the query set
        to the current user.

    Returns
    ----------
    HttpResponse: HttpResponse instance
        search results as json
    """

    search_terms = request.GET['search_terms'].split(' ')
    filters = request.GET.getlist('filters[]')
    fields_of_interest = [
        'id', 'name', 'cals_per_gram', 'fat_per_gram', 'carbs_per_gram',
        'protein_per_gram', 'servings__pk', 'servings__description', 'servings__grams',
        'servings__quantity']

    args = [
        'name', search_terms, 0.001, fields_of_interest,
        ['servings'], 50, filters
    ]

    if food_owner == 'user':
        args.append(Foods.searcher.filter_on_user(request.user))

    search_results = Foods.searcher.restructure_food_and_servings_queryset(
        Foods.searcher.rank_with_terms_and_filters(*args)
    )

    return HttpResponse(
        json.dumps(
            {'search-results':search_results}, cls=DjangoJSONEncoder
        ), content_type='application/json'
    )


def search_my_meals(request, meal_or_recipe):

    search_terms = request.GET['search_terms'].split(' ')

    fields_of_interest = [
        'main_food', 'main_food__ingredient', 'id', 'name',
        'main_food__ingredient__name', 'main_food__amount',
        'main_food__serving__description', 'notes__notes'
    ]

    filters = [{'meal': 'My Meals', 'recipe': 'My Recipes'}[meal_or_recipe]]

    args = [
        'name', search_terms, 0.001, fields_of_interest,
        ['servings', 'notes'], 20, filters
    ]
    kwargs = {'query_set': Foods.searcher.filter_on_user(request.user)}

    search_results = Foods.searcher.rank_with_terms_and_filters(*args, **kwargs)

    search_results_dict = Foods.searcher.add_nested_ingredients_to_ingredient_dict(
        Foods.searcher.restructure_ingredients_queryset_to_dict(search_results),
        fields_of_interest
    )

    return HttpResponse(
        json.dumps(
            {'search-results': search_results_dict}, cls=DjangoJSONEncoder
        ),
        content_type='application/json'
    )


def add_recipe(request):

    context = {
        'filters': [
            {
                'id_name': fg['informal_name'].lower().replace(' ', '-'),
                'informal_name': fg['informal_name']
            } for fg in
            FoodGroup.objects.all().values('informal_name').distinct()
        ]
    }

    return render(request, TEMPLATES_DIR + 'add_recipe.html', context)


def save_recipe(request):

    # request.POST['user'] = request.user
    form = MealRecipeForm(request.POST)
    context = {}
    if form.is_valid():
        form.instance.user = request.user
        form.save()
        context['status'] = 'success'

    else:
        context['errors'] = form.errors
        context['status'] = 'failure'

    return JsonResponse(context)


def add_food(request):

    if request.method == 'POST':
        form = NewFoodForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            form.save()

            return JsonResponse({'status_code': 201})

        return JsonResponse({'status_code': 400, 'errors': form.errors})

    context = {'add_food_form': NewFoodForm()}
    return render(request, TEMPLATES_DIR + 'add_food.html', context)

