import json
from collections import defaultdict
from django.core.paginator import Paginator
from .models import DispositionList, TransferPosting
from django.db.models.functions import Substr
from django.db.models.functions import Trim
from django.db.models import Count, Sum, Case, When
from django.db.models import Count, Sum, Case, When, F, Value
from django.db.models.functions import Coalesce


def fetchAllDispositionList(request):
    try:
        result = DispositionList.objects.all()
        paginator = Paginator(result, 20)
        page = request.GET.get('page')
        print("Page", page)
        DispositionResult = paginator.get_page(page)
        print("Disposition List ", DispositionResult)
        return DispositionResult, None

    except Exception as e:
        return None, str(e)


def DesignationWiseList():
    try:
        results = DispositionList.objects.annotate(trimmed_designation=Trim('Designation')).values(
            'trimmed_designation').annotate(total=Count('trimmed_designation'))
        return results
    except Exception as e:
        return str(e)


def getRetirementList():
    try:
        retirement = DispositionList.objects.annotate(
            year=Substr('Date_of_Retirement', 7, 4),
            month=Substr('Date_of_Retirement', 4, 2)
        ).filter(
            year='2024',
            month__in=['08', '09', '10', '11', '12']
        ).order_by('month')
        data = retirement.values('ZONE', 'Date_of_Retirement')
        # getZoneRetirementList(data)

        employee_to_be_retired = retirement.values('Name', 'CNIC_No', 'Designation', 'BPS', 'ZONE', 'Date_of_Birth',
                                                   'Date_of_Entry_into_Govt_Service', 'Date_of_Retirement', 'month')
        return employee_to_be_retired
    except Exception as e:
        return str(e)


def getZoneRetirementList():
    try:
        retirement = DispositionList.objects.annotate(
            year=Substr('Date_of_Retirement', 7, 4),
            month=Substr('Date_of_Retirement', 4, 2)
        ).filter(
            year='2024',
            month__in=['08', '09', '10', '11', '12']
        ).order_by('ZONE')
        data = retirement.values('ZONE', 'Date_of_Retirement')

        # Prepare data for Chart.js
        zone_counts = defaultdict(int)
        for item in data:
            zone_counts[item['ZONE']] += 1

        return zone_counts

    except Exception as e:
        return str(e)


def getZoneWiseOfficialsList(Zone):
    try:
        results = DispositionList.objects.filter(ZONE__in=[Zone]) \
            .annotate(zone=Trim(F('ZONE')), designation=Trim(F('Designation'))).values("zone", "designation").annotate(
            total=Count('id'))
        return results

    except Exception as e:
        print(str(e))


def ZoneWiseStrength():
    try:
        data = (DispositionList.objects
                .filter(ZONE__in=['Zone-I', 'Zone-II', 'Zone-III', 'Zone-IV', 'Zone-V','CCIR','Refund Zone','IP/TFD/HRM'])
                .values('ZONE', 'Designation')
                .annotate(total=Count('id'))
                .order_by('ZONE'))

        # Prepare data for the template
        zones = sorted(set(d['ZONE'] for d in data))
        designations = sorted(set(d['Designation'] for d in data))

        counts = {zone: {designation: 0 for designation in designations} for zone in zones}

        for entry in data:
            counts[entry['ZONE']][entry['Designation']] = entry['total']

        context = {
            'zones': zones,
            'designations': designations,
            'counts': counts,
            'results': '',
            'zone': ''
        }
        return context
    except Exception as e:
        return str(e)


def ZoneDesignationWiseComparison():
    try:
        aggregated_data = (DispositionList.objects
                           .values('ZONE', 'Designation')
                           .annotate(total=Count('id'))
                           .values('Designation', 'ZONE', 'total')
                           )

        # Pivot the data to get totals by zone
        pivoted_data = {}
        for entry in aggregated_data:
            designation = entry['Designation']
            zone = entry['ZONE']
            total = entry['total']

            if designation not in pivoted_data:
                pivoted_data[designation] = {'Zone-I': 0, 'Zone-II': 0, 'Zone-III': 0, 'Zone-IV': 0, 'Zone-V': 0,
                                             'Refund Zone': 0}

            pivoted_data[designation][zone] = total

        # Calculate total across all zones
        for designation, zones in pivoted_data.items():
            total = sum(zones.values())
            zones['Total Across All Zones'] = total
        data_for_graph = {
            'labels': list(pivoted_data.keys()),
            'datasets': [
                {
                    'label': 'CCIR',
                    'data': [zones.get('CCIR', 0) for zones in pivoted_data.values()],
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'IP/TFD/HRM',
                    'data': [zones.get('IP/TFD/HRM', 0) for zones in pivoted_data.values()],
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'borderWidth': 1
                },

                {
                    'label': 'Zone-I',
                    'data': [zones.get('Zone-I', 0) for zones in pivoted_data.values()],
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'Zone-II',
                    'data': [zones.get('Zone-II', 0) for zones in pivoted_data.values()],
                    'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                    'borderColor': 'rgba(54, 162, 235, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'Zone-III',
                    'data': [zones.get('Zone-III', 0) for zones in pivoted_data.values()],
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'borderColor': 'rgba(75, 192, 192, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'Zone-IV',
                    'data': [zones.get('Zone-IV', 0) for zones in pivoted_data.values()],
                    'backgroundColor': 'rgba(153, 102, 255, 0.2)',
                    'borderColor': 'rgba(153, 102, 255, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'Zone-V',
                    'data': [zones.get('Zone-V', 0) for zones in pivoted_data.values()],
                    'backgroundColor': 'rgba(255, 159, 64, 0.2)',
                    'borderColor': 'rgba(255, 159, 64, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'Refund Zone',
                    'data': [zones.get('Refund Zone', 0) for zones in pivoted_data.values()],
                    'backgroundColor': 'rgba(255, 99, 71, 0.2)',
                    'borderColor': 'rgba(255, 99, 71, 1)',
                    'borderWidth': 1
                },
            ]
        }
        print(data_for_graph)

        # Convert to JSON and pass to context
        data_json = json.dumps(data_for_graph)
        context = {
            'data_json': data_json,
        }
        return context
    except Exception as e:
        return str(e)


def StrengthComparison():
    try:

        base_queryset = DispositionList.objects.values('ZONE', 'Designation', 'BPS').annotate(total=Count('id'))
        aggregated_data = defaultdict(lambda: defaultdict(int))

        # Iterate over the base queryset to fill the aggregated data
        for item in base_queryset:
            designation = item['Designation']
            bps = item['BPS']
            zone = item['ZONE']
            total = item['total']

            # Aggregate the totals per zone
            aggregated_data[(designation, bps)][zone] += total
            # Also aggregate the total sum across all zones
            aggregated_data[(designation, bps)]['total_sum'] += total

        # Convert aggregated data to a list for easier handling in templates
        final_data = []
        for (designation, bps), zone_data in aggregated_data.items():
            final_data.append({

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
                'Zone_I_Refund Zone': zone_data.get('Zone-I / (Refund Zone)', 0),
                'Zone-V_CCIR': zone_data.get('Zone-V / CCIR', 0),
                'total_sum': zone_data['total_sum'],
            })

        return final_data
    except Exception as e:
        print(str(e))
        return str(e)


def getAllEmpTransferPosting():
    try:
        # Query to get distinct records
        distinct_transfers = TransferPosting.objects.select_related('employee_id').values(
            'employee_id__id',
            'employee_id__Name',
            'employee_id__Designation',
            'old_unit',
            'new_unit',
            'transfer_date',
            'transfer_document',
            'order_number'
        )

        return distinct_transfers
        #print(distinct_transfers)
    except Exception as e:
        return str(e)