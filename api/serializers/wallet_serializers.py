# IMPORTS #

import requests

from django.conf import settings
from django.db.models import Sum

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from api.validators import is_amount
from core.user.models import User
from core.wallet.models import(
    Wallet,
    WalletTransaction,
)




# USER INFORMATION SERIALIZER #

class UserInfoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'username',
        ]  




# WALLET SERIALIZER #

class WalletSerializer(serializers.ModelSerializer):

    user = UserInfoSerializer(read_only=True)
    balance = serializers.SerializerMethodField()


    class Meta:
        model = Wallet
        fields = [
            'user',
            'balance',
        ]

    def get_balance(self, obj):
        bal = WalletTransaction.objects.filter(
            wallet=obj, transaction_status="success").aggregate(Sum('amount'))['amount__sum']

        return bal




# WALLET DEPOSIT SERIALIZER #

class DepositSerializer(serializers.Serializer):

    amount = serializers.IntegerField(validators=[is_amount])
    email = serializers.EmailField(read_only=True)

    def save(self, **kwargs):
        user = self.context['request'].user
        wallet = Wallet.objects.get(user=user)

        self.validated_data['email'] = user.email
        data = self.validated_data
        url = 'https://api.paystack.co/transaction/initialize'
        headers = {"authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}

        r = requests.post(url, headers=headers, data=data)
        response = r.json()
        self.context['response'] = response

        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type="deposit",
            amount= data["amount"],
            paystack_payment_reference=response['data']['reference'],
            transaction_status="pending",
        )
        return response
    
    def to_representation(self, instance):
        response = self.context.get('response')

        representation = {
            'amount': instance['amount'],
            'email': instance['email'],
            'reference': response['data']['reference'],
            'url': response['data']['authorization_url']
        }
        return representation


