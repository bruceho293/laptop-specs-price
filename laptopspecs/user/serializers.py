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
    password = serializers.CharField(source="user.password", required=True, write_only=True)

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'password']

    def validate(self, attrs):
        current_user = attrs.get('user')
        if current_user is None:
            raise serializers.ValidationError(
              {"user": "There's no User object for validation."}
            )
        
        current_username = current_user.get('username')
        current_email = current_user.get('email')
        current_password = current_user.get('password')

        if current_username is None:
            raise serializers.ValidationError(
                {"username": "The username cannot be empty."}
            )
        if current_email is None:
            raise serializers.ValidationError(
                {"email": "The email cannot be empty."}
            )
        if current_password is None:
            raise serializers.ValidationError(
                {"password": "The password cannot be empty."}
            )
        if User.objects.filter(username=current_username).exists():
            raise serializers.ValidationError(
                {"username": "The username already exists."}
            )
        if User.objects.filter(email=current_email).exists():
            raise serializers.ValidationError(
                {"email": "The email already exists."}
            )

        return attrs
    
    def create(self, validated_data):
        validated_user = validated_data['user']
        
        validated_username = validated_user['username']
        validated_email = validated_user['email']
        validated_password = validated_user['password']

        UserProfile.custom_manager.create_user_profile(
          username=validated_username,
          email=validated_email,
          password=validated_password
        )
        
        return UserProfile.objects.get(user__username=validated_username)

