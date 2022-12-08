from rest_framework import serializers

from laptop.models import Laptop, Memo, Component
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

class LaptopListSerializer(BaseUserImpressionSerializer, serializers.ModelSerializer):
    class Meta:
        model = Laptop
        fields = ['name', 'slug', 'price', 'updated'] + \
            BaseUserImpressionSerializer.Meta.fields

class LaptopDetailSerializer(BaseUserImpressionSerializer, serializers.ModelSerializer):
    brand_name = serializers.ReadOnlyField(source='brand.name')
    specs = MemoSerializer(many=True, read_only=True)
    class Meta:
        model = Laptop
        fields = ['name', 'slug', 'brand_name', 'price', 'link', 'updated', 'specs'] + \
            BaseUserImpressionSerializer.Meta.fields