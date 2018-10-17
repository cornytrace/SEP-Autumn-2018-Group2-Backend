from rest_framework import serializers

from courses.models import Course, RegisteredAction


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["pk", "course_id", "course_slug", "course_name"]
        extra_kwargs = {"course_id": {"validators": []}}


class RegisteredActionSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["course"].queryset = Course.objects.filter(
            user=self.context["request"].user
        )

    course = serializers.SlugRelatedField("course_id", queryset=Course.objects.all())

    class Meta:
        model = RegisteredAction
        fields = ["pk", "course", "title", "date", "description"]
