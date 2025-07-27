from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from rest_framework.exceptions import ValidationError
from django.core.mail import EmailMessage
from drf_spectacular.utils import extend_schema
from user import schema_specs

from user.models import User
from user.serializers import RegisterSerializer, UserChangePasswordSerializer, UserSerializer, UserUpdateSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

# Create your views here.


class RegisterUserView(CreateAPIView):
    """User registration endpoint."""

    model = User
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def get_fcm_client(self):
        """Get the FCM client based on the request."""
        return self.kwargs.get("fcm_client", "brickly")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["fcm_client"] = self.get_fcm_client()
        return context


class UserChangePasswordView(UpdateAPIView):
    serializer_class = UserChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ("patch",)

    def patch(self, request, *args, **kwargs):
        serializer = UserChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        old_password = serializer.validated_data.get("old_password")
        new_password1 = serializer.validated_data.get("new_password1")
        new_password2 = serializer.validated_data.get("new_password2")
        if not user.check_password(old_password):
            return Response({"message": "Invalid old password."}, HTTP_400_BAD_REQUEST)
        if new_password1 != new_password2:
            return Response(
                {"message": "New passwords do not match."},
                status=HTTP_400_BAD_REQUEST,
            )
        try:
            request.user.set_password(new_password1)
            request.user.save()
        except Exception as e:
            error_message = {"error": "Something went wrong!"}
            status_code = HTTP_500_INTERNAL_SERVER_ERROR
            if e.args:
                if isinstance(e.args[0], ValidationError):
                    error_message = {
                        "password": [str(error) for arg in e.args[0] for error in arg],
                    }
                    status_code = HTTP_400_BAD_REQUEST
                else:
                    error_message = {"error": e.args[0]}
            raise ValidationError(error_message, status_code)
        return Response(
            {"message": "Password successfully changed."},
            status=HTTP_200_OK,
        )
    

class UserView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ("get", "patch", "delete")

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.request.user, many=False)
        data = serializer.data
        return Response(data)

    @extend_schema(request=UserUpdateSerializer)
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        new_email = request.data.get("email")
        new_phone_number = request.data.get("phone_number")

        # Check if email or phone number exists for another user
        if new_email:
            existing_user = (
                User.objects.filter(email__iexact=new_email)
                .exclude(id=instance.id)
                .first()
            )
            if existing_user:
                return Response(
                    {
                        "message": "This email is already associated with another account.",
                        "combine_user": True,
                        "user_id": existing_user.id,
                    },
                    status=status.HTTP_409_CONFLICT,
                )

        if new_phone_number:
            existing_user = (
                User.objects.filter(phone_number=new_phone_number)
                .exclude(id=instance.id)
                .first()
            )
            if existing_user:
                return Response(
                    {
                        "message": "This phone number is already associated with another account.",
                        "combine_user": True,
                        "user_id": existing_user.id,
                    },
                    status=status.HTTP_409_CONFLICT,
                )

        # Proceed with the update if no conflict
        self.serializer_class = UserUpdateSerializer
        self.partial_update(request, *args, **kwargs)

        return Response(UserSerializer(self.request.user, many=False).data)

    @extend_schema(responses=schema_specs.USER_DELETE)
    def delete(self, request, *args, **kwargs):
        user = self.request.user
        user.is_active = False
        user.save()
        return Response(
            {
                "message": "Your account has been deactivated. It will be deleted after 30 days.",
            },
            status=HTTP_200_OK,
        )


def send_verification_email(to_email, verification_code):
    subject = "Verify Your Email"
    message = f"Your verification code is {verification_code}"
    from_mail = "arshakk2002@gmail.com"
    rec_list = [to_email]

    email = EmailMessage(
        subject,
        message,
        from_mail,
        rec_list,
    )
    email.send()

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        request_data = request.data.copy()
        if "email" in request_data:
            request_data["email"] = request_data["email"].lower()
        request._full_data = request_data
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            email = request.data["email"]
            user = User.objects.get(email=email)
            response.data["name"] = user.first_name
            response.data["email"] = user.email
            response.data["new_user"] = user.new_user
            response.data["admin"] = user.is_superuser
            if response.data["new_user"] is True:
                user.new_user = False
                user.save()
            return response