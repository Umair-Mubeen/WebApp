# Generated by Django 5.0.7 on 2024-08-11 09:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('WebApp', '0003_remove_transferposting_cnic_no_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transferposting',
            name='remarks',
        ),
        migrations.RemoveField(
            model_name='transferposting',
            name='zone',
        ),
    ]