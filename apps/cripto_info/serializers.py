from rest_framework.serializers import ModelSerializer

from apps.cripto_info.models import Bots


# from apps.cripto_info.models import GraphModel
#
#
# class GraphSerializer(ModelSerializer):
#
#     class Meta:
#         model = GraphModel
#         fields = ["id"]

class BotsSerializer(ModelSerializer):

    class Meta:
        model = Bots
        fields = '__all__'
