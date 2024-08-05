from collections import defaultdict
from django.http import HttpResponse
from django.core.paginator import Paginator
from .models import DispositionList
from django.db.models.functions import Substr
from django.db.models import Count
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


def getDispositionList():
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
