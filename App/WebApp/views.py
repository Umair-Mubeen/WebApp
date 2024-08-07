import json

from django.db.models import Q, Count
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login, logout
from .Utitlities import DesignationWiseList, getRetirementList, getZoneRetirementList, fetchAllDispositionList, \
    getZoneWiseOfficialsList, ZoneWiseStrength
from .models import DispositionList


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
            results = DesignationWiseList()
            employee_to_be_retired = getRetirementList()
            zone_counts = getZoneRetirementList()
            zones = list(zone_counts.keys())
            counts = list(zone_counts.values())

            return render(request, 'Dashboard.html',
                          {'results': results, 'retired': employee_to_be_retired, 'zones': zones, 'counts': counts})
    except Exception as e:
        print(str(e))


def getDispositionList(request):
    try:
        if isLoggedIn(request) is False:
            return redirect('/')

        disposition_result, error = fetchAllDispositionList(request)
        if error:
            return HttpResponse(f"An error occurred: {error}", status=500)
        return render(request, 'DispositionList.html', {'DispositionResult': disposition_result})
    except Exception as e:
        return str(e)


def Search(request):
    try:
        if isLoggedIn(request) is False:
            return redirect('/')

        if request.method == 'POST':
            type = request.POST.get('type')
            searchValue = request.POST.get('parameter')
            if type == 'CNIC':
                result = DispositionList.objects.filter(CNIC_No=searchValue)
                return render(request, 'search.html', {'result': result})
            else:
                result = DispositionList.objects.filter(Personal_No=searchValue)
                return render(request, 'search.html', {'result': result})

        return render(request, 'search.html')
    except Exception as e:
        return HttpResponse(str(e))


def Zone(request):
    try:
        if isLoggedIn(request) is False:
            return redirect('/')
        context = ZoneWiseStrength()
        print(type(context))
        if request.method == 'POST':
            searchZone = request.POST.get('Zone')
            results = getZoneWiseOfficialsList(searchZone)
            print(results)
            results_list = list(results)
            results_json = json.dumps(results_list, indent=4)
            context.update({"results": results_json, 'zone': searchZone})
            return render(request, 'Zone.html', context)

        return render(request, 'Zone.html', context)
    except Exception as e:
        return HttpResponse(str(e))


def TransferPosting(request):
    try:
        if isLoggedIn(request) is False:
            return redirect('/')

        disposition_result, error = fetchAllDispositionList(request)
        if error:
            return HttpResponse(f"An error occurred: {error}", status=500)
        return render(request, 'DispositionList.html', {'DispositionResult': disposition_result})
    except Exception as e:
        return str(e)


def Logout(request):
    logout(request)
    return redirect('/')


def isLoggedIn(request):
    if request.user.is_authenticated:
        print("True Logged In")
        return True

    else:
        print("False Logged In")
        return False
