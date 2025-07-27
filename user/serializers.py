from django.db.transaction import atomic
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField
from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    SerializerMethodField,
)
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from user.models import User


class RegisterSerializer(ModelSerializer):
    password = CharField(write_only=True)
    first_name = CharField(required=False)
    last_name = CharField(required=False)  # Make last_name optional
    phone_number = CharField(required=False)  # Make phone_number optional

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "password",
            "phone_number",
            "profile_picture",
        )

    @atomic
    def create(self, validated_data):
        try:
            # Check if the optional fields are present in validated_data
            phone_number = validated_data.get("phone_number")
            last_name = validated_data.get("last_name")
            first_name = validated_data.get("first_name")
            profile_picture = validated_data.get("profile_picture")

            user = User.objects.create_user(
                username=validated_data["email"].lower(),
                email=validated_data["email"].lower(),
                first_name=first_name,
                last_name=last_name,  # Use last_name if available
                password=validated_data["password"],
                phone_number=phone_number,  # Use phone_number if available
                profile_picture=profile_picture,
            )

            return user

        except Exception as e:
            error_message = {"error": "Something went wrong!"}
            status_code = HTTP_500_INTERNAL_SERVER_ERROR

            if e.args:
                error_message = {
                    "error": e,
                }
                status_code = HTTP_400_BAD_REQUEST

            raise ValidationError(error_message, status_code)


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        exclude = ("password",)


class UserUpdateSerializer(ModelSerializer):
    first_name = CharField(required=False)
    last_name = CharField(required=False)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "profile_picture",
            "phone_number",
            "email",
        )


class UserChangePasswordSerializer(Serializer):
    old_password = CharField(required=True)
    new_password1 = CharField(required=True)
    new_password2 = CharField(required=True)




