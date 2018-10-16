from datetime import date

import factory
from django.utils.crypto import get_random_string
from factory.django import DjangoModelFactory


class CourseFactory(DjangoModelFactory):
    class Meta:
        model = "courses.Course"

    course_id = factory.LazyFunction(get_random_string)
    course_slug = "capstone-recommender-systems"
    course_name = "Capstone Recommender Systems"


class RegisteredActionFactory(DjangoModelFactory):
    class Meta:
        model = "courses.RegisteredAction"

    course = factory.SubFactory(CourseFactory)
    title = "Updated quiz 1"
    date = date(2017, 7, 16)
    description = "Changed the second question in quiz 1 to make it clearer"
