from rest_framework.serializers import ModelSerializer

from apps.cripto_info.models import Bots


class BotsSerializer(ModelSerializer):

    class Meta:
        model = Bots
        fields = ['id', 'name', 'description', 'is_active', 'market', 'time', 'picture']
