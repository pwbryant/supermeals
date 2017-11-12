from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Fieldset, ButtonHolder, Layout, Field
from django.contrib.auth.models import User

EMPTY_USERNAME_ERROR = 'Username Missing'
EMPTY_PASSWORD_ERROR = 'Password Missing'

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


class GuestLoginForm(forms.Form):

	guest = forms.CharField()

	helper = FormHelper()
	helper.form_method = 'POST'
	helper.form_action = 'logging_in'
	helper.layout = Layout(
		Field('guest',type='hidden')
	)
	helper.add_input(Submit('guest','Continue as Guest',css_class='btn-primary'))	

