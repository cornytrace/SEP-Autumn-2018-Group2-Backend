import pytest

from courses.serializers import CourseSerializer, RegisteredActionSerializer


@pytest.mark.django_db
def test_can_serialize_course(course):
    """
    Test that a course is serialized correctly.
    """
    assert CourseSerializer(course).data == {
        "pk": course.pk,
        "course_id": course.course_id,
        "course_slug": "capstone-recommender-systems",
        "course_name": "Capstone Recommender Systems",
    }


@pytest.mark.django_db
def test_can_serialize_registered_action(teacher, registered_action):
    """
    Test that a registered action is serialized correctly.
    """

    class Request:
        pass

    obj = Request()
    obj.user = teacher
    assert RegisteredActionSerializer(
        registered_action, context={"request": obj}
    ).data == {
        "course": registered_action.course_id,
        "date": "2017-07-16",
        "description": "Changed the second question in quiz 1 to make it clearer",
        "pk": registered_action.pk,
        "title": "Updated quiz 1",
    }
