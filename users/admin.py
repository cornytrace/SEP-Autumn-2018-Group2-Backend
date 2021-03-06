from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from users.models import User


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password", "role", "organization", "courses")}),
        (_("Personal info"), {"fields": ("display_name",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )
    list_display = ("email", "display_name", "role", "is_staff")
    search_fields = ("email", "display_name", "role")
    ordering = ("email",)


admin.site.register(User, UserAdmin)
