from django.db import models


class Course(models.Model):
    course_id = models.CharField(unique=True, max_length=30)
    course_slug = models.CharField(max_length=100)
    course_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.course_name}"


class RegisteredAction(models.Model):
    course = models.ForeignKey(
        "Course",
        related_name="registered_actions",
        on_delete=models.DO_NOTHING,
        to_field="course_id",
    )
    title = models.CharField(max_length=100)
    date = models.DateField()
    description = models.TextField()

    def __str__(self):
        return f"{self.title}"
