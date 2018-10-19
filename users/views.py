import calendar
import json

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from oauth2_provider.models import get_access_token_model
from oauth2_provider.views import ProtectedResourceView, introspect
from rest_framework import decorators, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from users.models import User
from users.serializers import PasswordResetSerializer, UserSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def list(self, request):
        queryset = User.objects.all()
        if not request.user.is_staff:
            queryset = queryset.filter(pk=request.user.pk)
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        if not request.user.is_staff and pk != str(request.user.pk):
            raise PermissionDenied()
        return super().retrieve(request, pk)

    def get_permissions(self):
        if self.action == "password_reset" or self.action == "forgot_password":
            return [AllowAny()]
        elif self.action == "list" or self.action == "retrieve" or self.action == "me":
            return [IsAuthenticated()]
        return super().get_permissions()

    @decorators.action(methods=["get"], detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @decorators.action(methods=["put", "post"], detail=True)
    def password_reset(self, request, pk=None):
        user = self.get_object()
        serializer = PasswordResetSerializer(
            user, data=request.data, context={"request": self.request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "password set"})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(methods=["put", "post"], detail=False)
    def forgot_password(self, request):
        try:
            user = User.objects.get(email=request.data["email"])
            token = default_token_generator.make_token(user)
            link = (
                settings.FRONTEND_URL
                + "resetpassword/"
                + str(token)
                + "/"
                + str(user.pk)
            )
            send_mail(
                "Password Reset Request",
                '<a href="' + link + '"> Click here to reset your password</a>',
                "noreply@" + request.get_host(),
                [user.email],
            )
        except User.DoesNotExist as e:
            pass

        return Response(status=200)


class TestView(ProtectedResourceView):
    def get(self, request, **kwargs):
        return JsonResponse({"success": "You have a valid access token"})


class IntrospectTokenView(introspect.IntrospectTokenView):
    @staticmethod
    def get_token_response(token_value=None):
        try:
            token = get_access_token_model().objects.get(token=token_value)
        except ObjectDoesNotExist:
            return HttpResponse(
                content=json.dumps({"active": False}),
                status=401,
                content_type="application/json",
            )
        else:
            if token.is_valid():
                data = {
                    "active": True,
                    "scope": token.scope,
                    "exp": int(calendar.timegm(token.expires.timetuple())),
                }
                if token.application:
                    data["client_id"] = token.application.client_id
                if token.user:
                    data["username"] = token.user.get_username()
                    data["role"] = token.user.role
                    data["courses"] = list(
                        token.user.courses.values_list("course_id", flat=True)
                    )
                return HttpResponse(
                    content=json.dumps(data),
                    status=200,
                    content_type="application/json",
                )
            else:
                return HttpResponse(
                    content=json.dumps({"active": False}),
                    status=200,
                    content_type="application/json",
                )
