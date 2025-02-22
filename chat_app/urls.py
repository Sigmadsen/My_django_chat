from django.urls import path
from rest_framework_simplejwt.views import TokenObtainSlidingView

from chat_app.views import (
    ThreadViewSet,
    ThreadMessageViewSet,
)


urlpatterns = [
    path("api/token/", TokenObtainSlidingView.as_view(), name="token_obtain"),
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
    path(
        "api/threads/<int:thread_pk>/messages/",
        ThreadMessageViewSet.as_view({"post": "create", "get": "list"}),
        name="messages",
    ),
    path(
        "api/threads/<int:thread_pk>/messages/<int:pk>/",
        ThreadMessageViewSet.as_view({"patch": "partial_update"}),
        name="messages",
    ),
    path(
        "api/threads/<int:thread_pk>/messages/unread_count/",
        ThreadMessageViewSet.as_view({"get": "unread_count"}),
        name="unread_count",
    ),
]
