from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from meals.models import Macros


#LoginForm/SignUpForm errors
EMPTY_USERNAME_ERROR = 'Username Missing'
EMPTY_EMAIL_ERROR = 'Email Missing'
EMPTY_PASSWORD_ERROR = 'Password Missing'
DUPLICATE_USERNAME_ERROR = 'Username taken'
INVALID_USERNAME_ERROR = 'Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters.'
#MyMacrosForm erros
INVALID_POST_ERROR = 'Invalid POST'
EMPTY_AGE_ERROR = 'Age Missing'
EMPTY_WEIGHT_ERROR = 'Weight Missing'
EMPTY_HEIGHT_ERROR = 'Height Missing'
EMPTY_MACRO_ERROR = 'Macro Ratios Missing'
DEFAULT_INVALID_INT_ERROR = 'Enter a whole number'

class HorizontalRadioRenderer(forms.RadioSelect):
	def render(self):
		return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))

class LoginForm(forms.models.ModelForm):
	
	class Meta:

		model = User
		fields = ('username','password',)
		widgets = {
			'username': forms.fields.TextInput(attrs = {
				'placeholder': 'Username',
				'class': 'form-control input-sm',
			}),
			'password': forms.fields.TextInput(attrs = {
				'placeholder': 'Password',
				'class': 'form-control input-sm',
			}),
		}

		#error constants
		error_messages = {
			'username': {'required': EMPTY_USERNAME_ERROR},
			'password': {'required': EMPTY_PASSWORD_ERROR}
		}


class SignUpForm(forms.models.ModelForm):
	
	class Meta:

		model = User
		fields = ('username','email','password',)
		widgets = {
			'username': forms.fields.TextInput(attrs = {
				'placeholder': 'Username',
				'class': 'form-control input-sm',
			}),
			'email': forms.fields.TextInput(attrs = {
				'placeholder': 'Email',
				'class': 'form-control input-sm',
			}),
			'password': forms.fields.TextInput(attrs = {
				'placeholder': 'Password',
				'class': 'form-control input-sm',
			}),
		}

		#error constants
		error_messages = {
			'username': {'required': EMPTY_USERNAME_ERROR,'unique':DUPLICATE_USERNAME_ERROR},
			'password': {'required': EMPTY_PASSWORD_ERROR}
		}



class MyMacrosForm(forms.models.ModelForm):
	
	MACRO_RATIO_CHOICES = (
		('30_35_35','Protein: 30%, Fat: 35%, Carbs: 35%',),
		('40_40_20','Protein: 40%, Fat: 40%, Carbs: 20%',),
		('30_20_50','Protein: 30%, Fat: 20%, Carbs: 50%',),
	)
	MACRO_RATIO_ERRORS = {
		'required': INVALID_POST_ERROR,
		'invalid_choice': INVALID_POST_ERROR,

	}
	macro_ratios = forms.ChoiceField(choices=MACRO_RATIO_CHOICES,widget=forms.RadioSelect,error_messages=MACRO_RATIO_ERRORS,required=True)
	class Meta:

		model = Macros
		fields = ('gender','age','weight','height','activity','direction','macro_ratios')
		widgets = {
			'gender': forms.RadioSelect(),
			'age': forms.fields.TextInput(attrs = {
				'placeholder': 'Age',
				'class': 'form-control input-sm',
			}),
			'weight': forms.fields.TextInput(attrs = {
				'placeholder': 'Weight(lbs)',
				'class': 'form-control input-sm',
			}),
			'height': forms.fields.TextInput(attrs = {
				'placeholder': 'Height(in)',
				'class': 'form-control input-sm',
			}),
			'activity': forms.RadioSelect(),
			'direction': forms.RadioSelect(),
		}

		#error constants
		error_messages = {
			'gender': {
				'required': INVALID_POST_ERROR,
				'invalid_choice': INVALID_POST_ERROR
			},
			'age': {
				'required': EMPTY_AGE_ERROR,
				'invalid':DEFAULT_INVALID_INT_ERROR,
			},
			'weight': {
				'required': EMPTY_WEIGHT_ERROR,
				'invalid':DEFAULT_INVALID_INT_ERROR,
			},
			'height': {
				'required': EMPTY_HEIGHT_ERROR,
				'invalid':DEFAULT_INVALID_INT_ERROR,
			},
			'activity': {
				'required': INVALID_POST_ERROR,
				'invalid_choice': INVALID_POST_ERROR,
			},
			'direction': {
				'required': INVALID_POST_ERROR,
				'invalid_choice': INVALID_POST_ERROR,
			}
		}


