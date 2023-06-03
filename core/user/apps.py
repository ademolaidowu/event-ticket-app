from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.user'
    verbose_name = "User Account Database"

    def ready(self):
        import core.user.signals
