import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient

from account.models import CustomUser, Profile, ProfilePicture
from account.serializers import CustomUserSerializer, ProfileSerializer, ProfilePictureSerializer
from account.validators import CustomPasswordValidator


# Create your tests here.
class AccountModelTestCase(TestCase):
    def setUp(self):
        self.password_validator = CustomPasswordValidator()

        self.data_for_superuser = {
            "email": "superuser@superuser.com",
            "username": "superuser",
            "first_name": "super",
            "last_name": "user",
            "password": "Strong_1"
        }

        self.data_for_user = {
            "email": "user@user.com",
            "username": "user",
            "first_name": "user",
            "last_name": "user",
            "password": "Strong_1"
        }

        self.password_validator.validate(self.data_for_superuser['password'])
        self.password_validator.validate(self.data_for_user['password'])

        self.superuser = CustomUser.objects.create_superuser(**self.data_for_superuser)
        self.user = CustomUser.objects.create(**self.data_for_user)

    def test_superuser_creation(self):
        self.assertEqual(CustomUser.objects.filter(is_superuser=True).count(), 1)
        self.assertEqual(self.superuser.email, self.data_for_superuser['email'])
        self.assertEqual(self.superuser.username, self.data_for_superuser['username'])
        self.assertTrue(self.superuser.is_staff)
        self.assertTrue(self.superuser.is_superuser)

    def test_superuser_creation_who_is_not_staff_or_is_not_superuser(self):
        with self.assertRaises(ValueError):
            CustomUser.objects.create_superuser(email="superuser2@superuser.com", username="superuser2",
                                                password="strong_psw", is_staff=False)
        with self.assertRaises(ValueError):
            CustomUser.objects.create_superuser(email="superuser2@superuser.com", username="superuser2",
                                                password="strong_psw", is_superuser=False)

    def test_user_creation(self):
        self.assertEqual(CustomUser.objects.filter(is_superuser=False).count(), 1)
        self.assertEqual(self.user.email, self.data_for_user['email'])
        self.assertEqual(self.user.username, self.data_for_user['username'])
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    def test_get_full_name(self):
        self.assertEqual(self.superuser.get_full_name(), self.superuser.first_name + " " + self.superuser.last_name)
        self.assertEqual(self.user.get_full_name(), self.user.first_name + " " + self.user.last_name)

    def test_user_creation_without_email(self):
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(email="", username="user2", password="strong_psw")

    def test_user_creation_without_username(self):
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(email="user2@user2.com", username="", password="strong_psw")

    def test_user_creation_without_password(self):
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(email="user2@user2.com", username="user2", password="")

    def test_user_creation_with_existing_email(self):
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(email="user@user.com", username="user2", password="strong_psw")

    def test_user_creation_with_existing_username(self):
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(email="user2@user2.com", username="user", password="strong_psw")

    def test_user_representation(self):
        self.assertEqual(str(self.superuser), self.superuser.username)
        self.assertEqual(str(self.user), self.user.username)

    def test_update_user_email(self):
        self.user.email = "user@new.com"
        self.user.save()
        self.assertEqual(self.user.email, "user@new.com")

    def test_update_user_username(self):
        self.user.username = "new_user"
        self.user.save()
        self.assertEqual(self.user.username, "new_user")

    def test_validate_password(self):
        validation_tests = [
            ("short", "This password must contain at least 8 characters."),
            ("no_number", "This password must contain at least 1 digit."),
            ("12345678", "This password must contain at least 1 letter."),
            ("no_upper_123", "This password must contain at least 1 uppercase letter."),
            ("NO_LOWER_123", "This password must contain at least 1 lowercase letter."),
            ("noSpecial123", "This password must contain at least 1 special character."),
        ]

        expected_help_text = (
            "Your password must contains at least 8 characters, "
            "1 digit, 1 letter, 1 uppercase letter, 1 lowercase letter and 1 special character."
        )

        for password, message in validation_tests:
            with self.assertRaises(ValidationError) as context:
                self.password_validator.validate(password)
            self.assertEqual(context.exception.message, message)

        self.assertEqual(self.password_validator.get_help_text(), expected_help_text)

    def test_user_deletion(self):
        self.user.delete()
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(CustomUser.objects.filter(is_superuser=False).count(), 0)
        self.assertEqual(CustomUser.objects.filter(is_superuser=True).count(), 1)
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(ProfilePicture.objects.count(), 1)

    def test_profile_creation(self):
        self.assertEqual(Profile.objects.count(), 2)
        self.assertEqual(self.superuser.profile.user, self.superuser)
        self.assertEqual(self.user.profile.user, self.user)

    def test_profile_representation(self):
        self.assertEqual(str(self.superuser.profile), self.superuser.username + "'s Profile")
        self.assertEqual(str(self.user.profile), self.user.username + "'s Profile")

    def test_profile_picture_creation(self):
        self.assertEqual(ProfilePicture.objects.count(), 2)
        self.assertEqual(self.superuser.profile.profile_picture.profile, self.superuser.profile)
        self.assertEqual(self.user.profile.profile_picture.profile, self.user.profile)

    def test_profile_picture_representation(self):
        self.assertEqual(str(self.superuser.profile.profile_picture), self.superuser.username + "'s Profile Picture")
        self.assertEqual(str(self.user.profile.profile_picture), self.user.username + "'s Profile Picture")


class AccountAPITestCase(APITestCase):
    def setUp(self):
        self.custom_user_serializer = CustomUserSerializer()
        self.profile_serializer = ProfileSerializer()
        self.profile_picture_serializer = ProfilePictureSerializer()

        self.data_for_superuser = {
            "email": "superuser@superuser.com",
            "username": "superuser",
            "first_name": "super",
            "last_name": "user",
            "password": "Strong_1"
        }

        self.data_for_user = {
            "email": "user@user.com",
            "username": "user",
            "first_name": "user",
            "last_name": "user",
            "password": "Strong_1"
        }

        self.data_for_user2 = {
            "email": "user2@user2.com",
            "username": "user2",
            "first_name": "user2",
            "last_name": "user2",
            "password": "Strong_1"
        }

        self.superuser = CustomUser.objects.create_superuser(**self.data_for_superuser)
        self.client_for_superuser = self.create_client(user=self.superuser)

        self.user = CustomUser.objects.create(**self.data_for_user)
        self.client_for_user = self.create_client(user=self.user)
        self.user_detail = reverse('user-detail', args=[self.user.id])
        self.user_profile_detail = reverse('user-profile-detail', args=[self.user.id, self.user.profile.id])
        self.user_profile_picture_detail = reverse('user-profile-picture-detail',
                                                   args=[self.user.id,
                                                         self.user.profile.id,
                                                         self.user.profile.profile_picture.id])

        self.user2 = CustomUser.objects.create(**self.data_for_user2)
        self.client_for_user2 = self.create_client(user=self.user2)
        self.user2_detail = reverse('user-detail', args=[self.user2.id])

        # unauthorized client
        self.client = self.create_client()

    def test_api_get_users_profiles_and_profile_pictures(self):
        user_list = reverse('user-list')
        profile_list = reverse('profile-list')
        profile_picture_list = reverse('profile-picture-list')

        response = self.client_for_superuser.get(user_list)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

        response = self.client_for_superuser.get(profile_list)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

        response = self.client_for_superuser.get(profile_picture_list)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

        response = self.client_for_user.get(user_list)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        response = self.client_for_user.get(profile_list)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        response = self.client_for_user.get(profile_picture_list)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        response = self.client.get(user_list)
        self.assertEqual(response.status_code, 403)

        response = self.client.get(profile_list)
        self.assertEqual(response.status_code, 403)

        response = self.client.get(profile_picture_list)
        self.assertEqual(response.status_code, 403)

    def test_superuser_can_access_all_details(self):

        response = self.client_for_superuser.get(self.user_detail)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.user.id)

        response = self.client_for_superuser.get(self.user2_detail)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.user2.id)

    def test_normal_user_can_access_only_own_details(self):

        response = self.client_for_user.get(self.user_detail)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.user.id)

        response = self.client_for_user.get(self.user2_detail)
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_cannot_access_any_details(self):

        response = self.client.get(self.user_detail)
        self.assertEqual(response.status_code, 403)

        response = self.client.get(self.user2_detail)
        self.assertEqual(response.status_code, 403)

    def test_superuser_can_update_all_details(self):

        self.data_for_user['username'] = "new_username"

        response = self.client_for_superuser.put(self.user_detail, self.data_for_user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], "new_username")

        new_image_directory = os.path.join(settings.MEDIA_ROOT, 'profile_pics')
        image_path = os.path.join(new_image_directory, 'new_photo.jpeg')
        new_picture_data = open(image_path, 'rb').read()
        new_picture = SimpleUploadedFile('new_photo.jpeg', new_picture_data, content_type='image/jpeg')

        profile_picture_data = self.profile_picture_serializer.data
        profile_picture_data['image'] = new_picture
        profile_picture_data['profile'] = self.user.profile.id

        response = self.client_for_superuser.put(self.user_profile_picture_detail, profile_picture_data)
        self.assertEqual(response.status_code, 200)

        profile_picture_data['image'] = ''
        response = self.client_for_superuser.put(self.user_profile_picture_detail, profile_picture_data)
        self.assertEqual(response.status_code, 200)

        image_path = os.path.join(new_image_directory, 'gif_image.gif')
        new_picture_data = open(image_path, 'rb').read()
        new_picture = SimpleUploadedFile('gif_image.gif', new_picture_data, content_type='image/gif')

        profile_picture_data['image'] = new_picture

        response = self.client_for_superuser.put(self.user_profile_picture_detail, profile_picture_data)
        print(response.content)
        self.assertEqual(response.status_code, 400)



        self.data_for_user2['username'] = "new_username2"

        response = self.client_for_superuser.put(self.user2_detail, self.data_for_user2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], "new_username2")


    def test_normal_user_can_update_only_own_details(self):

        self.data_for_user['username'] = "new_username"

        response = self.client_for_user.put(self.user_detail, self.data_for_user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], "new_username")

        self.data_for_user2['username'] = "new_username2"

        response = self.client_for_user.put(self.user2_detail, self.data_for_user2)
        self.assertEqual(response.status_code, 403)

    def test_unauthenticated_user_cannot_update_any_details(self):

        self.data_for_user['username'] = "new_username"

        response = self.client.put(self.user_detail, self.data_for_user)
        self.assertEqual(response.status_code, 403)

        self.data_for_user2['username'] = "new_username2"

        response = self.client.put(self.user2_detail, self.data_for_user2)
        self.assertEqual(response.status_code, 403)

    def test_superuser_can_delete_all_details(self):

        response = self.client_for_superuser.delete(self.user_detail)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(CustomUser.objects.count(), 2)
        self.assertEqual(Profile.objects.count(), 2)
        self.assertEqual(ProfilePicture.objects.count(), 2)

        response = self.client_for_superuser.delete(self.user2_detail)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(ProfilePicture.objects.count(), 1)

    def test_normal_user_can_delete_only_own_details(self):

        response = self.client_for_user.delete(self.user_detail)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(CustomUser.objects.count(), 2)
        self.assertEqual(Profile.objects.count(), 2)
        self.assertEqual(ProfilePicture.objects.count(), 2)

        response = self.client_for_user.delete(self.user2_detail)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(CustomUser.objects.count(), 2)

    def test_unauthenticated_user_cannot_delete_any_details(self):

        response = self.client.delete(self.user_detail)
        self.assertEqual(response.status_code, 403)

        response = self.client.delete(self.user2_detail)
        self.assertEqual(response.status_code, 403)

    def create_client(self, user=None):
        client = APIClient()
        if user is not None:
            client.force_authenticate(user=user)
        return client
