from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'role', 'department', 'designation', 'blood_group', 'mobile_number', 'profile_picture', 'profile_picture_url', 'date_of_birth')

    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'], # Email is now required and unique
            password=validated_data['password'],
            role=validated_data.get('role', User.EMPLOYEE),
            department=validated_data.get('department', ''),
            designation=validated_data.get('designation', ''),
            blood_group=validated_data.get('blood_group', ''),
            mobile_number=validated_data.get('mobile_number', ''),
            profile_picture=validated_data.get('profile_picture', None),
            date_of_birth=validated_data.get('date_of_birth', None)
        )
        return user

class UserSerializer(serializers.ModelSerializer):

    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'is_approved', 'is_rejected', 'department', 'designation', 'blood_group', 'mobile_number', 'profile_picture', 'profile_picture_url', 'date_of_birth')

    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    
    """Serializer for updating user profile including profile picture"""
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'email', 'department', 'designation', 'blood_group', 'mobile_number', 'profile_picture', 'profile_picture_url', 'date_of_birth')

    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None

    def update(self, instance, validated_data):
        # Only update fields that are provided
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.department = validated_data.get('department', instance.department)
        instance.designation = validated_data.get('designation', instance.designation)
        
        # Handle blood_group - only update if provided and not empty
        if 'blood_group' in validated_data:
            blood_group = validated_data.get('blood_group')
            instance.blood_group = blood_group if blood_group else None
        
        # Handle mobile_number - only update if provided
        if 'mobile_number' in validated_data:
            instance.mobile_number = validated_data.get('mobile_number')
        
        # Handle profile picture - only update if provided
        if 'profile_picture' in validated_data:
            instance.profile_picture = validated_data['profile_picture']
        
        # Handle date of birth - only update if provided
        if 'date_of_birth' in validated_data:
            instance.date_of_birth = validated_data['date_of_birth']
        
        instance.save()
        return instance

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            try:
                user_obj = User.objects.get(email=email)
            except User.DoesNotExist:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')

            user = authenticate(username=user_obj.username, password=password)
            
            if not user:
                 msg = 'Unable to log in with provided credentials.'
                 raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        data['user'] = user
        return data
    
