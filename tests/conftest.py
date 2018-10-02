import os
from datetime import timedelta

import pytest
from django.conf import settings
from django.utils import timezone
from oauth2_provider.models import Application
from pytest_factoryboy import register
from rest_framework.test import APIClient

from coursera.models import Course
from eit_dashboard.db_router import DatabaseRouter
from users.models import User

from .courses.factories import CourseFactory
from .users.factories import AccessTokenFactory, UserFactory

collect_ignore = []
if settings.DATABASES["coursera"]["ENGINE"] not in [
    "django.db.backends.postgresql",
    "django.db.backends.postgresql_psycopg2",
]:
    collect_ignore.append("coursera/")
else:
    os.environ["USE_COURSERA_DB"] = "True"

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
def teacher(_teacher, coursera_course):
    _teacher.courses.get_or_create(
        course_id=coursera_course.pk,
        defaults={
            "course_slug": coursera_course.slug,
            "course_name": coursera_course.name,
        },
    )
    return _teacher


@pytest.fixture
def coursera_course(coursera_course_id):
    return Course.objects.get(pk=coursera_course_id)


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    if not os.environ.get("USE_COURSERA_DB"):
        del settings.DATABASES["coursera"]


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


@pytest.fixture
def db_router():
    return DatabaseRouter()
