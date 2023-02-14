import math
from rest_framework import serializers

from laptop.models import Laptop, Memo, Component, Brand
from laptop.utils import get_closest_components_price
from user.models import UserImpression

class BaseUserImpressionSerializer(serializers.Serializer):
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()

    class Meta:
        fields = ['like_count', 'dislike_count']
        
    def get_like_count(self, obj):
        return UserImpression.objects.filter(laptop=obj, liked=True).count()
    
    def get_dislike_count(self, obj):
        return UserImpression.objects.filter(laptop=obj, liked=False).count()

class BaseLaptopMethodFieldSerializer(serializers.Serializer):
    price_difference = serializers.SerializerMethodField()

    class Meta:
        fields = ['price_difference']

    def get_price_difference(self, obj):
        # `obj`is a Laptop obj.
        # TODO: Find a way to get the price comparision. CURRENT: Too heavy on the database query.
        #
        # CURRENT ALTERNATIVE: 
        # Save the computed price difference in the database and retrieve that price.
        # Update the price difference if it's changed in Laptop Detail page.
        
        # Return the laptop price for now.
        return obj.specs_price_difference

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['name', 'logo']

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

class LaptopSerializer(BaseLaptopMethodFieldSerializer, BaseUserImpressionSerializer, serializers.ModelSerializer):  
    class Meta:
        model = Laptop
        fields = ['name', 'slug', 'price', 'updated'] + \
            BaseLaptopMethodFieldSerializer.Meta.fields + \
            BaseUserImpressionSerializer.Meta.fields 
        extra_kwargs = {'price': {'coerce_to_string': False}}

class LaptopDetailSerializer(LaptopSerializer):
    brand_name = serializers.ReadOnlyField(source='brand.name')
    specs = MemoSerializer(many=True, read_only=True)
    class Meta:
        model = LaptopSerializer.Meta.model
        fields = LaptopSerializer.Meta.fields + ['brand_name', 'link', 'specs']
        extra_kwargs = {'price': {'coerce_to_string': False}}