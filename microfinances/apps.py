from django.apps import AppConfig


class MicrofinancesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'microfinances'

    def ready(self):
        import microfinances.signals
