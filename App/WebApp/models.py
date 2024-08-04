from django.db import models


# Create your models here.
class DispositionList(models.Model):
    Name = models.CharField(max_length=255, null=True, blank=True)
    Designation = models.CharField(max_length=255, null=True, blank=True)
    BPS = models.CharField(max_length=255, null=True, blank=True)
    ZONE = models.CharField(max_length=255, null=True, blank=True)
    Date_of_Birth = models.CharField(max_length=255, null=True, blank=True)
    CNIC_No = models.CharField(max_length=255, null=True, blank=True)
    Date_of_Entry_into_Govt_Service = models.CharField(max_length=255, null=True, blank=True)
    Date_of_Promotion = models.CharField(max_length=255, null=True, blank=True)
    Date_of_Retirement = models.CharField(max_length=255, null=True, blank=True)
    Date_of_Posting_in_rto_ii_Karachi = models.CharField(max_length=255, null=True, blank=True)
    Date_of_Posting_in_Zone = models.CharField(max_length=255, null=True, blank=True)
    Personal_No = models.CharField(max_length=255, null=True, blank=True)
    Cell_No = models.CharField(max_length=255, null=True, blank=True)
    Education = models.CharField(max_length=255, null=True, blank=True)
    Domicile = models.CharField(max_length=255, null=True, blank=True)
    Residential_Address = models.CharField(max_length=255, null=True, blank=True)
    Basic_Pay = models.CharField(max_length=255, null=True, blank=True)
    Personal_Pay = models.CharField(max_length=255, null=True, blank=True)
    Total = models.CharField(max_length=255, null=True, blank=True)
    Email_Address = models.CharField(max_length=255, null=True, blank=True)
    Remarks = models.CharField(max_length=255, null=True, blank=True)
