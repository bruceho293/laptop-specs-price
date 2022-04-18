from django.contrib import admin

from laptop.models import Laptop, Component, Brand

# Register your models here.
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "link")

@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "brand", "price", "updated")
    ordering = ['-updated']

@admin.register(Laptop)
class LaptopAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "brand", "price", "updated")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ['-updated']