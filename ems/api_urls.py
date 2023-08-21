from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_extensions.routers import ExtendedDefaultRouter
from account.views import CustomUserViewSet, ProfileViewSet, ProfilePictureViewSet, CreateUserView
from events.views import EventViewSet, EventPictureViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'users', CustomUserViewSet, basename='user')
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'profile-pictures', ProfilePictureViewSet, basename='profile-picture')

router.register(r'events', EventViewSet, basename='event')


user_router = ExtendedDefaultRouter()
(
    user_router.register(r'users', CustomUserViewSet, basename='user')
    .register(r'profiles', ProfileViewSet, basename='user-profile', parents_query_lookups=['user'])
    .register(r'profile-pictures', ProfilePictureViewSet, basename='user-profile-picture',
              parents_query_lookups=['profile__user', 'profile'])
)

event_router = ExtendedDefaultRouter()
(
    event_router.register(r'events', EventViewSet, basename='event')
    .register(r'event-pictures', EventPictureViewSet, basename='event-picture', parents_query_lookups=['event'])
)


api_urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/create-user/', CreateUserView.as_view(), name='create-user'),
    path('api/v1/', include(user_router.urls)),
    path('api/v1/', include(event_router.urls)),
]
