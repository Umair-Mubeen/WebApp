import logging
from collections import defaultdict
from datetime import date, datetime

from django.db.models import Count, Sum, Q
from django.db.models.functions import Substr, ExtractYear
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
            zone_transfer_data = (TransferPosting.objects.values('zone_type').annotate(total_transfers=Count('id')).
            order_by('zone_type'))

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
            zone_transfer_data = (TransferPosting.objects.filter(zone_type=request.user.userType).
                                  values('zone_type','new_unit').annotate(total_transfers=Count('id')).order_by('zone_type', 'new_unit'))

            # Prepare data for Chart.js
            zones = list(set(entry['zone_type'] for entry in zone_transfer_data))  # Unique zone names
            #units = list(set(entry['new_unit'] for entry in zone_transfer_data))  # Unique units
            units = list(set(entry['new_unit'] for entry in zone_transfer_data if entry['new_unit'] is not None))  # Unique units

            unit_counts = {unit: 0 for unit in units}

            # Aggregate the total number of transfers for each unit
            for entry in zone_transfer_data:
                unit = entry['new_unit']
                unit_counts[unit] = entry['total_transfers']

        # Return the context to the template
        #units = 0 if units is None else units
        #0 if units is None else None
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
        # Group retirements by zone and count them from November 2024 to December 2025
        if is_admin(request.user):
            retirement = DispositionList.objects.annotate(
                year=Substr('Date_of_Retirement', 7, 4),
                month=Substr('Date_of_Retirement', 4, 2)
            ).filter(
                Q(year='2024', month__gte='11') | Q(year__in=[str(y) for y in range(2025, 2034)]) | Q(year='2034',
                                                                                                      month__lte='12')
            ).order_by('ZONE')

        if is_zone_admin(request.user):
            retirement = DispositionList.objects.annotate(
                year=Substr('Date_of_Retirement', 7, 4),
                month=Substr('Date_of_Retirement', 4, 2)
            ).filter(
                Q(year='2024', month__gte='11') | Q(year__in=[str(y) for y in range(2025, 2034)]) | Q(year='2034',
                                                                                                      month__lte='12'),
            ZONE=zone
            ).order_by('ZONE')

        zone_counts = defaultdict(int)
        for item in retirement.values('ZONE'):
            zone_counts[item['ZONE']] += 1

        print(zone_counts)
        return zone_counts
    except Exception as e:
        return str(e)


def get_age_range_count(request):
    try:
        current_year = date.today().year
        # Get all employees' dates of birth
        if is_admin(request.user):
            employees = DispositionList.objects.values_list('Date_of_Birth', flat=True).filter(status=1)
        if is_zone_admin(request.user):
            employees = DispositionList.objects.values_list('Date_of_Birth', flat=True).filter(ZONE=request.user.userType,status=1)
        # Dictionary to count people in each age range
        age_ranges = {'18-30': 0,'31-40': 0,'41-50': 0,'51-60': 0}

        # Loop through employees and calculate age
        for dob in employees:
            try:
                if dob:  # Check if Date_of_Birth is not null
                    # Calculate the age
                    dob_cleaned = dob.strip()  # Remove any leading/trailing spaces
                    dob_date = datetime.strptime(dob_cleaned, '%d.%m.%Y').date()

                    # Calculate the age
                    age = current_year - dob_date.year

                    # Increment the appropriate age range
                    if 18 <= age <= 30:
                        age_ranges['18-30'] += 1
                    elif 31 <= age <= 40:
                        age_ranges['31-40'] += 1
                    elif 41 <= age <= 50:
                        age_ranges['41-50'] += 1
                    elif 51 <= age <= 60:
                        age_ranges['51-60'] += 1
            except ValueError:
                print(f"Error parsing Date_of_Birth: {dob}")
                break
        # Return the age range data as JSON
        print(age_ranges)
        return age_ranges

    except Exception as e:
        print(str(e))


def get_zone_age_range_chart(request):
    try:
        # Define the zones (assuming you have a zone field in the DispositionList model)
        zones = ['Refund Zone', 'CSO', 'CCIR', 'Zone-I', 'Zone-II', 'Zone-III', 'Zone-IV', 'Zone-V']
        # Initialize a dictionary to hold counts for each age range and zone
        zone_age_ranges = {
            '18-30': {zone: 0 for zone in zones},
            '31-40': {zone: 0 for zone in zones},
            '41-50': {zone: 0 for zone in zones},
            '51-60': {zone: 0 for zone in zones}
        }

        # Count employees for each age range and zone
        if is_admin(request.user):
            for zone in zones:
                zone_age_ranges['18-30'][zone] = DispositionList.objects.filter(Q(emp_age__gte=18) & Q(emp_age__lte=30), ZONE=zone,status=1).count()
                zone_age_ranges['31-40'][zone] = DispositionList.objects.filter(Q(emp_age__gte=31) & Q(emp_age__lte=40), ZONE=zone,status=1).count()
                zone_age_ranges['41-50'][zone] = DispositionList.objects.filter(Q(emp_age__gte=41) & Q(emp_age__lte=50), ZONE=zone,status=1).count()
                zone_age_ranges['51-60'][zone] = DispositionList.objects.filter(Q(emp_age__gte=51) & Q(emp_age__lte=60), ZONE=zone,status=1).count()
            context = {'zone_age_ranges': zone_age_ranges}

        if is_zone_admin(request.user):
            zone = request.user.userType
            zone_age_ranges['18-30'] = DispositionList.objects.filter(Q(emp_age__gte=18) & Q(emp_age__lte=30),ZONE=zone,status=1).count()
            zone_age_ranges['31-40'] = DispositionList.objects.filter(Q(emp_age__gte=31) & Q(emp_age__lte=40),ZONE=zone,status=1).count()
            zone_age_ranges['41-50'] = DispositionList.objects.filter(Q(emp_age__gte=41) & Q(emp_age__lte=50),ZONE=zone,status=1).count()
            zone_age_ranges['51-60'] = DispositionList.objects.filter(Q(emp_age__gte=51) & Q(emp_age__lte=60),ZONE=zone,status=1).count()
            context = {'zone_age_ranges':zone_age_ranges}

            print(context)
        return context
    except Exception as e:
        print(str("Error", str(e)))


def get_retirement_year_count(request):
    try:
        yearList = [2024, 2025, 2026, 2027, 2028, 2029, 2030]
        current_year = date.today().year
        # Get all employees' dates of birth
        if is_admin(request.user):
            employees = DispositionList.objects.values_list('Date_of_Retirement', flat=True).filter(status=1)
        if is_zone_admin(request.user):
            employees = DispositionList.objects.values_list('Date_of_Retirement', flat=True).filter(ZONE=request.user.userType,status=1)

        # Dictionary to count people in each age range
        year_ranges = {
            '2025': 0,
            '2026': 0,
            '2027': 0,
            '2028': 0,
            '2029': 0,
            '2030': 0,
            '2031': 0,
            '2032': 0,
            '2033': 0,
            '2034': 0,

        }

        # Loop through employees and calculate retirement year

        for retirement in employees:
            try:
                if retirement:  # Check if Date_of_Retirement is not null
                    # Calculate the age
                    dob_cleaned = retirement.strip()  # Remove any leading/trailing spaces
                    retirement_date = datetime.strptime(dob_cleaned, '%d.%m.%Y').date()
                    # Calculate the year
                    year = retirement_date.year
                    if year == 2024:
                        year_ranges['2024'] += 1
                    if year == 2025:
                        year_ranges['2025'] += 1
                    if year == 2026:
                        year_ranges['2026'] += 1
                    if year == 2027:
                        year_ranges['2027'] += 1
                    elif year == 2028:
                        year_ranges['2028'] += 1
                    if year == 2029:
                        year_ranges['2029'] += 1
                    if year == 2030:
                        year_ranges['2030'] += 1
                    if year == 2031:
                        year_ranges['2031'] += 1
                    if year == 2032:
                        year_ranges['2032'] += 1
                    if year == 2033:
                        year_ranges['2033'] += 1
                    if year == 2034:
                        year_ranges['2034'] += 1
            except ValueError:
                print(f"Error parsing Date_of_Retirement: {retirement}")
                break
        # Return the age range data as JSON
        return year_ranges

    except Exception as e:
        print(str(e))


def get_zone_wise_count(request):
    try:
        # Dictionary to count the number of dispositions in each zone
        zone_counts = defaultdict(int)

        # Query all dispositions from the database and order by ZONE
        employees = DispositionList.objects.filter(status=1).order_by('ZONE')

        # Loop through employees and count them by zone
        for employee in employees:
            zone = employee.ZONE  # Get the zone from the employee record
            if zone:  # Check if the zone is not null
                zone_counts[zone] += 1  # Increment the count for the corresponding zone

        # Convert defaultdict to a regular dict
        zone_counts = dict(zone_counts)

        # Sort the zone counts by total count in descending order
        sorted_zone_counts = dict(sorted(zone_counts.items(), key=lambda item: item[1]))

        # Return the sorted zone counts as JSON or render it in a template
        return {'zone_counts': sorted_zone_counts}

    except Exception as e:
        print(str(e))
        # Handle exception (e.g., return an error response)
        return {'error': str(e)}