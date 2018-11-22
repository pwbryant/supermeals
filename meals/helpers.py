from django import forms
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank

from meals.models import Foods, FoodGroup, Ingredients, Servings, FoodNotes
from meals.forms import MacroIngredientForm


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

    for ing_form in ingredient_formset:
        new_ing = ing_form.save(commit=False)
        new_ing.main_food = new_food
        new_ing.save()

    new_food.set_macros_per_gram()
    new_food.save()

def get_search_results(request, food_owner):

    search_terms = request.GET['search_terms'].split(' ')
    filter_names = request.GET.getlist('filters[]')

    # 'none' indicates that no-filter was select, therefore all food groups
    # should be searched
    if filter_names[0] == 'none':
        filter_names = [
            fg['informal_name'] for fg in
            FoodGroup.objects.all().values('informal_name').distinct()
        ]

    # build query
    vector = SearchVector('name')
    terms_query = SearchQuery(search_terms[0])

    for term in search_terms[1:]:
        terms_query |= SearchQuery(term)

    # below if statements handle wether to restrict to only user created foods
    if food_owner == 'user':
        search_results = list(
            Foods.objects.filter(user=request.user).annotate(
                rank=SearchRank(vector, terms_query)
            ).filter(
                food_group__informal_name__in=filter_names
            ).filter(rank__gte=0.001).order_by('-rank')[:50].values()
        )

    if food_owner == 'all':
        search_results = list(
            Foods.objects.annotate(
                rank=SearchRank(vector, terms_query)
            ).filter(
                food_group__informal_name__in=filter_names
            ).filter(rank__gte=0.001).order_by('-rank')[:50].values()
        )

    # add servings
    for result in search_results:
        result['servings'] = list(Servings.objects.filter(
            food__pk=result['id']
        ).values('quantity', 'grams', 'description'))

    return search_results
