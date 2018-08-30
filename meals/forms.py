from django import forms
from django.contrib.auth.models import User
from meals.models import Macros, MealTemplate


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


class MacroMealForm(forms.Form):

    name = forms.CharField(widget=forms.fields.TextInput())

    cals_per_gram = forms.DecimalField(
        max_digits=6, decimal_places=4,
        widget=forms.HiddenInput()
    )
    fat_per_gram = forms.DecimalField(
        max_digits=6, decimal_places=4,
        widget=forms.HiddenInput()
    )
    carbs_per_gram = forms.DecimalField(
        max_digits=6, decimal_places=4,
        widget=forms.HiddenInput()
    )
    protein_per_gram = forms.DecimalField(
        max_digits=6, decimal_places=4,
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        ingredient_count = kwargs.pop('ingredient_count')
        super(MacroMealForm, self).__init__(*args, **kwargs)

        for i in range(ingredient_count):
            self.fields['ingredient_id_{}'.format(i)] = forms.IntegerField()
            self.fields['ingredient_amt_{}'.format(i)] = forms.IntegerField()
            self.fields['ingredient_unit_{}'.format(i)] = forms.CharField()

#     def get_ingredient_info(self):

#         for name, value in self.cleaned_data.items():
#             if name.startswith('ingredient'):
#                 yield (self.fields[name]

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


class MealTemplateForm(forms.models.ModelForm):

	class Meta:
		model = MealTemplate
		fields = ("cals_percent",)
	
		error_messages = {
			"cals_percent": {
				"required": EMPTY_CALS_ERROR,
				"invalid":DEFAULT_INVALID_INT_ERROR,
			},
		}



