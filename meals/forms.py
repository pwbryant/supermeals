from django import forms
from django.contrib.auth.models import User
from meals.models import Macros

#LoginForm/SignUpForm errors
EMPTY_USERNAME_ERROR = 'Username Missing'
EMPTY_EMAIL_ERROR = 'Email Missing'
EMPTY_PASSWORD_ERROR = 'Password Missing'
DUPLICATE_USERNAME_ERROR = 'Username taken'
INVALID_USERNAME_ERROR = 'Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters.'
#MyMacrosForm erros
EMPTY_GENDER_ERROR = 'Gender Missing'
EMPTY_AGE_ERROR = 'Age Missing'
EMPTY_WEIGHT_ERROR = 'Weight Missing'
EMPTY_HEIGHT_ERROR = 'Height Missing'

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
	
        
	class Meta:

		model = Macros
		fields = ('gender','age','weight','height',)
		
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
		}

		#error constants
		error_messages = {
			'gender': {'required': EMPTY_GENDER_ERROR},
			'age': {'required': EMPTY_AGE_ERROR},
			'weight': {'required': EMPTY_WEIGHT_ERROR},
			'height': {'required': EMPTY_HEIGHT_ERROR}
		}

