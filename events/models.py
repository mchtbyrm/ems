from django.contrib.auth import get_user_model
from django.db import models

from ems.constants import EVENTS_TYPES

User = get_user_model()


# Create your models here.
class Event(models.Model):

    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True, null=True)
    location = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    participants = models.ManyToManyField(User, related_name='participating_events', blank=True)
    event_type = models.CharField(max_length=25, choices=EVENTS_TYPES, default='Other')

    def __str__(self):
        return self.title + '(' + self.event_type + ')' + " by " + self.organizer.username


class EventPicture(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_pictures')
    image = models.ImageField(upload_to='event_pics', default='event_pics/default.png')

    def __str__(self):
        return self.event + "'s Event Picture" + str(self.id)

