# Generated by Django 5.0.7 on 2024-08-17 14:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebApp', '0006_alter_transferposting_transfer_document'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeaveApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_name', models.CharField(max_length=100)),
                ('employee_cnic', models.CharField(max_length=15)),
                ('leave_type', models.CharField(choices=[('Casual Leave', 'Casual Leave'), ('Earned Leave', 'Earned Leave'), ('Ex-Pakistan Leave', 'Ex-Pakistan Leave')], max_length=50)),
                ('leave_start_date', models.DateField()),
                ('leave_end_date', models.DateField()),
                ('reason', models.TextField()),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='WebApp.dispositionlist')),
            ],
        ),
    ]