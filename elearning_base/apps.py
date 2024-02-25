from django.apps import AppConfig


class ElearningBaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'elearning_base'

    #Override the ready method to import signals
    def ready(self):
        import elearning_base.signals
