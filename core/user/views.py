'''
    This view handles the User Management System
'''

# IMPORTS #

import jwt

from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings
from django.urls import reverse
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

from rest_framework import status, views
from rest_framework.generics import (
    CreateAPIView,
    GenericAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema 

from .models import User, UserProfile
from api.utils import Util
# from api.mixins import (
#     UserQuerySetMixin,
# )
from api.serializers.user_serializers import (
    UserLoginSerializer,
    UserRegistrationSerializer,
)




# USER LOG IN VIEW #

class UserLoginAPIView(GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

user_login = UserLoginAPIView.as_view()




# USER LOG OUT VIEW #

class UserLogoutAPIView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response("Log out successful", status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
user_logout = UserLogoutAPIView.as_view()




# USER REGISTRATION VIEW #

class UserRegistrationAPIView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    # POST
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            new_user = serializer.save()

            if new_user:
                user = User.objects.get(email=new_user.email)
                token = RefreshToken.for_user(user).access_token
                current_site=get_current_site(self.request).domain
                related_link = reverse('core.user:verify-email')
                
                url = 'http://'+current_site+related_link+"?token="+str(token)
                email_body = 'Hi '+user.first_name+', \nKindly use the link below to verify your mail \n'+url
                data = {
                    'email_body': email_body,
                    'email_subject': 'Verify your email',
                    'to_email': user.email,
                }
                Util.send_email(data)  

                return Response(status=status.HTTP_201_CREATED) 

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

user_registration = UserRegistrationAPIView.as_view()




# USER REGISTRATION - EMAIL CONFIRMATION VIEW #
class RegisterEmailVerificationAPIView(views.APIView):
    
    token_param_config = openapi.Parameter(
        'token',
        in_=openapi.IN_QUERY,
        description='Description',
        type=openapi.TYPE_STRING,
    )

    # GET 
    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(user_id=payload['user_id'])
            if not user.is_active:
                user.is_active = True
                user.save()
            return Response({'success': 'Account has been successfully activated'}, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Expired Token'}, status=status.HTTP_400_BAD_REQUEST)

        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid Token'}, status=status.HTTP_400_BAD_REQUEST)

register_email_verification = RegisterEmailVerificationAPIView.as_view()




# class RegisterUserInformationAPIView(GenericAPIView):
#     serializer_class = UserProfileDetailSerializer

# register_user_information = RegisterUserInformationAPIView.as_view()




# # ==============================================================================
# # ACCOUNT PROFILE VIEW
# # ==============================================================================

# class UserProfileAPIView(GenericAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserProfileUpdateSerializer
#     permission_classes = [IsAuthenticated]
#     pagination_class = None

#     def get_serializer_class(self):
#         if self.request.method == 'GET':
#             return UserProfileDetailSerializer
#         return UserProfileUpdateSerializer

#     def get_object(self):
#         qs = self.get_queryset()
#         authenticated_user = self.request.user
#         return qs.get(user_id=authenticated_user.user_id)


#     # GET #
#     def get(self, request, *args, **kwargs):
#         obj_data = self.get_object()

#         serializer = UserProfileDetailSerializer(obj_data)
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     # PATCH #
#     def patch(self, request, *args, **kwargs):
#         obj_data = self.get_object()

#         serializer = self.serializer_class(
#             obj_data, data=request.data, partial=True,
#             context={"request": request}
#         )

#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#             return Response(
#                 {'success': True, 'message': 'Your profile has been updated successfully'},
#                 status=status.HTTP_200_OK,
#             )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# user_profile = UserProfileAPIView.as_view()




# class ChangePasswordAPIView(GenericAPIView):
#     queryset = User.accounts.all()
#     permission_classes = [IsAuthenticated]
#     serializer_class = ChangePasswordSerializer

#     def patch(self, request):
#         serializer = self.serializer_class(data=request.data)

#         serializer.is_valid(raise_exception=True)
#         return Response(
#             {'success': True, 'message': 'Your password has been changed successfully'},
#             status=status.HTTP_200_OK,
#         )

# change_password = ChangePasswordAPIView.as_view()





# # ==============================================================================
# # ACCOUNT PASSWORD RESET VIEWS
# # ==============================================================================
# class RequestPasswordResetEmailAPIView(GenericAPIView):
#     serializer_class = PasswordResetEmailRequestSerializer

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         email = request.data['email']

#         if User.objects.filter(email=email).exists():
#             user = User.objects.get(email=email)
#             uidb64 = urlsafe_base64_encode(smart_bytes(user.user_uuid))
#             token = PasswordResetTokenGenerator().make_token(user)

#             current_site=get_current_site(request=request).domain
#             related_link = reverse(
#                 'core.account:password-reset-confirm',
#                 kwargs={'uidb64':uidb64, 'token': token}
#             )
            
#             url = 'http://'+ current_site + related_link
#             email_body = 'Hi '+ user.first_name + ', \nKindly use the link below to reset your password \n' + url
#             data = {
#                 'email_body': email_body,
#                 'email_subject': 'Reset Your Password',
#                 'to_email': user.email,
#             }
#             Util.send_email(data)

#         return Response(
#             {'success': 'We have sent you a link to reset your password'},
#             status=status.HTTP_200_OK
#         )

# request_password_reset = RequestPasswordResetEmailAPIView.as_view()




# class PasswordTokenConfirmAPIView(views.APIView):

#     def get(self, request, uidb64, token):

#         try:
#             user_uuid = smart_str(urlsafe_base64_decode(uidb64))
#             user = User.objects.get(user_uuid=user_uuid)

#             if not PasswordResetTokenGenerator().check_token(user, token):
#                 return Response(
#                     {'error': 'Token is invalid, kindly request a new one'},
#                     status=status.HTTP_401_UNAUTHORIZED
#                 ) 
            
#             return Response(
#                 {'success': True, 'message': 'Credentials Valid', 'uidb64': uidb64, 'token': token},
#                 status=status.HTTP_200_OK
#             )

#         except DjangoUnicodeDecodeError as identifier:
#             if not PasswordResetTokenGenerator().check_token(user, token):
#                 return Response(
#                     {'error': 'Token is invalid, kindly request a new one'},
#                     status=status.HTTP_401_UNAUTHORIZED
#                 )             

# password_token_confirmation = PasswordTokenConfirmAPIView.as_view()




# class SetNewPasswordAPIView(GenericAPIView):
#     serializer_class = SetNewPasswordSerializer

#     def patch(self, request):
#         serializer = self.serializer_class(data=request.data)

#         serializer.is_valid(raise_exception=True)
#         return Response(
#             {'success': True, 'message': 'Password reset success'},
#             status=status.HTTP_200_OK,
#         )

# set_new_password = SetNewPasswordAPIView.as_view()