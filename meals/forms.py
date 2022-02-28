import os
from decimal import Decimal
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from meals.models import (
    Macros,
    Foods,
    Ingredients,
    Servings,
    FoodNotes,
    FoodGroup,
    FoodType,
)


# LoginForm/SignUpForm errors
EMPTY_USERNAME_ERROR = "Username Missing"
EMPTY_EMAIL_ERROR = "Email Missing"
EMPTY_PASSWORD_ERROR = "Password Missing"
DUPLICATE_USERNAME_ERROR = "Username taken"
INVALID_USERNAME_ERROR = "Enter a valid username. This value may contain only \
letters, numbers, and @/./+/-/_ characters."

# MyMacrosForm erros
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


class NewFoodServingForm(forms.ModelForm):
    class Meta:
        model = Servings
        fields = ["grams", "quantity", "description"]
        widgets = {
            "grams": forms.TextInput(
                attrs={"id": "add-food-grams", "class": "input__input input__input--sm"}
            ),
            "quantity": forms.TextInput(
                attrs={
                    "id": "add-food-unit-quantity",
                    "class": "input__input input__input--sm",
                }
            ),
            "description": forms.TextInput(
                attrs={
                    "id": "add-food-unit-desc",
                    "class": "input__input input__input--md",
                }
            ),
        }
        labels = {
            "grams": "Servings (grams)",
            "description": "Servings Unit (ex. cups, tsp, package, etc.)",
            "quantity": "Unit Quantity",
        }


class NewFoodForm(forms.ModelForm):

    small_input_class = "input__input input__input--sm"
    cals = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        widget=forms.TextInput(
            attrs={"id": "add-food-cals", "class": small_input_class}
        ),
    )
    fat = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        widget=forms.TextInput(
            attrs={"id": "add-food-fat", "class": small_input_class, "placeholder": "g"}
        ),
    )
    carbs = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        widget=forms.TextInput(
            attrs={
                "id": "add-food-carbs",
                "class": small_input_class,
                "placeholder": "g",
            }
        ),
    )
    sugar = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        widget=forms.TextInput(
            attrs={
                "id": "add-food-sugar",
                "class": small_input_class,
                "placeholder": "g",
            }
        ),
    )
    protein = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        widget=forms.TextInput(
            attrs={
                "id": "add-food-protein",
                "class": small_input_class,
                "placeholder": "g",
            }
        ),
    )

    # Offical food groups need to be read in
    with open(
        os.path.join(settings.BASE_DIR, "data", "meals", "food_groups.csv"), "r"
    ) as food_groups_file:

        choices = [
            (
                fd_grp.strip(),
                fd_grp.strip(),
            )
            for fd_grp in food_groups_file.readlines()
        ]

    food_group = forms.ChoiceField(
        choices=choices,
        label="Food Group",
        widget=forms.Select(
            attrs={"id": "add-food-food-group"},
        ),
    )

    class Meta:
        model = Foods
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={"id": "add-food-name", "class": "input__input input__input--lg"}
            )
        }
        labels = {"name": "Food Name"}

    def consume_grams(self, grams):
        """obtain grams for use in macro/gram calculations

        Parameters
        ----------
        grams: decimal.Decimal
        """

        self.cleaned_data["grams"] = grams

    def save(self):
        """save new food

        Save new Food along with its associated FoodType and
        FoodGroup.  Also calc the macros per gram fields from
        of the form macro input.
        """

        food = self.instance

        food.food_group = FoodGroup.objects.get(name=self.cleaned_data["food_group"])
        food.food_type = FoodType.objects.get(name="food")

        food.set_macros_per_gram(
            cals=Decimal(self.cleaned_data["cals"]),
            fat=Decimal(self.cleaned_data["fat"]),
            carbs=Decimal(self.cleaned_data["carbs"]),
            sugar=Decimal(self.cleaned_data["sugar"]),
            protein=Decimal(self.cleaned_data["protein"]),
            serving_amount=Decimal(self.cleaned_data["grams"]),
        )
        food.save()


class MealRecipeForm(forms.ModelForm):

    notes = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        ingredient_fields = [key for key in args[0] if key.startswith("ingredient")]

        for ing_field in ingredient_fields:

            if "amount" in ing_field:
                self.fields[ing_field] = RoundedDecimalField(
                    max_digits=6, decimal_places=2
                )
            else:
                self.fields[ing_field] = forms.IntegerField()

    def clean(self):
        """set all dynamically added ingredients

        Set all dynamically added form inputs for ingredients
        to one key in cleaned_data. This makes the ingredients
        easier to work with later, and allow for checking of duplicates
        """

        self.cleaned_data = super().clean()
        ingredients = set()
        ingredient_names = set()
        i = 0
        name_fieldname = f"ingredient_{i}"
        amount_fieldname = f"ingredient_amount_{i}"
        unit_fieldname = f"ingredient_unit_{i}"

        while self.cleaned_data.get(name_fieldname):

            name = self.cleaned_data[name_fieldname]
            if name in ingredient_names:
                self.add_error(name_fieldname, "Duplicate Ingredient")
            else:
                ingredient_names.add(name)
                amount = self.cleaned_data.get(amount_fieldname)
                unit = self.cleaned_data.get(unit_fieldname)
                if amount and name:
                    ingredients.add(
                        (
                            name,
                            amount,
                            unit,
                        )
                    )

            i += 1
            name_fieldname = f"ingredient_{i}"
            amount_fieldname = f"ingredient_amount_{i}"
            unit_fieldname = f"ingredient_unit_{i}"

        self.cleaned_data["ingredients"] = ingredients

    def save(self):
        """save new recipe

        Save new recipe as Foods, along with its associated
        FoodGroup, FoodType, Ingredients, and Servings.  Also
        sets the macros / gram fields on Foods
        """

        food = self.instance
        food.food_group = FoodGroup.objects.get(name="My Recipes")
        food.food_type = FoodType.objects.get(name="recipe")
        food.save()

        if self.cleaned_data.get("notes"):
            FoodNotes.objects.create(food=food, notes=self.cleaned_data["notes"])

        total_grams = 0
        for ing_pk, amount, unit in self.cleaned_data["ingredients"]:
            ingredient = Foods.objects.get(pk=ing_pk)
            serving = Servings.objects.get(pk=unit)
            ing = Ingredients.objects.create(
                main_food=food, ingredient=ingredient, serving=serving, amount=amount
            )
            total_grams += ing.grams

        Servings.objects.create(
            food=food, description="recipe", grams=total_grams, quantity=1
        )

        food.set_macros_per_gram()
        food.save()

    class Meta:
        model = Foods
        fields = ["name"]


class MacroMealForm(forms.ModelForm):

    notes = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Foods
        fields = ["name"]


class MacroIngredientForm(forms.ModelForm):

    ingredient_id = forms.IntegerField()
    unit = forms.CharField()
    amount = RoundedDecimalField(max_digits=6, decimal_places=2)

    class Meta:
        model = Ingredients
        fields = ["amount", "ingredient", "serving"]

    def __init__(self, *args, **kwargs):
        args = (kwargs.pop("data"),)
        post_data = args[0]

        prefix = kwargs["prefix"]
        ingredient = Foods.objects.get(pk=post_data[f"{prefix}-ingredient_id"])

        if post_data[f"{prefix}-unit"] == "g":
            serving = Servings.objects.get(food=None)
        else:
            serving = Servings.objects.get(
                food=ingredient, description=post_data[f"{prefix}-unit"]
            )

        args[0][f"{prefix}-serving"] = serving.pk
        args[0][f"{prefix}-ingredient"] = ingredient.pk

        super(MacroIngredientForm, self).__init__(*args, **kwargs)


class SignUpForm(forms.models.ModelForm):

    required = False

    class Meta:

        model = User
        fields = (
            "username",
            "email",
            "password",
        )
        widgets = {
            "username": forms.fields.TextInput(
                attrs={
                    "placeholder": "Username",
                    "class": "input__input input__input--lg",
                }
            ),
            "email": forms.fields.TextInput(
                attrs={
                    "placeholder": "Email",
                    "class": "input__input input__input--lg",
                }
            ),
            "password": forms.fields.TextInput(
                attrs={
                    "placeholder": "Password",
                    "class": "input__input input__input--lg",
                }
            ),
        }

        # error constants
        error_messages = {
            "username": {
                "required": EMPTY_USERNAME_ERROR,
                "unique": DUPLICATE_USERNAME_ERROR,
            },
            "password": {"required": EMPTY_PASSWORD_ERROR},
        }


class MakeMacrosForm(forms.models.ModelForm):

    data_type = "number"
    input_class = "input__input input__input--sm"
    tab_name = "my-macros"

    macro_error_messages = {
        "required": EMPTY_MACRO_ERROR,
        "invalid": INVALID_MACRO_ERROR,
        "min_value": OUT_OF_RANGE_MACRO_ERROR,
        "max_value": OUT_OF_RANGE_MACRO_ERROR,
    }
    choose_macro_classes = "form-control input-sm choose_macros"
    pct_attrs = {
        "placeholder": "%",
        "class": choose_macro_classes,
        "data-value": 0,
        "data-type": data_type,
    }
    g_attrs = {
        "placeholder": "g",
        "class": choose_macro_classes,
        "data-type": data_type,
    }

    height_0 = forms.CharField(
        label="Height",
        widget=forms.fields.TextInput(
            attrs={
                "id": f"{tab_name}-height-0",
                "data-type": data_type,
                "class": input_class,
            }
        ),
        required=True,
    )

    height_1 = forms.CharField(
        widget=forms.fields.TextInput(
            attrs={
                "id": f"{tab_name}-height-1",
                "data-type": data_type,
                "class": input_class,
            }
        ),
        required=False,
    )

    protein_g = forms.IntegerField(
        widget=forms.fields.TextInput(attrs=g_attrs),
        error_messages=macro_error_messages,
        required=True,
    )
    fat_percent = forms.IntegerField(
        min_value=0,
        max_value=100,
        widget=forms.fields.TextInput(attrs=pct_attrs),
        error_messages=macro_error_messages,
        required=True,
    )
    fat_g = forms.IntegerField(
        widget=forms.fields.TextInput(attrs=g_attrs),
        error_messages=macro_error_messages,
        required=True,
    )
    carbs_percent = forms.IntegerField(
        min_value=0,
        max_value=100,
        widget=forms.fields.TextInput(attrs=pct_attrs),
        error_messages=macro_error_messages,
        required=True,
    )
    carbs_g = forms.IntegerField(
        widget=forms.fields.TextInput(attrs=g_attrs),
        error_messages=macro_error_messages,
        required=True,
    )
    macro_error_messages["min_value"] = MACROS_DONT_ADD_UP_ERROR
    macro_error_messages["max_value"] = MACROS_DONT_ADD_UP_ERROR
    total_macro_percent = forms.IntegerField(
        min_value=100, max_value=100, error_messages=macro_error_messages, required=True
    )

    class Meta:

        data_type = "number"
        input_class = "input__input input__input--sm"
        tab_name = "my-macros"

        model = Macros
        fields = (
            "unit_type",
            "gender",
            "age",
            "weight",
            "height",
            "activity",
            "direction",
            "change_rate",
            "fat_percent",
            "carbs_percent",
            "protein_percent",
        )

        labels = {"change_rate": "Rate of Change"}
        widgets = {
            "unit_type": forms.RadioSelect(),
            "gender": forms.RadioSelect(),
            "age": forms.fields.TextInput(
                attrs={
                    "id": "my-macros-age",
                    "placeholder": "Age",
                    "data-type": data_type,
                    "class": input_class,
                }
            ),
            "weight": forms.fields.TextInput(
                attrs={
                    "id": f"{tab_name}-weight",
                    "data-type": data_type,
                    "class": input_class,
                }
            ),
            "activity": forms.RadioSelect(),
            "direction": forms.RadioSelect(),
            "change_rate": forms.fields.TextInput(
                attrs={
                    "id": f"{tab_name}-change-rate",
                    "class": "input__input input__input--sm",
                    "data-type": data_type,
                }
            ),
            "fat_percent": forms.fields.TextInput(
                attrs={
                    "id": "my-macros-fat-percent",
                    "placeholder": "%",
                    "data-type": data_type,
                    "class": input_class,
                }
            ),
            "carbs_percent": forms.fields.TextInput(
                attrs={
                    "id": "my-macros-carbs-percent",
                    "placeholder": "%",
                    "data-type": data_type,
                    "class": input_class,
                }
            ),
            "protein_percent": forms.fields.TextInput(
                attrs={
                    "id": "my-macros-protein-percent",
                    "placeholder": "%",
                    "data-type": data_type,
                    "class": input_class,
                }
            ),
        }

        # error constants
        error_messages = {
            "unit_type": {
                "required": INVALID_POST_ERROR,
                "invalid_choice": INVALID_POST_ERROR,
            },
            "gender": {
                "required": INVALID_POST_ERROR,
                "invalid_choice": INVALID_POST_ERROR,
            },
            "age": {
                "required": EMPTY_AGE_ERROR,
                "invalid": DEFAULT_INVALID_INT_ERROR,
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
                "invalid": DEFAULT_INVALID_INT_ERROR,
            },
            "height": {
                "required": EMPTY_HEIGHT_ERROR,
                "invalid": DEFAULT_INVALID_INT_ERROR,
            },
            "change_rate": {
                "required": EMPTY_RATE_ERROR,
                "invalid": DEFAULT_INVALID_INT_ERROR,
            },
        }

    def __init__(self, *args, **kwargs):

        if kwargs.get("unit_type"):
            initial = {"unit_type": kwargs.pop("unit_type")}
            kwargs["initial"] = initial
        super(MakeMacrosForm, self).__init__(*args, **kwargs)
