from django.apps import AppConfig


class AnnouncementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'announcement'

    def ready(self):
        """Register signal handlers when app is ready"""
        import announcement.signals
