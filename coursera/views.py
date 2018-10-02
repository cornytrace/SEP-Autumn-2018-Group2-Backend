
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from coursera.models import ClickstreamEvent, Course, Item
from coursera.serializers import CourseAnalyticsSerializer, VideoAnalyticsSerializer


class CourseAnalyticsViewSet(ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseAnalyticsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                id__in=list(
                    self.request.user.courses.values_list("course_id", flat=True)
                )
            )
        )


class VideoAnalyticsViewSet(ReadOnlyModelViewSet):
    queryset = Item.objects.all()
    serializer_class = VideoAnalyticsSerializer
    permission_classes = [IsAuthenticated]

    lookup_field = "item_id"
    lookup_url_kwarg = "item_id"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                branch__in=list(
                    self.request.user.courses.values_list("course_id", flat=True)
                )
            )
            .filter(branch=self.kwargs["course_id"])
        )
