from decimal import Decimal
import json
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from django.core.serializers.json import DjangoJSONEncoder

from meals.forms import SignUpForm, MakeMacrosForm, MacroMealForm
from meals.models import Macros, MealTemplate, Foods, Servings
from meals.helpers import get_ingredient_count


# Constants
KG_TO_LB = .45359237
IN_TO_CM = .3937
TEMPLATES_DIR = 'meals/'

# Create your views here.
def home_or_login(request):

    if request.user.is_authenticated():
        return render(request, TEMPLATES_DIR + 'base.html')
        #return render(request, 'meals/base.html')

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


def validate_POST(POST):
    """
    Validates mean_num and tdee from POST since these aren't
    part of a form

    Args:
        POST: request object's POST dict

    Returns:
        tuple of tdee, meal_num, and the validation error list
    """

    validation_errors = []

    meal_num = POST.get('meal-number', -1)
    tdee = POST.get('tdee', -1)

    if meal_num in ['', -1] or not meal_num.isdigit():
        validation_errors.append('Enter Valid Number of Meals')
        meal_num = -1
    else:
        meal_num = int(meal_num)

    if tdee in ['', -1]:
        validation_errors.append('TDEE Missing')
        tdee = -1
    else:
        tdee = int(tdee)

    return (tdee, meal_num, validation_errors,)


def create_meal_template_dict(POST):
    """
    Creates dict containing fields needed for MealTemplate model.

    Args:
        POST: request object's POST dict

    Returns:
        tuple containing dict used for creating a MealTemplate
        and a list that collects validation errors.
    """

    tdee, meal_num, validation_errors = validate_POST(POST)
    meal_template_dict = {}
    if meal_num > 0:
        for i in range(int(meal_num)):
            cals = POST.get('meal-%d' % i, '')
            try:
                cals = float(cals)
            except:
                cals = cals
            if isinstance(cals, float):
                template = 'template %d' % i
                meal_template_dict[template] = {}
                meal_template_dict[template]['name'] = 'meal_%d' % i
                meal_template_dict[template]['cals_percent'] = cals / tdee * 100
            else:
                validation_errors.append('All Meal Calorie Fields Must Contain a Number')

    validation_errors = ''.join(['<li>' + error + '</li>' for error in validation_errors])
    return (meal_template_dict, validation_errors, )


def save_meal_templates(request):
    """
    If validation errors present return a failed status key and errors,
    else return status of 1 (success).

    Args:
        request: HttpRequest object

    Returns:
        dict with a status key, and possibly validation errors
    """

    meal_template_dict, validation_errors = create_meal_template_dict(request.POST)
    if validation_errors:
        return {'status':0, 'errors':'<ul>' + validation_errors + '</ul>'}

    for model_fields in meal_template_dict.values():
        model_fields['user'] = request.user
        try:
            with transaction.atomic():
                MealTemplate.objects.create(**model_fields)
        except IntegrityError:
            pass
    return {'status':1}


def create_macro_form_dict(POST):
    """
    Creates dict containing fields needed for MakeMacroForm model.

    Args:
        POST: request object's POST dict

    Returns:
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
    """
    Attempts to save new Macro model object, but passes still
    with Integrity Error.

    Args:
        request: HTTP request object

    Returns:
        dict with status, form, and unit-type upon
        success or failure
    """
    macro_form_dict = create_macro_form_dict(request.POST)
    macro_form = MakeMacrosForm(macro_form_dict, unit_type=macro_form_dict['unit_type'])
    if not macro_form.is_valid():
        return {
            'status':0,
            'form':macro_form,
            'unit_type':macro_form_dict['unit_type']
        }

    macro_dict = macro_form_dict
    [macro_dict.pop(key) for key in  ['fat_g', 'carbs_g', 'protein_g', 'carbs_percent', 'total_macro_percent']]
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

    return {
        'status':1,
        'form':macro_form,
        'unit-type':macro_form_dict['unit_type']
    }


def save_my_macros_and_meal_templates(request):
    """
    Controls the processing and saving of Macros and MealTemplate models

    Args:
        request: HTTP request object

    Returns:
        If success HttpResponse(1), else, renders my_macros, dict of errors
    """

    my_macro_response = save_my_macros(request)
    meal_template_response = save_meal_templates(request)

    if [my_macro_response['status'], meal_template_response['status']] == [1, 1]:
        return HttpResponse('1')

    error_dict = {**my_macro_response}

    if meal_template_response != 1:
        error_dict = {**meal_template_response, **error_dict}

    return render(request, 'my_macros.html', error_dict) 


def make_meal_template_unique_cal_dict_list(user, tdee):
    """
    Creates dictionaries to be used for the MealTemplate dropdown in the
    meal maker tab.

    Args:
        user: User object for session
        tdee: Total Daily Energy Expenditure

    Returns:
        list of dictionaries corresponding to each unique calorie amount
    """

    meal_templates = MealTemplate.objects.filter(user=user)
    meal_templates_list = []
    unique_cals_dict = {}
    #for the meal cals dropdown.
    #the next two for loops take each uniqe cal to make label of all meals with that cal value
    for mt in meal_templates:
        if mt.cals_percent not in unique_cals_dict:
            unique_cals_dict[mt.cals_percent] = []
        unique_cals_dict[mt.cals_percent].append(str(int(mt.name.split('_')[-1]) + 1))
    for cp in unique_cals_dict:
        unique_cals_dict[cp].sort()
        cals = round(tdee * cp / Decimal('100'))
        meal_templates_list.append({
            'value':cals,
            'text': 'Meal ' + ','.join(unique_cals_dict[cp]) + ' - ' + str(cals) + ' cals'
        })
    meal_templates_list.sort(key=lambda x: x['text'])
    return meal_templates_list


def make_macro_breakdown_dict_list(macro):
    """
    Creates dictionaries to be used for the Macro inputs on the
    meal maker tab.

    Args:
        macro: Saved Macro object

    Returns:
        list of dictionaries corresponding to each macro
    """

    fat_pct = macro.fat_percent
    protein_pct = macro.protein_percent
    return [
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


def get_meal_maker_template(request):
    """
    Get saved Macros and MealTemplates to pass to meal_maker.html.

    Args:
        request: HttpRequest object

    Returns:
        renders meal_maker.html with dict of saved info from MyMacros tab
        such as tdee, MealTemplate info, and the Macros breakdow
    """

    macro_set = Macros.objects.filter(user = request.user)
    form = MacroMealForm(ingredients=0)
    if macro_set:
        macro = macro_set[0]
        tdee = macro.calc_tdee()

        meal_templates_dict_list = make_meal_template_unique_cal_dict_list(request.user, tdee)
        macro_breakdown_dict_list = make_macro_breakdown_dict_list(macro)
        template_data = {
            'tdee':round(tdee),
            'meal_templates':meal_templates_dict_list,
            'macro_breakdown':macro_breakdown_dict_list,
            'macro_meal_form': form
        }
    else:
        template_data = {'macro_meal_form': form}

    return render(request, TEMPLATES_DIR + 'meal_maker.html', template_data)


def search_foods(request):
    """
    Seach usda foods db based on 'search_terms' key, submitted by user.
    Args:
        request: HttpRequest object
    Returns:
        HttpResponse of search results as json
    """
    search_terms = request.GET['search_terms'].split(' ')

    vector = SearchVector('name')
    terms_query = SearchQuery(search_terms[0])

    for term in search_terms[1:]:
        terms_query |= SearchQuery(term)
    
    search_results = list(
        Foods.objects.annotate(
            rank=SearchRank(vector, terms_query)
        ).order_by('-rank')[:50].values()
    )

    # add servings
    for result in search_results:
        result['servings'] = list(Servings.objects.filter(
            food__pk=result['id']
        ).values('quantity', 'grams', 'description'))

    return HttpResponse(
        json.dumps(
            {'search-results':search_results}, cls=DjangoJSONEncoder
        ), content_type='application/json'
    )


def save_macro_meal(request):

    # print('request.POST', request.POST)
    context = {'status': 0}

    ingredient_count = get_ingredient_count(request)
    form = MacroMealForm(request.POST or None, ingredient_count=ingredient_count)
    if form.is_valid():
        data = form.cleaned_data
        with transaction.atomic():
            Foods.objects.create(
                name=data['name'],
                cals_per_gram=data['cals_per_gram'],
                fat_per_gram=data['fat_per_gram'],
                carbs_per_gram=data['carbs_per_gram'],
                protein_per_gram=data['protein_per_gram'],
            )

        context['status'] = 1
    else:
        print(form.errors)
    return JsonResponse(context)
