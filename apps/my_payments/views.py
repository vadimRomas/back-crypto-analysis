import braintree

from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, get_object_or_404, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from apps.my_payments.config_gateway import confirm_gateway
from apps.my_payments.models import Currency, PaymentStatus, PaymentModel
from apps.my_payments.serializers import PaymentSerializer


class Payment(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = PaymentModel.objects.all()
    serializer_class = PaymentSerializer

    def get_object(self):
        pk = self.request.user.id
        payments = get_object_or_404(PaymentModel, pk=pk)
        return payments


class UpdatePayment(UpdateAPIView):
    queryset = PaymentModel.objects.all()
    serializer_class = PaymentSerializer


def checkout_page(request):
    # generate all other required data that you may need on the #checkout page and add them to context.
    result = confirm_gateway()

    try:
        braintree_client_token = braintree.ClientToken.generate({"customer_id": result.customer.id})
    except:
        braintree_client_token = braintree.ClientToken.generate({})

    context = {'braintree_client_token': braintree_client_token}

    return render(request, 'checkout.html', context)


def payment(request):
    nonce_from_the_client = request.POST['paymentMethodNonce']

    customer_kwargs = {
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "email": request.user.email,
    }

    braintree.Customer.create(customer_kwargs)

    try:
        braintree.Transaction.sale({
            "amount": "0.10",
            "payment_method_nonce": nonce_from_the_client,
            "options": {
                "submit_for_settlement": True
            }
        })
    except:
        return HttpResponse('BAD REQUEST!')

    Payment(
        amount=0.10,
        currency=Currency.USD,
        status=PaymentStatus.pay,
        user='1'
    )
    return HttpResponse('Ok')


# def return_pay(request):
#     pay_id = request.POST['id']
#     payment = Payment(id=pay_id)
#     payment.status = PaymentStatus.not_pay
#
#     return 203
