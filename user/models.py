from django.db import models
from django.contrib.auth.models import AbstractUser

from django.db.models import (
    BooleanField,
    CharField,
    EmailField,
    ImageField,
    UUIDField,
    DateTimeField,
    Model
)
from django.utils.translation import gettext_lazy as _
from uuid import uuid4
from rest_framework_simplejwt.tokens import RefreshToken

# Create your models here.

class BaseModel(Model):
    created_at = DateTimeField(
        auto_now_add=True,
        editable=False,
        help_text="Created time",
        null=True,
    )
    updated_at = DateTimeField(
        auto_now=True,
        editable=False,
        help_text="Updated time",
        null=True,
    )
    # created_user = ForeignKey('users.User',on_delete=models.SET_NULL,null=True,blank=True,related_name='created_user')

    class Meta:
        abstract = True


class User(BaseModel, AbstractUser):
    id = UUIDField(
        default=uuid4,
        primary_key=True,
        editable=False,
        help_text=_("Using UUID instead of Integer"),
    )
    email = EmailField(_("email address"), unique=True, null=True, blank=True)
    first_name = CharField(max_length=225, null=True, blank=True)
    last_name = CharField(max_length=225, null=True, blank=True)
    new_user = BooleanField(default=True)
    phone_number = CharField(max_length=25, unique=True, null=True, blank=True)
    profile_picture = ImageField(upload_to="profile_pictures/", null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def get_tokens(self):
        refresh = RefreshToken.for_user(self)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def __str__(self):
        # Ensure a string is returned, even if email is None
        return self.email or self.phone_number or "User"
