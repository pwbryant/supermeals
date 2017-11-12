from django.test import TestCase

from meals.forms import LoginForm,SignUpForm,  EMPTY_USERNAME_ERROR, EMPTY_PASSWORD_ERROR

class LoginFormTest(TestCase):

	def test_form_login_has_placeholder_and_css_classes(self):
		form = LoginForm()
		self.assertIn('placeholder="Username"', form.as_p())
		self.assertIn('placeholder="Password"', form.as_p())
		self.assertIn('class="form-control input-sm"', form.as_p())

	def test_form_validation_for_blank_inputs(self):
		form = LoginForm(data={'username':'','password':''})
		self.assertFalse(form.is_valid())
		self.assertEqual(
			form.errors['username'],
			[EMPTY_USERNAME_ERROR]
		)
		self.assertEqual(
			form.errors['password'],
			[EMPTY_PASSWORD_ERROR]
		)

class SignUpFormTest(TestCase):

	def test_form_sign_up_has_placeholder_and_css_classes(self):
		form = SignUpForm()
		self.assertIn('placeholder="Username"', form.as_p())
		self.assertIn('placeholder="Email"', form.as_p())
		self.assertIn('placeholder="Password"', form.as_p())
		self.assertIn('class="form-control input-sm"', form.as_p())

	def test_form_validation_for_blank_inputs(self):
		form = SignUpForm(data={'username':'','password':''})
		self.assertFalse(form.is_valid())
		self.assertEqual(
			form.errors['username'],
			[EMPTY_USERNAME_ERROR]
		)
		self.assertEqual(
			form.errors['password'],
			[EMPTY_PASSWORD_ERROR]
		)
