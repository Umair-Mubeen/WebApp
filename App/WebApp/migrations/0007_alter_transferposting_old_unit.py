# Generated by Django 5.0.7 on 2024-08-25 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebApp', '0006_transferposting_zone_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transferposting',
            name='old_unit',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
