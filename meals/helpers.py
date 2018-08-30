def get_ingredient_count(request):
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
        key[-1] for key in request.POST if key.startswith('ingredient')
    ]))

    return ingredients
