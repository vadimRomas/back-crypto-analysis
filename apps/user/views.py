import bcrypt
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


# def lambda_create_user(event, context):
#     password = event['password']
#     first_name = event['first_name']
#     last_name = event['last_name']
#     email = event['email']
#
#     # Adding the salt to password
#     salt = bcrypt.gensalt()
#     # Hashing the password
#     hashed = bcrypt.hashpw(password, salt)
#
#     # printing the salt
#     print("Salt :")
#     print(salt)
#
#     # printing the hashed
#     print("Hashed")
#     print(hashed)
#     try:
#         User(
#             first_name=first_name,
#             last_name=last_name,
#             email=email,
#             password=hashed
#         )
#     except:
#         return ('Bad Request', 400)
#
#     return ('Created', 201)
#
#
# def lambda_update_user(event, context):
#     user_id = event['id']
#
#
# def lambda_delete_user(event, context):
#     ...
