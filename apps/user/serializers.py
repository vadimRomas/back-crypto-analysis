from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer, ValidationError

from apps.user.models import UserAPIKeysModel

UserModel = get_user_model()


class UserSerializer(ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['id', 'email', 'password', 'first_name', 'last_name']
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        try:
            user = UserModel.objects.create_user(**validated_data)
        except ValueError as err:
            raise ValidationError(err)
        return user

    def update(self, user, validated_data):
        user.email = validated_data.get('email', user.email)
        user.content = validated_data.get('password', user.password)
        user.created = validated_data.get('last_name', user.last_name)
        user.save()
        return user


class APIKeysSerializer(ModelSerializer):
    class Meta:
        model = UserAPIKeysModel
        fields = ['id', 'api_key', 'secret_key', 'user', 'name', 'cryptocurrency_exchange', 'testnet', 'market']
        extra_kwargs = {
            'user': {'read_only': True},
            'secret_key': {'write_only': True}
        }

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
