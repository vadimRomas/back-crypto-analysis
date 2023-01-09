from rest_framework.serializers import ModelSerializer

from apps.my_payments.models import PaymentModel


class PaymentSerializer(ModelSerializer):
    class Meta:
        model = PaymentModel
        fields = ["id", "amount", "currency", "status", "user"]
        extra_kwargs = {
            "user": {"read_only": True}
        }

