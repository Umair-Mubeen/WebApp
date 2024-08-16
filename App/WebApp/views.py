import json
import mimetypes

from django.db.models import Q, Count
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login, logout
from .Utitlities import DesignationWiseList, getRetirementList, getZoneRetirementList, fetchAllDispositionList, \
    getZoneWiseOfficialsList, ZoneWiseStrength, ZoneDesignationWiseComparison, StrengthComparison, \
    getAllEmpTransferPosting
from .models import DispositionList, TransferPosting


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
        print(isLoggedIn(request))
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
        return HttpResponse(str(e))


def Dashboard(request):
    try:
        if not isLoggedIn(request):
            return redirect('/')
        else:
            label = "Employee yet to be Retired in the Year 2024,Regional Tax Office - II"
            Comparison = ZoneDesignationWiseComparison()
            results = DesignationWiseList()
            employee_to_be_retired = getRetirementList()
            zone_counts = getZoneRetirementList()
            zones = list(zone_counts.keys())
            counts = list(zone_counts.values())
            context = {
                'zones': zones,
                'counts': counts,
                'retired': employee_to_be_retired,
                'results': results,
                'Comparison': Comparison,
                'label': label,
            }
            return render(request, 'Dashboard.html', context)
    except Exception as e:
        return str(e)


def getDispositionList(request):
    try:
        if not isLoggedIn(request):
            return redirect('/')

        disposition_result, error = fetchAllDispositionList(request)
        if error:
            return HttpResponse(f"An error occurred: {error}", status=500)
        return render(request, 'DispositionList.html', {'DispositionResult': disposition_result})
    except Exception as e:
        return str(e)


def Search(request):
    try:
        if not isLoggedIn(request):
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
        if not isLoggedIn(request):
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


def EmployeeTransferPosting(request):
    try:
        if not isLoggedIn(request):
            return redirect('/')
        data = DispositionList.objects.values('id', 'Name', 'Designation', 'ZONE')

        if request.method == 'POST':
            emp_name = request.POST.get('emp_name')
            old_unit = request.POST.get('old_unit')
            new_unit = request.POST.get('new_unit')
            order_number = request.POST.get('order_number')
            transfer_order_date = request.POST.get('transfer_order_date')
            transfer_reason = request.POST.get('transfer_reason')
            order_approved_by = request.POST.get('order_approved_by')
            image = request.FILES.get('image')

            # Check if an image or PDF file is uploaded
            if image:
                file_type = mimetypes.guess_type(image.name)[0]
                if not file_type or (not file_type.startswith('image') and not file_type == 'application/pdf'):
                    return HttpResponse("Uploaded file is not a valid image or PDF.", status=400)
            else:
                return HttpResponse("No file uploaded.", status=400)

            # Save data to the database
            employee_id = DispositionList.objects.get(id=emp_name)

            transfer_posting = TransferPosting(
                employee=employee_id,
                old_unit=old_unit,
                new_unit=new_unit,
                order_number=order_number,
                transfer_date=transfer_order_date,
                reason_for_transfer=transfer_reason,
                order_approved_by=order_approved_by,
                transfer_document=image
            )
            transfer_posting.save()

            return render(request, 'TransferPosting.html',
                          {'title': 'Transfer Posting !', 'icon': 'success', 'message': 'Data Inserted SuccessFully !',
                           'data': data})

        else:
            return render(request, 'TransferPosting.html', {'data': data})

    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}", status=500)


def ManageEmployeeTransferPosting(request):
    try:
        if not isLoggedIn(request):
            return redirect('/')
        transfer_records = getAllEmpTransferPosting()
        for item in transfer_records:
            transfer_document = item.get('transfer_document', None)
            if transfer_document.endswith('.pdf'):
                item['is_pdf'] = True
            else:
                item['is_image'] = False

        return render(request, 'ManageTransferPosting.html', {'transfer_records': transfer_records})

    except Exception as e:
        return HttpResponse(str(e))


def Strength(request):
    try:
        if not isLoggedIn(request):
            return redirect('/')
        final_data = StrengthComparison()
        return render(request, 'strength.html', {'data': final_data, 'Comparison': ZoneDesignationWiseComparison()})
    except Exception as e:
        return render(request, 'strength.html', {'error_message': str(e)})


def Logout(request):
    logout(request)
    return redirect('/')


def isLoggedIn(request):
    if request.user.is_authenticated:
        print(True)
        return True

    else:
        print(False)
        return False
