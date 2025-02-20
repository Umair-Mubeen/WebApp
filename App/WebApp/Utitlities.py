import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta, date
from urllib import request

from dateutil.relativedelta import relativedelta  # More accurate for months
from django.db.models import Value, Case, When, CharField, F
from django.db.models.functions import Replace, Substr, Concat, Cast, ExtractYear
from django.db.models.fields import DateField, IntegerField

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count, F, When, BooleanField, Value, Func, CharField
from django.db.models.functions import Substr, Trim, Concat
from django.db.models import Case, When, BooleanField, F
from datetime import datetime, timedelta
from django.db.models.functions import Concat, Replace
from django.http import JsonResponse, HttpResponse

from .models import DispositionList, TransferPosting, LeaveApplication, Explanation

logger = logging.getLogger(__name__)


def fetchAllDispositionList(request):
    try:
        # Determine the base queryset based on user role
        if is_zone_admin(request.user):
            result = DispositionList.objects.filter(ZONE=request.user.userType, status=1)
        elif is_admin(request.user):
            print("admin")
            result = (DispositionList.objects.filter(status=1).annotate(bps_as_int=Cast('BPS', IntegerField()))
                      .order_by('-bps_as_int')
                      )
        else:
            result = DispositionList.objects.none()  # No results for other roles

        return result, None

    except Exception as e:
        return None, str(e)


def DesignationWiseList(zone, request):
    try:
        # Annotate designations after trimming whitespace and count occurrences
        if is_admin(request.user):
            results = DispositionList.objects.filter(status=1) \
                .annotate(trimmed_designation=Trim('Designation')) \
                .values('trimmed_designation') \
                .annotate(total=Count('trimmed_designation'))
        if is_zone_admin(request.user):
            results = DispositionList.objects.filter(status=1, ZONE=zone). \
                annotate(trimmed_designation=Trim('Designation')).values('trimmed_designation') \
                .annotate(total=Count('trimmed_designation'))
        return results
    except Exception as e:
        return str(e)


def getRetirementList(zone, request):
    try:
        current_date = datetime.now().date()
        next_year_date = current_date + relativedelta(months=12)
        two_months_ago = current_date - relativedelta(months=3)

        # Convert dates to 'YYYY-MM-DD' format for comparison
        next_year_date_str = next_year_date.strftime('%Y-%m-%d')
        two_months_ago_str = two_months_ago.strftime('%Y-%m-%d')

        if is_admin(request.user):
            retirement = DispositionList.objects.annotate(
                # Standardize the Date_of_Retirement format by replacing '.' with '-'
                standardized_retirement=Replace('Date_of_Retirement', Value('.'), Value('-')),
                # Extract day, month, and year from standardized date
                day=Substr('standardized_retirement', 1, 2),
                month=Substr('standardized_retirement', 4, 2),
                year=Substr('standardized_retirement', 7, 4),
                # Reconstruct Date_of_Retirement in 'YYYY-MM-DD' format
                retirement_date_str=Concat('year', Value('-'), 'month', Value('-'), 'day', output_field=CharField()),
                # Cast the retirement_date_str into a DateField
                retirement_date=Cast('retirement_date_str', output_field=DateField()),
                # Annotate 'retired' as 'Yes' if retirement_date is before current date and within the past 2 months
                emp_retired=Case(
                    When(retirement_date__lte=two_months_ago_str, then=Value('Yes')),
                    default=Value(''),
                    output_field=CharField()
                )
            ).filter(
                # Include employees retired from two months ago to the next 12 months
                retirement_date__gte=two_months_ago,
                retirement_date__lte=next_year_date,
                status=1
            ).order_by('retirement_date')
        if is_zone_admin(request.user):
            retirement = DispositionList.objects.annotate(
                standardized_retirement=Replace('Date_of_Retirement', Value('.'), Value('-')),
                day=Substr('standardized_retirement', 1, 2),
                month=Substr('standardized_retirement', 4, 2),
                year=Substr('standardized_retirement', 7, 4),
                retirement_date_str=Concat('year', Value('-'), 'month', Value('-'), 'day', output_field=CharField()),
                retirement_date=Cast('retirement_date_str', output_field=DateField()),
                emp_retired=Case(
                    When(retirement_date__lte=two_months_ago, then=Value('Yes')),
                    default=Value('No'),
                    output_field=CharField()
                )
            ).filter(
                retirement_date__gte=two_months_ago,
                retirement_date__lte=next_year_date,
                ZONE=request.user.userType,
                status=1
            ).order_by('retirement_date')

        # Return relevant fields for employees to be retired
        employee_to_be_retired = retirement.values(
            'Name', 'CNIC_No', 'Designation', 'BPS', 'ZONE', 'Date_of_Birth',
            'Date_of_Entry_into_Govt_Service', 'Date_of_Retirement', 'month', 'emp_retired'
        )

        # Pagination
        paginator = Paginator(employee_to_be_retired, 10)  # Show 10 records per page
        page = request.GET.get('page')

        try:
            paginated_data = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page
            paginated_data = paginator.page(1)
        except EmptyPage:
            # If page is out of range, deliver last page of results
            paginated_data = paginator.page(paginator.num_pages)

        return paginated_data
    except Exception as e:
        print(str(e))


def getZoneWiseOfficialsList(zone):
    try:
        # Trim fields and count officials by zone and designation
        results = DispositionList.objects.filter(status=1, ZONE__in=[zone]) \
            .annotate(zone=Trim(F('ZONE')), designation=Trim(F('Designation'))) \
            .values("zone", "designation").annotate(total=Count('id'))
        results_list = list(results)
        results_json = json.dumps(results_list, indent=4)
        print(results_json)
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
        zones = ['CCIR', 'IP/TFD/HRM', 'Zone-I', 'Zone-II', 'Zone-III', 'Zone-IV', 'Zone-V', 'Refund Zone']

        for i, zone in enumerate(zones):
            datasets.append({'label': zone, 'data': [pivoted_data[designation].get(zone, 0) for designation in labels]})

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
        base_queryset = DispositionList.objects.filter(status=1).values('ZONE', 'Designation', 'BPS').annotate(
            total=Count('id'))

        # Aggregate data
        aggregated_data = defaultdict(lambda: defaultdict(int))
        total_zones = defaultdict(int)  # For storing totals per zone

        for item in base_queryset:
            designation = item['Designation']
            bps = item['BPS']
            zone = item['ZONE']
            total = item['total']

            # Add to aggregated data
            aggregated_data[(designation, bps)][zone] += total

            # Add to total_zones for respective zone
            total_zones[zone] += total

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
                'CSO': zone_data.get('CSO', 0),
                'AdPool': zone_data.get('Admin Pool', 0),
                'total_sum': sum(zone_data.values()),

            }
            for (designation, bps), zone_data in aggregated_data.items()
        ]
        # Append totals row
        total_row = {
            'Designation': 'Total',
            'BPS': '',
            'CCIR': total_zones.get('CCIR', 0),
            'Zone_I': total_zones.get('Zone-I', 0),
            'Zone_II': total_zones.get('Zone-II', 0),
            'Zone_III': total_zones.get('Zone-III', 0),
            'Zone_IV': total_zones.get('Zone-IV', 0),
            'Zone_V': total_zones.get('Zone-V', 0),
            'Refund_Zone': total_zones.get('Refund Zone', 0),
            'IP_TFD_HRM': total_zones.get('IP/TFD/HRM', 0),
            'CSO': total_zones.get('CSO', 0),
            'AdPool': total_zones.get('Admin Pool', 0),
            'total_sum': sum(total_zones.values()),
            'row_color': 'table-info'
        }

        final_data.append(total_row)

        return final_data

    except Exception as e:
        return str(e)


def getAllEmpTransferPosting(userType, zoneType):
    try:
        filters = {}
        if userType == 2:  # Employee
            filters['zone_type'] = zoneType
        filters['employee__status'] = 1  # Add the status filter from the related employee table

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
        ).order_by('-chief_transfer_date')

        return distinct_transfers

    except Exception as e:
        logger.error(f"Error in getAllEmpTransferPosting: {e}")
        return []  # Return an empty list on error


def getAllEmpLeaveApplication(userType, zoneType):
    try:
        filters = {}
        if userType == 2:  # Employee
            filters['zone_type'] = zoneType
        filters['employee__status'] = 1  # Add the status filter from the related employee table

        leave_application = LeaveApplication.objects.select_related('employee').filter(
            **filters).values(
            'employee__id',
            'employee__Name',
            'employee__Designation',
            'employee__BPS',
            'id',
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


def getAllEmpLeaveExplanation(userType, zoneType):
    try:
        filters = {}
        if userType == 2:  # Employee
            filters['zone_type'] = zoneType

        employee_explanation = Explanation.objects.select_related('employee').filter(
            **filters).values(
            'employee__id',
            'employee__Name',
            'employee__Designation',
            'employee__BPS',
            'id',
            'exp_type',
            'exp_issue_date',
            'exp_reply_date',
            'exp_document',
            'zone_type'
        )
        return employee_explanation
    except Exception as e:
        return str(e)


def is_admin(user):
    return user.is_superuser == 1


def is_zone_admin(user):
    return user.is_superuser == 2


def calculate_tax(income, tax_brackets, apply_surcharge):
    try:
        surcharge_threshold = 10000000
        surcharge_rate = 0.10
        for (lower, upper), (rate, base_tax) in tax_brackets.items():
            if lower <= income <= upper:
                month = 0
                if rate == 0:
                    tax = 0
                else:
                    amount_exceeding = income - lower
                    tax_on_exceeding = amount_exceeding * rate

                    if lower == 600001 and upper == 1200000:
                        tax = round(tax_on_exceeding)  # No base tax added
                        month = round(tax / 12)
                    elif lower == 600001 and upper == 800000:
                        tax = round(tax_on_exceeding)  # No base tax added
                        month = tax / 12

                    else:
                        tax = round(base_tax + tax_on_exceeding)
                        month = round(tax / 12)
                total_tax_with_surcharge = 0
                surcharge = 0
                if apply_surcharge and income > surcharge_threshold:
                    surcharge = round(tax * surcharge_rate)
                    total_tax_with_surcharge = round(tax + surcharge)
                    print('surcharge =>', surcharge)
                    month = round(total_tax_with_surcharge / 12)

                return {
                    'income': income,
                    'lower': lower,
                    'upper': upper,
                    'base_tax': base_tax,
                    'amount_exceeding': amount_exceeding if rate != 0 else 0,
                    'rate': rate * 100,
                    'tax_on_exceeding': round(tax_on_exceeding) if rate != 0 else 0,
                    'total_tax': tax,
                    'per_month': month,
                    'total_tax_with_surcharge': total_tax_with_surcharge,
                    'surcharge': surcharge
                }
        return None
    except Exception as e:
        print(str(e))


def getAllBoardTransferPosting(userType, zoneType):
    try:
        filters = {}
        if userType == 2:  # Employee
            filters['zone_type'] = zoneType
        filters['employee__status'] = 2  # Add the status filter from the related employee table

        distinct_transfers = TransferPosting.objects.select_related('employee').filter(
            **filters
        ).values(
            'employee__id',
            'employee__Name',
            'employee__Designation',
            'employee__BPS',
            'employee__ZONE',
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
        ).order_by('-chief_transfer_date')

        return distinct_transfers

    except Exception as e:
        logger.error(f"Error in getAllEmpTransferPosting: {e}")
        return []  # Return an empty list on error
