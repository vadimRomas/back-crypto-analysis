from django.contrib import admin
from apps.my_payments.models import PaymentModel


@admin.register(PaymentModel)
class MyPaymentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'currency', 'status')
#     fields = ['id', 'amount', 'currency', 'status']

    # def get_users(self, obj):
    #     return "\n".join([p.users for p in obj.user.all()])

    # @admin.display(empty_value='???')
    # def view_birth_date(self, obj):
    #     return obj.birth_date


# admin.site.register(MyPaymentsAdmin)
