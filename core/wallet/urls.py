'''
    This file contains urls for the Wallet Views
'''
from django.urls import path

from core.wallet.views import (
    wallet_information_view,
    wallet_deposit_view,
    verify_deposit_view,
)



app_name = 'core.wallet'

urlpatterns = [
    path('', wallet_information_view, name='wallet-info'),
    path('deposit/', wallet_deposit_view, name='wallet-deposit'),
    path('deposit/verify/<str:reference>/', verify_deposit_view, name='verify-deposit'),
]