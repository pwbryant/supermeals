import json
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder

from meals.forms import SignUpForm, MakeMacrosForm, MacroMealForm, \
        MealRecipeForm, NewFoodForm, NewFoodServingForm
from meals.models import Macros, Foods, FoodGroup, Ingredients, Servings, \
        FoodNotes, FoodType
from meals.helpers import make_ingredient_formset, \
        save_meal_notes_ingredients, make_macro_breakdown_dict_list

from meals.decorators import user_is_not_guest

# Constants
KG_TO_LB = .45359237
IN_TO_CM = .3937
TEMPLATES_DIR = 'meals/'

BAD_REQUEST = 400
OK = 200
CREATED = 201
# Create your views here.

@login_required
def home_or_login(request):
    return render(request, TEMPLATES_DIR + 'base.html')


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

    return render(request, TEMPLATES_DIR + 'sign_up.html', {"form":form})


@login_required
def get_my_macros(request):
    """get form and template for my macros tab

    Parameters
    ----------
    request: HttpRequest instance

    Returns
    ----------
    render response
    """

    form = MakeMacrosForm(unit_type='imperial')
    return render(request, TEMPLATES_DIR + 'my_macros.html', {
        'form':form
    })


@login_required
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


@login_required
def get_meal_maker_template(request):
    """passes saved info to meal_maker tab

    Parameters
    ----------
    request: HttpRequest instance

    Returns
    ----------
    render: render instance
        renders meal_maker.html with info from MyMacros tab
        such as tdee, MealTemplate info, and the Macros breakdown
    """

    macro_set = Macros.objects.filter(user=request.user)
    if macro_set:
        macro = macro_set[0]
        macro_breakdown_dict_list = make_macro_breakdown_dict_list(macro)# in helpers.py
        tdee = macro.calc_tdee()
        context = {
            'tdee': round(tdee),
            'has_macro': True
        }
    else:
        macro_breakdown_dict_list = make_macro_breakdown_dict_list()
        context = {'has_macro': False}

    context['macro_breakdown'] = macro_breakdown_dict_list
    context['macro_meal_form'] = MacroMealForm()

    # informal name to use in input id, and to use in label
    context['filters'] = [
        {
            'id_name': fg['name'].lower().replace(' ', '-'),
            'name': fg['name']
        } for fg in
        FoodGroup.objects.all().values('name').distinct()
    ]
    return render(request, TEMPLATES_DIR + 'meal_maker.html', context)


@user_is_not_guest
@login_required
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
    ingredient_formset = make_ingredient_formset(request)#in helpers.py

    context = {'status': 0, 'errors': ''}
    if meal_form.is_valid() and ingredient_formset.is_valid():
        save_meal_notes_ingredients(request.user, meal_form, ingredient_formset)#in helpers.py
        context['status'] = 1

    else:
        context['status'] = 0
        meal_error_dict = dict([
            (k, [e for e in v]) for k, v in meal_form.errors.items()
        ])
        context['errors'] = json.dumps(meal_error_dict)

    return JsonResponse(context)


@user_is_not_guest
@login_required
def get_my_meals(request):
    return render(request, TEMPLATES_DIR + 'my_meals.html')


@user_is_not_guest
@login_required
def delete_my_meals(request):

    meal_id = request.POST.get('meal_id')
    if meal_id and meal_id.isdigit():
        Foods.objects.get(pk=meal_id).delete()
        return JsonResponse({'status': 1})

    return JsonResponse({'status': 0})


@login_required
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
        'protein_per_gram', 'servings__pk', 'servings__description',
        'servings__grams', 'servings__quantity'
    ]

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


@login_required
def search_my_meals(request, meal_or_recipe):
    """search db for saved meals

    Fetch a saved meal/recipe along with its attendant
    ingredients, servings, and notes

    Parameters
    ----------
    request: HttpRequest object
    meal_or_recipe: str
        search for either meals or recipes

    Returns
    ----------
    HttpResponse: HttpResponse instance
        search results as json
    """

    search_terms = request.GET['search_terms'].split(' ')

    fields_of_interest = [
        'main_food', 'main_food__ingredient', 'id', 'name',
        'main_food__ingredient__name', 'main_food__amount',
        'main_food__serving__description', 'notes__notes'
    ]
    filters = [{'meal': 'My Meals', 'recipe': 'My Recipes'}[meal_or_recipe]]
    rank_by_field = 'name'
    rank_threshold = 0.001
    foreign_key_relations = ['servings', 'notes']
    record_limit = 20
    search_args = [
        rank_by_field, search_terms, rank_threshold, fields_of_interest,
        foreign_key_relations, record_limit, filters
    ]
    search_kwargs = {'query_set': Foods.searcher.filter_on_user(request.user)}

    search_results_dict = Foods.searcher.add_nested_ingredients_to_ingredient_dict(
        Foods.searcher.restructure_ingredients_queryset_to_dict(
            Foods.searcher.rank_with_terms_and_filters(*search_args, **search_kwargs)
        ), fields_of_interest
    )

    return HttpResponse(
        json.dumps(
            {'search-results': search_results_dict}, cls=DjangoJSONEncoder
        ),
        content_type='application/json'
    )


@user_is_not_guest
@login_required
def render_add_recipe(request):
    """render add_recipe.html
    
    Adds food groups to context in add_recipe.html

    Parameters
    ----------
    request: HttpRequest object

    Returns
    ----------
    HttpResponse object with rendered template 
    """

    context = {
        'filters': [
            {
                'id_name': fg['name'].lower().replace(' ', '-'),
                'name': fg['name']
            } for fg in
            FoodGroup.objects.all().values('name')
        ]
    }

    return render(request, TEMPLATES_DIR + 'add_recipe.html', context)


@user_is_not_guest
@login_required
def save_recipe(request):
    """save new recipe

    If post, handle when additional serving info is present / absent
    and save both food and its potential associated servings. Of note,
    fd_form needs to be passed grams (.consume_grams())so that it can
    calculate macros / gram.

    Parameters
    ----------
    request: HttpRequest object

    Returns
    ----------
    JsonResponse
        success/failure status/errors
    """

    # request.POST['user'] = request.user
    form = MealRecipeForm(request.POST)
    context = {}
    if form.is_valid():
        form.instance.user = request.user
        form.save()
        context['status'] = CREATED

    else:
        context['errors'] = form.errors
        context['status'] = BAD_REQUEST

    return JsonResponse(context)


@user_is_not_guest
@login_required
def add_food(request):
    """load page or save new food

    If post, handle when additional serving info is present / absent
    and save both food and its potential associated servings. Of note,
    fd_form needs to be passed grams (.consume_grams())so that it can
    calculate macros / gram.

    Parameters
    ----------
    request: HttpRequest object

    Returns
    ----------
    JsonResponse / or template render
    """

    if request.method == 'POST':
        fd_form = NewFoodForm(request.POST)
        srv_form = NewFoodServingForm(request.POST)
        if request.POST.get('description'): #indicates additional serving info
            if fd_form.is_valid() and srv_form.is_valid():
                fd_form.consume_grams(srv_form.cleaned_data['grams'])
                fd_form.instance.user = request.user
                fd_form.save()
                srv_form.instance.food = fd_form.instance
                srv_form.save()
                return JsonResponse({'status_code': CREATED})

        else:
            srv_form.is_valid() # generate serving errors
            # Only leave grams errors if they exist,
            srv_form.errors.pop('quantity', None)
            srv_form.errors.pop('description', None)
            if fd_form.is_valid() and not srv_form.errors.get('grams'):
                fd_form.consume_grams(srv_form.cleaned_data['grams']) 
                fd_form.instance.user = request.user
                fd_form.save()
                return JsonResponse({'status_code': CREATED})

        return JsonResponse({
            'status_code': BAD_REQUEST,
            'errors': {**srv_form.errors, **fd_form.errors}
        })

    context = {
        'add_food_form': NewFoodForm(),
        'add_food_srv_form': NewFoodServingForm()
    }
    return render(request, TEMPLATES_DIR + 'add_food.html', context)
