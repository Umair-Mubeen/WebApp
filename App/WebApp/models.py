from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
from django.utils import timezone


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
    additional_charge = models.CharField(max_length=255, null=True, blank=True)
    additional_charge_lro = models.CharField(max_length=255, null=True, blank=True)
    emp_age = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=255, null=True, blank=True)
    status = models.IntegerField(default=1)


class TransferPosting(models.Model):
    employee = models.ForeignKey('DispositionList', on_delete=models.CASCADE)  # Assuming using CNIC as FK

    old_zone = models.CharField(max_length=255, blank=True)  # ccir
    new_zone = models.CharField(max_length=255, blank=True)  # ccir
    chief_order_number = models.CharField(max_length=255)  # chief office
    chief_transfer_date = models.DateField(null=True)  # chief office
    chief_reason_for_transfer = models.TextField(blank=True, null=True)  # chief office
    chief_order_approved_by = models.CharField(max_length=255)  # Person who approved the transfer chief office
    chief_transfer_document = models.FileField(upload_to='transfer_documents/', max_length=250, default=None,null=True)  # ccir
    old_unit = models.CharField(max_length=255, blank=True, null=True)  # zone
    new_unit = models.CharField(max_length=255, blank=True, null=True)  # zone
    zone_range = models.CharField(max_length=255, blank=True, null=True)  # zone
    zone_order_number = models.IntegerField(default=0)  # Zone office
    zone_transfer_date = models.DateField(auto_now_add=True)  # Zone office
    zone_reason_for_transfer = models.TextField(blank=True, null=True)  # Zone office
    zone_order_approved_by = models.CharField(max_length=255,
                                              blank=True)  # Person who approved the transfer Zone office
    zone_transfer_document = models.FileField(upload_to='transfer_documents/', max_length=250, default=None,
                                              null=True)  #
    zone_type = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class LeaveApplication(models.Model):
    LEAVE_TYPES = [
        ('Casual Leave', 'Casual Leave'),
        ('Earned Leave', 'Earned Leave'),
        ('Ex-Pakistan Leave', 'Ex-Pakistan Leave'),
        ('Medical Leave', 'Medical Leave'),
        ('Study Leave', 'Study Leave'),
        ('Special Leave', 'Special Leave'),
        ('Maternity Leave', 'Maternity Leave'),

    ]
    employee = models.ForeignKey('DispositionList', on_delete=models.CASCADE)  # Assuming using CNIC as FK
    leave_type = models.CharField(max_length=50, choices=LEAVE_TYPES)
    leave_start_date = models.DateField()
    leave_end_date = models.DateField()
    leave_document = models.FileField(upload_to='leave_documents/', null=True,
                                      blank=True)  # Field for leave application
    reason = models.TextField()
    days_granted = models.PositiveIntegerField(default=0)  # Field for number of days granted
    zone_type = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)


class Explanation(models.Model):
    EXPLANATION_TYPES = [
        ('Unapproved Leave', 'Unapproved Leave'),
        ('Attendance Issue', 'Attendance Issue'),
        ('Absent', 'Absent'),
        ('Habitual Absentee', 'Habitual Absentee'),
        ('Performance', 'Performance'),
        ('Misconduct Explanation', 'Misconduct Explanation'),
        ('Delay Explanation', 'Delay Explanation'),
        ('Leave Explanation', 'Leave Explanation'),
        ('Disciplinary', 'Disciplinary'),
    ]

    employee = models.ForeignKey('DispositionList', on_delete=models.CASCADE)
    exp_type = models.CharField(max_length=50, choices=EXPLANATION_TYPES)
    exp_issue_date = models.DateField(default=timezone.now)
    exp_reply_date = models.DateField()
    exp_document = models.FileField(upload_to='explanation_docs/', blank=True, null=True)
    zone_type = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)


class CustomUser(AbstractUser):
    userType = models.CharField(
        choices=[('ZONE', 'Zone-I'), ('ZONE', 'Zone-II'), ('ZONE', 'Zone-III'), ('ZONE', 'Zone-IV'),
                 ('ZONE', 'Zone-V')], max_length=50)