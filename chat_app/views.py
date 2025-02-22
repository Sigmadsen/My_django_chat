from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response

from chat_app.models import Thread
from chat_app.serializers import ThreadSerializer


class Home(APIView):
    def get(self, request):
        content = {"message": "Test JWTAuthentication access!"}
        return Response(content)


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
