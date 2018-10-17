import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_can_view_course(admin_api_client, course):
    response = admin_api_client.get(
        reverse("courses-api:course-detail", kwargs={"pk": course.pk})
    )
    assert response.status_code == 200, str(response.content)
    assert response.data == {
        "pk": course.pk,
        "course_id": course.course_id,
        "course_slug": "capstone-recommender-systems",
        "course_name": "Capstone Recommender Systems",
    }, "view did not return correct data"


@pytest.mark.django_db
def test_can_view_registered_action(teacher, teacher_api_client, registered_action):
    response = teacher_api_client.get(
        reverse(
            "courses-api:registeredaction-detail", kwargs={"pk": registered_action.pk}
        )
    )
    assert response.status_code == 200, str(response.content)
    assert response.data == {
        "course": registered_action.course_id,
        "date": "2017-07-16",
        "description": "Changed the second question in quiz 1 to make it clearer",
        "pk": registered_action.pk,
        "title": "Updated quiz 1",
    }, "view did not return correct data"


@pytest.mark.django_db
def test_can_filter_action_list(teacher, teacher_api_client, registered_action):
    response = teacher_api_client.get(
        reverse(
            "courses-api:registeredaction-list",
            kwargs={"platform": "coursera", "course_id": registered_action.course_id},
        )
    )
    assert response.status_code == 200, str(response.content)


@pytest.mark.django_db
def test_can_create_registered_action(teacher_api_client, teacher, course):
    response = teacher_api_client.post(
        reverse("courses-api:registeredaction-list"),
        {
            "course": course.course_id,
            "date": "2017-09-20",
            "title": "Title",
            "description": "-",
        },
    )
    assert response.status_code == 400, str(response.content)

    teacher.courses.add(course)
    response = teacher_api_client.post(
        reverse("courses-api:registeredaction-list"),
        {
            "course": course.course_id,
            "date": "2017-09-20",
            "title": "Title",
            "description": "-",
        },
    )
    assert response.status_code == 201, str(response.content)
