from django.contrib import admin
from .models import shopping,ShoeSize,UserProfile,Category,Order

admin.site.register(shopping)

admin.site.register(ShoeSize)

admin.site.register(Order)

admin.site.register(Category)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'email', 'profile_image')
