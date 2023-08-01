from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from account.models import Profile, ProfilePicture

User = get_user_model()


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=Profile)
def create_profile_picture(sender, instance, created, **kwargs):
    if created:
        ProfilePicture.objects.create(profile=instance)
