from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLES = (
        ('admin', 'Admin'),
        ('org_user', 'Organizational User'),
        ('user', 'Normal User'),
    )

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=ROLES, default='user')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return True


class FinancialServices(models.Model):
    company_name = models.CharField(max_length=255)
    legal_status = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField()
    mobile = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    nature_of_business = models.CharField(max_length=255)
    # Could be DecimalField but matching form input
    net_worth = models.CharField(max_length=100)
    last_turnover = models.CharField(max_length=100)
    current_loan_liability = models.CharField(max_length=100)
    last_it_paid = models.CharField(max_length=100)
    fund_looking_for = models.CharField(max_length=100)
    purpose_of_funding = models.TextField()
    nature_of_funding = models.CharField(max_length=255)
    offered_roi = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name


class AdvisoryApplication(models.Model):
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10)
    dob = models.DateField()
    email = models.EmailField()
    mobile = models.CharField(max_length=20)
    address = models.TextField()
    interest_invest = models.CharField(max_length=255)
    interest = models.CharField(max_length=50)
    range_investment = models.CharField(max_length=100)
    expected_roi = models.CharField(max_length=50)
    duration = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
