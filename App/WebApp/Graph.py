import logging
from collections import defaultdict

from django.db.models import Count, Sum
from django.db.models.functions import Substr
from django.http import JsonResponse

from .Utitlities import is_admin, is_zone_admin
from .models import TransferPosting, LeaveApplication, Explanation, DispositionList

logger = logging.getLogger(__name__)


# <............ Graph Functions Starts Here ...............>
def transfer_posting_chart(request):
    try:
        userType = None
        # Aggregating transfers by zone_type
        if is_admin(request.user):
            userType = 1
            # For admin, get data for all zones (returns list of dicts)
            zone_transfer_data = TransferPosting.objects.values('zone_type').annotate(
                total_transfers=Count('id')).order_by(
                'zone_type')

            # For this case, use dictionary-style access
            zones = [entry['zone_type'] for entry in zone_transfer_data]
            total_transfers = [entry['total_transfers'] for entry in zone_transfer_data]
            context = {
                'zones': zones,
                'total_transfers': total_transfers,
                'userType': userType
            }
            return context
        elif is_zone_admin(request.user):
            userType = 2
            # Filter records based on the user's zone_type (which corresponds to userType)
            zone_transfer_data = TransferPosting.objects.filter(zone_type=request.user.userType).values('zone_type',
                                                                                                        'new_unit').annotate(
                total_transfers=Count('id')
            ).order_by('zone_type', 'new_unit')

            # Prepare data for Chart.js
            zones = list(set(entry['zone_type'] for entry in zone_transfer_data))  # Unique zone names
            units = list(set(entry['new_unit'] for entry in zone_transfer_data))  # Unique units
            unit_counts = {unit: 0 for unit in units}

            # Aggregate the total number of transfers for each unit
            for entry in zone_transfer_data:
                unit = entry['new_unit']
                unit_counts[unit] = entry['total_transfers']

        # Return the context to the template
        context = {
            'zones': zones,
            'units': units,
            'unit_counts': unit_counts,
            'userType': userType

        }
        return context
    except Exception as e:
        print(str(e))


def get_employee_leave_data(request, emp_id=None):
    try:
        leave_summary = {}
        zoneType = None

        # Determine if the user is an admin
        if is_admin(request.user):
            # Filter by the user's zone_type if not admin
            if emp_id:
                leave_data = LeaveApplication.objects.filter(employee_id=emp_id)
                for zone in leave_data:
                    zoneType = zone.zone_type

                casual_leave = leave_data.filter(leave_type='Casual Leave', zone_type=zoneType)
                earned_leave = leave_data.filter(leave_type='Earned Leave', zone_type=zoneType)
                ex_pakistan_leave = leave_data.filter(leave_type='Ex-Pakistan Leave', zone_type=zoneType)
                medical_leave = leave_data.filter(leave_type='Medical Leave', zone_type=zoneType)
                study_leave = leave_data.filter(leave_type='Study Leave', zone_type=zoneType)
                maternity_leave = leave_data.filter(leave_type='Maternity Leave', zone_type=zoneType)
                special_leave = leave_data.filter(leave_type='Special Leave', zone_type=zoneType)
                leave_summary = {
                    'casual_leave': {
                        'count': casual_leave.count(),
                        'days': casual_leave.aggregate(total_days=Sum('days_granted'))['total_days'] or 0,
                    },
                    'earned_leave': {
                        'count': earned_leave.count(),
                        'days': earned_leave.aggregate(total_days=Sum('days_granted'))['total_days'] or 0,
                    },
                    'ex_pakistan_leave': {
                        'count': ex_pakistan_leave.count(),
                        'days': ex_pakistan_leave.aggregate(total_days=Sum('days_granted'))['total_days'] or 0,
                    },

                    'medical_leave': {
                        'count': medical_leave.count(),
                        'days': medical_leave.aggregate(total_days=Sum('days_granted'))['total_days'] or 0,
                    },
                    'study_leave': {
                        'count': study_leave.count(),
                        'days': study_leave.aggregate(total_days=Sum('days_granted'))['total_days'] or 0,
                    },
                    'maternity_leave': {
                        'count': maternity_leave.count(),
                        'days': maternity_leave.aggregate(total_days=Sum('days_granted'))['total_days'] or 0,
                    },
                    'special_leave': {
                        'count': special_leave.count(),
                        'days': special_leave.aggregate(total_days=Sum('days_granted'))['total_days'] or 0,
                    },
                }
                return JsonResponse(leave_summary)

            # Group by zone_type Graph Leave Chart
            zones = LeaveApplication.objects.values('zone_type').distinct()
            for zone in zones:
                zone_type = zone['zone_type']

                casual_leave = LeaveApplication.objects.filter(leave_type='Casual Leave', zone_type=zone_type)
                earned_leave = LeaveApplication.objects.filter(leave_type='Earned Leave', zone_type=zone_type)
                ex_pakistan_leave = LeaveApplication.objects.filter(leave_type='Ex-Pakistan Leave', zone_type=zone_type)
                medical_leave = LeaveApplication.objects.filter(leave_type='Medical Leave', zone_type=zone_type)
                study_leave = LeaveApplication.objects.filter(leave_type='Study Leave', zone_type=zone_type)
                maternity_leave = LeaveApplication.objects.filter(leave_type='Maternity Leave', zone_type=zone_type)
                special_leave = LeaveApplication.objects.filter(leave_type='Special Leave', zone_type=zone_type)

                leave_summary[zone_type] = {
                    'casual_leave': {
                        'count': casual_leave.count(),
                        'days': casual_leave.aggregate(total_days=Sum('days_granted'))['total_days'] or 0,
                    },
                    'earned_leave': {
                        'count': earned_leave.count(),
                        'days': earned_leave.aggregate(total_days=Sum('days_granted'))['total_days'] or 0,
                    },
                    'ex_pakistan_leave': {
                        'count': ex_pakistan_leave.count(),
                        'days': ex_pakistan_leave.aggregate(total_days=Sum('days_granted'))['total_days'] or 0,
                    },

                    'medical_leave': {
                        'count': medical_leave.count(),
                        'days': medical_leave.aggregate(total_days=Sum('days_granted'))['total_days'] or 0,
                    },
                    'study_leave': {
                        'count': study_leave.count(),
                        'days': study_leave.aggregate(total_days=Sum('days_granted'))['total_days'] or 0,
                    },
                    'maternity_leave': {
                        'count': maternity_leave.count(),
                        'days': maternity_leave.aggregate(total_days=Sum('days_granted'))['total_days'] or 0,
                    },
                    'special_leave': {
                        'count': special_leave.count(),
                        'days': special_leave.aggregate(total_days=Sum('days_granted'))['total_days'] or 0,
                    },
                }
            leave_summary.update({'userType': 1})
            return leave_summary
        if is_zone_admin(request.user):
            if emp_id:
                leave_data = LeaveApplication.objects.filter(employee_id=emp_id)
            else:
                leave_data = LeaveApplication.objects.filter(zone_type=request.user.userType)

            zoneType = request.user.userType
            casual_leave = leave_data.filter(leave_type='Casual Leave', zone_type=zoneType)
            earned_leave = leave_data.filter(leave_type='Earned Leave', zone_type=zoneType)
            ex_pakistan_leave = leave_data.filter(leave_type='Ex-Pakistan Leave', zone_type=zoneType)
            medical_leave = leave_data.filter(leave_type='Medical Leave', zone_type=zoneType)
            study_leave = leave_data.filter(leave_type='Study Leave', zone_type=zoneType)
            maternity_leave = leave_data.filter(leave_type='Maternity Leave', zone_type=zoneType)
            special_leave = leave_data.filter(leave_type='Special Leave', zone_type=zoneType)

            leave_summary = {
                'casual_leave': {
                    'count': casual_leave.count(),
                    'days': casual_leave.aggregate(total_days=Sum('days_granted'))['total_days'] or 0,
                },
                'earned_leave': {
                    'count': earned_leave.count(),
                    'days': earned_leave.aggregate(total_days=Sum('days_granted'))['total_days'] or 0,
                },
                'ex_pakistan_leave': {
                    'count': ex_pakistan_leave.count(),
                    'days': ex_pakistan_leave.aggregate(total_days=Sum('days_granted'))['total_days'] or 0,
                },

                'medical_leave': {
                    'count': medical_leave.count(),
                    'days': medical_leave.aggregate(total_days=Sum('days_granted'))['total_days'] or 0,
                },
                'study_leave': {
                    'count': study_leave.count(),
                    'days': study_leave.aggregate(total_days=Sum('days_granted'))['total_days'] or 0,
                },
                'maternity_leave': {
                    'count': maternity_leave.count(),
                    'days': maternity_leave.aggregate(total_days=Sum('days_granted'))['total_days'] or 0,
                },
                'special_leave': {
                    'count': special_leave.count(),
                    'days': special_leave.aggregate(total_days=Sum('days_granted'))['total_days'] or 0,
                },
            }
            if emp_id:
                return JsonResponse(leave_summary)

        leave_summary.update({'userType': request.user.is_superuser})
        print(leave_summary)
        return leave_summary
    except Exception as e:
        logger.error(f"Error in get_employee_leave_data function: {e}")
        return {'error': str(e)}


def get_employee_explanation_data(request, emp_id=None):
    try:
        explanation_summary = {}

        # Check if user is admin
        if is_admin(request.user):
            # Group by zone_type and aggregate explanation data for each zone
            zones = Explanation.objects.values('zone_type').distinct()

            for zone in zones:
                zone_type = zone['zone_type']

                explanations = Explanation.objects.filter(zone_type=zone_type)

                explanation_summary[zone_type] = {
                    'unapproved_leave': {
                        'count': explanations.filter(exp_type='Unapproved Leave').count(),
                    },
                    'attendance_issue': {
                        'count': explanations.filter(exp_type='Attendance Issue').count(),
                    },
                    'absent': {
                        'count': explanations.filter(exp_type='Absent').count(),
                    },
                    'habitual_absentee': {
                        'count': explanations.filter(exp_type='Habitual Absentee').count(),
                    },
                    'performance': {
                        'count': explanations.filter(exp_type='Performance').count(),
                    },
                    'misconduct_explanation': {
                        'count': explanations.filter(exp_type='Misconduct Explanation').count(),
                    },
                    'delay_explanation': {
                        'count': explanations.filter(exp_type='Delay Explanation').count(),
                    },
                    'leave_explanation': {
                        'count': explanations.filter(exp_type='Leave Explanation').count(),
                    },
                    'disciplinary': {
                        'count': explanations.filter(exp_type='Disciplinary').count(),
                    },
                }

        elif is_zone_admin(request.user):
            # Filter by the user's zone_type if not admin
            explanations = Explanation.objects.filter(zone_type=request.user.userType)
            if emp_id:
                explanations = explanations.filter(employee__id=emp_id)

            explanation_summary = {
                'unapproved_leave': {
                    'count': explanations.filter(exp_type='Unapproved Leave').count(),
                },
                'attendance_issue': {
                    'count': explanations.filter(exp_type='Attendance Issue').count(),
                },
                'absent': {
                    'count': explanations.filter(exp_type='Absent').count(),
                },
                'habitual_absentee': {
                    'count': explanations.filter(exp_type='Habitual Absentee').count(),
                },
                'performance': {
                    'count': explanations.filter(exp_type='Performance').count(),
                },
                'misconduct_explanation': {
                    'count': explanations.filter(exp_type='Misconduct Explanation').count(),
                },
                'delay_explanation': {
                    'count': explanations.filter(exp_type='Delay Explanation').count(),
                },
                'leave_explanation': {
                    'count': explanations.filter(exp_type='Leave Explanation').count(),
                },
                'disciplinary': {
                    'count': explanations.filter(exp_type='Disciplinary').count(),
                },
            }

            if emp_id:
                return JsonResponse(explanation_summary)
        return explanation_summary

    except Exception as e:
        logger.error(f"Error in get_employee_explanation_data function: {e}")
        return {'error': str(e)}


def getZoneRetirementList(zone, request):
    try:
        # Group retirements by zone and count them
        if is_admin(request.user):
            retirement = DispositionList.objects.annotate(
                year=Substr('Date_of_Retirement', 7, 4),
                month=Substr('Date_of_Retirement', 4, 2)
            ).filter(
                year='2024',
                month__in=['08', '09', '10', '11', '12'],
            ).order_by('ZONE')

        if is_zone_admin(request.user):
            retirement = DispositionList.objects.annotate(
                year=Substr('Date_of_Retirement', 7, 4),
                month=Substr('Date_of_Retirement', 4, 2)
            ).filter(
                year='2024',
                month__in=['08', '09', '10', '11', '12'],
                ZONE=zone
            ).order_by('ZONE')

        zone_counts = defaultdict(int)
        for item in retirement.values('ZONE'):
            zone_counts[item['ZONE']] += 1

        return zone_counts
    except Exception as e:
        return str(e)

# <............ Graph Functions Starts Ends Here ...............>