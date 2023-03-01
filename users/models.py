# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

import re

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

import datetime


# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, password=None, username=None, **extra_fields):
        """Create, save and return a new user."""
        # if not email:
        #     raise ValueError('required')
        # user = self.model(email=self.normalize_email(email), **extra_fields)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, password=None):
        """Create and return a new superuser."""
        user = self.create_user(username=username, password=password)
        user.is_active = True
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class UserAccount(AbstractBaseUser, PermissionsMixin):
    future_date = datetime.datetime.now()
    GENDER = (
        (1, 'male'),
        (2, 'female'),
    )
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True, blank=False, null=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=future_date)
    date_update = models.DateTimeField(auto_now=future_date)
    is_student = models.BooleanField('student status', default=True)
    is_supervisor = models.BooleanField('supervisor status', default=False)
    description = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)

    USERNAME_FIELD = 'username'
    objects = UserManager()

    @property
    def get_full_name(self):
        return f"{self.username}"

    def get_short_name(self):
        return self.username

    def __str__(self):
        return self.username + ' ' + self.last_name

    class Meta:
        verbose_name_plural = "User Accounts"


User = get_user_model()

token_generator = default_token_generator

SHA1_RE = re.compile('^[a-f0-9]{40}$')


class StatusApproved:
    APPROVED = "APPROVED"
    UNDER_REVIEW = "UNDER REVIEW"
    REJECTED = "REJECTED"

    @classmethod
    def get_status_approved(self):
        return [self.APPROVED, self.UNDER_REVIEW, self.REJECTED]


class Subscriptions(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(default='')
    status = models.CharField(max_length=100, default=StatusApproved.UNDER_REVIEW, choices=(
        ("APPROVED", StatusApproved.APPROVED), ("UNDER REVIEW", StatusApproved.UNDER_REVIEW),
        ("REJECTED", StatusApproved.REJECTED))
                              )

    def __str__(self):
        return self.name


class UserSubscription(models.Model):
    student = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    Subscriptions = models.ManyToManyField(Subscriptions, related_name='subscriptions')

    # def __str__(self):
    #     return self.Subscriptions
