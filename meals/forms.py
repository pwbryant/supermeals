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
EMPTY_MACRO_ERROR = 'Macro Info Missing'
DEFAULT_INVALID_INT_ERROR = 'Enter a whole number'
EMPTY_RATE_ERROR = 'Weight Change Rate Missing'
INVALID_MACRO_ERROR = 'Invalid Macro Ratio Values'
OUT_OF_RANGE_MACRO_ERROR = 'Macro Percent Out Of Range'

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


class MakeMacrosForm(forms.models.ModelForm):

	unit_choices = (
		('imperial','Imperial',),
		('metric','Metric',),
	)
	unit_type = forms.ChoiceField(choices=unit_choices,widget=forms.RadioSelect(),initial='imperial',required=True)
	macro_error_messages = {
		'required': EMPTY_MACRO_ERROR,
		'invalid': INVALID_MACRO_ERROR,
		'min_value': OUT_OF_RANGE_MACRO_ERROR,
		'max_value': OUT_OF_RANGE_MACRO_ERROR
	}
	pct_attrs = {'placeholder':'%','class': 'form-control input-sm'}
	g_attrs = {'placeholder':'g','class': 'form-control input-sm'}
	protein_percent = forms.IntegerField(min_value=0,max_value=100,widget=forms.fields.TextInput(attrs=pct_attrs),error_messages = macro_error_messages,required=True)
	protein_g = forms.IntegerField(widget=forms.fields.TextInput(attrs=g_attrs),error_messages = macro_error_messages,required=True)
	fat_percent = forms.IntegerField(min_value=0,max_value=100,widget=forms.fields.TextInput(attrs=pct_attrs),error_messages = macro_error_messages,required=True)
	fat_g = forms.IntegerField(widget=forms.fields.TextInput(attrs=g_attrs),error_messages = macro_error_messages,required=True)
	carbs_percent = forms.IntegerField(min_value=0,max_value=100,widget=forms.fields.TextInput(attrs=pct_attrs),error_messages = macro_error_messages,required=True)
	carbs_g = forms.IntegerField(widget=forms.fields.TextInput(attrs=g_attrs),error_messages = macro_error_messages,required=True)

	class Meta:

		model = Macros
		fields = ('gender','age','activity','direction',)
		widgets = {
			'gender': forms.RadioSelect(),
			'age': forms.fields.TextInput(attrs = {
				'placeholder': 'Age',
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
			'activity': {
				'required': INVALID_POST_ERROR,
				'invalid_choice': INVALID_POST_ERROR,
			},
			'direction': {
				'required': INVALID_POST_ERROR,
				'invalid_choice': INVALID_POST_ERROR,
			},
		}



class MetricTDEEForm(forms.models.ModelForm):

	class Meta:

		model = Macros
		fields = ('weight','height','change_rate',)
		widgets = {
			'weight': forms.fields.TextInput(attrs = {
				'placeholder': 'kg',
				'class': 'form-control input-sm',
			}),
			'height': forms.fields.TextInput(attrs = {
				'placeholder': 'cm',
				'class': 'form-control input-sm',
			}),
			'change_rate': forms.fields.TextInput(attrs = {
				'placeholder': 'kg/wk',
				'class': 'form-control input-sm',
			}),
		}

		#error constants
		error_messages = {
			'height': {
				'required': EMPTY_HEIGHT_ERROR,
				'invalid':DEFAULT_INVALID_INT_ERROR,
			},
			'weight': {
				'required': EMPTY_WEIGHT_ERROR,
				'invalid':DEFAULT_INVALID_INT_ERROR,
			},
			'change_rate': {
				'required': EMPTY_RATE_ERROR,
				'invalid':DEFAULT_INVALID_INT_ERROR,
			},
		}


class ImperialHeightWidget(forms.MultiWidget):
	def __init__(self, attrs=None):
		widgets = (
		forms.TextInput(attrs={'placeholder':'ft'}),
		forms.TextInput(attrs={'placeholder':'in'}),
		)
		#error_messages = {'height':{'required':'poo required','invalid': 'poo invalid'}}
		super(ImperialHeightWidget, self).__init__(widgets, attrs)

	def decompress(self, value):
		if value:
			data = value.split(',')
			return [data[0], data[1]]
		return [None, None]

	def format_output(self, rendered_widgets):
		return u'\n'.join(rendered_widgets)


	def value_from_datadict(self, data, files, name):
		try:
			return data[name]
		except:
			return None
		pass



class ImperialTDEEForm(forms.models.ModelForm):

	class Meta:

		model = Macros
		fields = ('weight','height','change_rate',)
		widgets = {
			'weight': forms.fields.TextInput(attrs = {
				'placeholder': 'lbs',
				'class': 'form-control input-sm',
			}),
			'height': ImperialHeightWidget(),
			'change_rate': forms.fields.TextInput(attrs = {
				'placeholder': 'lb/wk',
				'class': 'form-control input-sm',
			}),
		}

		#error constants
		error_messages = {
			'height': {
				'required': EMPTY_HEIGHT_ERROR,
				'invalid':DEFAULT_INVALID_INT_ERROR,
			},
			'weight': {
				'required': EMPTY_WEIGHT_ERROR,
				'invalid':DEFAULT_INVALID_INT_ERROR,
			},
			'change_rate': {
				'required': EMPTY_RATE_ERROR,
				'invalid':DEFAULT_INVALID_INT_ERROR,
			},
		}

