from django.apps import AppConfig


class ProductionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rv_grafica.production"
    verbose_name = "Órdenes de Producción"
