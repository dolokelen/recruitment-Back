# Generated by Django 5.0.6 on 2024-06-09 02:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0011_remove_applicationstagecompletedaudittrial_application_stage_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='applicant',
            name='rejection_reason',
        ),
        migrations.RemoveField(
            model_name='applicationstage',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='applicationstage',
            name='employee',
        ),
        migrations.RemoveField(
            model_name='applicationstage',
            name='is_current',
        ),
        migrations.RemoveField(
            model_name='applicationstage',
            name='is_recruitment_complemented',
        ),
        migrations.RemoveField(
            model_name='applicationstage',
            name='is_rejected',
        ),
        migrations.RemoveField(
            model_name='applicationstage',
            name='other_rejection_reason',
        ),
        migrations.RemoveField(
            model_name='applicationstage',
            name='rejection_reason',
        ),
        migrations.RemoveField(
            model_name='applicationstage',
            name='status',
        ),
        migrations.AddField(
            model_name='applicant',
            name='apply_at',
            field=models.DateTimeField(auto_now_add=True, default='2024-06-09 10:00:00'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='applicationstage',
            name='order',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='ApplicantStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('Under review', 'Under review'), ('Pending', 'Pending'), ('Unsuccessful', 'Unsuccessful'), ('Successful', 'Successful')], max_length=13)),
                ('rejection_reason', models.CharField(blank=True, choices=[('Police clearance', 'Police clearance'), ('National id', 'National ID'), ('Diploma', 'Diploma'), ('Transcript', 'Transcript'), ('Writen exams', 'Written exams'), ('Interview', 'Interview'), ('Job readiness', 'Job readiness'), ('Absent', 'Absent'), ('Document', 'Document'), ('Disorderly conduct', 'Disorderly conduct'), ('Other', 'Other')], max_length=18, null=True)),
                ('other_rejection_reason', models.TextField(blank=True, null=True)),
                ('process_at', models.DateTimeField(auto_now_add=True)),
                ('process_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='stages', to='recruitment.employee')),
            ],
        ),
    ]
