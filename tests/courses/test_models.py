from datetime import date

import pytest

from courses.models import Course, RegisteredAction


@pytest.mark.django_db
def test_can_create_course():
    """
    Test that a course can be created through the ORM.
    """
    course = Course.objects.create(
        course_id="bmHtyVrIEee3CwoIJ_9DVg",
        course_slug="capstone-recommender-systems",
        course_name="Capstone Recommender Systems",
    )
    assert course.pk is not None, "course has no pk"
    Course.objects.get(pk=course.pk)


@pytest.mark.django_db
@pytest.mark.parametrize("field", ["course_id"])
def test_unique_fields(field):
    """
    Test that the Course.course_id field is unique.
    """
    assert Course._meta.get_field(field).unique, f"Course.{field} is not unique"


@pytest.mark.django_db
def test_course_str(course):
    """
    Test that the string representation of a Course is the course's name.
    """
    assert (
        str(course) == "Capstone Recommender Systems"
    ), "incorrect string representation"


@pytest.mark.django_db
def test_can_create_registered_action(course):
    """
    Test that a registered action can be created through the ORM.
    """
    action = RegisteredAction.objects.create(
        course=course,
        title="Updated quiz 2",
        date=date(2018, 4, 19),
        description="Removed the last question from quiz 2",
    )
    assert action.pk is not None, "action has no pk"
    RegisteredAction.objects.get(pk=action.pk)


@pytest.mark.django_db
def test_registered_action_str(registered_action):
    """
    Test that the string representation of a RegisteredAction is the action's title.
    """
    assert str(registered_action) == "Updated quiz 1", "incorrect string representation"
