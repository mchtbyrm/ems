from django.contrib import admin

from events.models import Event, EventPicture

# Register your models here.
admin.site.register(Event)
admin.site.register(EventPicture)
