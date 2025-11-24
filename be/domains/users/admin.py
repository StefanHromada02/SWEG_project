from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "study_program",
        "created_at"
    )

    list_filter = (
        "study_program",
        "created_at"
    )

    search_fields = (
        "name",
        "study_program",
        "interests"
    )

    readonly_fields = (
        "created_at",
    )
