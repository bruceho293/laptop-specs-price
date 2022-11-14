from rest_framework import serializers

from django.contrib.auth.models import User
from user.models import UserImpression, UserProfile

class UserImpressionSerializer(serializers.ModelSerializer):
    laptop_id = serializers.IntegerField(source="laptop.id", read_only=True)
    
    class Meta:
        model = UserImpression
        fields = ['laptop_id', 'liked']


class UserProfileDetailSerializer(serializers.ModelSerializer):
    impression = serializers.SerializerMethodField()
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'impression']

    def get_impression(self, obj):
        qs = UserImpression.objects.filter(profile=obj)
        return [UserImpressionSerializer(imp).data for imp in qs]

class UserProfileRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", required=True)
    email = serializers.EmailField(source="user.email", required=True)
    password = serializers.CharField(source="user.password,", required=True)

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'password']

    def validate(self, attrs):
        username = attrs['username']
        email = attrs['email']

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
              {"username": "The username already exists."}
            )
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
              {"email": "The email already exists."}
            )

        return attrs
    
    def create(self, validated_data):
        user_profile = UserProfile.custom_manager.create_user_profile(
          username=validated_data['username'],
          email=validated_data['email'],
          password=validated_data['password']
        )
        return user_profile

