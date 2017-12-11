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


	
	m_height = forms.CharField(widget=forms.fields.TextInput(attrs= {
		'placeholder':'cm',
		'class':'form-control input-sm'
	}),required=False)
	m_weight = forms.CharField(widget=forms.fields.TextInput(attrs= {
		'placeholder':'kg',
		'class':'form-control input-sm'
	}),required=False)
	m_change_rate = forms.CharField(widget=forms.fields.TextInput(attrs= {
		'placeholder':'kg/wk',
		'class':'form-control input-sm change_rate'
	}),required=False)
	i_height_0 = forms.CharField(widget=forms.fields.TextInput(attrs= {
		'placeholder':'ft',
		'class':'form-control input-sm'
	}),required=False)
	i_height_1 = forms.CharField(widget=forms.fields.TextInput(attrs= {
		'placeholder':'in',
		'class':'form-control input-sm'
	}),required=False)
	i_weight = forms.CharField(widget=forms.fields.TextInput(attrs= {
		'placeholder':'lb',
		'class':'form-control input-sm'
	}),required=False)
	i_change_rate = forms.CharField(widget=forms.fields.TextInput(attrs= {
		'placeholder':'lb/wk',
		'class':'form-control input-sm change_rate'
	}),required=False)

	macro_error_messages = {
		'required': EMPTY_MACRO_ERROR,
		'invalid': INVALID_MACRO_ERROR,
		'min_value': OUT_OF_RANGE_MACRO_ERROR,
		'max_value': OUT_OF_RANGE_MACRO_ERROR
	}
	choose_macro_classes = 'form-control input-sm choose_macros'
	pct_attrs = {'placeholder':'%','class': choose_macro_classes,'data-value':0}
	g_attrs = {'placeholder':'g','class': choose_macro_classes}
	protein_percent = forms.IntegerField(min_value=0,max_value=100,widget=forms.fields.TextInput(attrs=pct_attrs),error_messages = macro_error_messages,required=True)
	protein_g = forms.IntegerField(widget=forms.fields.TextInput(attrs=g_attrs),error_messages = macro_error_messages,required=True)
	fat_percent = forms.IntegerField(min_value=0,max_value=100,widget=forms.fields.TextInput(attrs=pct_attrs),error_messages = macro_error_messages,required=True)
	fat_g = forms.IntegerField(widget=forms.fields.TextInput(attrs=g_attrs),error_messages = macro_error_messages,required=True)
	carbs_percent = forms.IntegerField(min_value=0,max_value=100,widget=forms.fields.TextInput(attrs=pct_attrs),error_messages = macro_error_messages,required=True)
	carbs_g = forms.IntegerField(widget=forms.fields.TextInput(attrs=g_attrs),error_messages = macro_error_messages,required=True)
	class Meta:

		model = Macros
		fields = ('unit_type','gender','age','weight','height','activity','direction','change_rate',)
	
		widgets = {
			'unit_type': forms.RadioSelect(),
			'gender': forms.RadioSelect(),
			'age': forms.fields.TextInput(attrs = {
				'placeholder': 'Age',
				'class': 'form-control input-sm',
			}),
			'weight': forms.fields.TextInput(attrs = {
				'class': 'form-control input-sm',
			}),
			'height': forms.fields.TextInput(),
			'activity': forms.RadioSelect(),
			'direction': forms.RadioSelect(),
			'change_rate': forms.fields.TextInput(attrs = {
				'class': 'form-control input-sm',
			}),
		}

		#error constants
		error_messages = {
			'unit_type': {
				'required': INVALID_POST_ERROR,
				'invalid_choice': INVALID_POST_ERROR
			},
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
			'weight': {
				'required': EMPTY_WEIGHT_ERROR,
				'invalid':DEFAULT_INVALID_INT_ERROR,
			},
			'height': {
				'required': EMPTY_HEIGHT_ERROR,
				'invalid':DEFAULT_INVALID_INT_ERROR,
			},
			'change_rate': {
				'required': EMPTY_RATE_ERROR,
				'invalid':DEFAULT_INVALID_INT_ERROR,
			},
		}
	
	def __init__(self,*args,**kwargs):
		initial = {'unit_type':kwargs.pop('unit_type')}
		kwargs['initial'] = initial
		super(MakeMacrosForm,self).__init__(*args,**kwargs)

