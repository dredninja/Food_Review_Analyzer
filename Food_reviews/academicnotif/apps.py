from django.apps import AppConfig


class AcademicnotifConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'academicnotif'
class YourAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'academicnotif'

    def ready(self):
        import academicnotif.signals