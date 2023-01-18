from collections import namedtuple
from decimal import Decimal

from django.db import models
from django.conf import settings
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from django.core.validators import MaxValueValidator, MinValueValidator



# Fields
def round_decimal(value, places):
    if value is not None:
        return round(value, places)


class RoundedDecimalField(models.DecimalField):
    def to_python(self, value):
        value = super(RoundedDecimalField, self).to_python(value)
        return round_decimal(value, self.decimal_places)


# Managers
class SearchFoods(models.Manager):
    def filter_on_user(self, user):
        """return records owned by user

        Parameters
        ----------
        user: User object

        Returns
        ----------
        QuerySet
            records beloning to user
        """

        return self.get_queryset().filter(user=user)

    def rank_with_terms_and_filters(
        self,
        rank_on_field,
        rank_by_values,
        rank_threshold,
        result_fields,
        relations=None,
        limit=None,
        food_group_filters=None,
        query_set=None,
    ):

        """search for foods in db

        Parameters
        ----------
        rank_on_field: str
            field than has rank applied to it based on rank_by_values
        rank_by_valus: str
            search terms
        rank_threshold: float
            value measures relevance of record to search terms.
        result_fields: list
            contains fields which are to be returned
        relations: list
            fields related by foreign key and thereby used for prefetch_related
        limit: int
            number of records to return
        food_group_filters: list
            contains food group names with which to filter queryset
        queryset: QuerySet object
            any existing QuerySet upon which the search can be executed upon

        Returns
        ----------
        QuerySet
            QuerySet containing dicts corresponding to result_fields arg
        """

        if query_set is None:
            query_set = self.get_queryset()

        if food_group_filters:
            query_set = query_set.filter(food_group__name__in=food_group_filters)

        rank_on_field = SearchVector(rank_on_field)

        if rank_by_values != ["_all_"]:

            rank_by_values = self.make_query(rank_by_values)

            query_set = (
                query_set.annotate(rank=SearchRank(rank_on_field, rank_by_values))
                .filter(rank__gte=rank_threshold)
                .order_by("-rank")
            )
        else:
            query_set = query_set.order_by("-date")

        if relations:
            for relation in relations:
                query_set = query_set.prefetch_related(relation)

        if limit:
            query_set = query_set[:limit]

        return query_set.values(*result_fields)

    def make_query(self, search_terms):
        """build 'or' based search query

        Build 'or' based search query using search terms and
        the postgres SearchQuery class

        Parameters
        ----------
        search_terms: list
            contains terms to search db with

        Returns
        ----------
        query: CombinedSearchQuery object
        """

        query = SearchQuery(search_terms[0])
        for term in search_terms[1:]:
            query |= SearchQuery(term)

        return query

    def restructure_food_and_servings_queryset(self, search_results):
        """restructure layout of results query

        Rearrange/format/add grams info to search results to make them easier to

        Parameters
        ----------
        search_results: QuerySet object
            contains search results

        Returns
        ----------
        search_results: list
            contains reformatted dicts of the search_results
        """

        grams_serving = Servings.objects.get(food=None, description="g")
        grams_dict = {
            "servings__pk": grams_serving.pk,
            "servings__description": grams_serving.description,
            "servings__grams": grams_serving.grams,
            "servings__quantity": grams_serving.quantity,
        }

        search_results_dict = {}
        for result in search_results:
            food_name = result["name"]
            if food_name not in search_results_dict:
                # add grams serving for all foods
                # dict keys have to be in the below format to match query
                # field names
                result.update({"servings": [grams_dict]})
                search_results_dict[food_name] = result

            servings = dict(
                (
                    key,
                    item,
                )
                for key, item in result.items()
                if key.startswith("servings__")
            )
            search_results_dict[food_name]["servings"].append(servings)
            search_results_dict[food_name] = dict(
                (
                    key,
                    item,
                )
                for key, item in search_results_dict[food_name].items()
                if not key.startswith("servings__")
            )

        search_results = list(search_results_dict.values())
        return search_results

    def restructure_ingredients_queryset_to_dict(self, query_set):
        """restructure qeury set to dict

        Rearrange/format/add info to meal/ingredients queryset to make them easier to
        work with down stream

        Parameters
        ----------
        query_set: QuerySet object
            contians ingredient model objects

        Returns
        ----------
        search_results_dict: dict
        """

        search_results_dict = {"meals": [], "meal_info": {}}
        for result in query_set:
            meal_id = result["id"]
            if meal_id not in search_results_dict["meal_info"]:
                meal_name = result["name"]
                macros_profile = Foods.objects.get(pk=meal_id).get_macros_profile()
                search_results_dict["meal_info"][meal_id] = []
                search_results_dict["meals"].append(
                    {"name": meal_name, "id": meal_id, "macros_profile": macros_profile}
                )
            search_results_dict["meal_info"][meal_id].append(result)

        return search_results_dict

    def add_nested_ingredients_to_ingredient_dict(
        self, ingredient_dict, fields_of_interest
    ):
        """"""

        for id_ in ingredient_dict["meal_info"]:
            for ing_dict in ingredient_dict["meal_info"][id_]:
                self.get_nested_ingredients(ing_dict, fields_of_interest)

        return ingredient_dict

    def get_nested_ingredients(self, ing_dict, fields_of_interest):
        """get ingredients made up of other ingredients

        Some ingredients are themselves made up of ingredients,
        and so this function recursively drills down to get all the
        ingredients associated with a meal.

        Parameters
        ----------
        ing_dict: dict
            contains meal and ingredient info
        fields_of_interest: list
            contains fields to be fetched in queries

        Returns
        ----------
        ing_dict: dict
            contains meal and ingredient info
        """
        ing_food_id = ing_dict["ingredients__ingredient"]
        ings = Foods.objects.filter(pk=ing_food_id).values(*fields_of_interest)
        if ings[0]["ingredients"]:
            ing_dict["meal_info"] = {ing_food_id: []}
            for sub_ing_dict in ings:
                ing_dict["meal_info"][ing_food_id].append(sub_ing_dict)
                self.get_nested_ingredients(sub_ing_dict, fields_of_interest)

        return ing_dict


# Create your models here.
class Macros(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    UNIT_CHOICES = (
        (
            "imperial",
            "Imperial",
        ),
        (
            "metric",
            "Metric",
        ),
    )
    unit_type = models.CharField(
        max_length=8, choices=UNIT_CHOICES, default="imperial", blank=False
    )

    GENDER_CHOICES = (
        (
            "male",
            "Male",
        ),
        (
            "female",
            "Female",
        ),
    )
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, blank=False)

    age = models.IntegerField(blank=False)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=False)
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=False)

    ACTIVITY_CHOICES = (
        (
            "none",
            "",
        ),
        (
            "light",
            "",
        ),
        (
            "medium",
            "",
        ),
        (
            "high",
            "",
        ),
        (
            "very high",
            "",
        ),
    )
    activity = models.CharField(
        max_length=9, choices=ACTIVITY_CHOICES, default="none", blank=False
    )

    DIRECTIONS = (
        (
            "lose",
            "Lose",
        ),
        (
            "maintain",
            "Maintain",
        ),
        (
            "gain",
            "Gain",
        ),
    )
    direction = models.CharField(
        max_length=8, choices=DIRECTIONS, default="lose", blank=False
    )

    change_rate = models.DecimalField(max_digits=9, decimal_places=8, blank=False)
    fat_percent = models.DecimalField(max_digits=4, decimal_places=2, blank=False)
    protein_percent = models.DecimalField(max_digits=4, decimal_places=2, blank=False)

    def calc_tdee(self):
        """calculate total daily energy expenditure

        RETURNS
        -------
        tdee: decimal.Decimal
        """

        activity_factor = {
            "none": Decimal("1.2"),
            "light": Decimal("1.375"),
            "medium": Decimal("1.55"),
            "high": Decimal("1.725"),
            "very high": Decimal("1.9"),
        }[self.activity]

        direction_factor = {
            "maintain": Decimal("0"),
            "lose": Decimal("-1"),
            "gain": Decimal("1"),
        }[self.direction]

        # convert kg to lb by dividing by .45359237
        weight_change = self.change_rate / Decimal(".45359237") * direction_factor * 500

        tdee = (
            (Decimal("10") * self.weight)
            + (Decimal("6.25") * self.height)
            - (Decimal("5") * self.age)
        )
        if self.gender == "male":
            tdee += 5
        else:
            tdee -= 161

        tdee = (tdee * activity_factor) + weight_change
        return tdee

    def __repr__(self):
        return f"{self.user.username}'s Macro Info"

    def __str__(self):
        return self.__repr__()


class FoodType(models.Model):
    """ Designates Food as Meal, Recipe, or Food"""

    name = models.TextField(blank=False, unique=True)

    def __repr__(self):
        return "{}".format(self.name)

    def __str__(self):
        return self.__repr__()


class FoodGroup(models.Model):
    """ USDA DB Food Group"""

    name = models.TextField(blank=False, unique=True)
    rank = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ("rank",)

    def __repr__(self):
        return f"{self.name}, {self.rank}"

    def __str__(self):
        return self.__repr__()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.__class__.objects.filter(rank__gte=self.rank).update(
                rank=models.F("rank") + 1
            )
        super().save(*args, **kwargs)


FoodMacros = namedtuple("FoodMacros", "cals, fat, carbs, sugar, protein")


class Foods(models.Model):

    _grams = None
    max_digits = 6
    decimal_places = 4

    name = models.TextField(blank=False, unique=True)
    cals_per_gram = models.DecimalField(
        max_digits=max_digits, decimal_places=decimal_places, blank=False, null=True
    )
    fat_per_gram = models.DecimalField(
        max_digits=max_digits, decimal_places=decimal_places, blank=False, null=True
    )
    carbs_per_gram = models.DecimalField(
        max_digits=max_digits, decimal_places=decimal_places, blank=False, null=True
    )
    protein_per_gram = models.DecimalField(
        max_digits=max_digits, decimal_places=decimal_places, blank=False, null=True
    )
    sugar_per_gram = models.DecimalField(
        max_digits=max_digits, decimal_places=decimal_places, blank=False, null=True
    )
    date = models.DateTimeField(auto_now_add=True, null=True)
    food_type = models.ForeignKey("FoodType", null=True, on_delete=models.SET_NULL)
    food_group = models.ForeignKey("FoodGroup", null=True, on_delete=models.SET_NULL)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)

    objects = models.Manager()
    searcher = SearchFoods()

    def __repr__(self):
        return "{}".format(self.name)

    def __str__(self):
        return self.__repr__()

    @property
    def grams(self):
        if self._grams is None:
            self._grams = sum([i.grams for i in self.ingredients.all()])
        return self._grams

    @grams.setter
    def grams(self, grams):
        self._grams = grams

    @property
    def cals(self):
        return self.grams * self.cals_per_gram

    @property
    def fat(self):
        return self.grams * self.fat_per_gram

    @property
    def carbs(self, as_cals=True):
        return self.grams * self.carbs_per_gram

    @property
    def sugar(self, as_cals=True):
        return self.grams * self.sugar_per_gram

    @property
    def protein(self):
        return self.grams * self.protein_per_gram

    @property
    def macros(self):
        cals = self.cals
        fat = self.fat / 9
        carbs = self.carbs / 4
        sugar = self.sugar / 4
        protein = self.protein / 4
        macros = FoodMacros(
            cals=cals, fat=fat, carbs=carbs, sugar=sugar, protein=protein
        )
        return macros

    def set_macros_per_gram(
        self,
        cals=None,
        fat=None,
        carbs=None,
        sugar=None,
        protein=None,
        serving_amount=None,
    ):
        """calculate the values for the macros / gram fields

        Set the macros / gram fields.  If single food call use calc_macro_per_gram(),
        but if food made up of ingredients then use calc_ingredients_macro_per_gram()

        Parameters
        ----------
        all args None or decimal.Decimal
        """

        if cals:
            self.cals_per_gram = self.calc_macro_per_gram("cals", cals, serving_amount)
            self.fat_per_gram = self.calc_macro_per_gram("fat", fat, serving_amount)
            self.carbs_per_gram = self.calc_macro_per_gram(
                "carbs", carbs, serving_amount
            )
            self.sugar_per_gram = self.calc_macro_per_gram(
                "sugar", sugar, serving_amount
            )
            self.protein_per_gram = self.calc_macro_per_gram(
                "protein", protein, serving_amount
            )
        else:
            ings = self.ingredients.all()
            self.cals_per_gram = self.calc_ingredients_macro_per_gram("cals")
            self.fat_per_gram = self.calc_ingredients_macro_per_gram("fat")
            self.carbs_per_gram = self.calc_ingredients_macro_per_gram("carbs")
            self.sugar_per_gram = self.calc_ingredients_macro_per_gram("sugar")
            self.protein_per_gram = self.calc_ingredients_macro_per_gram("protein")

    def get_macros_profile(self):
        grams = self.grams
        total_cals = Decimal(self.cals_per_gram * grams)
        macros_dict = {
            "cals": total_cals,
            "fat": self.fat_per_gram * grams / 9,
            "fat_pct": (self.fat_per_gram * grams / total_cals) * 100,
            "carbs": self.carbs_per_gram * grams / 4,
            "carbs_pct": (self.carbs_per_gram * grams / total_cals) * 100,
            "sugar": self.sugar_per_gram * grams / 4,
            "sugar_pct": (self.sugar_per_gram * grams / total_cals) * 100,
            "protein": self.protein_per_gram * grams / 4,
            "protein_pct": (self.protein_per_gram * grams / total_cals) * 100,
        }

        return macros_dict

    def calc_ingredients_macro_per_gram(self, macro):
        ingredients = self.ingredients.all()
        macro_per_gram = (
            sum(
                [
                    ing.ingredient.__getattribute__(f"{macro}_per_gram") * ing.grams
                    for ing in ingredients
                ]
            )
            / self.grams
        )

        return macro_per_gram

    def calc_macro_per_gram(self, macro, macro_amount, serving_amount):
        macro_multipliers = {"cals": 1, "fat": 9, "carbs": 4, "sugar": 4, "protein": 4}
        macro_per_gram = macro_amount * macro_multipliers[macro] / serving_amount

        return macro_per_gram


class FoodNotes(models.Model):

    notes = models.TextField(blank=False, null=False)
    food = models.ForeignKey("Foods", related_name="notes", on_delete=models.CASCADE)

    def __repr__(self):
        return f"{self.food.name}: Notes "

    def __str__(self):
        return self.__repr__()


class Servings(models.Model):

    max_digits = 6
    decimal_places = 2
    quantity = models.DecimalField(max_digits=max_digits, decimal_places=decimal_places)
    description = models.CharField(max_length=200)
    grams = models.DecimalField(max_digits=max_digits, decimal_places=decimal_places)
    food = models.ForeignKey(
        "Foods", on_delete=models.CASCADE, related_name="servings", null=True
    )

    @property
    def grams_per_serving_unit(self):
        return self.grams / self.quantity

    def __repr__(self):
        if self.food:
            return "{0} - {1}".format(self.food.name, self.description)
        return "{0}".format(self.description)

    def __str__(self):
        return self.__repr__()


class Ingredients(models.Model):

    main_food = models.ForeignKey(
        "Foods",
        on_delete=models.CASCADE,
        related_name="ingredients",
    )

    ingredient = models.ForeignKey(
        "Foods",
        on_delete=models.CASCADE,
        related_name="as_ingredient",
    )

    serving = models.ForeignKey(
        "Servings",
        on_delete=models.CASCADE,
    )

    amount = models.DecimalField(max_digits=6, decimal_places=2)

    @property
    def grams(self):
        serving = self.get_serving()
        return self.amount * serving.grams_per_serving_unit

    def get_serving(self):
        return self.serving

    def __repr__(self):
        return "{0} - {1}".format(self.main_food.name, self.ingredient.name)

    def __str__(self):
        return self.__repr__()

    def save(self, *args, **kwargs):
        # TO DO: update related food servings
        super().save(*args, **kwargs)
