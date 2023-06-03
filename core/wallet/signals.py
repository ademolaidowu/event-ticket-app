from django.db.models.signals import post_save
from django.dispatch import receiver

from core.user.models import User
from core.wallet.models import Wallet


# USER WALLET SIGNALS #

@receiver(post_save, sender=User)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.wallet.save()