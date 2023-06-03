import requests
from django.conf import settings

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from core.wallet.models import (
    Wallet,
    WalletTransaction,
)
from api.serializers.wallet_serializers import (
    WalletSerializer,
    DepositSerializer,
)




# WALLET INFORMATION VIEW #

class WalletInformation(GenericAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            wallet_data = self.get_queryset().filter(user=user)
            serializer = WalletSerializer(wallet_data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(status=status.HTTP_404_NOT_FOUND)

wallet_information_view = WalletInformation.as_view()




# WALLET DEPOSIT VIEW #

class DepositFund(GenericAPIView):
    serializer_class = DepositSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request}
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

wallet_deposit_view = DepositFund.as_view()




# WALLET DEPOSIT VERIFICATION VIEW #

class VerifyDeposit(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, reference):
        try:
            transaction = WalletTransaction.objects.get(
                paystack_payment_reference=reference,
                wallet__user=request.user
            )
            reference = transaction.paystack_payment_reference

            url = 'https://api.paystack.co/transaction/verify/{}'.format(reference)
            headers = {"authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
            r = requests.get(url, headers=headers)
            resp = r.json()

            if resp['data']['status'] == 'success':
                transaction_status = resp['data']['status']
                amount = resp['data']['amount']
                WalletTransaction.objects.filter(
                    paystack_payment_reference=reference).update(transaction_status=transaction_status, amount=amount)
                
                return Response(resp['data']['status'], status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

verify_deposit_view = VerifyDeposit.as_view()
