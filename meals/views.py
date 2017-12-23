from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.utils import IntegrityError
from django.db import transaction
import json
from decimal import Decimal
from meals.forms import LoginForm, SignUpForm, MakeMacrosForm, MealTemplateForm
from meals.models import Macros,MealTemplate

# Create your views here.
def home_or_login(request):
	if request.user.is_authenticated:
		return render(request, 'home.html') 
	else:
		return redirect('meals/login/')


def to_login(request):
	
	return render(request, 'login.html', {'form': LoginForm()}) 


def logging_in(request):
	if request.POST.get('guest'):
		username = 'guest'
		password = '321!beware'	
	else:
		username,password = request.POST.get('username'),request.POST.get('password')
	user = authenticate(request,username=username,password=password)
	if user is not None:
		login(request, user)
		return redirect('/')	
	else:
		error = 'Username or Password incorrect'
		return render(request,'login.html',{"error":error,"form":LoginForm()})


def logging_off(request):

	logout(request)
	return redirect('/')	


def sign_up(request):
	return render(request, 'sign_up.html', {"form":SignUpForm()})


def create_account(request):
	
	username = request.POST.get('username','')
	email = request.POST.get('email','')
	password = request.POST.get('password','')
	form = SignUpForm(data=request.POST)
	if form.is_valid():
		user = User()
		user.username = username
		user.email = email
		user.set_password(password)
		user.save()
		login(request, user)
		return redirect('/')	
	
	return render(request,'sign_up.html',{"form":form})

def get_my_macros(request):
	#form = MakeMacrosForm()
	form = MakeMacrosForm(unit_type='imperial')
	return render(request, 'my_macros.html',{
		'form':form
	})

def create_meal_template_dict(POST):

	validation_errors = []

	meal_template_dict = {}
	meal_num = int(POST.get('meal_number',0))
	tdee = int(POST.get('tdee',-1))
	if tdee == -1:
		validation_errors.append('TDEE Missing')
	
	unique_cals = {}
	if meal_num > 0:
		for i in range(int(meal_num)):
			cals = POST.get('meal_%d' % i,'')
			if cals.isdigit():
				if cals not in unique_cals:
					unique_cals[cals] = []
				unique_cals[cals].append(str(i + 1))
			else:
				validation_errors.append('All Meal Calorie Fields Must Contain a Number')
	else:		
		validation_errors.append('Enter Number of Meals')

	template_num = 1
	for cal_key,meal_nums in unique_cals.items():
		template = 'template %d' % template_num
		meal_template_dict[template] = {}
		meal_template_dict[template]['name'] = 'meals %s' % ','.join(meal_nums) 
		meal_template_dict[template]['number_of_meals'] = len(meal_nums) 
		meal_template_dict[template]['cals_percent'] = int(cal_key) / tdee * 100 
		
		template_num += 1

	validation_errors = ''.join(['<li>' + error + '</li>' for error in validation_errors])
	return (meal_template_dict,validation_errors,)
	
def save_meal_templates(request):
	meal_template_dict,validation_errors = create_meal_template_dict(request.POST)
	if len(validation_errors) > 0:
		return {'errors':'<ul>' + validation_errors + '</ul>'}

	for model_fields in meal_template_dict.values():
		model_fields['user'] = request.user
		try:
			with transaction.atomic():
				MealTemplate.objects.create(**model_fields)
			pass	
		except IntegrityError:
			pass
	
	return 1

def create_macro_form_dict_from_POST(POST):

	macro_form_dict = {}
	macro_form_dict['unit_type'] = POST['unit_type']
	if macro_form_dict['unit_type'] == 'imperial':
		height1 = POST.get('i_height_0','')
		height2 = POST.get('i_height_1','')
		if height1 != '' and height2 != '':
			macro_form_dict['height'] = str((int(height1) * 12) + int(height2))
		macro_form_dict['weight'] = POST.get('i_weight','')
		macro_form_dict['change_rate'] = POST.get('i_change_rate','')

	if macro_form_dict['unit_type'] == 'metric':
		macro_form_dict['height'] = POST.get('m_height',0)
		macro_form_dict['weight'] = POST.get('m_weight',0)
		macro_form_dict['change_rate'] = POST.get('m_change_rate','')
	macro_form_dict['total_macro_percent'] = int(POST.get('protein_percent',0)) + int(POST.get('fat_percent',0)) + int(POST.get('carbs_percent',0))
	macro_form_dict = {
				**{
					'gender':POST.get('gender',''),'age':POST.get('age',''),
					'activity':POST.get('activity',''),'direction':POST.get('direction',''),
					'fat_percent':POST.get('fat_percent',''),'fat_g':POST.get('fat_g',''),
					'carbs_percent':POST.get('carbs_percent',''),'carbs_g':POST.get('carbs_g',''),
					'protein_percent':POST.get('protein_percent',''),'protein_g':POST.get('protein_g','')
				},
				**macro_form_dict
			}

	return macro_form_dict

def save_my_macros(request):

	macro_form_dict = create_macro_form_dict_from_POST(request.POST) 
	macro_form = MakeMacrosForm(macro_form_dict,unit_type=macro_form_dict['unit_type'])	
	if not macro_form.is_valid():
		return {
			'form':macro_form,
			'unit_type':macro_form_dict['unit_type']
		}

	macro_dict = macro_form_dict
	[macro_dict.pop(key) for key in  ['fat_g','carbs_g','protein_g','carbs_percent','total_macro_percent']]
	macro_dict['change_rate'] = Decimal(macro_dict['change_rate']) 
	macro_dict['protein_percent'] = Decimal(macro_dict['protein_percent']) 
	macro_dict['fat_percent'] = Decimal(macro_dict['fat_percent']) 
	macro_dict['user'] = request.user
	try:
		with transaction.atomic():
			Macros.objects.create(**macro_dict)
		pass	
	except IntegrityError:
		pass

	return 1


def save_my_macros_and_meal_templates(request):
	
	my_macro_response = save_my_macros(request)
	meal_template_response = save_meal_templates(request)

	if [my_macro_response,meal_template_response] == [1,1]:
		return HttpResponse('1')

	error_dict = {}
	if my_macro_response != 1:
 		error_dict = {**my_macro_response}

	if meal_template_response != 1:
 		error_dict = {**meal_template_response,**error_dict}

	return render(request,'my_macros.html',error_dict) 

