from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

from meals.models import MM_user

# Create your views here.
def home_or_login(request):
	print(request.user)
	if request.user.is_authenticated:
		return render(request, 'home.html') 
	else:
		return redirect('/login')

def to_login(request):
	
	return render(request, 'login.html') 


def logging_in(request):

	username,password = request.POST['username'],request.POST['password']
	user = authenticate(request,username=username,password=password)
	if user is not None:
		login(request, user)
		#return redirect('/')
		return HttpResponse('1')
	else:
		return HttpResponse('0')


def meal_lab(request):
	return render(request, 'meal_lab.html')


def sign_up(request):
	return render(request, 'sign_up.html')


def create_account(request):
	
	try:
		user = User()
		user.username = request.POST.get('username','')
		user.email = request.POST.get('email','')
		user.password = request.POST.get('password','')
		user.save()
		login(request, user)

		return HttpResponse('1')
	except: 
		return HttpResponse('0')
