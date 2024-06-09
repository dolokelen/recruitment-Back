from django.conf import settings
from django.db import models, transaction
from django.core.validators import FileExtensionValidator

from .validators import (
    validate_file_size,
    validate_year,
    validate_district
)
from .utilities import (
    image_upload_path, degree_upload_path, emp_degree_upload_path,
    community_letter_upload_path, emp_community_letter_upload_path,
    reference_letter_upload_path, emp_reference_letter_upload_path, 
    application_upload_path, emp_application_upload_path,
    resume_upload_path, emp_resume_upload_path, police_clearance_upload_path,
    tor_upload_path, applicant_id_number_generator,
    pyp_id_number_generator
)


class CountyChoice(models.Model):
    """
    The field is not called 'birth_county' because other models
    are inheriting this Abstract model 
    """
    COUNTY_CHOICES = (
        ('Bomi', 'Bomi'),
        ('Bong', 'Bong'),
        ('Gbarpolu', 'Gbarpolu'),
        ('Grand Bassa', 'Grand Bassa'),
        ('Grand Cape Mount', 'Grand Cape Mount'),
        ('Grand Gedeh', 'Grand Gedeh'),
        ('Grand Kru', 'Grand Kru'),
        ('Lofa', 'Lofa'),
        ('Margibi', 'Margibi'),
        ('Maryland', 'Maryland'),
        ('Montserrado', 'Montserrado'),
        ('Nimba', 'Nimba'),
        ('River cess', 'River cess'),
        ('River Gee', 'River Gee'),
        ('Sinoe', 'Sinoe')
    )
    county = models.CharField(max_length=16, choices=COUNTY_CHOICES)

    class Meta:
        abstract = True


class Person(CountyChoice):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female')
    )
    RELIGION_CHOICES = (
        ('Christian', 'Christian'),
        ('Muslim', 'Muslim'),
        ('None', 'None')
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
    #Create all instances of ApplicationStage after creating your instance
    open_date = models.DateField()
    close_date = models.DateField()
    is_current = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self._state.adding:
                self.is_current = True
                ApplicationDate.objects.exclude(
                    pk=self.pk).update(is_current=False)
            elif not self.is_current:
                return super().save(*args, **kwargs)
            else:
                pass

        return super().save(*args, **kwargs)


class Applicant(Person):
    id_number = models.CharField(
        max_length=255, default=applicant_id_number_generator)
    application_date = models.ForeignKey(
        ApplicationDate, on_delete=models.PROTECT, related_name='applicants')
    status = models.CharField(max_length=100, default='Under review')# will be updated when creating an instance of ApplicantStatus
    apply_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self._state.adding:
                instance = ApplicationDate.objects.get(is_current=True)
                self.application_date = instance

            return super().save(*args, **kwargs)


class QualificationChoice(models.Model):
    QUALIFICATION_CHOICES = (
        ('Bachelor', 'Bachelor'),
        ('Master', 'Master'),
        ('PhD', 'PhD')
    )
    qualification = models.CharField(
        max_length=8, choices=QUALIFICATION_CHOICES)

    class Meta:
        abstract = True


class Employee(Person, QualificationChoice):
    EMPLOYMENT_CHOICES = (
        ('Internship', 'Internship'),
        ('Part Timer', 'Part Timer'),
        ('Full Timer', 'Full Timer')
    )
    employment = models.CharField(max_length=255, choices=EMPLOYMENT_CHOICES)
    position = models.CharField(max_length=255)
    supervisor = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='supervisees')
    salary = models.DecimalField(max_digits=6, decimal_places=2)
    exit_date = models.DateField(null=True)


class ApplicationStage(models.Model):
    """
    All instances are auto created any time a new of ApplicationDate is created.
    """
    NAME_CHOICES = (
        ('Publicity', 'Publicity'),
        ('Credential varification', 'Credential varification'),
        ('Writen exams', 'Writen exams'),
        ('Interview', 'Interview'),
        ('Job readiness orientation', 'Job readiness orientation'),
        ('Placement', 'Placement')
    )
    name = models.CharField(max_length=25, choices=NAME_CHOICES)
    application_date = models.ForeignKey(
        ApplicationDate, on_delete=models.PROTECT, related_name='stages')
    applicants = models.ManyToManyField(Applicant, related_name='stages')  
    order = models.PositiveIntegerField()#use to move qualify applicants to the next stage[1,2,3...]

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self._state.adding:
                instance = ApplicationDate.objects.get(is_current=True)
                self.application_date = instance

            return super().save(*args, **kwargs)


class ApplicantStatus(models.Model):
    """ Return instances associated with the requested status """
    #Update Applicant -> 'status' after creating your instance
    STATUS_CHOICES = (
    ('Under review', 'Under review'),
    ('Pending', 'Pending'),
    ('Unsuccessful', 'Unsuccessful'),
    ('Successful', 'Successful'),
    )
    REJECTION_REASON_CHOICES = (
        ('Police clearance', 'Police clearance'),
        ('National id', 'National ID'),
        ('Diploma', 'Diploma'),
        ('Transcript', 'Transcript'),
        ('Writen exams', 'Written exams'),
        ('Interview', 'Interview'),
        ('Job readiness', 'Job readiness'),
        ('Absent', 'Absent'),
        ('Document', 'Document'),
        ('Disorderly conduct', 'Disorderly conduct'),
        ('Other', 'Other')
    )
    status = models.CharField(max_length=13, choices=STATUS_CHOICES)
    rejection_reason = models.CharField(
        max_length=18, choices=REJECTION_REASON_CHOICES, null=True, blank=True)
    other_rejection_reason = models.TextField(null=True, blank=True)
    process_by = models.ForeignKey(
        Employee, on_delete=models.PROTECT, related_name='stages')
    process_at = models.DateTimeField(auto_now_add=True)


# Use the 'pre_save and post_save' signals of ApplicationStage
# class ApplicantStatusAuditTrial(models.Model):
#     employee = models.ForeignKey(Employee, on_delete=models.PROTECT)
#     applicant = models.ForeignKey(
#         Applicant, on_delete=models.PROTECT, related_name='audits')
#     previous_status = models.CharField(max_length=255)
#     new_status = models.CharField(max_length=255)
#     action = models.CharField(max_length=255)
#     created_at = models.DateTimeField()


# class ApplicationStageCompletedAuditTrial(models.Model):
#     employee = models.ForeignKey(Employee, on_delete=models.PROTECT)
#     application_stage = models.ForeignKey(
#         ApplicationStage, on_delete=models.PROTECT)
#     previous_is_cruitment_completed = models.BooleanField()
#     new_is_cruitment_completed = models.BooleanField()
#     # I just want to track the employee who change the
#     # is_recruitment_completed to True, b/c when this is done
#     # I'll delete some models instances which cannot be revert.


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
    tor = models.FileField(upload_to=tor_upload_path, null=True, blank=True)
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
    pyp = models.ForeignKey(Pyp, on_delete=models.PROTECT,
                            related_name='institutions')


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
    """
    Refactor the common fields of EmployeeDocument model and this!
    """
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
    cgpa = models.DecimalField(max_digits=3, decimal_places=2)
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
    applicant = models.OneToOneField(
        Applicant, primary_key=True, on_delete=models.CASCADE, related_name='document')
    police_clearance = models.FileField(upload_to=police_clearance_upload_path, validators=[
                                        FileExtensionValidator(allowed_extensions=['pdf'])])


class PypDocument(Document):
    pyp = models.ForeignKey(
        Pyp, on_delete=models.CASCADE, related_name='documents')
    police_clearance = models.FileField(upload_to=police_clearance_upload_path, validators=[
                                        FileExtensionValidator(allowed_extensions=['pdf'])])


class EmployeeDocument(QualificationChoice):
    """
    The file upload is using the instance id and so I can't use
    one function to get the instance id in utilities.py 
    Refactor the common fields of Document model and this!
    """
    graduation_year = models.PositiveIntegerField(validators=[validate_year])
    major = models.CharField(max_length=100)
    manor = models.CharField(max_length=100)
    institution = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    county = models.CharField(max_length=100)  # providence/state
    degree = models.FileField(upload_to=emp_degree_upload_path, validators=[
                              FileExtensionValidator(allowed_extensions=['pdf'])])
    cgpa = models.DecimalField(max_digits=3, decimal_places=2)
    application_letter = models.FileField(upload_to=emp_application_upload_path, validators=[
                                          FileExtensionValidator(allowed_extensions=['pdf'])])
    community_letter = models.FileField(upload_to=emp_community_letter_upload_path, validators=[
                                        FileExtensionValidator(allowed_extensions=['pdf'])])
    reference_letter = models.FileField(upload_to=emp_reference_letter_upload_path, validators=[
                                        FileExtensionValidator(allowed_extensions=['pdf'])])
    resume = models.FileField(upload_to=emp_resume_upload_path, validators=[
                              FileExtensionValidator(allowed_extensions=['pdf'])])
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='documents')


class Contact(models.Model):
    phone = models.CharField(max_length=20, unique=True)

    class Meta:
        abstract = True


class ApplicantContact(Contact):
    applicant = models.ForeignKey(
        Applicant, on_delete=models.CASCADE, related_name='contacts')


class PypContact(Contact):
    pyp = models.ForeignKey(
        Pyp, on_delete=models.CASCADE, related_name='contacts')


class EmployeeContact(Contact):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='contacts')


class Supervisor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE)
    pyp = models.ForeignKey(Pyp, on_delete=models.CASCADE,
                            related_name='supervisors')
    position = models.CharField(max_length=100)


class Mentor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE)
    pyp = models.ForeignKey(
        Pyp, on_delete=models.CASCADE, related_name='mentors')
    position = models.CharField(max_length=100)


class SupervisorContact(Contact):
    supervisor = models.ForeignKey(
        Supervisor, on_delete=models.CASCADE, related_name='contacts')


class MentorContact(Contact):
    mentor = models.ForeignKey(
        Mentor, on_delete=models.CASCADE, related_name='contacts')


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
    pyp = models.ForeignKey(
        Pyp, on_delete=models.CASCADE, related_name='devices')


class EmployeeEquipment(Equipment):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='devices')


class EmployeeInstitution(Institution):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='institutions')


class EmployeeDepartment(Department):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='departments')
