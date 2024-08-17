import json
import mimetypes
import logging
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .Utitlities import (
    DesignationWiseList,
    getRetirementList,
    getZoneRetirementList,
    fetchAllDispositionList,
    getZoneWiseOfficialsList,
    ZoneWiseStrength,
    ZoneDesignationWiseComparison,
    StrengthComparison,
    getAllEmpTransferPosting
)
from .models import DispositionList, TransferPosting

logger = logging.getLogger(__name__)


def index(request):
    if request.user.is_authenticated:
        return redirect('Dashboard')
    return render(request, 'login.html')


def userLogin(request):
    if request.user.is_authenticated:
        return redirect('Dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            request.session['UserName'] = username
            return render(request, 'Dashboard.html', {
                'title': 'Welcome to Dashboard!',
                'icon': 'success',
                'message': 'Login Successful!'
            })
        return render(request, 'login.html', {
            'title': 'Invalid',
            'icon': 'error',
            'message': 'Invalid Username or Password!'
        })

    return render(request, 'login.html', {
        'title': 'Invalid Method',
        'icon': 'error',
        'message': 'Method shall be POST rather than GET!'
    })


@login_required
def Dashboard(request):
    try:
        label = "Employee yet to be Retired in the Year 2024, Regional Tax Office - II"
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
        logger.error(f"Error in Dashboard view: {e}")
        return HttpResponse("An error occurred.", status=500)


@login_required
def getDispositionList(request):
    try:
        disposition_result, error = fetchAllDispositionList(request)
        if error:
            return HttpResponse(f"An error occurred: {error}", status=500)
        return render(request, 'DispositionList.html', {'DispositionResult': disposition_result})
    except Exception as e:
        logger.error(f"Error in getDispositionList view: {e}")
        return HttpResponse("An error occurred.", status=500)


@login_required
def Search(request):
    try:
        if request.method == 'POST':
            search_type = request.POST.get('type')
            search_value = request.POST.get('parameter')
            filter_args = {'CNIC_No': search_value} if search_type == 'CNIC' else {'Personal_No': search_value}
            result = DispositionList.objects.filter(**filter_args)
            return render(request, 'search.html', {'result': result})
        return render(request, 'search.html')
    except Exception as e:
        logger.error(f"Error in Search view: {e}")
        return HttpResponse("An error occurred.", status=500)


@login_required
def Zone(request):
    try:
        context = ZoneWiseStrength()
        if request.method == 'POST':
            search_zone = request.POST.get('Zone')
            results = getZoneWiseOfficialsList(search_zone)
            context.update({"results": results, 'zone': search_zone})
        return render(request, 'Zone.html', context)
    except Exception as e:
        logger.error(f"Error in Zone view: {e}")
        return HttpResponse("An error occurred.", status=500)


@login_required
def EmployeeTransferPosting(request):
    try:
        data = DispositionList.objects.values('id', 'Name', 'Designation', 'ZONE')

        if request.method == 'POST':
            emp_name = request.POST.get('emp_name')
            image = request.FILES.get('image')

            if image:
                file_type = mimetypes.guess_type(image.name)[0]
                if not file_type or (not file_type.startswith('image') and not file_type == 'application/pdf'):
                    return HttpResponse("Uploaded file is not a valid image or PDF.", status=400)
            else:
                return HttpResponse("No file uploaded.", status=400)

            transfer_posting = TransferPosting(
                employee=DispositionList.objects.get(id=emp_name),
                old_unit=request.POST.get('old_unit'),
                new_unit=request.POST.get('new_unit'),
                order_number=request.POST.get('order_number'),
                transfer_date=request.POST.get('transfer_order_date'),
                reason_for_transfer=request.POST.get('transfer_reason'),
                order_approved_by=request.POST.get('order_approved_by'),
                transfer_document=image
            )
            transfer_posting.save()

            return render(request, 'TransferPosting.html', {
                'title': 'Transfer Posting!',
                'icon': 'success',
                'message': 'Data Inserted Successfully!',
                'data': data
            })

        return render(request, 'TransferPosting.html', {'data': data})
    except Exception as e:
        logger.error(f"Error in EmployeeTransferPosting view: {e}")
        return HttpResponse(f"An error occurred: {str(e)}", status=500)


@login_required
def ManageEmployeeTransferPosting(request):
    try:
        transfer_records = getAllEmpTransferPosting()
        for item in transfer_records:
            transfer_document = item.get('transfer_document')
            mime_type = mimetypes.guess_type(transfer_document)[0] if transfer_document else None
            if mime_type == 'application/pdf':
                item['is_pdf'] = True
            elif mime_type and mime_type.startswith('image'):
                item['is_image'] = True

        return render(request, 'ManageTransferPosting.html', {'transfer_records': transfer_records})
    except Exception as e:
        logger.error(f"Error in ManageEmployeeTransferPosting view: {e}")
        return HttpResponse("An error occurred.", status=500)


@login_required
def Strength(request):
    try:
        final_data = StrengthComparison()
        return render(request, 'strength.html', {
            'data': final_data,
            'Comparison': ZoneDesignationWiseComparison()
        })
    except Exception as e:
        logger.error(f"Error in Strength view: {e}")
        return render(request, 'strength.html', {'error_message': str(e)})


def Logout(request):
    logout(request)
    return redirect('/')
