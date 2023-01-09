from django.urls import path

from apps.user.views import User, UserCreate
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('register', UserCreate.as_view()),
    path('', User.as_view()),
    path('login', TokenObtainPairView.as_view(), name='tokens'),
    path('refresh', TokenRefreshView.as_view(), name='refresh'),
]
