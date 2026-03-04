from django.contrib import admin
from .models import PushSubscription,Notification

# Register your models her

admin.site.register(Notification),
admin.site.register(PushSubscription)