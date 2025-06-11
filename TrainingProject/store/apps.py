from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "store"

    def ready(self):
        from django.contrib.auth.models import Group
        Group.objects.get_or_create(name='Customers')

