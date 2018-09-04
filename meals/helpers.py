from django.core.exceptions import ValidationError
from django.db import IntegrityError

from meals.models import Foods, Ingredients, Servings, FoodNotes

from decimal import Decimal


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

    ingredients = len(set([
        key[-1] for key in post_data if key.startswith('ingredient')
    ]))

    return ingredients


def save_meal(post_data):
    """save new food and ingredients

    Parameters
    ----------
    post_data: dict
        contains validated form data

    Returns
    -------
    ingredients: None
    """

    try:
        main_food = Foods.objects.create(
           name=post_data['name'],
           cals_per_gram=post_data['cals_per_gram'],
           fat_per_gram=post_data['fat_per_gram'],
           carbs_per_gram=post_data['carbs_per_gram'],
           protein_per_gram=post_data['protein_per_gram']
        )

        if post_data.get('notes', False):
            FoodNotes.objects.create(food=main_food, notes=post_data['notes'])
        
        Servings.objects.create(
            food=main_food, grams=Decimal(post_data['total_grams']),
            quantity=Decimal(1), description='entire recipe'
        )

        for i in range(get_ingredient_count(post_data)):
            ingredient_id = post_data[f'ingredient_id_{i}']
            ingredient_amt = post_data[f'ingredient_amt_{i}']
            ingredient_unit = post_data[f'ingredient_unit_{i}']

            fs = Foods.objects.all()
            ingredient = Foods.objects.get(pk=ingredient_id)
            if ingredient_unit == 'g':
                # Serving object for grams has not associated food ob
                serving = Servings.objects.get(
                    food=None
                )
            else:
                serving = Servings.objects.get(
                    food=ingredient,
                    description=ingredient_unit
                )

            Ingredients.objects.create(
                main_food=main_food,
                ingredient=ingredient, 
                serving=serving,
                amount=ingredient_amt
            )
            error = ''
            status = 1

    except IntegrityError as e:
        error = e.__cause__
        status = 0
        
    except ValidationError as e:
        error = '\n'.join(e.messages) 
        status = 0

    return (status, error,)

