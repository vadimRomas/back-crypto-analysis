import enum
from typing import Iterable

from django.contrib.auth import get_user_model
from django.db import models
from decimal import Decimal

from payments import PurchasedItem
from payments.models import BasePayment

UserModel = get_user_model()


class A(enum.Enum):
    PRO = 0
    Start = 1
    Minimum = 2


class Currency(enum.Enum):
    USD = 0
    EUR = 1
    UAN = 2
    USDT = 3


class PaymentStatus(enum.Enum):
    pay = 0
    not_pay = 1
    returned = 2


class PaymentModel(models.Model):
    class Meta:
        db_table = 'payment'

    amount = models.FloatField()
    currency = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    created = models.DateField(auto_now=True)
    user = models.ManyToManyField(UserModel, related_name='user')


class Payment(BasePayment):

    def get_failure_url(self) -> str:
        # Return a URL where users are redirected after
        # they fail to complete a payment:
        return f"http://example.com/payments/{self.pk}/failure"

    def get_success_url(self) -> str:
        # Return a URL where users are redirected after
        # they successfully complete a payment:
        return f"http://example.com/payments/{self.pk}/success"

    def get_purchased_items(self) -> Iterable[PurchasedItem]:
        # Return items that will be included in this payment.
        yield PurchasedItem(
            name='The Hound of the Baskervilles',
            sku='BSKV',
            quantity=9,
            price=Decimal(10),
            currency='USD',
        )
