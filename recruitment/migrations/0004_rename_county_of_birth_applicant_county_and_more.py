# Generated by Django 5.0.4 on 2024-04-22 05:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0003_alter_applicantdocument_applicant'),
    ]

    operations = [
        migrations.RenameField(
            model_name='applicant',
            old_name='county_of_birth',
            new_name='county',
        ),
        migrations.RenameField(
            model_name='applicantaddress',
            old_name='county_of_birth',
            new_name='county',
        ),
        migrations.RenameField(
            model_name='employee',
            old_name='county_of_birth',
            new_name='county',
        ),
        migrations.RenameField(
            model_name='employeeaddress',
            old_name='county_of_birth',
            new_name='county',
        ),
        migrations.RenameField(
            model_name='pyp',
            old_name='county_of_birth',
            new_name='county',
        ),
        migrations.RenameField(
            model_name='pypaddress',
            old_name='county_of_birth',
            new_name='county',
        ),
    ]
