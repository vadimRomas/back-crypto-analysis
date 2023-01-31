from django.contrib.auth import get_user_model
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView, get_object_or_404, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

from apps.user.serializers import UserSerializer

UserModel = get_user_model()


class User(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        pk = self.request.user.id
        user = get_object_or_404(UserModel, pk=pk)
        return user


class UserCreate(CreateAPIView):
    permission_classes = [AllowAny]
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer


class ListUsers(ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer


