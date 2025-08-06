from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style

style = color_style()


class AppConfig(DjangoAppConfig):
    name = "edc_visit_tracking_app"
    verbose_name = "Visit Tracking Test App"
