from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'role', 'department', 'designation', 'blood_group', 'mobile_number')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'], # Email is now required and unique
            password=validated_data['password'],
            role=validated_data.get('role', User.EMPLOYEE),
            department=validated_data.get('department', ''),
            designation=validated_data.get('designation', ''),
            blood_group=validated_data.get('blood_group', ''),
            mobile_number=validated_data.get('mobile_number', '')
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'is_approved', 'department', 'designation', 'blood_group', 'mobile_number')

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
    
