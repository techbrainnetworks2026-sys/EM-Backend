from django.apps import AppConfig


class LeaveConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'leave'

    def ready(self):
        """Register signal handlers when app is ready"""
        import leave.signals
