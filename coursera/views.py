from django.contrib.postgres.fields import JSONField
from django.db.models.functions import Cast
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ReadOnlyModelViewSet

from coursera.models import ClickstreamEvent, Course, Item
from coursera.serializers import CourseAnalyticsSerializer, VideoAnalyticsSerializer


class CourseAnalyticsViewSet(ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseAnalyticsSerializer

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

    lookup_field = "value_json__item_id"
    lookup_url_kwarg = "item_id"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(value_json=Cast("value", output_field=JSONField()))
            .filter(course_id=self.kwargs["course_id"])
        )
