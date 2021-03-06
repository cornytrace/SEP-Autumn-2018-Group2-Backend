from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from courses.models import Course, RegisteredAction
from courses.serializers import CourseSerializer, RegisteredActionSerializer


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminUser]


class RegisteredActionViewSet(ModelViewSet):
    queryset = RegisteredAction.objects.order_by("date")
    serializer_class = RegisteredActionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset().filter(course__user=self.request.user)
        if "course_id" in self.kwargs:
            queryset = queryset.filter(course_id=self.kwargs["course_id"])
        return queryset
