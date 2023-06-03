from django.contrib import auth
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import (
    smart_str,
    force_str,
    smart_bytes,
    DjangoUnicodeDecodeError,
)
from django.utils.http import (
    urlsafe_base64_decode,
    urlsafe_base64_encode,
)

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from django_countries.serializers import CountryFieldMixin

from core.user.models import (
    User,
    UserProfile,
)


from api.validators import (
    unique_user_username,
    unique_user_email,
    validate_username,
    validate_name,
    validate_password_format,
)




# USER DATA SERIALIZER #

class UserIdentificationSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=100,
        required=False,
        read_only=True,
    ) 


class UserPublicSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name',
            'last_name', 'username',
        ]


class UserProfilePublicSerializer(CountryFieldMixin, serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = [
            'user_type', 'business_id',
            'phone_number', 'gender', 'address',
            'city', 'country',
        ]  




# USER LOGIN SERIALIZER #

class UserLoginSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
        max_length=255, required=True,
    )

    password = serializers.CharField(
        max_length=50, write_only=True,
        required=True,
    )

    username = serializers.CharField(
        max_length=255, read_only=True,
    )

    tokens = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email', 'username',
            'password', 'tokens',
        ]

    def get_tokens(self, obj):
        user = User.objects.get(email=obj['email'])

        return {
            'access': user.tokens()['access'],
            'refresh': user.tokens()['refresh']
        }

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        user = auth.authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Email is not verified')
        if not user.profile.status == 'enabled':
            raise AuthenticationFailed('Account has been blocked')

        return {
            'email':user.email,
            'username':user.username,
            'tokens': user.tokens
        }




# USER REGISTRATION SERIALIZER #

class UserRegistrationSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
        max_length=255, required=True,
        validators=[unique_user_email],
    )

    username = serializers.CharField(
        required=True,
        validators=[validate_username, unique_user_username],
    )

    first_name = serializers.CharField(
        required=True, validators=[validate_name],
    )

    last_name = serializers.CharField(
        required=True, validators=[validate_name],
    )

    password = serializers.CharField(
        max_length=50, write_only=True, required=True,
        validators=[validate_password, validate_password_format],
    )

    password2 = serializers.CharField(
        max_length=50, write_only=True, required=True,
    )

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'username',
            'email', 'password', 'password2',
        ]
        extra_kwargs = {
            "user_id": {"read_only": True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'].lower(),
            first_name=validated_data['first_name'].capitalize(),
            last_name=validated_data['last_name'].capitalize(),
        )
        
        user.set_password(validated_data['password'])
        user.save()

        return user


























# # ==============================================================================
# # PASSWORD RESET SERIALIZERS
# # ==============================================================================

# class PasswordResetEmailRequestSerializer(serializers.Serializer):

#     email = serializers.EmailField(
#         min_length=6,
#         required=True,
#     )

#     class Meta:
#         fields = [
#             'email',
#         ]




# class SetNewPasswordSerializer(serializers.Serializer):

#     password = serializers.CharField(
#         max_length=50,
#         write_only=True,
#         required=True,
#         validators=[validate_password, validate_password_format],
#     )

#     password2 = serializers.CharField(
#         max_length=50,
#         write_only=True,
#         required=True,
#     )

#     token = serializers.CharField(
#         write_only=True,
#         required=True,
#     )

#     uidb64 = serializers.CharField(
#         write_only=True,
#         required=True,
#     )

#     class Meta:
#         fields = [
#             'password', 'password2',
#             'token', 'uidb64',
#         ]

#     def validate(self, attrs):

#         if attrs['password'] != attrs['password2']:
#             raise serializers.ValidationError({"password": "Password fields didn't match."})

#         try:
#             password = attrs.get('password')
#             token = attrs.get('token')
#             uidb64 = attrs.get('uidb64')

#             user_uuid = force_str(urlsafe_base64_decode(uidb64))
#             user = User.objects.get(user_uuid=user_uuid)
#             if not PasswordResetTokenGenerator().check_token(user, token):
#                 raise AuthenticationFailed('The reset link is invalid', 401)

#             user.set_password(password)
#             user.save()

#             return(user)
            
#         except Exception as e:
#             raise AuthenticationFailed('The reset link is invalid', 401)
        
#         return super().validate(attrs)
    









# class UserRegistrationInformationSerializer(CountryFieldMixin, serializers.ModelSerializer):

#     user = UserPublicSerializer()

#     gender = serializers.ChoiceField(
#         choices=UserProfile.Gender,
#     )


#     class Meta:
#         model = UserProfile
#         fields = [
#             'user',
#             'user_type',
#             'business_id',
#             'phone_number',
#             'gender',
#             'address',
#             'city',
#             'country',
             
#         ]
#         extra_kwargs = {
#             'city': {'required': True},
#             'country': {'required': True},
#             'user.email': {'read_only': True},
#         }

#         # def validate_user_username(self, value):
#         #     user = self.context['request'].user
#         #     if User.objects.exclude(user_uuid=user.user_uuid).filter(username__iexact=value).exists():
#         #         raise serializers.ValidationError({"username": "This username already exists."})
#         #     return value

#         def update(self, instance, validated_data):
#             user_data = validated_data.pop('user')

#             user = User.accounts.get(user_id=instance.user.user_id)
#             print(user)

#             # instance.first_name = validated_data['first_name']
#             # instance.last_name = validated_data['last_name']
#             # instance.email = validated_data['email']
#             # instance.username = validated_data['username']
#             instance.save()

#             user.first_name = user_data.get('first_name')
#             user.last_name = user_data.get('last_name')
#             user.username = user_data.get('username')
#             user.save()

#             return instance









# # ==============================================================================
# # ACCOUNT PROFILE SERIALIZER
# # ==============================================================================

# class UserProfileDetailSerializer(serializers.ModelSerializer):

#     profile = UserProfilePublicSerializer()

#     class Meta:
#         model = User
#         fields = [
#             'email', 'username', 'first_name', 'last_name', 'profile',
#         ]




# class UserProfileUpdateSerializer(serializers.ModelSerializer):

#     username = serializers.CharField(
#         required=True,
#         validators=[validate_username, unique_user_username],
#     )

#     first_name = serializers.CharField(
#         required=True,
#         validators=[validate_name],
#     )

#     last_name = serializers.CharField(
#         required=True,
#         validators=[validate_name],
#     )

#     profile = UserProfilePublicSerializer()

#     class Meta:
#         model = User
#         fields = [
#             'username', 'first_name', 'last_name', 'profile',
#         ]
#         extra_kwargs = {
#             'email': {'read_only': True},
#         }

#         # def validate_user_username(self, value):
#         #     user = self.context['request'].user
#         #     if User.objects.exclude(user_uuid=user.user_uuid).filter(username__iexact=value).exists():
#         #         raise serializers.ValidationError({"username": "This username already exists."})
#         #     return value

#     def update(self, instance, validated_data):
#         #current_user = self.context['request'].user

#         profile_data = validated_data.pop('profile', [])
#         profile = instance.profile
#         # user = User.accounts.get(user_id=current_user.user_id)

#         instance.username = validated_data.get('username', instance.username)
#         instance.first_name = validated_data.get('first_name', instance.first_name)
#         instance.last_name = validated_data.get('last_name', instance.last_name)
#         instance.save()

#         if profile_data != []:
#             profile.user_type = profile_data.get('user_type', profile.user_type)
#             profile.business_id = profile_data.get('business_id', profile.business_id)
#             profile.phone_number = profile_data.get('phone_number', profile.phone_number)
#             profile.gender = profile_data.get('gender', profile.gender)
#             profile.address = profile_data.get('address', profile.address)
#             profile.city = profile_data.get('city', profile.city)
#             profile.country = profile_data.get('country', profile.country)
#             profile.save()

#         return instance




# class ChangePasswordSerializer(serializers.ModelSerializer):

#     old_password = serializers.CharField(
#         write_only=True,
#         required=True,
#     )

#     password = serializers.CharField(
#         max_length=50,
#         write_only=True,
#         required=True,
#         validators=[validate_password, validate_password_format],
#     )

#     password2 = serializers.CharField(
#         max_length=50,
#         write_only=True,
#         required=True,
#     )


#     class Meta:
#         model = User
#         fields = [
#             'old_password',
#             'password',
#             'password2',
#         ]

#     def validate(self, attrs):
#         if attrs['password'] != attrs['password2']:
#             raise serializers.ValidationError({"password": "Password fields didn't match."})
#         return attrs

#     def validate_old_password(self, value):
#         user = self.context['request'].user
#         if not user.check_password(value):
#             raise serializers.ValidationError({"old_password": "Incorrect password."})
#         return value

#     def update(self, instance, validated_data):
#         instance.set_password(validated_data['password'])
#         instance.save()
#         return instance



