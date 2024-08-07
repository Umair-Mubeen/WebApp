from collections import defaultdict
from django.http import HttpResponse
from django.core.paginator import Paginator
from .models import DispositionList
from django.db.models.functions import Substr
from django.db.models import Count, F, Case, Value, When
from django.db.models.functions import Trim


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
