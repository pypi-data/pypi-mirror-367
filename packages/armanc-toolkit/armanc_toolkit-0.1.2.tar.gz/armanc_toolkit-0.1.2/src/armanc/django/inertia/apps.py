from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules

class InertiaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'armanc.django.inertia'
    verbose_name = 'Armanc Django Inertia'

    def ready(self):
        return autodiscover_modules("adapters")

