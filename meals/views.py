from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.utils import IntegrityError
from django.db import transaction
import json
from decimal import Decimal
from meals.forms import LoginForm, SignUpForm, MakeMacrosForm,ImperialTDEEForm,MetricTDEEForm
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
	form = MakeMacrosForm()
	i_tdee_form = ImperialTDEEForm(data={'weight':5,'change_rate':5,'height':'5,3'})
	m_tdee_form = MetricTDEEForm()
	return render(request, 'my_macros.html',{
		'form':form,
		'i_tdee_form':i_tdee_form,
		'm_tdee_form':m_tdee_form
	})

def save_my_macros(request):

	post_dict = dict((key,value[0]) for key,value in request.POST.lists())
	unit_type = request.POST.get('unit_type','')
	if unit_type == 'imperial':
		height1 = request.POST.get('height_0','')
		height2 = request.POST.get('height_1','')
		if height1 != '' and height2 != '':
			post_dict['height'] = str((int(height1) * 12) + int(height2))

	tdee_form = ImperialTDEEForm(post_dict)
	if tdee_form.is_valid():
		print('tdee valid')
	else:
		print(tdee_form.errors)
	

	macro_form = MakeMacrosForm(request.POST)	
	if macro_form.is_valid():
		print('macro valid')
	else:
		print(macro_form.errors)
	
	post_dict['user'] = request.user
	create_macro_dict = {
		'user':post_dict.get('user',''),
		'gender':post_dict.get('gender',''),
		'age':post_dict.get('age',''),
		'weight':post_dict.get('weight',''), 
		'height':post_dict.get('height',''),
		'activity':post_dict.get('activity',''), 
		'direction':post_dict.get('direction',''),		
		'change_rate':Decimal(post_dict.get('change_rate','')), 
		'fat_percent':Decimal(post_dict.get('fat_pct','')), 
		'protein_percent':Decimal(post_dict.get('protein_pct','')), 
	}
	try:
		with transaction.atomic():
			Macros.objects.create(**create_macro_dict)
	except IntegrityError:
		pass
	return redirect('/')	
