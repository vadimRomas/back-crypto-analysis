from rest_framework.serializers import ModelSerializer


class AWSSerializer(ModelSerializer):
    class Meta:
        fields = ["id", "bucket", "url", "user"]
