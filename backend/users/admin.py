from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name',
                    'last_name', 'user_type']
    list_filter = ['email', 'username']
    search_fields = ['username', 'email']
    empty_value_display = '-пусто-'

    def user_type(self, obj):
        if obj.is_superuser:
            return 'Администратор'
        elif obj.is_staff:
            return 'Авторизованный пользователь'
        else:
            return 'Гость'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['user', 'author']
