from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from meals.models import Macros, Foods, Ingredients, Servings, FoodNotes, \
    FoodGroup, FoodType

from decimal import Decimal


#LoginForm/SignUpForm errors
EMPTY_USERNAME_ERROR = "Username Missing"
EMPTY_EMAIL_ERROR = "Email Missing"
EMPTY_PASSWORD_ERROR = "Password Missing"
DUPLICATE_USERNAME_ERROR = "Username taken"
INVALID_USERNAME_ERROR = "Enter a valid username. This value may contain only \
letters, numbers, and @/./+/-/_ characters."

#MyMacrosForm erros
INVALID_POST_ERROR = "Invalid POST"
EMPTY_AGE_ERROR = "Age Missing"
EMPTY_WEIGHT_ERROR = "Weight Missing"
EMPTY_HEIGHT_ERROR = "Height Missing"
EMPTY_MACRO_ERROR = "Macro Info Missing"
DEFAULT_INVALID_INT_ERROR = "Enter a whole number"
EMPTY_RATE_ERROR = "Weight Change Rate Missing"
INVALID_MACRO_ERROR = "Invalid Macro Ratio Values"
OUT_OF_RANGE_MACRO_ERROR = "Macro Percent Out Of Range"
MACROS_DONT_ADD_UP_ERROR = "Macro Percentages Do Not Add Up Too 100"
EMPTY_CALS_ERROR = "Meal/Snack Calories Missing"


# FUNCTIONS
# ==================================================

def round_decimal(value, places):
    if value is not None:
        return round(value, places)


# FIELDS
# ==================================================

class RoundedDecimalField(forms.DecimalField):
    def to_python(self, value):
        value = super(RoundedDecimalField, self).to_python(value)
        return round_decimal(value, self.decimal_places)


# FORMS
# ==================================================


class NewFoodForm(forms.ModelForm):

    serving = forms.DecimalField(
        max_digits=6, decimal_places=2, widget=forms.TextInput(
            attrs={'id': 'add-food-serving'}
        )
    )
    cals = forms.DecimalField(
        max_digits=6, decimal_places=2, widget=forms.TextInput(
            attrs={'id': 'add-food-cals'}
        )
    )
    fat = forms.DecimalField(
        max_digits=6, decimal_places=2, widget=forms.TextInput(
            attrs={'id': 'add-food-fat'}
        )
    )
    carbs = forms.DecimalField(
        max_digits=6, decimal_places=2, widget=forms.TextInput(
            attrs={'id': 'add-food-carbs'}
        )
    )
    sugar = forms.DecimalField(
        max_digits=6, decimal_places=2, widget=forms.TextInput(
            attrs={'id': 'add-food-sugar'}
        )
    )
    protein = forms.DecimalField(
        max_digits=6, decimal_places=2, widget=forms.TextInput(
            attrs={'id': 'add-food-protein'}
        )
    )

    choices = tuple(
        (fg['name'], fg['name'],) for fg
        in FoodGroup.objects.all().values('name').distinct()
        if not fg['name'].startswith('My')
    )
    food_group = forms.ChoiceField(
        choices=choices, label='Food Group', widget=forms.Select(
            attrs={'id': 'add-food-food-group'},
        )
    )


    class Meta:
        model = Foods
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'id': 'add-food-name'})}


    def save(self):

        food = self.instance
        food.food_group = FoodGroup.objects.get(
            name=self.cleaned_data['food_group']
        )
        food.food_type = FoodType.objects.get(name='food')

        food.set_macros_per_gram(
            Decimal(self.cleaned_data['cals']),
            Decimal(self.cleaned_data['fat']),
            Decimal(self.cleaned_data['carbs']),
            Decimal(self.cleaned_data['sugar']),
            Decimal(self.cleaned_data['protein']),
            Decimal(self.cleaned_data['serving'])
        )
        food.save()
                    


class MealRecipeForm(forms.ModelForm):

    notes = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        ingredient_fields = [
            key for key in args[0] if key.startswith('ingredient')
        ]

        for ing_field in ingredient_fields:

            if 'amount' in ing_field:
                self.fields[ing_field] = RoundedDecimalField(
                    max_digits=6, decimal_places=2
                )
            else:
                self.fields[ing_field] = forms.IntegerField()


    def clean(self):

        self.cleaned_data = super().clean()
        ingredients = set()
        ingredient_names = set()
        i = 0
        name_fieldname = f'ingredient_{i}'
        amount_fieldname = f'ingredient_amount_{i}'
        unit_fieldname = f'ingredient_unit_{i}'

        while self.cleaned_data.get(name_fieldname):

            name = self.cleaned_data[name_fieldname]
            if name in ingredient_names:
                self.add_error(name_fieldname, 'Duplicate Ingredient')
            else:
                ingredient_names.add(name)
                amount = self.cleaned_data.get(amount_fieldname)
                unit = self.cleaned_data.get(unit_fieldname)
                if amount and name:
                    ingredients.add((name, amount, unit,))

            i += 1
            name_fieldname = f'ingredient_{i}'
            amount_fieldname = f'ingredient_amount_{i}'
            unit_fieldname = f'ingredient_unit_{i}'

        self.cleaned_data['ingredients'] = ingredients

    
    def save(self):

        food = self.instance
        food.food_group = FoodGroup.objects.get(name='My Recipes')
        food.food_type = FoodType.objects.get(name='recipe')
        food.save()

        if self.cleaned_data.get('notes'):
            FoodNotes.objects.create(
                food=food, notes=self.cleaned_data['notes']
            )

        for ing_pk, amount, unit in self.cleaned_data['ingredients']:
            ingredient = Foods.objects.get(pk=ing_pk)
            serving = Servings.objects.get(pk=unit)
            ing = Ingredients.objects.create(
                main_food=food,
                ingredient=ingredient,
                serving=serving,
                amount=amount
            )

        food.set_macros_per_gram()
        food.save()

    class Meta:
        model = Foods
        fields = ['name']


class MacroMealForm(forms.ModelForm):

    notes = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Foods
        fields = ['name']

        
class MacroIngredientForm(forms.ModelForm):

    ingredient_id = forms.IntegerField()
    unit = forms.CharField()
    amount = RoundedDecimalField(
        max_digits=6, decimal_places=2
    )

    class Meta:
        model = Ingredients
        fields = ['amount', 'ingredient', 'serving']

    def __init__(self, *args, **kwargs):
        args = (kwargs.pop('data'),)
        post_data = args[0]

        prefix = kwargs['prefix']
        ingredient = Foods.objects.get(
            pk=post_data[f'{prefix}-ingredient_id']
        )

        if post_data[f'{prefix}-unit'] == 'g':
            serving = Servings.objects.get(food=None)
        else:
            serving = Servings.objects.get(
                food=ingredient, description=post_data[f'{prefix}-unit']
            )

        args[0][f'{prefix}-serving'] = serving.pk
        args[0][f'{prefix}-ingredient'] = ingredient.pk

        super(MacroIngredientForm, self).__init__(*args, **kwargs)

    

# class oldMacroMealForm(forms.Form):

#     name = forms.CharField(widget=forms.fields.TextInput())
#     notes = forms.CharField(widget=forms.Textarea, required=False)

#     cals_per_gram = RoundedDecimalField(
#         max_digits=6, decimal_places=4,
#         widget=forms.HiddenInput()
#     )
#     fat_per_gram = RoundedDecimalField(
#         max_digits=6, decimal_places=4,
#         widget=forms.HiddenInput()
#     )
#     carbs_per_gram = RoundedDecimalField(
#         max_digits=6, decimal_places=4,
#         widget=forms.HiddenInput()
#     )
#     protein_per_gram = RoundedDecimalField(
#         max_digits=6, decimal_places=4,
#         widget=forms.HiddenInput()
#     )
#     total_grams = RoundedDecimalField(
#         max_digits=8, decimal_places=4,
#         widget=forms.HiddenInput()
#     )

#     def __init__(self, *args, **kwargs):
#         ingredient_count = kwargs.pop('ingredient_count')
#         super(MacroMealForm, self).__init__(*args, **kwargs)

#         for i in range(ingredient_count):
#             self.fields['ingredient_id_{}'.format(i)] = forms.IntegerField()
#             self.fields['ingredient_amt_{}'.format(i)] = RoundedDecimalField(
#                 max_digits=6, decimal_places=2
#             )
#             self.fields['ingredient_unit_{}'.format(i)] = forms.CharField()


class SignUpForm(forms.models.ModelForm):

    required=False
    class Meta:

        model = User
        fields = ("username", "email", "password",)
        widgets = {
            "username": forms.fields.TextInput(attrs = {
                "placeholder": "Username",
                "class": "input__input input__input--lg",
            }),
            "email": forms.fields.TextInput(attrs = {
                "placeholder": "Email",
                "class": "input__input input__input--lg",
            }),
            "password": forms.fields.TextInput(attrs = {
                "placeholder": "Password",
                "class": "input__input input__input--lg",
            }),
        }

        #error constants
        error_messages = {
                "username": {"required": EMPTY_USERNAME_ERROR,"unique":DUPLICATE_USERNAME_ERROR},
                "password": {"required": EMPTY_PASSWORD_ERROR}
        }


class MakeMacrosForm(forms.models.ModelForm):
	
	m_height = forms.CharField(widget=forms.fields.TextInput(attrs= {
		"placeholder":"cm",
		"data-type":"number"
	}),required=False)
	m_weight = forms.CharField(widget=forms.fields.TextInput(attrs= {
		"placeholder":"kg",
		"data-type":"number"
	}),required=False)
	m_change_rate = forms.CharField(widget=forms.fields.TextInput(attrs= {
		"placeholder":"kg/wk",
		"data-type":"number"
	}),required=False)
	i_height_0 = forms.CharField(widget=forms.fields.TextInput(attrs= {
		"placeholder":"ft",
		"data-type":"number"
	}),required=False)
	i_height_1 = forms.CharField(widget=forms.fields.TextInput(attrs= {
		"placeholder":"in",
		"data-type":"number"
	}),required=False)
	i_weight = forms.CharField(widget=forms.fields.TextInput(attrs= {
		"placeholder":"lb",
		"data-type":"number"
	}),required=False)
	i_change_rate = forms.CharField(widget=forms.fields.TextInput(attrs= {
		"placeholder":"lb/wk",
		"data-type":"number"
	}),required=False)

	macro_error_messages = {
		"required": EMPTY_MACRO_ERROR,
		"invalid": INVALID_MACRO_ERROR,
		"min_value": OUT_OF_RANGE_MACRO_ERROR,
		"max_value": OUT_OF_RANGE_MACRO_ERROR
	}
	
	choose_macro_classes = "form-control input-sm choose_macros"
	pct_attrs = {"placeholder":"%","class": choose_macro_classes,"data-value":0,"data-type":"number"}
	g_attrs = {"placeholder":"g","class": choose_macro_classes,"data-type":"number"}
	protein_percent = forms.IntegerField(min_value=0,max_value=100,widget=forms.fields.TextInput(attrs=pct_attrs),error_messages = macro_error_messages,required=True)
	protein_g = forms.IntegerField(widget=forms.fields.TextInput(attrs=g_attrs),error_messages = macro_error_messages,required=True)
	fat_percent = forms.IntegerField(min_value=0,max_value=100,widget=forms.fields.TextInput(attrs=pct_attrs),error_messages = macro_error_messages,required=True)
	fat_g = forms.IntegerField(widget=forms.fields.TextInput(attrs=g_attrs),error_messages = macro_error_messages,required=True)
	carbs_percent = forms.IntegerField(min_value=0,max_value=100,widget=forms.fields.TextInput(attrs=pct_attrs),error_messages = macro_error_messages,required=True)
	carbs_g = forms.IntegerField(widget=forms.fields.TextInput(attrs=g_attrs),error_messages = macro_error_messages,required=True)
	macro_error_messages["min_value"] =MACROS_DONT_ADD_UP_ERROR 
	macro_error_messages["max_value"] =MACROS_DONT_ADD_UP_ERROR 
	total_macro_percent = forms.IntegerField(min_value=100,max_value=100,error_messages = macro_error_messages,required=True)
	
	class Meta:

		model = Macros
		fields = ("unit_type","gender","age","weight","height","activity","direction","change_rate",)
	
		widgets = {
			"unit_type": forms.RadioSelect(),
			"gender": forms.RadioSelect(),
			"age": forms.fields.TextInput(attrs = {
				"placeholder": "Age",
				"data-type":"number"
			}),
			"weight": forms.fields.TextInput(attrs = {
				"data-type":"number"
			}),
			"height": forms.fields.TextInput(attrs = {
				"data-type":"number"
			}),
			"activity": forms.RadioSelect(),
			"direction": forms.RadioSelect(),
			"change_rate": forms.fields.TextInput(attrs = {
				"data-type":"number"
			}),
		}

		#error constants
		error_messages = {
			"unit_type": {
				"required": INVALID_POST_ERROR,
				"invalid_choice": INVALID_POST_ERROR
			},
			"gender": {
				"required": INVALID_POST_ERROR,
				"invalid_choice": INVALID_POST_ERROR
			},
			"age": {
				"required": EMPTY_AGE_ERROR,
				"invalid":DEFAULT_INVALID_INT_ERROR,
			},
			"activity": {
				"required": INVALID_POST_ERROR,
				"invalid_choice": INVALID_POST_ERROR,
			},
			"direction": {
				"required": INVALID_POST_ERROR,
				"invalid_choice": INVALID_POST_ERROR,
			},
			"weight": {
				"required": EMPTY_WEIGHT_ERROR,
				"invalid":DEFAULT_INVALID_INT_ERROR,
			},
			"height": {
				"required": EMPTY_HEIGHT_ERROR,
				"invalid":DEFAULT_INVALID_INT_ERROR,
			},
			"change_rate": {
				"required": EMPTY_RATE_ERROR,
				"invalid":DEFAULT_INVALID_INT_ERROR,
			},
		}
	
	def __init__(self,*args,**kwargs):
		initial = {"unit_type":kwargs.pop("unit_type")}
		kwargs["initial"] = initial
		super(MakeMacrosForm,self).__init__(*args,**kwargs)
