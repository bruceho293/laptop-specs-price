from rest_framework import serializers

from laptop.models import Laptop, Memo, Component

class ComponentSerializer(serializers.ModelSerializer):
    brand_name = serializers.ReadOnlyField(source='brand.name')
    class Meta:
        model = Component
        fields = ['name', 'category', 'brand_name', 'price', 'link', 'updated']

class ComponentListSerializer(serializers.ModelSerializer):
    brand = serializers.ReadOnlyField(source='brand__name')
    total_price = serializers.ReadOnlyField()
    comp_count = serializers.ReadOnlyField()

    class Meta:
        model = Component
        fields = ['name', 'category', 'brand', 'link', 'updated', 'total_price', 'comp_count']
        
class MemoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Memo
        fields = ['name', 'category']

class LaptopListSerializer(serializers.ModelSerializer):
    brand_name = serializers.ReadOnlyField(source='brand.name')
    specs_count = serializers.ReadOnlyField(source='specs.count')
    class Meta:
        model = Laptop
        fields = ['name', 'slug', 'brand_name', 'price', 'specs_count']

class LaptopDetailSerializer(serializers.ModelSerializer):
    brand_name = serializers.ReadOnlyField(source='brand.name')
    specs = MemoSerializer(many=True, read_only=True)
    class Meta:
        model = Laptop
        fields = ['name', 'slug', 'brand_name', 'price', 'link', 'updated', 'specs']