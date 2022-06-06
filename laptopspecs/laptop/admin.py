from django.contrib import admin

from laptop.models import Laptop, Component, Brand, Memo, LaptopNote
from laptop.managers import ComponentType

class SpecsInline(admin.TabularInline):
    model = LaptopNote
    verbose_name = "Specification"
    fields = ('laptop', 'memo', 'qnty', 'get_category')
    readonly_fields = ('get_category',)
    extra = 0

    @admin.display(description="Component Type")
    def get_category(self, obj):
        return obj.memo.category
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "memo":
            kwargs["queryset"] = Memo.objects.all().order_by("category", "name")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# Register your models here.
@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "link")
    ordering = ['name']

@admin.register(Memo)
class MemoAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    ordering = ['category', 'name']

@admin.register(LaptopNote)
class LaptopNoteAdmin(admin.ModelAdmin):
    ordering = ['laptop']

@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "brand", "price", "updated")
    ordering = ['category', 'name']

@admin.register(Laptop)
class LaptopAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "updated")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ['name']

    inlines = [SpecsInline]
    exclude = ("specs",)