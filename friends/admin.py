from django.contrib import admin

from .models import User, Friendship


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username')


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_user', 'to_user', 'status')
