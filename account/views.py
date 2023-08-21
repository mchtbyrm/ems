from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import CreateAPIView

from account.models import CustomUser, Profile, ProfilePicture
from account.serializers import CustomUserSerializer, ProfileSerializer, ProfilePictureSerializer


# Create your views here.
class CreateUserView(CreateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get('pk', None)

        if user_id is not None:
            if self.request.user.is_superuser or self.request.user.is_staff or self.request.user.id == int(user_id):
                return CustomUser.objects.filter(id=user_id)
            else:
                raise PermissionDenied('You do not have permission to view this user.')

        if self.request.user.is_superuser or self.request.user.is_staff:
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=self.request.user.id)

    def update(self, request, *args, **kwargs):
        if not request.user.is_superuser and not request.user.is_staff:
            if request.user.id != int(kwargs['pk']):
                raise PermissionDenied('You do not have permission to update this user.')
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_superuser and not request.user.is_staff:
            if request.user.id != int(kwargs['pk']):
                raise PermissionDenied('You do not have permission to delete this user.')
        return super().destroy(request, *args, **kwargs)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.DjangoModelPermissions]

    def get_queryset(self):
        user_id = self.kwargs.get('parent_lookup_user', None)

        if user_id is not None:
            if self.request.user.is_superuser or self.request.user.is_staff or self.request.user.id == int(user_id):
                return Profile.objects.filter(user__id=user_id)
            else:
                raise PermissionDenied('You do not have permission to view this profile.')

        if self.request.user.is_superuser or self.request.user.is_staff:
            return Profile.objects.all()
        return Profile.objects.filter(user=self.request.user)


class ProfilePictureViewSet(viewsets.ModelViewSet):
    queryset = ProfilePicture.objects.all()
    serializer_class = ProfilePictureSerializer
    permission_classes = [permissions.DjangoModelPermissions]

    def get_queryset(self):

        user_id = self.kwargs.get('parent_lookup_profile__user', None)
        profile_id = self.kwargs.get('parent_lookup_profile', None)

        if user_id is not None and profile_id is not None:
            if self.request.user.is_superuser or self.request.user.is_staff or self.request.user.id == int(user_id):
                return ProfilePicture.objects.filter(profile__user__id=user_id, profile__id=profile_id)
            else:
                raise PermissionDenied('You do not have permission to view this profile picture.')

        if self.request.user.is_superuser or self.request.user.is_staff:
            return ProfilePicture.objects.all()
        return ProfilePicture.objects.filter(profile__user=self.request.user)
