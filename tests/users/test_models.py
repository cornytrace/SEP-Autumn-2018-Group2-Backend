import pytest
from oauth2_provider.models import Application

from users.models import User


def test_email_is_username():
    assert User.USERNAME_FIELD == "email", "USERNAME_FIELD is not correct"


@pytest.mark.django_db
def test_can_create_user():
    """
    Test that a new normal user can be created.
    """
    user = User.objects.create_user("test_user@example.com", "password")
    assert user.email == "test_user@example.com", "email is set incorrectly"
    assert user.check_password("password"), "password is set incorreclty"


@pytest.mark.django_db
def test_can_create_superuser():
    """
    Test that a new superuser (admin) can be created.
    """
    user = User.objects.create_superuser("admin@example.com", "password")
    assert user.is_superuser, "user is not a superuser"


@pytest.mark.django_db
def test_superuser_must_be_staff():
    """
    Test that a new superuser (admin) must be a staff member.
    """
    with pytest.raises(ValueError):
        User.objects.create_superuser("admin@example.com", "password", is_staff=False)


@pytest.mark.django_db
def test_superuser_must_be_superuser():
    """
    Test that a new superuser (admin) must have the flag superuser.
    """
    with pytest.raises(ValueError):
        User.objects.create_superuser(
            "admin@example.com", "password", is_superuser=False
        )


@pytest.mark.django_db
def test_user_can_login(user):
    """
    Test that an existing user can log in.
    """
    assert user.check_password("password"), "password is incorrect"


@pytest.mark.django_db
def test_application_exists():
    """
    Test that the Application object exists.
    """
    assert Application.objects.exists(), "application is not created"
