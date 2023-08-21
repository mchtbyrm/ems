from django.shortcuts import render
from rest_framework import viewsets, permissions
from events.models import Event, EventPicture
from events.serializers import EventSerializer, EventPictureSerializer


# Create your views here.

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.DjangoModelPermissions]


class EventPictureViewSet(viewsets.ModelViewSet):
    queryset = EventPicture.objects.all()
    serializer_class = EventPictureSerializer
    permission_classes = [permissions.DjangoModelPermissions]

