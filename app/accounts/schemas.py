from typing import Optional

from django.contrib.auth import get_user_model
from ninja import ModelSchema, Schema
from pydantic import Field, field_validator

User = get_user_model()


class MessageSchema(Schema):
    message: str
    detail: Optional[str] = None


class LoginInputSchema(Schema):
    login_id: str = Field(..., description="User's email or username.")
    password: str = Field(min_length=10)

    @field_validator("login_id")
    def validate_login_id(cls, value):
        if not value:
            raise ValueError("The login_id field cannot be empty.")
        return value


class UserResponseModelSchema(ModelSchema):
    class Config:
        model = User
        model_fields = ["id", "email", "username"]


class LoginResponseSchema(Schema):
    user: UserResponseModelSchema
