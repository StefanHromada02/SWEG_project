from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # Felder, die in der Admin-Liste angezeigt werden
    list_display = (
        "title",
        "user",
        "created_at"
    )

    # Filtern nach User und Datum
    list_filter = (
        "user",
        "created_at"
    )

    # Felder, die durchsucht werden können (mit ForeignKey-Lookup)
    search_fields = (
        "title",
        "text",
        "user__username"
    )

    # Die Erstellungszeit sollte nicht im Bearbeitungsformular geändert werden
    readonly_fields = (
        "created_at",
    )