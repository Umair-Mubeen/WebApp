# Generated by Django 5.0.7 on 2024-08-30 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebApp', '0010_leaveapplication_zone_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaveapplication',
            name='created_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='leaveapplication',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]