from rest_framework import serializers

from courses.models import Course, RegisteredAction


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["pk", "course_id", "course_slug", "course_name"]
        extra_kwargs = {"course_id": {"validators": []}}


class RegisteredActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisteredAction
        fields = ["pk", "course_id", "title", "date", "description"]
