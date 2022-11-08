from rest_framework import serializers

from user.models import UserImpression, UserProfile

class UserImpressionSerializer(serializers.ModelSerializer):
    laptop_id = serializers.IntegerField(source="laptop.id", read_only=True)
    
    class Meta:
        model = UserImpression
        fields = ['laptop_id', 'liked']


class UserProfileSerializer(serializers.ModelSerializer):
    impression = serializers.SerializerMethodField()
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'impression']

    def get_impression(self, obj):
        qs = UserImpression.objects.filter(profile=obj)
        return [UserImpressionSerializer(imp).data for imp in qs]
        