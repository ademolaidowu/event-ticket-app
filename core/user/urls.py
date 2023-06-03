'''
    This file contains urls for the User Management System
'''

from django.urls import path


from .views import (
    user_login,
    user_logout,
    user_registration,
    register_email_verification,
#     request_password_reset,
#     password_token_confirmation,
#     set_new_password,
#     register_user_information,
#     user_profile,
#     change_password,
)



app_name = 'core.user'
urlpatterns = [
    path('login/', user_login, name='login-user'),
    path('logout/', user_logout, name='logout'),
    path('register/', user_registration, name='register-user'),
    path('register/email-verification/', register_email_verification, name='verify-email'),
#     path('register/user-information/', register_user_information, name='user-information'),
#     path('profile/', user_profile, name='user-profile'),
#     path('change-password/', change_password, name='user-profile'),
#     path('password-reset-email/', request_password_reset, name='password-reset-request'),
#     path('password-reset/<uidb64>/<token>/', password_token_confirmation, name='password-reset-confirm'),
#     path('password-reset-complete/', set_new_password, name='password-reset-complete'),
]