from django.shortcuts import render
from django.http import HttpResponse
from meals.models import User

# Create your views here.
def home_page(request):
	return render(request, 'home.html') 

def meal_lab(request):
	return render(request, 'meal_lab.html')

def sign_up(request):
	return render(request, 'sign_up.html')

def create_account(request):
	
	user = User()
	user.username = request.POST.get('username','')
	user.email = request.POST.get('email','')
	user.password = request.POST.get('password','')
	user.save()

	return HttpResponse('1') 

