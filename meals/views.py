from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.utils import IntegrityError
import json

from meals.models import MM_user

# Create your views here.
def home_or_login(request):

	if request.user.is_authenticated:
		return render(request, 'home.html') 
	else:
		return redirect('meals/login/')


def to_login(request):
	
	return render(request, 'login.html') 


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
		return render(request,'login.html',{"error":error})


def logging_off(request):

	logout(request)
	return redirect('/')	


def sign_up(request):

	return render(request, 'sign_up.html')


def create_account(request):
	
	try:
		user = User()
		user.username = request.POST.get('username','')
		user.email = request.POST.get('email','')
		user.set_password(request.POST.get('password',''))
		user.save()
		login(request, user)
		return redirect('/')	

	except IntegrityError: 
		
		return render(request,'sign_up.html',{"error":"This username is already taken"})
		
