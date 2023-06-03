from django.apps import AppConfig


class EventConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.event'
    verbose_name = "Event Database"
