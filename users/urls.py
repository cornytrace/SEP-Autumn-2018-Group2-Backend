from django.contrib.auth.views import LoginView
from django.urls import path

from users.views import IntrospectTokenView

app_name = "users"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("introspect/", IntrospectTokenView.as_view(), name="introspect"),
]
