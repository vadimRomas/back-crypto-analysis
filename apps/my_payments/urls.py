from django.urls import path

from apps.my_payments.views import Payment, checkout_page, payment, UpdatePayment

urlpatterns = [
    path('', Payment.as_view()),
    path('checkout', checkout_page),
    path('pay', payment),
    path('return/<int:pk>', UpdatePayment.as_view())
]
