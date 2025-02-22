from django.urls import path

from chat_app.views import (
    Home,
    ThreadViewSet,
)

urlpatterns = [
    path("", Home.as_view(), name="check_authorization"),
    # TODO: Thread endpoints
    path(
        "api/threads/",
        ThreadViewSet.as_view({"post": "create", "get": "list"}),
        name="threads",
    ),
    path(
        "api/threads/<int:pk>/",
        ThreadViewSet.as_view({"delete": "destroy"}),
        name="delete_thread",
    ),
    # TODO: Message endpoints
]
