from django.urls import path

from chat_app.views import (
    Home,
    ThreadViewSet,
)

urlpatterns = [
    path("", Home.as_view(), name="check_authorization"),
    # TODO: Thread endpoints
    path(
        "api/threads/", ThreadViewSet.as_view({"post": "create"}), name="create_thread"
    ),
    # TODO: Message endpoints
]
