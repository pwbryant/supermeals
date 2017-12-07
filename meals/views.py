from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.utils import IntegrityError
from django.db import transaction
import json
from decimal import Decimal
from meals.forms import LoginForm, SignUpForm, MakeMacrosForm
from meals.models import Macros

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
	form = MakeMacrosForm(unit_type='imperial')
	return render(request, 'my_macros.html',{
		'form':form,
		'unit_type':'imperial'
	})

def save_my_macros(request):
	
	POST = request.POST
	post_dict = dict((key,value[0]) for key,value in POST.lists())
	unit_type = POST.get('choose_unit_type','')
	if unit_type == 'imperial':
		height1 = POST.get('i_height_0','')
		height2 = POST.get('i_height_1','')
		if height1 != '' and height2 != '':
			post_dict['height'] = str((int(height1) * 12) + int(height2))
		post_dict['weight'] = POST.get('i_weight','')
		post_dict['change_rate'] = POST.get('i_change_rate','')

	if unit_type == 'metric':
		post_dict['height'] = POST.get('m_height','')
		post_dict['weight'] = POST.get('m_weight','')
		post_dict['change_rate'] = POST.get('m_change_rate','')
	
	macro_form = MakeMacrosForm(post_dict,unit_type=unit_type)	
	if not macro_form.is_valid():
		return render(request,'my_macros.html', {
			'form':macro_form,
			'unit_type':unit_type
		})

	
	post_dict.pop('choose_unit_type')
	if unit_type == 'imperial':
		post_dict.pop('i_height_0')
		post_dict.pop('i_height_1')
		post_dict.pop('i_weight')
		post_dict.pop('i_change_rate')
	if unit_type == 'metric':
		post_dict.pop('m_height')
		post_dict.pop('m_weight')
		post_dict.pop('m_change_rate')

	post_dict.pop('fat_g')
	post_dict.pop('protein_g')
	post_dict.pop('carbs_g')
	post_dict.pop('carbs_percent')
	
	post_dict['user'] = request.user
	post_dict['change_rate'] = Decimal(post_dict['change_rate']) 
	post_dict['protein_percent'] = Decimal(post_dict['protein_percent']) 
	post_dict['fat_percent'] = Decimal(post_dict['fat_percent']) 
	try:
		with transaction.atomic():
			Macros.objects.create(**post_dict)
		pass	
	except IntegrityError:
		pass

	return HttpResponse('1')
