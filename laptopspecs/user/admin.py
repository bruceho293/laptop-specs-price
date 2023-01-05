from django.contrib import admin

from user.models import UserProfile, UserImpression
from laptop.models import Laptop

class ImpressionInline(admin.TabularInline):
    model = UserImpression
    verbose_name = "Laptop Likes-Dislikes"
    fields = ('profile', 'laptop', 'liked')
    extra = 0
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "laptop":
            kwargs["queryset"] = Laptop.objects.all().order_by("name")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# Register your models here.
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user']
    ordering = ['user__username']

    inlines = [ImpressionInline]
    exclude = ("imp_lapop",)