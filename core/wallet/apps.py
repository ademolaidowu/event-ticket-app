from django.apps import AppConfig


class WalletConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.wallet'
    verbose_name = "User Wallet"

    def ready(self):
        import core.wallet.signals