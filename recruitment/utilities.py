import os
from django.db import connection


def image_upload_path(instance, filename):
    instance_id = str(instance.user.id)
    _, extension = os.path.splitext(filename)
    file_path = f'recruitment/images/{instance_id}{extension}'

    return file_path


def tor_upload_path(instance, filename):
    instance_id = str(instance.user.id)
    _, extension = os.path.splitext(filename)
    file_path = f'recruitment/tor/{instance_id}{extension}'

    return file_path


def police_clearance_upload_path(instance, filename):
    instance_id = str(instance.applicant.user.id)
    _, extension = os.path.splitext(filename)
    file_path = f'recruitment/police-clearance/{instance_id}{extension}'

    return file_path


def degree_upload_path(instance, filename):
    instance_id = str(instance.applicant.user.id)
    _, extension = os.path.splitext(filename)
    file_path = f'recruitment/degree/{instance_id}{extension}'

    return file_path


def application_upload_path(instance, filename):
    instance_id = str(instance.applicant.user.id)
    _, extension = os.path.splitext(filename)
    file_path = f'recruitment/application/{instance_id}{extension}'

    return file_path


def community_letter_upload_path(instance, filename):
    instance_id = str(instance.applicant.user.id)
    _, extension = os.path.splitext(filename)
    file_path = f'recruitment/community-letter/{instance_id}{extension}'

    return file_path


def resume_upload_path(instance, filename):
    instance_id = str(instance.applicant.user.id)
    _, extension = os.path.splitext(filename)
    file_path = f'recruitment/resume/{instance_id}{extension}'

    return file_path


def reference_letter_upload_path(instance, filename):
    instance_id = str(instance.applicant.user.id)
    _, extension = os.path.splitext(filename)
    file_path = f'recruitment/reference-letter/{instance_id}{extension}'

    return file_path


def emp_degree_upload_path(instance, filename):
    instance_id = str(instance.employee.user.id)
    _, extension = os.path.splitext(filename)
    file_path = f'recruitment/degree/{instance_id}{extension}'

    return file_path


def emp_application_upload_path(instance, filename):
    instance_id = str(instance.employee.user.id)
    _, extension = os.path.splitext(filename)
    file_path = f'recruitment/application/{instance_id}{extension}'

    return file_path


def emp_community_letter_upload_path(instance, filename):
    instance_id = str(instance.employee.user.id)
    _, extension = os.path.splitext(filename)
    file_path = f'recruitment/community-letter/{instance_id}{extension}'

    return file_path


def emp_resume_upload_path(instance, filename):
    instance_id = str(instance.employee.user.id)
    _, extension = os.path.splitext(filename)
    file_path = f'recruitment/resume/{instance_id}{extension}'

    return file_path


def emp_reference_letter_upload_path(instance, filename):
    instance_id = str(instance.employee.user.id)
    _, extension = os.path.splitext(filename)
    file_path = f'recruitment/reference-letter/{instance_id}{extension}'

    return file_path


def applicant_id_number_generator():
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT MAX(id_number) FROM recruitment_applicant')
        latest_applicant_number = cursor.fetchone()[0]
    new_applicant_number = int(latest_applicant_number) + \
        1 if latest_applicant_number is not None else 1
    new_applicant_number = str(new_applicant_number).zfill(3)
    return new_applicant_number


def pyp_id_number_generator():
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT MAX(id_number) FROM recruitment_pyp')
        latest_pyp_number = cursor.fetchone()[0]
    new_pyp_number = int(latest_pyp_number) + \
        1 if latest_pyp_number is not None else 1
    new_pyp_number = str(new_pyp_number).zfill(3)
    return new_pyp_number
