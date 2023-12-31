from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from account.models import CustomUser, Profile, ProfilePicture
from utils import resize_and_save_image


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    user_full_name = serializers.SerializerMethodField()

    def get_user_full_name(self, obj):
        return obj.user.get_full_name()

    class Meta:
        model = Profile
        fields = '__all__'


class ProfilePictureSerializer(serializers.ModelSerializer):

    user_full_name = serializers.SerializerMethodField()

    def get_user_full_name(self, obj):
        return obj.profile.user.get_full_name()

    class Meta:
        model = ProfilePicture
        fields = '__all__'

    def update(self, instance, validated_data):
        try:
            print(validated_data)

            if 'image' in validated_data:
                print("Image")
                image = validated_data.pop('image')
                image = resize_and_save_image(image, image.name, thumbnail=True)
            else:
                print("No image")
                # default image
                image = instance._meta.get_field('image').get_default()

            validated_data['image'] = image
        except Exception as e:
            print(e)
            raise ValidationError("Image could not be updated.")

        return super().update(instance, validated_data)

    def validate_image(self, value):
        if not value.name.endswith(('.jpg', '.jpeg', '.png')):
            raise ValidationError("Image extension is not valid. It should be jpg, jpeg or png.")
        return value
