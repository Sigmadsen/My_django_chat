from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from chat_app.models import Thread, Message
from chat_app.serializers import ThreadSerializer, ThreadMessageSerializer


class ThreadViewSet(viewsets.ModelViewSet):
    serializer_class = ThreadSerializer

    def get_queryset(self):
        return Thread.objects.filter(participants=self.request.user)

    def create(self, request, *args, **kwargs):
        # Override this method to return status code 200 instead of 201 in case the thread is existing
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        headers = self.get_success_headers(serializer.data)
        status_code = (
            status.HTTP_200_OK
            if getattr(serializer, "_existing_thread", False)
            else status.HTTP_201_CREATED
        )
        return Response(serializer.data, status=status_code, headers=headers)


class ThreadMessageViewSet(viewsets.ModelViewSet):
    serializer_class = ThreadMessageSerializer

    def get_queryset(self):
        thread_id = self.kwargs.get("thread_pk")
        return Message.objects.filter(
            thread_id=thread_id, thread__participants=self.request.user
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["thread_id"] = self.kwargs.get("thread_pk")
        context["sender"] = self.request.user
        return context

    @action(detail=True, methods=["get"])
    def unread_count(self, request, thread_pk=None):
        user = request.user

        try:
            thread = Thread.objects.get(id=thread_pk, participants=user)
        except Thread.DoesNotExist:
            return Response(
                {
                    "detail": "You are not a participant of this thread or the thread does not exist."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        unread_count = (
            Message.objects.filter(
                thread_id=thread_pk,
                is_read=False,
            )
            .exclude(sender=user)
            .count()
        )

        return Response({"unread_count": unread_count}, status=status.HTTP_200_OK)
