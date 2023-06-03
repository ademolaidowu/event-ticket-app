'''
    This file contains validators for the serializers
'''

import re
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from core.user.models import User



# SERIALIZER VALIDATORS #

unique_user_username = UniqueValidator(queryset=User.objects.all(), lookup='iexact', message='A user with this username already exists')
unique_user_email = UniqueValidator(queryset=User.objects.all(), lookup='iexact', message='A user with this email already exists')


def validate_username(value):
    if not re.match(r'^[A-Za-z0-9_]+$', value):
        raise serializers.ValidationError('Username can only contain alphanumeric characters or underscores.')
    else: 
        return value


def validate_name(value):
    if not re.match(r'^[A-Za-z]+$', value):
        raise serializers.ValidationError('Names can only contain letters')
    else: 
        return value


def validate_password_format(value):
    if not re.match(r'^[A-Za-z0-9@!]+$', value):
        raise serializers.ValidationError('Username can only contain alphanumeric characters or special characters like @, !') 
    elif len(value) < 8:
        raise serializers.ValidationError('Password needs to be at least 8 characters.')
    else:
        return value


def is_amount(value):
    if value <= 0:
        raise serializers.ValidationError('Invalid amount')
    return value

