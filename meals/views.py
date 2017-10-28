from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home_page(request):
	return render(request, 'home.html') 

def meal_lab(request):
	return render(request, 'meal_lab.html')

def sign_up(request):
	return render(request, 'sign_up.html')

def create_account(request):
	
	return HttpResponse('1') 
