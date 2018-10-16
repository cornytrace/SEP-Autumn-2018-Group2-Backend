import os
from datetime import timedelta

import pytest
from django.conf import settings
from django.utils import timezone
from oauth2_provider.models import Application
from pytest_factoryboy import register
from rest_framework.test import APIClient

from users.models import User

from .courses.factories import CourseFactory, RegisteredActionFactory
from .users.factories import AccessTokenFactory, UserFactory

register(UserFactory)
register(
    UserFactory,
    "admin",
    email="admin@example.com",
    role=User.ADMIN,
    is_staff=True,
    is_superuser=True,
)
register(UserFactory, "_teacher", email="teacher@example.com", role=User.TEACHER)
register(UserFactory, "qdt", email="qdt@example.com", role=User.QDT)
register(CourseFactory)
register(RegisteredActionFactory)


@pytest.fixture
def coursera_course_id():
    return "27_khHs4EeaXRRKK7mMjqw"


@pytest.fixture
def coursera_application():
    return Application.objects.get(name="Coursera API")


@pytest.fixture
def introspection_access_token(coursera_application):
    return coursera_application.accesstoken_set.filter(
        scope__contains="introspection"
    ).first()


@pytest.fixture
def introspection_client(introspection_access_token):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {introspection_access_token.token}")
    return client


@pytest.fixture
def teacher(_teacher, coursera_course_id):
    _teacher.courses.get_or_create(
        course_id=coursera_course_id,
        defaults={
            "course_slug": "design-thinking-entrepreneurship",
            "course_name": "Innovation & Entrepreneurship - From Design Thinking to Funding",
        },
    )
    return _teacher


@pytest.fixture
def user_access_token(user):
    return AccessTokenFactory(user=user)


@pytest.fixture
def admin_access_token(admin):
    return AccessTokenFactory(user=admin)


@pytest.fixture
def teacher_access_token(teacher):
    return AccessTokenFactory(user=teacher)


@pytest.fixture
def application_access_token(teacher, coursera_application):
    return AccessTokenFactory(user=teacher, application=coursera_application)


@pytest.fixture
def invalid_token(teacher):
    return AccessTokenFactory(user=teacher, expires=timezone.now() - timedelta(days=7))


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_api_client(user_access_token):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {user_access_token}")
    return client


@pytest.fixture
def admin_api_client(admin_access_token):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_access_token}")
    return client


@pytest.fixture
def teacher_api_client(teacher_access_token):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {teacher_access_token}")
    return client
