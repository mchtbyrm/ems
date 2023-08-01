from django.urls import path, include
from rest_framework.routers import DefaultRouter

from account.views import CustomUserViewSet, ProfileViewSet, ProfilePictureViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'users', CustomUserViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'profile-pictures', ProfilePictureViewSet)


api_urlpatterns = [
    path('api/v1/', include(router.urls)),
]
