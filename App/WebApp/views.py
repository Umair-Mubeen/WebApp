from django.db.models import Count
from django.db.models.functions import Trim
from django.shortcuts import render
from io import StringIO
from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from .models import DispositionList
from django.db.models import Count, Func, Value


# Create your views here.


def index(request):
    try:
        if isLoggedIn(request):
            return redirect('Dashboard')
        else:
            return render(request, 'login.html')
    except Exception as e:
        return HttpResponse(str(e))


def userLogin(request):
    try:
        if isLoggedIn(request):
            return redirect('Dashboard')

        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                request.session['UserName'] = username
                request.session.save()
                return render(request, 'Dashboard.html',
                              {'title': 'Welcome to Dashboard !', 'icon': 'success',
                               'message': 'Login SuccessFully!'})

            else:
                return render(request, 'login.html',
                              {'title': 'Invalid ', 'icon': 'error', 'message': 'Invalid Username or Password!'})

        else:
            render(request, 'login.html',
                   {'title': 'Invalid Method ', 'icon': 'error', 'message': 'Method shall be POST rather than GET !'})
    except Exception as e:
        return render(request, 'login.html')


def Dashboard(request):
    try:
        if isLoggedIn(request) is False:
            return redirect('/')
        else:
            results = DispositionList.objects.annotate(trimmed_designation=Trim('Designation')).values('trimmed_designation').annotate(total=Count('trimmed_designation'))
            print(results)
            return render(request, 'Dashboard.html', {'results':results})
    except Exception as e:
        print(str(e))

def Logout(request):
    logout(request)
    return redirect('/')


def isLoggedIn(request):
    if request.user.is_authenticated:
        print("True Logged In")
        return True
        # if 'UserName' not in request.session:
        #     return False
    else:
        print("False Logged In")
        return False
