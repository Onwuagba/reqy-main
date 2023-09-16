from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.core.validators import RegexValidator
# from django.utils import timezone
import uuid

# Create your models here.

class MyManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        
        if not email:
            raise ValueError("Email is required")

        user = self.model(
            email = self.normalize_email(email),
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    email = models.EmailField(max_length=255, unique=True, verbose_name='email address')
    phone_regex = RegexValidator(regex=r'^(\+\d{1,3}[- ]?)?\d{9,13}$', message="Phone number must be entered in the format: '+234-0000000000'. Up to 13 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, unique=True, blank=True, null=True) 
    default_pwd = models.BooleanField(default=True) #checks that the newly created user does not have the first password set
    regToken = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='token')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = MyManager()

    def __str__(self):
        return f'{self.email}'

class Organisation(models.Model):
    name = models.CharField(max_length=80, unique=True)
    short_name = models.CharField(max_length=10, unique=True) #This will be used for the sub-domain. cia.reqy.com
    domain = models.URLField(max_length=150, unique=True) #ensures that only emails ending with this domain can be added to organisation
    logo = models.FileField(upload_to='com_logo/', null=True, verbose_name="logo")
    added_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

#pivot table to link org and users
class OrganisationUser(models.Model):
    user_id = models.ForeignKey(User, related_name='org_staff', on_delete=models.CASCADE)
    org_id = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    # The role is here cos user can be an admin in 1 org and a staff in another
    ROLE = [
        ('S', 'Staff'), 
        ('A', 'Approver'),
        ('Ad', 'Admin'),
    ]
    role = models.CharField(max_length=2, choices=ROLE, default='S')
    added_on = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, related_name='org_admin', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'org_id'], name='unique_userOrg')
        ]

class Department(models.Model):
    name = models.CharField(max_length=80)
    orgID = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'orgID'], name='unique_deptOrg')
        ]

#pivot table to link department and users
class DepartmentUser(models.Model):
    user_id = models.ForeignKey(User, related_name='dept_staff', on_delete=models.CASCADE)
    department_id = models.ForeignKey(Department, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'department_id'], name='unique_userDept')
        ]

#File storage for system
class FileStorage(models.Model):
    org_id = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    Platform = [
        ('G', 'Google Drive'), 
        ('O', 'One Drive'),
        ('D', 'Drop Box'),
        ('S', 'Local Server'),
    ]
    orgPlatform = models.CharField(max_length=2, choices=Platform, default='S')
    date_setup = models.DateTimeField(auto_now_add=True)
    note = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}"

# Approval line for requisition. This will be displayed to all staff within a dept
class DeptApprover(models.Model):
    dept_id = models.ForeignKey(Department, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, related_name='dept_approver', on_delete=models.CASCADE)
    sequence = models.PositiveIntegerField(null=True, blank=True) #1=1st appprover, 2=2nd approver, 3,.. If empty, the requisition is sent to the main organisation's approver automatically

    def __str__(self):
        return f"{self.id}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['dept_id', 'user_id'], name='unique_userDeptApp')
        ]
