from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator,MinValueValidator
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank

from decimal import Decimal
# Create your models here.

class Macros(models.Model):
	
    user = models.OneToOneField('auth.User',on_delete=models.CASCADE)
    UNIT_CHOICES = (
            ('imperial','Imperial',),
            ('metric','Metric',),
    )
    unit_type = models.CharField(
        max_length=8, choices=UNIT_CHOICES,default='imperial', blank=False
    )

    GENDER_CHOICES = (
            ('male','Male',),
            ('female','Female',),
    )
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, blank=False)
    age = models.IntegerField(blank=False)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=False)	
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=False)
    ACTIVITY_CHOICES = (
            ('none','',),
            ('light','',),
            ('medium','',),
            ('high','',),
            ('very high','',),
    )

    activity = models.CharField(
        max_length=9,choices=ACTIVITY_CHOICES,default='none',blank=False
    )
    DIRECTIONS = (
            ('lose','Lose',),
            ('maintain','Maintain',),
            ('gain','Gain',),
    )
    direction = models.CharField(max_length=8, choices=DIRECTIONS, default='lose', blank=False)	
    change_rate = models.DecimalField(max_digits=9, decimal_places=8, blank=False)
    fat_percent = models.DecimalField(max_digits=4, decimal_places=2 ,blank=False)
    protein_percent = models.DecimalField(max_digits=4, decimal_places=2, blank=False)

    def calc_tdee(self):
        activity_factor = {
            'none':Decimal('1.2'),
            'light':Decimal('1.375'),
            'medium':Decimal('1.55'),
            'high':Decimal('1.725'),
            'very high':Decimal('1.9')
        }[self.activity]

        direction_factor = {
                 'maintain': Decimal('0'),
                 'lose': Decimal('-1'),
                 'gain': Decimal('1'),
         }[self.direction];

        # convert kg to lb by dividing by .45359237
        weight_change = self.change_rate / Decimal('.45359237') * direction_factor * 500 
        
        tdee = (
            (Decimal('10') * self.weight) + (Decimal('6.25') * self.height)
            - (Decimal('5') * self.age)
        )
        if self.gender == 'male':
                tdee += 5 
        else:
                tdee -= 161

        tdee = (tdee * activity_factor) + weight_change

        return tdee


class FoodType(models.Model):
    """ Designates Food as Meal, Recipe, or Food"""

    name = models.TextField(blank=False, unique=True)

    def __repr__(self):
        return '{}'.format(self.name)


class FoodGroup(models.Model):
    """ USDA DB Food Group"""

    name = models.TextField(blank=False, unique=True)
    informal_name = models.TextField(blank=False)
    informal_rank = models.IntegerField(blank=True, null=True)


    class Meta:
        ordering = ('informal_rank',)

    def __repr__(self):
        return '{}'.format(self.name)


class SearchFoods(models.Manager):

    def filter_on_user(self, user):

        return self.get_queryset().filter(user=user)


    def rank_with_terms_and_filters(self,
            rank_on_field,
            rank_by_values, 
            filters,
            rank_threshold,
            limit,
            result_fields,
            query_set=None):

        rank_on_field = SearchVector(rank_on_field)
        rank_by_values = self.make_query(rank_by_values)

        if query_set is None:
            query_set = self.get_queryset()

        query_set = query_set.annotate(
            rank=SearchRank(rank_on_field, rank_by_values)
            ).filter(
                food_group__informal_name__in=filters
           ).filter(
                rank__gte=rank_threshold
            ).order_by('-rank').prefetch_related('servings')
            
        return query_set.values(*result_fields)[:limit]

    
    def make_query(self, search_terms):

        query = SearchQuery(search_terms[0])
        for term in search_terms[1:]:
            query |= SearchQuery(term)

        return query


    def restructure_food_and_servings_queryset(self, search_results):

        search_results_dict = {}
        for result in search_results:
            food_name = result['name']
            if food_name not in search_results_dict:
                result.update({'servings': []})
                search_results_dict[food_name] = result

            servings = dict(
                (key, item,) for key, item in result.items()
                if key.startswith('servings__')
            )
            search_results_dict[food_name]['servings'].append(servings)
            search_results_dict[food_name] = dict(
                (key, item,) for key, item in search_results_dict[food_name].items()
                if not key.startswith('servings__')
                )

        search_results = list( search_results_dict.values() )

        return search_results
        

    def restructure_ingredients_queryset_to_dict(self, query_set):
        search_results_dict = {'meals':[], 'meal_info':{}}
        for result in query_set:
            meal_id = result['id']
            if meal_id not in search_results_dict['meal_info']:
                meal_name = result['name']
                macros_profile = Foods.objects.get(pk=meal_id).get_macros_profile()
                search_results_dict['meal_info'][meal_id] = []
                search_results_dict['meals'].append(
                    {'name':meal_name, 'id':meal_id, 'macros_profile': macros_profile}
                )
            search_results_dict['meal_info'][meal_id].append(result)

        return search_results_dict


    def add_nested_ingredients_to_ingredient_dict(self, ingredient_dict,
            fields_of_interest):

        for id_ in ingredient_dict['meal_info']:
            for ing_dict in ingredient_dict['meal_info'][id_]:
                get_nested_ingredients(ing_dict, fields_of_interest)


    def get_nested_ingredients(self, ing_dict, fields_of_interest):
        ing_food_id = ing_dict['ingredient__id']
        ings = Ingredients.objects.filter(
            main_food=ing_food_id
        ).values(*fields_of_interest)
        if ings.count():
            ing_dict['meal_info'] = {ing_food_id:[]}
            for sub_ing_dict in ings:
                ing_dict['meal_info'][ing_food_id].append(sub_ing_dict)
                get_nested_ingredients(sub_ing_dict, fields_of_interest)

        return ing_dict


class Foods(models.Model):

    name = models.TextField(blank=False, unique=True)
    cals_per_gram = models.DecimalField(
        max_digits=6, decimal_places=4, blank=False, null=True
    )
    fat_per_gram = models.DecimalField(
        max_digits=6, decimal_places=4, blank=False, null=True
    )
    carbs_per_gram = models.DecimalField(
        max_digits=6, decimal_places=4, blank=False, null=True
    )
    protein_per_gram = models.DecimalField(
        max_digits=6, decimal_places=4, blank=False, null=True
    )
    sugar_per_gram = models.DecimalField(
        max_digits=6, decimal_places=4, blank=False, null=True
    )
    date = models.DateTimeField(auto_now_add=True, null=True)
    food_type = models.ForeignKey('FoodType', null=True)
    food_group = models.ForeignKey('FoodGroup', null=True)

    user = models.ForeignKey(User, null=True)

    objects = models.Manager()
    searcher = SearchFoods()

    def as_dict(self):
        return {
            'name': self.name,
            'cals_per_gram': self.cals_per_gram,
            'fat_per_gram': self.fat_per_gram,
            'carbs_per_gram': self.carbs_per_gram,
            'protein_per_gram': self.protein_per_gram
        }

    def __repr__(self):
        return '{}'.format(self.name)

    def set_macros_per_gram(self):
                
        ings = Ingredients.objects.filter(main_food=self)
        total_grams = sum([ing.serving.grams * ing.amount for ing in ings])

        self.cals_per_gram = self.calc_macro_per_gram(ings, 'cals', total_grams)
        self.fat_per_gram = self.calc_macro_per_gram(ings, 'fat', total_grams)
        self.carbs_per_gram = self.calc_macro_per_gram(ings, 'carbs', total_grams)
        self.protein_per_gram = self.calc_macro_per_gram(ings, 'protein', total_grams)


    def get_macros_profile(self):
                
        ings = Ingredients.objects.filter(main_food=self)
        total_grams = Decimal(sum([ing.serving.grams * ing.amount for ing in ings]))
        total_cals = Decimal(self.cals_per_gram * total_grams)

        macros_dict = {
            'cals': total_cals ,
            'fat':  self.fat_per_gram * total_grams / Decimal(9.0),
            'fat_pct':  (self.fat_per_gram * total_grams / total_cals) * 100,
            'carbs': self.carbs_per_gram * total_grams / Decimal(4.0),
            'carbs_pct': (self.carbs_per_gram * total_grams / total_cals) * 100,
            'protein': self.protein_per_gram * total_grams / Decimal(4.0),
            'protein_pct': (self.protein_per_gram * total_grams / total_cals) * 100
        }
        return macros_dict


    def calc_macro_per_gram(self, ingredients, macro, total_grams):
        macro_per_gram = sum([
            ing.ingredient.__getattribute__(f'{macro}_per_gram')
            * ing.serving.grams * ing.amount for ing in ingredients
        ]) / total_grams

        return macro_per_gram


class FoodNotes(models.Model):

    notes = models.TextField(blank=False, null=False) 
    food = models.ForeignKey('Foods', on_delete=models.CASCADE)


class Servings(models.Model):

    quantity = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.CharField(max_length=200)
    grams = models.DecimalField(max_digits=6, decimal_places=2)
    food = models.ForeignKey(
        'Foods',
        on_delete=models.CASCADE,
        related_name='servings',
        null=True
        )

    def __repr__(self):
        if self.food:
            return '{0} - {1}'.format(self.food.name, self.description)
        return '{0}'.format(self.description)
    

def round_decimal(value, places):
    if value is not None:
        return round(value, places)

class RoundedDecimalField(models.DecimalField):
    def to_python(self, value):
        value = super(RoundedDecimalField, self).to_python(value)
        return round_decimal(value, self.decimal_places)


class Ingredients(models.Model):
    
    main_food = models.ForeignKey(
            'Foods',
            on_delete=models.CASCADE,
            related_name='main_food',
            )

    ingredient = models.ForeignKey(
            'Foods',
            on_delete=models.CASCADE,
            related_name='ingredient',
            )

    serving = models.ForeignKey(
            'Servings',
            on_delete=models.CASCADE,
            )

    amount = models.DecimalField(max_digits=6, decimal_places=2)

    def __repr__(self):
        return '{0} - {1}'.format(
            self.main_food.name, self.ingredient.name
        )
