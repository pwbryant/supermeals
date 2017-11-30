from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.utils import IntegrityError
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
	i_tdee_form = ImperialTDEEForm()
	m_tdee_form = MetricTDEEForm()
	return render(request, 'my_macros.html',{
		'form':form,
		'i_tdee_form':i_tdee_form,
		'm_tdee_form':m_tdee_form
	})

def save_my_macros(request):
	
	create_macro_dict = {
		'user':request.user,
		'gender':request.POST.get('gender',''),
		'age':request.POST.get('age',''),
		'weight':request.POST.get('weight',''), 
		'height':request.POST.get('height','') ,
		'activity':request.POST.get('activity',''), 
		'direction':request.POST.get('direction',''), 
		'change_rate':request.POST.get('change_rate',''), 
		'fat_percent':request.POST.get('fat_percent',''), 
		'protein_percent':request.POST.get('protein_percent',''), 
	}
	Macros.objects.create(**create_macro_dict)
	return redirect('/')	
