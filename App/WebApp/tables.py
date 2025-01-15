import logging
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count, Sum
from django.http import JsonResponse

from .Utitlities import is_admin, is_zone_admin
from .models import LeaveApplication, Explanation, TransferPosting
logger = logging.getLogger(__name__)


# Employee Leave Application By Zone and Unit History Table
def CountLeaveIndividuals_table(request, empId : str | None = None):
    try:
        if is_admin(request.user):
            if empId:
                queryset = LeaveApplication.objects.select_related('employee').filter(employee_id=empId) \
                    .values('employee__Name', 'employee__Designation', 'employee__BPS', 'employee__ZONE', 'leave_type','leave_document') \
                    .annotate(
                    leave_count=Count('leave_type'),
                    total_days_granted=Sum('days_granted')
                ).order_by('-created_at')  # Order the queryset by 'employee__Name' or any other relevant field
                return queryset
            else:
                queryset = LeaveApplication.objects.select_related('employee').values('employee__Name',
                'employee__Designation', 'employee__BPS', 'employee__ZONE', 'leave_type','leave_document').\
                annotate(leave_count=Count('leave_type'),total_days_granted=Sum('days_granted')).order_by('-created_at')

        if is_zone_admin(request.user):
            if empId:
                queryset = LeaveApplication.objects.select_related('employee').filter(employee_id=empId) \
                    .filter(zone_type=request.user.userType) \
                    .values('employee__Name', 'employee__Designation', 'employee__BPS', 'employee__ZONE', 'leave_type','leave_document') \
                    .annotate(leave_count=Count('leave_type'),total_days_granted=Sum('days_granted')).order_by('-created_at')
                # Order the queryset by 'employee__Name' or another field
                return queryset
            else:
                queryset = LeaveApplication.objects.select_related('employee') \
                    .filter(zone_type=request.user.userType) \
                    .values('employee__Name', 'employee__Designation', 'employee__BPS', 'employee__ZONE', 'leave_type','leave_document') \
                    .annotate(
                    leave_count=Count('leave_type'),
                    total_days_granted=Sum('days_granted')
                ).order_by('-created_at')  # Order the queryset by 'employee__Name' or another field

        leave_paginator = Paginator(queryset, 10)  # Show 10 records per page
        page = request.GET.get('page')

        try:
            data = leave_paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            data = leave_paginator.page(1)
        except EmptyPage:
            # If page is out of range, deliver the last page of results.
            data = leave_paginator.page(leave_paginator.num_pages)

        return data

    except Exception as e:
        print(str(e))


# Employee Leave Application By Zone and Unit History Table
def CountExplanationIndividuals_table(request, empId : str | None = None):
    try:
        queryset = None

        # Admin logic
        if is_admin(request.user):
            if empId:
                queryset = Explanation.objects.select_related('employee').filter(employee_id=empId) \
                    .values('employee__Name', 'employee__Designation', 'employee__BPS', 'employee__ZONE', 'exp_type','exp_document') \
                    .annotate(exp_count=Count('exp_type')) \
                    .order_by('employee__Name')  # Sort by Name or other relevant field
                return queryset
            else:
                queryset = Explanation.objects.select_related('employee') \
                    .values('employee__Name', 'employee__Designation', 'employee__BPS', 'employee__ZONE', 'exp_type','exp_document') \
                    .annotate(exp_count=Count('exp_type')) \
                    .order_by('employee__Name')  # Sort by Name or other relevant field

        # Zone admin logic
        if is_zone_admin(request.user):
            if empId:
                print(empId)
                queryset = Explanation.objects.select_related('employee').filter(employee_id=empId) \
                    .filter(employee__ZONE=request.user.userType).values('employee__Name', 'employee__Designation',
                                                                         'employee__BPS', 'employee__ZONE', 'exp_type','exp_document') \
                    .annotate(exp_count=Count('exp_type')) \
                    .order_by('employee__Name')  # Sort by Name or other relevant field
                return queryset
            else:
                queryset = Explanation.objects.select_related('employee') \
                    .filter(employee__ZONE=request.user.userType).values('employee__Name', 'employee__Designation',
                                                                         'employee__BPS', 'employee__ZONE', 'exp_type','exp_document') \
                    .annotate(exp_count=Count('exp_type')) \
                    .order_by('employee__Name')  # Sort by Name or other relevant field

        if queryset:
            # Pagination logic
            paginator = Paginator(queryset, 10)  # Show 10 records per page
            page = request.GET.get('page')

            try:
                data = paginator.page(page)
            except PageNotAnInteger:
                data = paginator.page(1)
            except EmptyPage:
                data = paginator.page(paginator.num_pages)
        return data

    except Exception as e:
        print(f"Error occurred Count Explanation Table View: {str(e)}")


# Employee Transfer Posting By Zone and Unit History Table
def CountTransferPostingIndividuals_table(request, empId : str | None = None):
    try:
        queryset = None

        # Admin logic
        if is_admin(request.user):
            if empId:
                queryset = TransferPosting.objects.select_related('employee').filter(employee_id=empId) \
                    .values('employee__Name', 'employee__Designation', 'employee__CNIC_No', 'employee__BPS',
                            'employee__ZONE', 'old_zone',
                            'new_zone', 'old_unit', 'new_unit', 'chief_transfer_date', 'chief_order_number').order_by(
                    '-created_at')  # Sort by Name or other relevant
            else:
                queryset = TransferPosting.objects.select_related('employee') \
                .values('employee__Name', 'employee__Designation', 'employee__CNIC_No', 'employee__BPS',
                        'employee__ZONE', 'old_zone',
                        'new_zone', 'old_unit', 'new_unit', 'chief_transfer_date', 'chief_order_number').order_by(
                '-created_at')  # Sort by Name or other relevant

        # Zone admin logic
        if is_zone_admin(request.user):
            if empId:
                queryset = TransferPosting.objects.select_related('employee').filter(employee_id=empId) \
                    .values('employee__Name', 'employee__Designation', 'employee__CNIC_No', 'employee__BPS',
                            'employee__ZONE', 'old_zone',
                            'new_zone', 'old_unit', 'new_unit', 'zone_order_number', 'zone_transfer_date').filter(
                    zone_type=request.user.userType) \
                    .order_by('-created_at')  # Sort by Name or other relevant field
            else:
                queryset = TransferPosting.objects.select_related('employee') \
                .values('employee__Name', 'employee__Designation', 'employee__CNIC_No', 'employee__BPS',
                        'employee__ZONE', 'old_zone',
                        'new_zone', 'old_unit', 'new_unit', 'zone_order_number', 'zone_transfer_date').filter(
                zone_type=request.user.userType) \
                .order_by('-created_at')  # Sort by Name or other relevant field

        if queryset:
            # Pagination logic
            paginator = Paginator(queryset, 10)  # Show 10 records per page
            page = request.GET.get('page')

            try:
                data = paginator.page(page)
            except PageNotAnInteger:
                data = paginator.page(1)
            except EmptyPage:
                data = paginator.page(paginator.num_pages)
        return data

    except Exception as e:
        print(f"Error occurred Count Transfer Posting Table View: {str(e)}")


# Employee Transfer Positing By Zone and Unit History Based on EmpId Table
def get_employee_unit_data_table(request, emp_id):
    try:
        if emp_id:
            # Get the latest transfer record based on created_at
            latest_transfer_record = TransferPosting.objects.filter(employee_id=emp_id).order_by('-created_at').first()

            if latest_transfer_record:
                posting_summary = {
                    'units': {
                        'current_unit': latest_transfer_record.new_unit,
                        'previous_unit': latest_transfer_record.old_unit,
                    }
                }

                # Include zone information if the user is an admin
                if request.user.is_superuser == 1 or 2:
                    posting_summary['zones'] = {
                        'old_zone': latest_transfer_record.old_zone,
                        'new_zone': latest_transfer_record.new_zone,
                    }

                return JsonResponse(posting_summary)
            else:
                return JsonResponse({'error': 'No transfer records found'}, status=404)

        else:
            return JsonResponse({'error': 'Unauthorized or invalid employee ID'}, status=403)

    except Exception as e:
        logger.error(f"Error in get_employee_unit_data function: {e}")
        return JsonResponse({'error': str(e)}, status=500)


# Employee Explanation Application History Based on EmpId Table
def get_employee_exp_data_table(request, emp_id):
    try:
        if emp_id:
            # Get all explanation records based on employee_id
            explanation_records = Explanation.objects.filter(employee_id=emp_id).order_by('-created_at').all()
            explanations_list = []

            # Prepare the data in a JSON-friendly format
            for record in explanation_records:
                explanations_list.append({
                    'exp_type': record.exp_type,
                    'exp_issue_date': record.exp_issue_date.strftime('%Y-%m-%d'),
                    'exp_reply_date': record.exp_reply_date.strftime('%Y-%m-%d'),
                    'exp_document': record.exp_document.url if record.exp_document else None,
                    'zone_type': record.zone_type,
                    'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': record.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                })
            return JsonResponse({'explanations': explanations_list}, status=200)
        else:
            return JsonResponse({'error': 'Unauthorized or invalid employee ID'}, status=403)
    except Exception as e:
        logger.error(f"Error in get_employee_exp_data function: {e}")
        return JsonResponse({'error': str(e)}, status=500)  # table data
