# IMPORTS #

import uuid

from django.db import models
from django.db.models import Sum
from core.user.models import User
from django.utils import timezone




def generate_wallet_id():
    code = str(uuid.uuid4()).split("-")[-1] #generate unique wallet id

    try:
        qs_exists = Wallet.objects.filter(wallet_id=code).exists()
        if qs_exists:
            return generate_wallet_id()
        else:
            return 'w'+code
    except:
        return 'w'+code




class Wallet(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="wallet",
    )

    wallet_id = models.CharField(
        db_index=True,
        max_length=15,
        blank=False,
        null=False,
        default=generate_wallet_id,
        verbose_name='Wallet ID',
        editable=False,
    )

    date_created = models.DateTimeField(
        auto_now_add=True,
    )

    date_updated = models.DateTimeField(
        default=timezone.now,
    )

    @property
    def balance(self):
        transactions = self.transactions
        bal = transactions.filter(
            transaction_status="success"
        ).aggregrate(Sum('amount'))['amount__sum']

        return bal

    def __str__(self):
        return self.user.__str__()




class WalletTransaction(models.Model):

    transaction_type_choices = (
        ('deposit', 'Deposit'), 
        ('withdraw', 'Withdraw'), 
        ('transfer', 'Transfer'),
    )

    transaction_status_choices = (
        ('pending', 'Pending'), 
        ('success', 'Success'), 
        ('failed', 'Failed'),
    )


    wallet = models.ForeignKey(
        "Wallet",
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    transaction_type = models.CharField(
        max_length=25,
        choices=transaction_type_choices,
        blank=False,
        null=False,
        verbose_name='Transaction Type',
    )

    amount = models.DecimalField(
        default=0.00,
        blank=False,
        null=False,
        max_digits=100,
        decimal_places=2,
        verbose_name='Transaction Amount',
    )

    transaction_status = models.CharField(
        max_length=25,
        choices=transaction_status_choices,
        default='pending',
        blank=False,
        null=False,
        verbose_name='Transaction Type',
    )

    date_created = models.DateTimeField(
        auto_now_add=True,
    )

    date_updated = models.DateTimeField(
        default=timezone.now,
    )

    paystack_payment_reference = models.CharField(
        max_length=100,
        verbose_name="Paystack Ref No."
    )

    def __str__(self):
        return "{} - {}".format(self.wallet.user.__str__(), self.id)

