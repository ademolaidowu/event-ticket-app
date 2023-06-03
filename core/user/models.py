'''
    This model contains the User and User Profile Model for all accounts
'''

# IMPORTS #

import uuid

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.utils import timezone

from rest_framework_simplejwt.tokens import RefreshToken
from django_countries.fields import CountryField




# MODEL FUNCTIONS #

def generate_user_uuid():
    code = str(uuid.uuid4()).split("-")[-1] #generate unique user id

    try:
        qs_exists = User.objects.filter(user_uuid=code).exists()
        if qs_exists:
            return generate_user_uuid()
        else:
            return 'u'+code
    except:
        return 'u'+code




# CUSTOM USER MODEL MANAGER #

class UserManager(BaseUserManager):

    def _create_user(self, email, username, password, is_active, is_staff, is_admin, is_superuser):
        
        if not email:
            raise ValueError('Users must have an email address')
        
        if not username:
            raise ValueError('Users must have a username')

        now 	= timezone.now()
        email 	= self.normalize_email(email)
        user 	= self.model(
		    email=email,
		    username=username,
		    is_staff=is_staff,
		    is_active=is_active,
		    is_superuser=is_superuser,
		    is_admin=is_admin,
		    last_login=now,
		    date_joined=now,
		)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username, password):
        return self._create_user(email, username, password, False, False, False, False)

    def create_superuser(self, email, username, password):
        user = self._create_user(email, username, password, True, True, True, True)
        return user




# CUSTOM USER MODEL

class User(AbstractBaseUser, PermissionsMixin):

    class AccountManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(is_active=True)


    email = models.EmailField(
        max_length=100,
        unique=True,
        blank=False,
        null=False,
        db_index=True,
        verbose_name='Email',
        help_text='Enter email address',
    )

    username = models.CharField(
        max_length=50,
        unique=True,
        blank=False,
        null=False,
        db_index=True,
        verbose_name='Username',
        help_text='Username must be unique',
    )

    first_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='First name',
    )

    last_name = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Last name',
    )

    user_id = models.CharField(
        db_index=True,
        max_length=15,
        blank=False,
        null=False,
        default=generate_user_uuid,
        verbose_name='User ID',
        editable=False,
    )

    is_staff = models.BooleanField(
        default=False,
        help_text='Select to grant user staff privileges'
    )

    is_admin = models.BooleanField(
        default=False,
        help_text='Select to grant user admin privileges'
    )
        
    is_superuser = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=False,
        help_text='Select to activate user account'
    )

    last_login = models.DateTimeField(
        null=True,
        blank=True,
    )

    date_joined = models.DateTimeField(
        auto_now_add=True,
    )

    date_updated = models.DateTimeField(
        default=timezone.now,
    )


    USERNAME_FIELD 	= 'email'
    EMAIL_FIELD 	= 'email'
    REQUIRED_FIELDS = ['username',]

    objects = UserManager()
    accounts = AccountManager()


    class Meta:
        verbose_name = "User"
        verbose_name_plural = "User Data"
        ordering = ['-date_joined']

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return "/account/%i/" % (self.user_uuid)




# USER PROFILE MODEL #

class UserProfile(models.Model):
    
    class ProfileManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(status="ENABLED")

    # CHOICES
    gender_choices = (
        ('male', 'Male'), 
        ('female', 'Female'), 
        ('others', 'Others'),
    )

    userplan_choices = (
        ('freemium', 'Free'), 
        ('premium', 'Paid'),
    )

    usertype_choices = (
        ('personal', 'Personal'), 
        ('organization', 'Organization'),
    )

    status_choices = (
        ('enabled', 'Enabled'), 
        ('blocked', 'Blocked'),
    )


    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
    )

    status = models.CharField(
        max_length=10,
        choices=status_choices,
        default='enabled',
        blank=True,
        null=True,
        verbose_name='Account Status',
    )

    phone_number = models.CharField(
        max_length=16,
        blank=True,
        null=True,
        verbose_name='Mobile number',
    )

    gender = models.CharField(
        max_length=50,
        choices=gender_choices,
        default='others',
        blank=True,
        null=True,
        verbose_name='Gender',
    )

    address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Address',
    )

    city = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='State/City',
    )

    country = CountryField(
        blank_label='(Select Country)',
        blank=True,
        null=True,
    )

    user_plan = models.CharField(
        max_length=50,
        choices=userplan_choices,
        default='freemium',
        blank=False,
        null=False,
        verbose_name='User Plan',
    )

    user_type = models.CharField(
        max_length=50,
        choices=usertype_choices,
        default='personal',
        blank=False,
        null=False,
        verbose_name='Account Type',
    )

    business_id = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Business Registration Number',
        help_text='Provide Registration Number if account type is organization'
    )

    is_verified = models.BooleanField(
        default=False,
        help_text='Select to grant user popularity verification'
    )

    date_joined = models.DateTimeField(
        auto_now_add=True,
    )

    date_updated = models.DateTimeField(
        default=timezone.now,
    )

    objects = models.Manager() 
    accounts = ProfileManager()

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ['-date_joined']

    def __str__(self):
        return self.user.email