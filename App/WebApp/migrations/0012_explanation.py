# Generated by Django 5.0.7 on 2024-09-05 14:27

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebApp', '0011_leaveapplication_created_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Explanation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exp_type', models.CharField(choices=[('Unapproved Leave', 'Unapproved Leave'), ('Attendance Issue', 'Attendance Issue'), ('Absent', 'Absent'), ('Habitual Absentee', 'Habitual Absentee'), ('Performance', 'Performance'), ('Misconduct Explanation', 'Misconduct Explanation'), ('Delay Explanation', 'Delay Explanation'), ('Leave Explanation', 'Leave Explanation'), ('Disciplinary', 'Disciplinary')], max_length=50)),
                ('exp_issue_date', models.DateField(default=django.utils.timezone.now)),
                ('exp_reply_date', models.DateField()),
                ('exp_document', models.FileField(blank=True, null=True, upload_to='explanation_docs/')),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='WebApp.dispositionlist')),
            ],
        ),
    ]