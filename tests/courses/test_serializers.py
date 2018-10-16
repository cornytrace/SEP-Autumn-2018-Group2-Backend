import pytest

from courses.serializers import CourseSerializer, RegisteredActionSerializer


@pytest.mark.django_db
def test_can_serialize_course(course):
    assert CourseSerializer(course).data == {
        "pk": course.pk,
        "course_id": course.course_id,
        "course_slug": "capstone-recommender-systems",
        "course_name": "Capstone Recommender Systems",
    }


@pytest.mark.django_db
def test_can_serialize_registered_action(registered_action):
    assert RegisteredActionSerializer(registered_action).data == {
        "course_id": registered_action.course_id,
        "date": "2017-07-16",
        "description": "Changed the second question in quiz 1 to make it clearer",
        "pk": registered_action.pk,
        "title": "Updated quiz 1",
    }
