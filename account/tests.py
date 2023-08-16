from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from account.models import CustomUser, Profile, ProfilePicture
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
