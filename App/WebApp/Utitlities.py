import json
import logging
from collections import defaultdict
from django.core.paginator import Paginator
from django.db.models import Count, F, When, BooleanField
from django.db.models.functions import Substr, Trim
from django.db.models import Case, When, BooleanField, F

from .models import DispositionList, TransferPosting, LeaveApplication
logger = logging.getLogger(__name__)


def fetchAllDispositionList(request):
    try:
        # Paginate results
        if request.user.is_superuser == 2:
            result = DispositionList.objects.filter(ZONE=request.user.userType)
        else:
            result = DispositionList.objects.all()

        paginator = Paginator(result, 10)
        page = request.GET.get('page')
        disposition_result = paginator.get_page(page)
        return disposition_result, None
    except Exception as e:
        return None, str(e)


def DesignationWiseList(zone, request):
    try:
        # Annotate designations after trimming whitespace and count occurrences
        if request.user.userType == 'admin':
            results = DispositionList.objects.annotate(trimmed_designation=Trim('Designation')) \
                .values('trimmed_designation') \
                .annotate(total=Count('trimmed_designation'))
        else:
            results = DispositionList.objects.filter(ZONE=zone). \
                annotate(trimmed_designation=Trim('Designation')).values('trimmed_designation') \
                .annotate(total=Count('trimmed_designation'))
        return results
    except Exception as e:
        return str(e)


def getRetirementList(zone, request):
    try:
        # Extract year and month, filter for 2024 retirees, and order by month
        if request.user.userType == 'admin':

            retirement = DispositionList.objects.annotate(
                year=Substr('Date_of_Retirement', 7, 4),
                month=Substr('Date_of_Retirement', 4, 2)
            ).filter(
                year='2024',
                month__in=['08', '09', '10', '11', '12'],
            ).order_by('month')
        else:
            retirement = DispositionList.objects.annotate(
                year=Substr('Date_of_Retirement', 7, 4),
                month=Substr('Date_of_Retirement', 4, 2)
            ).filter(
                year='2024',
                month__in=['08', '09', '10', '11', '12'],
                ZONE=zone
            ).order_by('month')

        # Return relevant fields for employees to be retired
        employee_to_be_retired = retirement.values(
            'Name', 'CNIC_No', 'Designation', 'BPS', 'ZONE', 'Date_of_Birth',
            'Date_of_Entry_into_Govt_Service', 'Date_of_Retirement', 'month'
        )
        return employee_to_be_retired
    except Exception as e:
        return str(e)


def getZoneRetirementList(zone, request):
    try:
        # Group retirements by zone and count them
        if request.user.userType == 'admin':
            retirement = DispositionList.objects.annotate(
                year=Substr('Date_of_Retirement', 7, 4),
                month=Substr('Date_of_Retirement', 4, 2)
            ).filter(
                year='2024',
                month__in=['08', '09', '10', '11', '12'],
            ).order_by('ZONE')

        else:
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


def getZoneWiseOfficialsList(zone):
    try:
        # Trim fields and count officials by zone and designation
        results = DispositionList.objects.filter(ZONE__in=[zone]) \
            .annotate(zone=Trim(F('ZONE')), designation=Trim(F('Designation'))) \
            .values("zone", "designation").annotate(total=Count('id'))
        results_list = list(results)
        results_json = json.dumps(results_list, indent=4)

        return results_json
    except Exception as e:
        return str(e)


def ZoneWiseStrength():
    try:
        # Filter by zones and aggregate by zone and designation
        data = DispositionList.objects.filter(
            ZONE__in=['Zone-I', 'Zone-II', 'Zone-III', 'Zone-IV', 'Zone-V', 'CCIR', 'Refund Zone', 'IP/TFD/HRM']
        ).values('ZONE', 'Designation').annotate(total=Count('id')).order_by('ZONE')

        zones = sorted(set(d['ZONE'] for d in data))
        designations = sorted(set(d['Designation'] for d in data))

        # Initialize counts dictionary with zeros
        counts = {zone: {designation: 0 for designation in designations} for zone in zones}

        # Populate the counts dictionary
        for entry in data:
            counts[entry['ZONE']][entry['Designation']] = entry['total']

        context = {
            'zones': zones,
            'designations': designations,
            'counts': counts,
        }
        return context
    except Exception as e:
        return str(e)


def ZoneDesignationWiseComparison():
    try:
        # Aggregate counts by zone and designation
        aggregated_data = DispositionList.objects.values('ZONE', 'Designation') \
            .annotate(total=Count('id')).values('Designation', 'ZONE', 'total')

        # Pivot the data to organize it by zones
        pivoted_data = defaultdict(lambda: defaultdict(int))
        for entry in aggregated_data:
            designation = entry['Designation']
            zone = entry['ZONE']
            pivoted_data[designation][zone] = entry['total']

        # Prepare data for Chart.js
        labels = list(pivoted_data.keys())
        datasets = []
        colors = ['rgba(255, 99, 132, 0.2)', 'rgba(54, 162, 235, 0.2)', 'rgba(75, 192, 192, 0.2)',
                  'rgba(153, 102, 255, 0.2)', 'rgba(255, 159, 64, 0.2)', 'rgba(255, 99, 71, 0.2)']
        zones = ['CCIR', 'IP/TFD/HRM', 'Zone-I', 'Zone-II', 'Zone-III', 'Zone-IV', 'Zone-V', 'Refund Zone']

        for i, zone in enumerate(zones):
            datasets.append({
                'label': zone,
                'data': [pivoted_data[designation].get(zone, 0) for designation in labels],
                'backgroundColor': colors[i % len(colors)],
                'borderColor': colors[i % len(colors)].replace('0.2', '1'),
                'borderWidth': 1
            })

        data_json = json.dumps({'labels': labels, 'datasets': datasets})
        return {'data_json': data_json}
    except Exception as e:
        return str(e)


#
# def StrengthComparison():
#     try:
#         # Aggregate counts by zone, designation, and BPS
#         base_queryset = DispositionList.objects.values('ZONE', 'Designation', 'BPS').annotate(total=Count('id'))
#
#         aggregated_data = defaultdict(lambda: defaultdict(int))
#         for item in base_queryset:
#             designation = item['Designation']
#             bps = item['BPS']
#             zone = item['ZONE']
#             aggregated_data[(designation, bps)][zone] = item['total']
#
#         # Convert aggregated data to a list
#         final_data = [
#             {
#                 'Designation': designation,
#                 'BPS': bps,
#                 'Zone_I': zone_data.get('Zone-I', 0),
#                 'Zone_II': zone_data.get('Zone-II', 0),
#                 'Zone_III': zone_data.get('Zone-III', 0),
#                 'Zone_IV': zone_data.get('Zone-IV', 0),
#                 'Zone_V': zone_data.get('Zone-V', 0),
#                 'CCIR': zone_data.get('CCIR', 0),
#                 'Refund_Zone': zone_data.get('Refund Zone', 0),
#                 'IP_TFD_HRM': zone_data.get('IP/TFD/HRM', 0),
#                 'total_sum': sum(zone_data.values()),
#             }
#             for (designation, bps), zone_data in aggregated_data.items()
#         ]
#
#         return final_data
#     except Exception as e:
#         return str(e)

def StrengthComparison(userType, user_zone=None):
    try:
        # Base queryset with aggregation
        base_queryset = DispositionList.objects.values('ZONE', 'Designation', 'BPS').annotate(total=Count('id'))

        # Filter based on userType
        if userType == 2:  # Employee
            if user_zone:  # Ensure user_zone is provided
                base_queryset = base_queryset.filter(ZONE=user_zone)
            else:
                return "Error: Zone information is missing for the employee."

        # Aggregate data
        aggregated_data = defaultdict(lambda: defaultdict(int))
        for item in base_queryset:
            designation = item['Designation']
            bps = item['BPS']
            zone = item['ZONE']
            aggregated_data[(designation, bps)][zone] = item['total']

        # Convert aggregated data to a list
        final_data = [
            {
                'Designation': designation,
                'BPS': bps,
                'Zone_I': zone_data.get('Zone-I', 0),
                'Zone_II': zone_data.get('Zone-II', 0),
                'Zone_III': zone_data.get('Zone-III', 0),
                'Zone_IV': zone_data.get('Zone-IV', 0),
                'Zone_V': zone_data.get('Zone-V', 0),
                'CCIR': zone_data.get('CCIR', 0),
                'Refund_Zone': zone_data.get('Refund Zone', 0),
                'IP_TFD_HRM': zone_data.get('IP/TFD/HRM', 0),
                'total_sum': sum(zone_data.values()),
            }
            for (designation, bps), zone_data in aggregated_data.items()
        ]

        print(final_data)
        return final_data

    except Exception as e:
        return str(e)


def getAllEmpTransferPosting(userType, zoneType):
    try:
        filters = {}
        if userType == 2:  # Employee
            filters['zone_type'] = zoneType

        distinct_transfers = TransferPosting.objects.select_related('employee').filter(
            **filters
        ).values(
            'employee__id',
            'employee__Name',
            'employee__Designation',
            'employee__BPS',
            'id',
            'old_zone',
            'new_zone',
            'old_unit',
            'new_unit',
            'chief_order_number',
            'chief_transfer_date',
            'chief_transfer_document',
            'zone_range',
            'zone_transfer_document',
            'zone_order_number',
            'zone_transfer_date',
            'zone_type'
        ).annotate(
            zone_changed=Case(
                When(old_zone=F('new_zone'), then=False),
                default=True,
                output_field=BooleanField()
            )
        )

        return distinct_transfers

    except Exception as e:
        logger.error(f"Error in getAllEmpTransferPosting: {e}")
        return []  # Return an empty list on error


def getAllEmpLeaveApplication():
    try:

        # Use select_related to optimize foreign key access and avoid additional queries
        leave_application = LeaveApplication.objects.select_related('employee').values(
            'employee__id',
            'employee__Name',
            'employee__Designation',
            'employee__BPS',
            'leave_type',
            'leave_start_date',
            'leave_end_date',
            'days_granted',
            'reason',
            'leave_document'
        )
        return leave_application
    except Exception as e:
        return str(e)
