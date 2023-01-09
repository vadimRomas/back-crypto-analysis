from django.contrib import admin
from django.contrib.auth import get_user_model

UserModel = get_user_model()


@admin.register(UserModel)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email')

    # @admin.display(empty_value='???')
    # def view_birth_date(self, obj):
    #     return obj.birth_date


# admin.site.register(UserAdmin)
