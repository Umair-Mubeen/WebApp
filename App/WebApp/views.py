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
            print(user.userType)
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
        results = DesignationWiseList(request.user.userType, request)
        employee_to_be_retired = getRetirementList(request.user.userType, request)
        zone_counts = getZoneRetirementList(request.user.userType, request)
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
        if request.user.is_superuser == 1:  # admin
            data = DispositionList.objects.values('id', 'Name', 'Designation', 'ZONE', 'CNIC_No', 'Date_of_Birth',
                                                  'Date_of_Entry_into_Govt_Service', 'Date_of_Retirement')
        else:
            data = DispositionList.objects.values('id', 'Name', 'Designation', 'ZONE', 'CNIC_No', 'Date_of_Birth',
                                                  'Date_of_Entry_into_Govt_Service', 'Date_of_Retirement').filter(
                ZONE=request.user.userType)

        if request.method == 'POST':
            # search_type = request.POST.get('type')
            search_value = request.POST.get('emp_name')

            leave_application = LeaveApplication.objects.filter(employee_id=search_value).select_related('employee')
            transfer_records = TransferPosting.objects.filter(employee_id=search_value).select_related('employee')
            # filter_args = {'CNIC_No': search_value} if search_type == 'CNIC' else {'Personal_No': search_value}
            # result = DispositionList.objects.filter(id=search_value)
            result = DispositionList.objects.get(id=search_value)

            context = {
                'result': result,
                'data': data,
                'id': search_value,
                'leave_application': leave_application,
                'transfer_records': transfer_records
            }
            return render(request, 'search.html', context)
        return render(request, 'search.html', {'data': data})
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
        empId = request.GET.get('empId', '')
        rowId = request.GET.get('rowId', '')
        opType = request.GET.get('type','')

        # Determine if the user is an admin or zone admin and filter data accordingly
        if request.user.is_superuser == 1:
            data = DispositionList.objects.values('id', 'Name', 'Designation', 'ZONE')
        else:
            data = DispositionList.objects.values('id', 'Name', 'Designation', 'ZONE').filter(
                ZONE=request.user.userType)

        # fetch row from database zone admin in case of edit record
        if empId and rowId:
            postingRow = TransferPosting.objects.get(id=rowId, employee_id=empId, zone_type=request.user.userType)

            row = {
                'zone_current_unit': postingRow.old_unit or '',
                'zone_new_unit': postingRow.new_unit or '',
                'zone_order_number': postingRow.zone_order_number or '',
                'zone_transfer_date': postingRow.zone_transfer_date or '',
                'zone_transfer_reason': postingRow.zone_reason_for_transfer or '',
                'zone_order_approved_by': postingRow.zone_order_approved_by or ''
            }   # # f
        else:
            # Handle the case where both empId and rowId are None
            row = {
                'zone_current_unit': '',
                'zone_new_unit': '',
                'zone_order_number': '',
                'zone_transfer_date': '',
                'zone_transfer_reason': '',
                'zone_order_approved_by': ''
            }
            # You can add additional logic here, like logging an error or returning a response

        if request.method == 'POST':
            emp_name = request.POST.get('emp_name') or request.POST.get('hd_emp')
            image = request.FILES.get('image')
            hd_rowId = request.POST.get('hd_rowId')
            hd_type = request.POST.get('hd_type')

            # Validate uploaded file
            if not image:
                return HttpResponse("No file uploaded.", status=400)

            file_type = mimetypes.guess_type(image.name)[0]
            if not file_type or (not file_type.startswith('image') and file_type != 'application/pdf'):
                return HttpResponse("Uploaded file is not a valid image or PDF.", status=400)

            # Retrieve the employee object
            employee = DispositionList.objects.get(id=emp_name)

            if request.user.is_superuser == 1:
                print('admin create record')
                # Handling for superuser (admin)
                new_zone = request.POST.get('new_zone')
                employee.ZONE = new_zone
                employee.save()

                transfer_posting = TransferPosting(
                    employee=employee,
                    old_zone=request.POST.get('old_zone'),
                    new_zone=new_zone,
                    chief_order_number=request.POST.get('order_number'),
                    chief_transfer_date=request.POST.get('transfer_order_date'),
                    chief_reason_for_transfer=request.POST.get('transfer_reason'),
                    chief_order_approved_by=request.POST.get('order_approved_by'),
                    chief_transfer_document=image,
                    zone_type=new_zone
                )
            elif request.user.is_superuser == 2 and hd_type and hd_rowId:
                print("editing zone record employees")
                # Handling for zone admin
                transfer_posting = TransferPosting.objects.get(employee=employee)
                transfer_posting.old_unit = request.POST.get('zone_prev_unit')
                transfer_posting.new_unit = request.POST.get('zone_new_unit')
                transfer_posting.zone_range = request.POST.get('range')
                transfer_posting.zone_order_number = int(request.POST.get('order_number'))
                transfer_order_date_str = request.POST.get('transfer_order_date')
                try:
                    transfer_order_date = datetime.fromisoformat(transfer_order_date_str)
                except ValueError:
                    transfer_order_date = None

                transfer_posting.zone_transfer_date = transfer_order_date
                transfer_posting.zone_reason_for_transfer = request.POST.get('transfer_reason')
                transfer_posting.zone_order_approved_by = request.POST.get('order_approved_by')
                transfer_posting.zone_transfer_document = image

            else:  # in case no emp Id and row Id
                print('create transfer posting')
                transfer_posting = TransferPosting(
                    employee=employee,
                    old_unit=request.POST.get('zone_prev_unit'),
                    new_unit=request.POST.get('zone_new_unit'),
                    zone_range=request.POST.get('range'),
                    zone_order_number=request.POST.get('order_number'),
                    zone_transfer_date=request.POST.get('transfer_order_date'),
                    zone_reason_for_transfer=request.POST.get('transfer_reason'),
                    zone_order_approved_by=request.POST.get('order_approved_by'),
                    zone_transfer_document=image,
                    zone_type=request.user.userType
                )

            transfer_posting.save()

            return render(request, 'TransferPosting.html', {
                'title': 'Transfer Posting!',
                'icon': 'success',
                'message': 'Data Inserted Successfully!',
                'data': data,
            })

        return render(request, 'TransferPosting.html',
                      {'data': data, 'empId': empId, 'row' : row, 'rowId' : rowId, 'type' : opType})
    except Exception as e:
        logger.error(f"Error in EmployeeTransferPosting view: {e}")
        return HttpResponse(f"An error occurred: {str(e)}", status=500)


@login_required(login_url='userLogin')  # redirect when user is not logged in
def ManageEmployeeTransferPosting(request):
    try:
        print(request.user.userType)
        transfer_records = getAllEmpTransferPosting(request.user.is_superuser, request.user.userType)
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
        if request.user.is_superuser == 1:
            data = DispositionList.objects.values('id', 'Name', 'Designation', 'ZONE')
        else:
            data = DispositionList.objects.values('id', 'Name', 'Designation', 'ZONE').filter(
                ZONE=request.user.userType)
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
                'message': 'Your leave application has been submitted successfully.',
                'title': 'Leave Application',
                'icon': 'success'
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
        final_data = StrengthComparison(request.user.userType, None)
        return render(request, 'strength.html', {
            'data': final_data,
            'Comparison': ZoneDesignationWiseComparison(),
        })
    except Exception as e:
        logger.error(f"Error in Strength view: {e}")
        return render(request, 'strength.html', {'error_message': str(e)})


def Logout(request):
    logout(request)
    return redirect('/')
