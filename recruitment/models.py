from django.conf import settings
from django.db import models, transaction
from django.core.validators import FileExtensionValidator

from .validators import (
    validate_file_size, 
    validate_year, 
    validate_district
    )
from .utilities import (
    image_upload_path, degree_upload_path, 
    community_letter_upload_path,
    reference_letter_upload_path, application_upload_path,
    resume_upload_path, police_clearance_upload_path,
    tor_upload_path, applicant_id_number_generator,
    pyp_id_number_generator
    )


class CountyChoice(models.Model):
    COUNTY_CHOICES = (
        ('bomi', 'Bomi'),
        ('bong', 'Bong'),
        ('gbarpolu', 'Gbarpolu'),
        ('grand bassa', 'Grand Bassa'),
        ('grand cape mount', 'Grand Cape Mount'),
        ('grand gedeh', 'Grand Gedeh'),
        ('grand kru', 'Grand Kru'),
        ('lofa', 'Lofa'),
        ('margibi', 'Margibi'),
        ('maryland', 'Maryland'),
        ('montserrado', 'Montserrado'),
        ('nimba', 'Nimba'),
        ('river cess', 'River cess'),
        ('river gee', 'River Gee'),
        ('sinoe', 'Sinoe')
    )
    county_of_birth = models.CharField(max_length=16, choices=COUNTY_CHOICES)

    class Meta:
        abstract = True


class Person(CountyChoice):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female')
    )
    RELIGION_CHOICES = (
        ('christian', 'Christian'),
        ('muslim', 'Muslim'),
        ('none', 'None')
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE)
    birth_date = models.DateField()
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    religion = models.CharField(max_length=9, choices=RELIGION_CHOICES)
    image = models.ImageField(
        upload_to=image_upload_path, validators=[validate_file_size])
    joined_at = models.DateField(auto_now_add=True)

    class Meta:
        abstract = True


class ApplicationDate(models.Model):
    open_year = models.PositiveIntegerField(validators=[validate_year])
    open_month = models.PositiveIntegerField()
    open_date = models.PositiveIntegerField()
    close_year = models.PositiveIntegerField(validators=[validate_year])
    close_month = models.PositiveIntegerField()
    close_date = models.PositiveIntegerField()
    is_current = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self._state.adding:
                self.is_current = True

            previous_date = ApplicationDate.objects.filter(is_current=True)
            previous_date.update(is_current=False)

            return super().save(*args, **kwargs)


class Applicant(Person):
    id_number = models.CharField(
        max_length=255, default=applicant_id_number_generator)
    application_date = models.ForeignKey(
        ApplicationDate, on_delete=models.PROTECT, related_name='applicants')
    status = models.CharField(max_length=100, default='Under review')
    rejection_reason = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self._state.adding:
                instance = ApplicationDate.objects.get(is_current=True)
                self.application_date = instance

            return super().save(*args, **kwargs)


class QualificationChoice(models.Model):
    QUALIFICATION_CHOICES = (
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('phd', 'PhD')
    )
    qualification = models.CharField(
        max_length=8, choices=QUALIFICATION_CHOICES)

    class Meta:
        abstract = True


class Employee(Person, QualificationChoice):
    EMPLOYMENT_CHOICES = (
        ('internship', 'Internship'),
        ('part timer', 'Part Timer'),
        ('full timer', 'Full Timer')
    )
    employment = models.CharField(max_length=255, choices=EMPLOYMENT_CHOICES)
    position = models.CharField(max_length=255)
    supervisor = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL)
    salary = models.DecimalField(max_digits=6, decimal_places=2)
    exit_date = models.DateField(null=True)


class ApplicationStage(models.Model):
    STATUS_CHOICES = (
        ('under review', 'Under review'),
        ('pending', 'Pending'),
        ('unsuccessful', 'Unsuccessful'),
        ('successful', 'Successful'),
    )
    NAME_CHOICES = (
        ('publicity', 'Publicity'),
        ('credential varification', 'Credential varification'),
        ('writen exams', 'Writen exams'),
        ('interview', 'Interview'),
        ('job readiness orientation', 'Job readiness orientation'),
        ('placement', 'Placement')
    )
    REJECTION_REASON_CHOICES = (
        ('police clearance', 'Police clearance'),
        ('national id', 'National ID'),
        ('diploma', 'Diploma'),
        ('transcript', 'Transcript'),
        ('writen exams', 'Written exams'),
        ('interview', 'Interview'),
        ('job readiness', 'Job readiness'),
        ('absent', 'Absent'),
        ('document', 'Document'),
        ('disorderly conduct', 'Disorderly conduct'),
        ('other', 'Other')
    )
    name = models.CharField(max_length=25, choices=NAME_CHOICES)
    status = models.CharField(max_length=13, choices=STATUS_CHOICES)
    application_date = models.ForeignKey(
        ApplicationDate, on_delete=models.PROTECT, related_name='stages')
    applicants = models.ManyToManyField(Applicant, related_name='stages')
    rejection_reason = models.CharField(
        max_lenght=18, choices=REJECTION_REASON_CHOICES, null=True, blank=True)
    other_rejection_reason = models.TextField(null=True, blank=True)
    is_rejected = models.BooleanField(default=False)
    is_current = models.BooleanField(default=False)
    # Create signal to listen for any of the CURD operations and create an AuditTrial instance.
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='stages')
    created_at = models.DateTimeField(auto_now_add=True)
    # This will allow me to delete all instances of this model
    # for a particular recruitment cycle
    is_recruitment_complemented = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self._state.adding:
                self.is_current = True
                previous_stage = ApplicationStage.objects.filter(
                    is_current=True)
                previous_stage.update(is_current=False)

                instance = ApplicationDate.objects.get(is_current=True)
                self.application_date = instance
            
            if self.rejection_reason != 'Other':
                self.other_rejection_reason = None

            return super().save(*args, **kwargs)


# Use the 'pre_save and post_save' signals of ApplicationStage
class ApplicantStatusAuditTrial(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)
    applicant = models.ForeignKey(
        Applicant, on_delete=models.SET_NULL, related_name='audits')
    previous_status = models.CharField(max_length=255)
    new_status = models.CharField(max_length=255)
    action = models.CharField(max_length=255)
    created_at = models.DateTimeField()


class ApplicationStageCompletedAuditTrial(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT)
    application_stage = models.ForeignKey(
        ApplicationStage, on_delete=models.PROTECT)
    previous_is_cruitment_completed = models.BooleanField()
    new_is_cruitment_completed = models.BooleanField()
    # I just want to track the employee who change the
    # is_recruitment_completed to True, b/c when this is done
    # I'll delete some models instances which cannot be revert.


class CohortSponsor(models.Model):
    name = models.CharField(max_length=100)
    application_date = models.ForeignKey(
        ApplicationDate, on_delete=models.PROTECT)


class Cohort(models.Model):
    sponsors = models.ManyToManyField(CohortSponsor, related_name='cohorts')
    application_date = models.ForeignKey(
        ApplicationDate, on_delete=models.PROTECT)
    name = models.CharField(max_length=100, unique=True)
    # automate this 'is_current' by listening to the post_save of
    # ApplicationStage.name == 'placement' of the current
    # ApplicationDate and them make the previous PYP old
    is_currnt = models.BooleanField(default=True)
    # auto all the below fields from 'RejectedApplication'
    rejected_male_count = models.PositiveIntegerField()
    rejected_female_count = models.PositiveIntegerField()
    rejected_police_clearance_count = models.PositiveIntegerField()
    rejected_national_id_count = models.PositiveIntegerField()
    rejected_diploma_count = models.PositiveIntegerField()
    rejected_transcript = models.PositiveIntegerField()
    rejected_exams_count = models.PositiveIntegerField()
    rejected_interview_count = models.PositiveIntegerField()
    rejected_job_readiness_count = models.PositiveIntegerField()
    rejection_absent_count = models.PositiveIntegerField()
    rejection_other_count = models.PositiveIntegerField()


class Pyp(Person):  # Only create instance of this model if status is 'successful'
    # Subscribe to the 'update' signal of ApplicationStage, whenever this signal is fire
    # check ApplicationStage.status == 'successful' if yes create an instance of Pyp model
    # with that Applicant who was successful.
    # Duplicate all fields of Application here
    cohort = models.ForeignKey(
        Cohort, on_delete=models.PROTECT, related_name='pyps')
    id_number = models.CharField(
        max_length=255, default=pyp_id_number_generator)
    placement_date = models.DateField(null=True, blank=True)
    tor = models.FileField(upload_path=tor_upload_path, null=True, blank=True)
    employement_date = models.DateField(null=True, blank=True)
    position = models.CharField(max_length=100, default='PYP Fellow')
    # When the 'current' ApplicationStage.name == 'palcement'
    # then all previous Pyps are consider not current. meaning I've to listen for the post save
    # signal of 'ApplicationStage' and check if its 'name == 'placement' then I can make all
    # pyps old 'is_current == False'.
    is_current = models.BooleanField(default=True)
    # Automate it to the current ApplicationDate/the Applicant being created ApplicationDate
    application_date = models.ForeignKey(
        ApplicationDate, on_delete=models.PROTECT, related_name='pyps')

    def save(self, *args, **kwargs):
        if self._state.adding:
            instance = ApplicationDate.objects.get(is_current=True)
            self.application_date = instance
        
        return super().save(*args, **kwargs)


class Institution(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)

    class Meta: 
        abstract = True


class PypInstitution(Institution):
    pyp = models.ForeignKey(Pyp, on_delete=models.PROTECT, related_name='institutions')


class RejectedApplication(models.Model):
    # Listen to the 'ApplicationStage' post_save signal and move all
    # Applicant.status == 'unsuccessful' in 'RejectedApplication'
    # Delete all instances of 'RejectedApplication' if
    # 'ApplicationStage.name == 'credential varification'
    # it's possible that there's no unsuccessful Applicant so handle such error
    applicants = models.ManyToManyField(
        Applicant, related_name='rejected_applicants')
    # RejectedApplicant => when ApplicationStatus.name == 'Cred. Varif.
    # Applicant => Each time an applicant is copied to either Pyp or
    #               RejectedApplication, that means at the end of
    #               the process this model will be empty.
    # ApplicationStage => we can only delete this when we delete
    #               the AuditTrials b/c it's reference there,
    # AuditTrial => When the ApplicationStage changes from 'Publicity'

    # ** Let's keep all previous Applicant, ApplicationStage,
    #       RejectedApplicant and all AuditTrial until the new
    #       ApplicationDate is closed. Then we can delete all of the
    #       previous instances of the above models. Meaning we've to
    #       revisit the CASCADE behaviors of these models to avoid
    #       any error during deletion base on relationship constraints


class Document(QualificationChoice):
    # validate the length [4] of this field
    graduation_year = models.PositiveIntegerField(validators=[validate_year])
    major = models.CharField(max_length=100)
    manor = models.CharField(max_length=100)
    institution = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    county = models.CharField(max_length=100)  # providence/state
    # these are incomplete and validate its .pdf
    degree = models.FileField(upload_to=degree_upload_path, validators=[
                              FileExtensionValidator(allowed_extensions=['pdf'])])
    ccgpa = models.DecimalField(max_digits=3, decimal_places=2)
    # incomplate and must be .pdf
    application_letter = models.FileField(upload_to=application_upload_path, validators=[
                                          FileExtensionValidator(allowed_extensions=['pdf'])])
    community_letter = models.FileField(upload_to=community_letter_upload_path, validators=[
                                        FileExtensionValidator(allowed_extensions=['pdf'])])
    reference_letter = models.FileField(upload_to=reference_letter_upload_path, validators=[
                                        FileExtensionValidator(allowed_extensions=['pdf'])])
    resume = models.FileField(upload_to=resume_upload_path, validators=[
                              FileExtensionValidator(allowed_extensions=['pdf'])])
    
    class Meta:
        abstract = True


class ApplicantDocument(Document):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='documents')
    police_clearance = models.FileField(upload_to=police_clearance_upload_path, validators=[
                                        FileExtensionValidator(allowed_extensions=['pdf'])])


class PypDocument(Document):
    pyp = models.ForeignKey(Pyp, on_delete=models.CASCADE, related_name='documents')
    police_clearance = models.FileField(upload_to=police_clearance_upload_path, validators=[
                                        FileExtensionValidator(allowed_extensions=['pdf'])])


class EmployeeDocument(Document):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')


class Contact(models.Model):
    phone = models.CharField(max_length=20, unique=True)

    class Meta:
        abstract = True


class ApplicantContact(Contact):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='contacts')


class PypContact(Contact):
    pyp = models.ForeignKey(Pyp, on_delete=models.CASCADE, related_name='contacts')


class EmployeeContact(Contact):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='contacts')


class Supervisor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE)
    pyp = models.ForeignKey(Pyp, on_delete=models.CASCADE, related_name='supervisors')
    position = models.CharField(max_length=100)


class Mentor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE)
    pyp = models.ForeignKey(Pyp, on_delete=models.CASCADE, related_name='mentors')
    position = models.CharField(max_length=100)


class SupervisorContact(Contact):
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE, related_name='contacts')


class MentorContact(Contact):
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE, related_name='contacts')


class Address(CountyChoice):
    country = models.CharField(max_length=7, default='Liberia')
    # validate it aganist accepting 0
    district = models.PositiveIntegerField(validators=[validate_district])
    community = models.CharField(max_length=100)
    house_address = models.CharField(max_length=100)

    class Meta:
        abstract = True


class ApplicantAddress(Address):
    applicant = models.OneToOneField(
        Applicant, primary_key=True, on_delete=models.CASCADE, related_name='address')


class PypAddress(Address):
    pyp = models.OneToOneField(
        Pyp, primary_key=True, on_delete=models.CASCADE, related_name='address')


class EmployeeAddress(Address):
    employee = models.OneToOneField(
        Employee, primary_key=True, on_delete=models.CASCADE, related_name='address')


class Department(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)

    class Meta:
        abstract = True

class PypDepartment(Department):
    institution = models.ForeignKey(
        PypInstitution, on_delete=models.PROTECT, related_name='departments')
    supervisor = models.OneToOneField(
        Supervisor, primary_key=True, on_delete=models.CASCADE, related_name='department')


class Equipment(models.Model):
    name = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    storage = models.CharField(max_length=100)
    processor_type = models.CharField(max_length=100)
    ram_capicity = models.CharField(max_length=100)

    class Meta:
        abstract = True


class PypEquipment(Equipment):
    pyp = models.ForeignKey(Pyp, on_delete=models.CASCADE, related_name='devices')


class EmployeeEquipment(Equipment):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='devices')


class EmployeeInstitution(Institution):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='institutions')


class EmployeeDepartment(Department):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='departments')
