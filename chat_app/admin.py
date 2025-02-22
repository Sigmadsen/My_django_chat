from django.contrib import admin

from chat_app.models import Thread, Message


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ("id", "created", "updated", "get_participants")
    list_filter = ("created", "updated")

    def get_participants(self, obj):
        return ", ".join([p.username for p in obj.participants.all()])

    get_participants.short_description = "Participants"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "text", "created", "is_read")
    list_filter = ("is_read", "created")
    search_fields = ("text", "sender__username")
