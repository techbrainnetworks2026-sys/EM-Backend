from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):

    MANAGER = 'MANAGER'
    EMPLOYEE = 'EMPLOYEE'

    ROLE_CHOICES = [
        (MANAGER, 'Manager'),
        (EMPLOYEE, 'Employee'),
    ]

    email = models.EmailField(
        unique=True,
        help_text="User's primary email address. Must be unique."
    )

    BLOOD_GROUP_CHOICES = (
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=EMPLOYEE,
        help_text="Select the role of the user in the organization."
    )

    is_approved = models.BooleanField(
        default=False,
        help_text="Indicates whether the user account has been approved by an admin."
    )

    department = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Department the employee belongs to."
    )

    designation = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Job title or designation of the employee."
    )

    blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUP_CHOICES,
        blank=True,
        null=True,
        help_text="Employee's blood group."
    )

    mobile_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Employee's contact mobile number."
    )

    def save(self, *args, **kwargs):
        if self.role == self.MANAGER:
            self.is_approved = True  # Auto-approve managers
        # Employees remain unapproved until approved by admin

        super().save(*args, **kwargs)