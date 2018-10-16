from django.urls import path
from rest_framework.routers import DefaultRouter

from courses.views import CourseViewSet, RegisteredActionViewSet

app_name = "courses-api"

router = DefaultRouter()
router.register("courses", CourseViewSet)
router.register("actions", RegisteredActionViewSet)
urlpatterns = router.urls
