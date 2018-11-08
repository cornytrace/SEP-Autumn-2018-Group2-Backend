import json
from urllib.parse import urlparse

import pytest
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from oauth2_provider.models import Application, Grant

from courses.serializers import CourseSerializer
from users.models import User

USER_FIELDS = {"pk", "email", "display_name", "role", "organization", "courses"}


@pytest.mark.django_db
def test_test_view(user_api_client):
    """
    Test that an authenticated user can access the test view.
    """
    response = user_api_client.get(reverse("users-api:test-view"))
    assert response.status_code == 200, response.content
    assert json.loads(response.content) == {
        "success": "You have a valid access token"
    }, "response returned unexpected data"


@pytest.mark.django_db
def test_test_view_no_access(api_client):
    """
    Test that an unauthenticated user cannot access the test view.
    """
    response = api_client.get(reverse("users-api:test-view"))
    assert response.status_code == 403, "unauthenticated user could reach test view"


@pytest.mark.django_db
def test_login_template(client):
    """
    Test that the login page uses the correct template.
    """
    response = client.get(reverse("users:login"))
    assert "registration/login.html" in [
        t.name for t in response.templates if t.name is not None
    ], "did not use correct template"


@pytest.mark.django_db
def test_user_viewset_me(user_api_client, user):
    """
    Test that a user can view its own user details.
    """
    response = user_api_client.get(reverse("users-api:user-me"))
    assert response.status_code == 200, "authenticated user could not get data"
    assert response.data["pk"] == user.pk, "data returned to user is not its data"


@pytest.mark.django_db
def test_user_viewset_must_be_admin(user_api_client):
    """
    Test that only admins can view all user's details.
    """
    response = user_api_client.get(reverse("users-api:user-list"))
    assert len(response.data) <= 1, "regular user has permission"


@pytest.mark.django_db
def test_user_viewset_can_get_own_data(user_api_client, user):
    """
    Test that a regular user can view its own user details in the list view.
    """
    response = user_api_client.get(reverse("users-api:user-list"))
    assert len(response.data) == 1, "regular user cannot access own data"
    assert response.data[0]["pk"] == user.pk, "data returned to user is not its data"


@pytest.mark.django_db
def test_admin_can_access_user_viewset(admin_api_client):
    """
    Test that an admin can view the list of user details.
    """
    response = admin_api_client.get(reverse("users-api:user-list"))
    assert response.status_code == 200, response.content


@pytest.mark.django_db
def test_user_viewset_detail(admin_api_client, user):
    """
    Test that an admin can view the details of a specific user.
    """
    response = admin_api_client.get(
        reverse("users-api:user-detail", kwargs={"pk": user.pk})
    )
    assert response.status_code == 200, response.content
    assert response.data == {
        "pk": user.pk,
        "email": "john.doe@example.com",
        "display_name": "John Doe",
        "role": User.TEACHER,
        "organization": "",
        "courses": [],
    }, "response returned unexpected data"


@pytest.mark.django_db
def test_user_viewset_detail_cannot_get_other_data(user_api_client, user):
    """
    Test that a regular user cannot access a different user's details.
    """
    response = user_api_client.get(
        reverse("users-api:user-detail", kwargs={"pk": user.pk + 1})
    )
    assert response.status_code == 403, "regular user can access other users data"


@pytest.mark.django_db
@pytest.mark.parametrize("role", [User.TEACHER, User.QDT])
def test_user_viewset_create(admin_api_client, course, role):
    """
    Test that an admin can create a new user.
    """
    response = admin_api_client.post(
        reverse("users-api:user-list"),
        {
            "email": "new@example.com",
            "role": role,
            "courses": [CourseSerializer(course).data],
        },
        format="json",
    )
    assert response.status_code == 201, response.content
    assert response.data.keys() == USER_FIELDS
    assert (
        response.data.items() >= {"email": "new@example.com", "role": role}.items()
    ), "response returned unexpected data"
    user = User.objects.get(email="new@example.com")
    assert user.role == role, "user role is not f{role}"
    assert user.is_active, "new user is not active"
    assert not user.has_usable_password(), "user password was set"


@pytest.mark.django_db
@pytest.mark.parametrize("role", [User.TEACHER, User.QDT])
def test_user_viewset_user_is_not_a_superuser(admin_api_client, role):
    """
    Test that a new user with a non-admin role is not a superuser.
    """
    response = admin_api_client.post(
        reverse("users-api:user-list"), {"email": "new@example.com", "role": role}
    )
    assert response.status_code == 201, response.content
    user = User.objects.get(pk=response.data["pk"])
    assert user.role == role, f"user is not {role}"
    assert not user.is_staff, f"{role} user is a staff member"
    assert not user.is_superuser, f"{role} user is a superuser"


@pytest.mark.django_db
def test_user_viewset_create_admin(admin_api_client):
    """
    Test that a new user with an admin role is a superuser.
    """
    response = admin_api_client.post(
        reverse("users-api:user-list"),
        {"email": "admin2@example.com", "role": User.ADMIN},
    )
    assert response.status_code == 201, response.content
    user = User.objects.get(pk=response.data["pk"])
    assert user.role == User.ADMIN, "user is not an admin"
    assert user.is_staff, "admin is not a staff member"
    assert user.is_superuser, "admin is not a superuser"


@pytest.mark.django_db
def test_user_viewset_set_admin_status(admin_api_client, teacher):
    """
    Test that a user's role can be changed to admin.
    """
    assert teacher.role == User.TEACHER, f"user is not a teacher"
    assert not teacher.is_staff, "user is a staff member"
    assert not teacher.is_superuser, "user is a superuser"

    response = admin_api_client.patch(
        reverse("users-api:user-detail", kwargs={"pk": teacher.pk}),
        {"role": User.ADMIN},
    )
    assert response.status_code == 200, response.content
    admin = User.objects.get(pk=teacher.pk)
    assert admin.role == User.ADMIN, "user is not an admin"
    assert admin.is_staff, "user is not a staff member"
    assert admin.is_superuser, "user is not a superuser"


@pytest.mark.django_db
@pytest.mark.parametrize("role", [User.TEACHER, User.QDT])
def test_user_viewset_remove_admin_status(admin_api_client, admin, role):
    """
    Test that a user's admin role can be removed.
    """
    assert admin.role == User.ADMIN, "user is not an admin"
    assert admin.is_staff, "user is not a staff member"
    assert admin.is_superuser, "user is not a superuser"

    response = admin_api_client.patch(
        reverse("users-api:user-detail", kwargs={"pk": admin.pk}), {"role": role}
    )
    assert response.status_code == 200, response.content
    user = User.objects.get(pk=admin.pk)
    assert user.role == role, f"user is not a {role}"
    assert not user.is_staff, "user is a staff member"
    assert not user.is_superuser, "user is a superuser"


@pytest.mark.django_db
def test_user_viewset_update_email(admin_api_client, teacher):
    """
    Test that an admin can update a user's email.
    """
    assert teacher.email != "new@example.com", "email was already set"

    response = admin_api_client.patch(
        reverse("users-api:user-detail", kwargs={"pk": teacher.pk}),
        {"email": "new@example.com"},
    )
    assert response.status_code == 200, response.content
    teacher.refresh_from_db()
    assert teacher.email == "new@example.com", "email is not updated"


@pytest.mark.django_db
def test_user_viewset_full_update(admin_api_client, teacher, course):
    """
    Test that an admin can update a user's details.
    """
    assert teacher.role == User.TEACHER, f"user is not a teacher"
    assert not teacher.is_staff, "user is a staff member"
    assert not teacher.is_superuser, "user is a superuser"
    assert teacher.email != "new@example.com", "email was already set"
    assert not teacher.courses.filter(
        course_id=course.course_id
    ).exists(), "course already set"

    response = admin_api_client.put(
        reverse("users-api:user-detail", kwargs={"pk": teacher.pk}),
        {
            "email": "new@example.com",
            "role": User.QDT,
            "courses": [CourseSerializer(course).data],
        },
        format="json",
    )
    assert response.status_code == 200, response.content
    qdt = User.objects.get(pk=teacher.pk)
    assert qdt.role == User.QDT, f"user is not a qdt"
    assert not qdt.is_staff, "user is a staff member"
    assert not qdt.is_superuser, "user is a superuser"
    assert qdt.email == "new@example.com", "email is not updated"
    assert qdt.courses.filter(course_id=course.course_id).exists(), "course not set"


@pytest.mark.django_db
def test_create_user_send_email(admin_api_client, mailoutbox):
    """
    Test that creating a user sends an activation email.
    """
    admin_api_client.post(reverse("users-api:user-list"), {"email": "new@example.com"})
    assert len(mailoutbox) == 1, "no mails sent"
    m = mailoutbox[0]
    assert m.subject == "An account has been created", "subject does not match"
    assert list(m.to) == ["new@example.com"], "to address does not match"


@pytest.mark.django_db
def test_reset_password(user, api_client):
    """
    Test that password reset works.
    """
    token = default_token_generator.make_token(user)
    response = api_client.put(
        reverse("users-api:user-password-reset", kwargs={"pk": user.pk}),
        {"token": token, "password": "7jz*X6CkMH9s&hEEEF9%QrQ^"},
    )
    assert response.status_code == 200, response.content
    user.refresh_from_db()
    assert user.check_password(
        "7jz*X6CkMH9s&hEEEF9%QrQ^"
    ), "password was not set correctly"


@pytest.mark.django_db
def test_reset_password_low_quality_password(user, api_client):
    """
    Test that a low quality password is rejected.
    """
    token = default_token_generator.make_token(user)
    response = api_client.put(
        reverse("users-api:user-password-reset", kwargs={"pk": user.pk}),
        {"token": token, "password": "password"},
    )
    assert response.status_code == 400, "request with low-quality password succeeded"
    assert response.data == {
        "password": ["This password is too common."]
    }, "response returned unexpected data"


@pytest.mark.django_db
def test_reset_password_invalid_token(user, api_client):
    """
    Test that an invalid password reset token is rejected.
    """
    response = api_client.put(
        reverse("users-api:user-password-reset", kwargs={"pk": user.pk}),
        {"token": "invalid_token", "password": "new_password"},
    )
    assert response.status_code == 400, "request with invalid token succeeded"
    assert response.data == {
        "token": ["Invalid password reset token."]
    }, "response returned unexpected data"


@pytest.mark.django_db
def test_forgot_password_request(user, api_client, mailoutbox):
    """
    Test that the forgot password view sends a password reset email.
    """
    response = api_client.put(
        reverse("users-api:user-forgot-password"), {"email": "john.doe@example.com"}
    )
    assert response.status_code == 200, "response should always return 200"
    assert len(mailoutbox) == 1, "valid password reset request did not send email"


@pytest.mark.django_db
def test_forgot_password_unknown_email(user, api_client, mailoutbox):
    """
    Test that the forgot password view does not send a password reset email to an
    unknown email address.
    """
    response = api_client.put(
        reverse("users-api:user-forgot-password"), {"email": "jeff.wrong@example.com"}
    )
    assert response.status_code == 200, "response should always return 200"
    assert len(mailoutbox) == 0, "email was sent to an email adress unknown to us"


@pytest.mark.django_db
def test_authorize(api_client, user):
    """
    Test that the front-end application can authorize a user and generate an access
    token.
    """
    application = Application.objects.get(name="DASH-IT Frontend")

    response = api_client.post(
        reverse("oauth2_provider:token"),
        {
            "client_id": application.client_id,
            "grant_type": Application.GRANT_PASSWORD,
            "username": user.email,
            "password": "password",
        },
    )
    assert response.status_code == 200, response.content
    data = json.loads(response.content)
    assert "access_token" in data, "did not recieve access token"
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {data['access_token']}")
    test_response = api_client.get(reverse("users-api:test-view"))
    assert test_response.status_code == 200, response.content


@pytest.mark.django_db
def test_introspection_endpoint(introspection_client, teacher_access_token):
    """
    Test that a OAuth2 client with introspection capabilities can introspect
    a user's access token.
    """
    response = introspection_client.post(
        reverse("users:introspect"),
        {"token": teacher_access_token.token, "platform": "coursera"},
    )
    assert response.status_code == 200, str(response.content)
    data = json.loads(response.content)
    assert data["active"], "access token is not active"
    assert data["role"] == "teacher", "not a teacher"
    assert data["courses"] == ["27_khHs4EeaXRRKK7mMjqw"]


@pytest.mark.django_db
def test_introspection_non_existent_token(introspection_client):
    """
    Test that a non-existent token cannot be introspected.
    """
    response = introspection_client.post(
        reverse("users:introspect"),
        {"token": "non-existent-token", "platform": "coursera"},
    )
    assert response.status_code == 401, str(response.content)


@pytest.mark.django_db
def test_introspection_invalid_token(introspection_client, invalid_token):
    """
    Test that an invalid token can be introspected.
    """
    response = introspection_client.post(
        reverse("users:introspect"),
        {"token": invalid_token.token, "platform": "coursera"},
    )
    assert response.status_code == 200, str(response.content)
    data = json.loads(response.content)
    assert not data["active"], "invalid token is active"


@pytest.mark.django_db
def test_introspect_application_token(
    introspection_client, introspection_access_token, coursera_application
):
    """
    Test that the introspection access token can be introspected.
    """
    response = introspection_client.post(
        reverse("users:introspect"),
        {"token": introspection_access_token.token, "platform": "coursera"},
    )
    assert response.status_code == 200, str(response.content)
    data = json.loads(response.content)
    assert data["active"], "access token is not active"
    assert data["client_id"] == coursera_application.client_id, "wrong client id"
