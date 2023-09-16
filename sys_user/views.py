from django.shortcuts import render
from .forms import RegForm

# Create your views here.
def SignUp(request):
    context = {
        
    }
    return render(request, "auth/auth-signup.html", context)

def test1(request):
    context = {
        'form':RegForm()
    }
    return render(request, "auth/auth-signup2.html", context)

def login(request):
    context = {
    }
    return render(request, "auth/auth-login.html", context)

def forgotPassword(request):
    context = {
    }
    return render(request, "auth/auth-forgot.html", context)