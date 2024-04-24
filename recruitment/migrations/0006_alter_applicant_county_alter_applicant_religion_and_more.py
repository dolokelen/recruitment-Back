# Generated by Django 5.0.4 on 2024-04-23 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0005_rename_ccgpa_applicantdocument_cgpa_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicant',
            name='county',
            field=models.CharField(choices=[('Bomi', 'Bomi'), ('Bong', 'Bong'), ('Gbarpolu', 'Gbarpolu'), ('Grand Bassa', 'Grand Bassa'), ('Grand Cape Mount', 'Grand Cape Mount'), ('Grand Gedeh', 'Grand Gedeh'), ('Grand Kru', 'Grand Kru'), ('Lofa', 'Lofa'), ('Margibi', 'Margibi'), ('Maryland', 'Maryland'), ('Montserrado', 'Montserrado'), ('Nimba', 'Nimba'), ('River cess', 'River cess'), ('River Gee', 'River Gee'), ('Sinoe', 'Sinoe')], max_length=16),
        ),
        migrations.AlterField(
            model_name='applicant',
            name='religion',
            field=models.CharField(choices=[('Christian', 'Christian'), ('Muslim', 'Muslim'), ('None', 'None')], max_length=9),
        ),
        migrations.AlterField(
            model_name='applicantaddress',
            name='county',
            field=models.CharField(choices=[('Bomi', 'Bomi'), ('Bong', 'Bong'), ('Gbarpolu', 'Gbarpolu'), ('Grand Bassa', 'Grand Bassa'), ('Grand Cape Mount', 'Grand Cape Mount'), ('Grand Gedeh', 'Grand Gedeh'), ('Grand Kru', 'Grand Kru'), ('Lofa', 'Lofa'), ('Margibi', 'Margibi'), ('Maryland', 'Maryland'), ('Montserrado', 'Montserrado'), ('Nimba', 'Nimba'), ('River cess', 'River cess'), ('River Gee', 'River Gee'), ('Sinoe', 'Sinoe')], max_length=16),
        ),
        migrations.AlterField(
            model_name='applicantdocument',
            name='qualification',
            field=models.CharField(choices=[('Bachelor', 'Bachelor'), ('Master', 'Master'), ('PhD', 'PhD')], max_length=8),
        ),
        migrations.AlterField(
            model_name='applicationstage',
            name='name',
            field=models.CharField(choices=[('Publicity', 'Publicity'), ('Credential varification', 'Credential varification'), ('Writen exams', 'Writen exams'), ('Interview', 'Interview'), ('Job readiness orientation', 'Job readiness orientation'), ('Placement', 'Placement')], max_length=25),
        ),
        migrations.AlterField(
            model_name='applicationstage',
            name='rejection_reason',
            field=models.CharField(blank=True, choices=[('Police clearance', 'Police clearance'), ('National id', 'National ID'), ('Diploma', 'Diploma'), ('Transcript', 'Transcript'), ('Writen exams', 'Written exams'), ('Interview', 'Interview'), ('Job readiness', 'Job readiness'), ('Absent', 'Absent'), ('Document', 'Document'), ('Disorderly conduct', 'Disorderly conduct'), ('Other', 'Other')], max_length=18, null=True),
        ),
        migrations.AlterField(
            model_name='applicationstage',
            name='status',
            field=models.CharField(choices=[('Under review', 'Under review'), ('Pending', 'Pending'), ('Unsuccessful', 'Unsuccessful'), ('Successful', 'Successful')], max_length=13),
        ),
        migrations.AlterField(
            model_name='employee',
            name='county',
            field=models.CharField(choices=[('Bomi', 'Bomi'), ('Bong', 'Bong'), ('Gbarpolu', 'Gbarpolu'), ('Grand Bassa', 'Grand Bassa'), ('Grand Cape Mount', 'Grand Cape Mount'), ('Grand Gedeh', 'Grand Gedeh'), ('Grand Kru', 'Grand Kru'), ('Lofa', 'Lofa'), ('Margibi', 'Margibi'), ('Maryland', 'Maryland'), ('Montserrado', 'Montserrado'), ('Nimba', 'Nimba'), ('River cess', 'River cess'), ('River Gee', 'River Gee'), ('Sinoe', 'Sinoe')], max_length=16),
        ),
        migrations.AlterField(
            model_name='employee',
            name='employment',
            field=models.CharField(choices=[('Internship', 'Internship'), ('Part Timer', 'Part Timer'), ('Full Timer', 'Full Timer')], max_length=255),
        ),
        migrations.AlterField(
            model_name='employee',
            name='qualification',
            field=models.CharField(choices=[('Bachelor', 'Bachelor'), ('Master', 'Master'), ('PhD', 'PhD')], max_length=8),
        ),
        migrations.AlterField(
            model_name='employee',
            name='religion',
            field=models.CharField(choices=[('Christian', 'Christian'), ('Muslim', 'Muslim'), ('None', 'None')], max_length=9),
        ),
        migrations.AlterField(
            model_name='employeeaddress',
            name='county',
            field=models.CharField(choices=[('Bomi', 'Bomi'), ('Bong', 'Bong'), ('Gbarpolu', 'Gbarpolu'), ('Grand Bassa', 'Grand Bassa'), ('Grand Cape Mount', 'Grand Cape Mount'), ('Grand Gedeh', 'Grand Gedeh'), ('Grand Kru', 'Grand Kru'), ('Lofa', 'Lofa'), ('Margibi', 'Margibi'), ('Maryland', 'Maryland'), ('Montserrado', 'Montserrado'), ('Nimba', 'Nimba'), ('River cess', 'River cess'), ('River Gee', 'River Gee'), ('Sinoe', 'Sinoe')], max_length=16),
        ),
        migrations.AlterField(
            model_name='employeedocument',
            name='qualification',
            field=models.CharField(choices=[('Bachelor', 'Bachelor'), ('Master', 'Master'), ('PhD', 'PhD')], max_length=8),
        ),
        migrations.AlterField(
            model_name='pyp',
            name='county',
            field=models.CharField(choices=[('Bomi', 'Bomi'), ('Bong', 'Bong'), ('Gbarpolu', 'Gbarpolu'), ('Grand Bassa', 'Grand Bassa'), ('Grand Cape Mount', 'Grand Cape Mount'), ('Grand Gedeh', 'Grand Gedeh'), ('Grand Kru', 'Grand Kru'), ('Lofa', 'Lofa'), ('Margibi', 'Margibi'), ('Maryland', 'Maryland'), ('Montserrado', 'Montserrado'), ('Nimba', 'Nimba'), ('River cess', 'River cess'), ('River Gee', 'River Gee'), ('Sinoe', 'Sinoe')], max_length=16),
        ),
        migrations.AlterField(
            model_name='pyp',
            name='religion',
            field=models.CharField(choices=[('Christian', 'Christian'), ('Muslim', 'Muslim'), ('None', 'None')], max_length=9),
        ),
        migrations.AlterField(
            model_name='pypaddress',
            name='county',
            field=models.CharField(choices=[('Bomi', 'Bomi'), ('Bong', 'Bong'), ('Gbarpolu', 'Gbarpolu'), ('Grand Bassa', 'Grand Bassa'), ('Grand Cape Mount', 'Grand Cape Mount'), ('Grand Gedeh', 'Grand Gedeh'), ('Grand Kru', 'Grand Kru'), ('Lofa', 'Lofa'), ('Margibi', 'Margibi'), ('Maryland', 'Maryland'), ('Montserrado', 'Montserrado'), ('Nimba', 'Nimba'), ('River cess', 'River cess'), ('River Gee', 'River Gee'), ('Sinoe', 'Sinoe')], max_length=16),
        ),
        migrations.AlterField(
            model_name='pypdocument',
            name='qualification',
            field=models.CharField(choices=[('Bachelor', 'Bachelor'), ('Master', 'Master'), ('PhD', 'PhD')], max_length=8),
        ),
    ]
