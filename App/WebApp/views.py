from datetime import datetime
import mimetypes
import logging

from django.db.models import Sum
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
    getAllEmpTransferPosting,
    getAllEmpLeaveApplication
)
from .models import DispositionList, TransferPosting, LeaveApplication

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


@login_required(login_url='userLogin')  # redirect when user is not logged in
def Dashboard(request):
    try:
        if not request.user.is_authenticated:
            return redirect('/')

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
        return render(request, 'Dashboard.html', {'error': str(e)})


@login_required(login_url='userLogin')  # redirect when user is not logged in
def getDispositionList(request):
    try:
        disposition_result, error = fetchAllDispositionList(request)
        if error:
            logger.error(f"An error occurred: {error}", status=500)
        return render(request, 'DispositionList.html', {'DispositionResult': disposition_result})
    except Exception as e:
        logger.error(f"Error in getDispositionList view: {e}")
        return HttpResponse("An error occurred.", status=500)


@login_required(login_url='userLogin')  # redirect when user is not logged in
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


@login_required(login_url='userLogin')  # redirect when user is not logged in
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


@login_required(login_url='userLogin')  # redirect when user is not logged in
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


@login_required(login_url='userLogin')  # redirect when user is not logged in
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


@login_required(login_url='userLogin')  # redirect when user is not logged in
def submitLeaveApplication(request):
    try:
        data = DispositionList.objects.values('id', 'Name', 'Designation', 'ZONE')
        if request.method == 'POST':
            employee_name = request.POST.get('emp_name')
            leave_type = request.POST.get('leave_type')
            leave_start_date = request.POST.get('leave_start_date')
            leave_end_date = request.POST.get('leave_end_date')
            reason = request.POST.get('reason')
            leave_document = request.FILES.get('leave_document')
            # Calculate the number of days of leave
            start_date = datetime.strptime(leave_start_date, '%Y-%m-%d')
            end_date = datetime.strptime(leave_end_date, '%Y-%m-%d')
            leave_duration = (end_date - start_date).days + 1

            # Calculate the number of days of leave already taken in the current year
            current_year = datetime.now().year
            leave_taken = LeaveApplication.objects.filter(
                employee=employee_name,
                leave_type=leave_type,
                leave_start_date__year=current_year
            ).aggregate(Sum('days_granted'))['days_granted__sum'] or 0

            # Validate against the prescribed limits from database
            if leave_type == 'Casual Leave' and (leave_taken + leave_duration) > 20:
                context = {
                    'data': data,
                    'message': 'Casual Leave already take and cannot exceed 20 days per year.',
                    'title': 'Leave Application',
                    'icon': 'error'

                }
                return render(request, 'LeaveApplication.html', context)
            elif leave_type == 'Earned Leave' and (leave_taken + leave_duration) > 48:
                context = {
                    'data': data,
                    'message': 'Earned Leave already taken and cannot exceed 48 days per year.',
                    'title': 'Leave Application',
                    'icon': 'error'

                }
                return render(request, 'LeaveApplication.html', context)

            # Validate against the prescribed limits
            if leave_type == 'Casual Leave' and leave_duration > 20:
                context = {
                    'data': data,
                    'message': 'Casual Leave cannot exceed 20 days per year.',
                    'title': 'Leave Application',
                    'icon': 'error'

                }
                return render(request, 'LeaveApplication.html', context)
            elif leave_type == 'Earned Leave' and leave_duration > 48:
                context = {
                    'data': data,
                    'message': 'Earned Leave cannot exceed 48 days per year.',
                    'title': 'Leave Application',
                    'icon': 'error'

                }
                return render(request, 'LeaveApplication.html', context)

            # Determine the number of days granted (here we just use the requested duration)
            days_granted = leave_duration

            # Save the data to the database
            LeaveApplication.objects.create(
                employee=DispositionList.objects.get(id=employee_name),
                leave_type=leave_type,
                leave_start_date=leave_start_date,
                leave_end_date=leave_end_date,
                leave_document=leave_document,
                reason=reason,
                days_granted=days_granted
            )
            context = {
                'data': data,
                'message' : 'Your leave application has been submitted successfully.',
                'title' : 'Leave Application',
                'icon' : 'success'
            }
            return render(request, 'LeaveApplication.html', context)
        else:
            context = {
                'data': data
            }
            return render(request, 'LeaveApplication.html', context)
    except Exception as e:
        print(str(e))
        return HttpResponse(str(e))


@login_required(login_url='userLogin')  # redirect when user is not logged in
def ManageEmployeeLeaveApplication(request):
    try:
        leave_application = getAllEmpLeaveApplication()
        for item in leave_application:
            leave_document = item.get('leave_document')
            mime_type = mimetypes.guess_type(leave_document)[0] if leave_document else None
            print(mime_type)
            if mime_type == 'application/pdf':
                item['is_pdf'] = True
            elif mime_type and mime_type.startswith('image'):
                item['is_image'] = True

        return render(request, 'ManageLeaveApplication.html', {'leave_application': leave_application})
    except Exception as e:
        logger.error(f"Error in ManageLeaveApplication view: {e}")
        return HttpResponse("An error occurred.", status=500)


@login_required(login_url='userLogin')  # redirect when user is not logged in
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
