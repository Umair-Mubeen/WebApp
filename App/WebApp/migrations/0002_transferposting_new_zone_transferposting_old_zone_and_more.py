# Generated by Django 5.0.7 on 2024-08-22 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transferposting',
            name='new_zone',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='transferposting',
            name='old_zone',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='transferposting',
            name='zone_range',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]