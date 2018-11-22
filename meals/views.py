from decimal import Decimal
import json
import simplejson
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from django.core.serializers.json import DjangoJSONEncoder
from django import forms

from meals.forms import SignUpForm, MakeMacrosForm, MacroMealForm, \
        MacroIngredientForm
from meals.models import Macros, Foods, FoodGroup, Ingredients, Servings, \
        FoodNotes
from meals.helpers import get_ingredient_count, make_ingredient_formset, \
        save_meal_notes_ingredients, get_search_results


# Constants
KG_TO_LB = .45359237
IN_TO_CM = .3937
TEMPLATES_DIR = 'meals/'

# Create your views here.
def home_or_login(request):

    if request.user.is_authenticated():
        return render(request, TEMPLATES_DIR + 'base.html')

    return redirect('login')


def sign_up(request):
    return render(request, TEMPLATES_DIR + 'sign_up.html', {'form': SignUpForm()})


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


def create_macro_form_dict(POST):
    """
    Creates dict containing fields needed for MakeMacroForm model.

    Parameters
    ----------
        POST: QueryDict

    Returns
    ----------
        dict with fields for MakeMacroForm model
    """
    macro_form_dict = {}
    macro_form_dict['unit_type'] = POST['unit-type']
    if macro_form_dict['unit_type'] == 'imperial':
        height1 = POST.get('height-i-ft', '')
        height2 = POST.get('height-i-in', '')
        if height1 != '' and height2 != '':
            macro_form_dict['height'] = str(
                round(((int(height1) * 12) + int(height2)) / IN_TO_CM, 2)
            )

        macro_form_dict['weight'] = POST.get('weight-i', '')
        macro_form_dict['change_rate'] = POST.get('change-rate-i', '')
        if macro_form_dict['weight'] != '':
            macro_form_dict['weight'] = str(round(int(macro_form_dict['weight']) * KG_TO_LB, 2))

        if macro_form_dict['change_rate'] != '':
            macro_form_dict['change_rate'] = str(
                round(int(macro_form_dict['change_rate']) * KG_TO_LB, 8)
            )

    if macro_form_dict['unit_type'] == 'metric':
        macro_form_dict['height'] = POST.get('height-m', 0)
        macro_form_dict['weight'] = POST.get('weight-m', 0)
        macro_form_dict['change_rate'] = POST.get('change-rate-m', '')

    macro_form_dict['total_macro_percent'] = int(POST.get('protein-pct', 0))\
            + int(POST.get('fat-pct', 0)) + int(POST.get('carbs-pct', 0))
    macro_form_dict = {
        **{
            'gender':POST.get('gender', ''), 'age':POST.get('age', ''),
            'activity':POST.get('activity', ''), 'direction':POST.get('direction', ''),
            'fat_percent':POST.get('fat-pct', ''), 'fat_g':POST.get('fat-g', ''),
            'carbs_percent':POST.get('carbs-pct', ''), 'carbs_g':POST.get('carbs-g', ''),
            'protein_percent':POST.get('protein-pct', ''), 'protein_g':POST.get('protein-g', '')
        },
        **macro_form_dict
    }
    return macro_form_dict


def save_my_macros(request):
    """saves new Macro

    Attempts to save new Macro model object, but passes still
    with Integrity Error.

    Parameters
    ----------
    request: HttpRequest instance

    Returns
    ----------
    context: dict
        dict with status, form, and unit-type upon
        success or failure

    Raises
    ----------
    IngegrityError
    """

    macro_form_dict = create_macro_form_dict(request.POST)
    macro_form = MakeMacrosForm(macro_form_dict, unit_type=macro_form_dict['unit_type'])

    context = {
        'form':macro_form,
        'unit_type':macro_form_dict['unit_type']
    }

    if not macro_form.is_valid():
        context['status'] = 0
        return context

    macro_dict = macro_form_dict
    for key in ['fat_g', 'carbs_g', 'protein_g', 'carbs_percent', 'total_macro_percent']:
        macro_dict.pop(key)

    macro_dict['height'] = Decimal(macro_dict['height'])
    macro_dict['weight'] = Decimal(macro_dict['weight'])
    macro_dict['change_rate'] = Decimal(macro_dict['change_rate'])
    macro_dict['protein_percent'] = Decimal(macro_dict['protein_percent'])
    macro_dict['fat_percent'] = Decimal(macro_dict['fat_percent'])
    macro_dict['user'] = request.user
    try:
        with transaction.atomic():
            Macros.objects.create(**macro_dict)
    except IntegrityError:
        pass

    return HttpResponse('1')


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
    context['food_groups'] = [
        (
            fg['informal_name'].lower().replace(' ', '-'),
            fg['informal_name'],
        ) for fg in
        FoodGroup.objects.all().values('informal_name').distinct()
    ]
    return render(request, TEMPLATES_DIR + 'meal_maker.html', context)


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

    search_results = get_search_results(request, food_owner)

    return HttpResponse(
        json.dumps(
            {'search-results':search_results}, cls=DjangoJSONEncoder
        ), content_type='application/json'
    )


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
        meal_error_dict = dict([(k, [e for e in v]) for k,v in meal_form.errors.items()])
        context['errors'] = simplejson.dumps(meal_error_dict)
        # ingredient_error_dict = [
        #     [k for k in ingredient_formset.errors]
        # ]
        # print('ingredient_error_dict', ingredient_error_dict)
        # context['errors'] += ingredient_formset.errors

    return JsonResponse(context)


def get_my_meals(request):

    return render(request, TEMPLATES_DIR + 'my_meals.html')


def easy_picks(request, pick_type):

    context = {'status': 'success'}
    if pick_type == 'recent':
        context['my_meals'] = list(
            Foods.objects.filter(user=request.user).order_by('-date').values()
        )
    else:
        context['my_meals'] = list(
            Foods.objects.filter(user=request.user).order_by('name').values()
        )

    return JsonResponse(context)


def get_nested_ingredients(ing_dict, info_of_interest):
    ing_food_id = ing_dict['ingredient__id']
    ings = Ingredients.objects.filter(main_food = ing_food_id).values(*info_of_interest)
    if ings.count():
        ing_dict['meal_info'] = {ing_food_id:[]}
        for sub_ing_dict in ings:
            ing_dict['meal_info'][ing_food_id].append(sub_ing_dict)
            get_nested_ingredients(sub_ing_dict, info_of_interest)
    return ing_dict


def search_my_meals(request):
    
    search_terms = request.GET['search_terms'].split(' ')

    vector = SearchVector('main_food__name')
    terms_query = SearchQuery(search_terms[0])

    for term in search_terms[1:]:
        terms_query |= SearchQuery(term)

    info_of_interest = [
        'id', 'ingredient__id', 'main_food', 'main_food__id', 'main_food__name', 'ingredient__name',
        'amount', 'serving__description'
    ]

    search_results = Ingredients.objects.filter(main_food__user=request.user).annotate(
        rank=SearchRank(vector, terms_query)
    ).filter(rank__gte=0.001).order_by('-rank')[:50].values(*info_of_interest)

    # make dict instead of dict list to allow easier access to ingredients
    # via main_food__id
    search_results_dict = {'meals':[], 'meal_info':{}}
    for result in search_results:
        meal_id = result['main_food__id']
        if meal_id not in search_results_dict['meal_info']:
            meal_name = result['main_food__name']
            meal_id = result['main_food__id']
            macros_profile = Foods.objects.get(pk=meal_id).get_macros_profile()
            search_results_dict['meal_info'][meal_id] = []
            search_results_dict['meals'].append(
                {'name':meal_name, 'id':meal_id, 'macros_profile': macros_profile}
            )
        search_results_dict['meal_info'][meal_id].append(result)
    
    # get nested ingredients if meals contains multi Food ingredients
    for id_ in search_results_dict['meal_info']:
        for ing_dict in search_results_dict['meal_info'][id_]:
            get_nested_ingredients(ing_dict, info_of_interest)

    return HttpResponse(
        json.dumps({'search-results': search_results_dict}, cls=DjangoJSONEncoder),
        content_type='application/json'
    )
        
