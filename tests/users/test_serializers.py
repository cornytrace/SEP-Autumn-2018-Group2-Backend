import pytest
from django.contrib.auth.tokens import default_token_generator
from django.core import exceptions
from rest_framework import serializers

from users.models import User
from users.serializers import PasswordResetSerializer, UserSerializer


@pytest.mark.django_db
def test_serialize_user(user):
    """
    Test that all properties of the User model are serialized correctly.
    """
    assert UserSerializer(user).data == {
        "pk": user.pk,
        "email": "john.doe@example.com",
        "display_name": "John Doe",
        "role": User.TEACHER,
        "organization": "",
        "courses": [],
    }


@pytest.mark.django_db
def test_validate_token(user):
    """
    Test that the server can create valid password reset tokens.
    """
    token = default_token_generator.make_token(user)
    serializer = PasswordResetSerializer(instance=user)
    assert serializer.validate_token(token) == token, "token validation failed"
    with pytest.raises(serializers.ValidationError):
        serializer.validate_token("invalid_token")


@pytest.mark.django_db
def test_validate_password(user):
    """
    Test that the password requirements validator works.
    """
    serializer = PasswordResetSerializer(instance=user)
    assert (
        serializer.validate_password("JzS@*4682JP#%a#uT3QQvndf")
        == "JzS@*4682JP#%a#uT3QQvndf"
    ), "password validation failed"
    with pytest.raises(exceptions.ValidationError):
        serializer.validate_password("password")
    with pytest.raises(exceptions.ValidationError):
        serializer.validate_password("short")
    with pytest.raises(exceptions.ValidationError):
        serializer.validate_password("john.doe@example.org")


@pytest.mark.django_db
def test_update_password(user):
    """
    Test that a changed password is updated in the model, and saved to the database.
    """
    serializer = PasswordResetSerializer()
    user = serializer.update(user, {"password": "new_password"})
    assert user.check_password("new_password"), "password was not updated"
    user.refresh_from_db()
    assert user.check_password("new_password"), "updated password was not saved"
