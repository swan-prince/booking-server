from rest_framework import serializers, exceptions
from django.contrib.auth import authenticate, password_validation

from users.models import User


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get("email", "")
        password = data.get("password", "")

        if email and password:
            user = authenticate(email=email, password=password)
            if user:
                if user.is_active:
                    data["user"] = user
                else:
                    msg = "User is deactivated."
                    raise exceptions.ValidationError(msg)
            else:
                msg = "Unable to login with given credentials."
                raise exceptions.ValidationError(msg)
        else:
            msg = "Must provide username and password both."
            raise exceptions.ValidationError(msg)
        return data


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    avatar = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ['email', 'full_name', 'password', 'avatar']

    def validate(self, attrs):
        email = attrs.get("email", "")
        if User.objects.filter(email=email).exists():
            msg = "Email is already in use."
            raise exceptions.ValidationError(msg)
        
        password = attrs.get("password", None)
        if password is None:
            raise exceptions.ValidationError('Password can\'t be blank.')
        
        password_validation.validate_password(password)
        
        return super().validate(attrs)
    
    def update(self, instance, validated_data):
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        password = validated_data.get('password', None)
        instance.set_password(password)
        instance.save()
        return instance

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate_email(self, email):
        try:
            User.objects.get(email=email)
            return email
        except User.DoesNotExist:
            raise serializers.ValidationError("This email does not exist.")

    def validate_password(self, password):
        password_validation.validate_password(password)
        return password


class UserVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField()

    def validate_email(self, email):
        try:
            User.objects.get(email=email)
            return email
        except User.DoesNotExist:
            raise serializers.ValidationError("This email does not exist.")
