from rest_framework import serializers

from events.models import Event, EventPicture


class EventPictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventPicture
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    event_pictures = serializers.SerializerMethodField()

    def get_event_pictures(self, obj):
        event_pictures = obj.event_pictures.filter(event=obj)
        return EventPictureSerializer(event_pictures, many=True).data

    class Meta:
        model = Event
        fields = '__all__'



