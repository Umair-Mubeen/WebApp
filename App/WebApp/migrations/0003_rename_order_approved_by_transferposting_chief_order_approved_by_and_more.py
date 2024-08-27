# Generated by Django 5.0.7 on 2024-08-24 08:21

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebApp', '0002_transferposting_new_zone_transferposting_old_zone_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transferposting',
            old_name='order_approved_by',
            new_name='chief_order_approved_by',
        ),
        migrations.RenameField(
            model_name='transferposting',
            old_name='order_number',
            new_name='chief_order_number',
        ),
        migrations.RenameField(
            model_name='transferposting',
            old_name='reason_for_transfer',
            new_name='chief_reason_for_transfer',
        ),
        migrations.RenameField(
            model_name='transferposting',
            old_name='transfer_date',
            new_name='chief_transfer_date',
        ),
        migrations.RenameField(
            model_name='transferposting',
            old_name='transfer_document',
            new_name='chief_transfer_document',
        ),
        migrations.AddField(
            model_name='transferposting',
            name='zone_order_approved_by',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='transferposting',
            name='zone_order_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='transferposting',
            name='zone_reason_for_transfer',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='transferposting',
            name='zone_transfer_date',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='transferposting',
            name='zone_transfer_document',
            field=models.FileField(default=None, max_length=250, null=True, upload_to='transfer_documents/'),
        ),
    ]
