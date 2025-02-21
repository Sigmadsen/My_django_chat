from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from rest_framework import serializers

from chat_app.models import Thread


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class ThreadSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    participants = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Thread
        fields = ["id", "username", "participants", "created", "updated"]

    def validate_username(self, value):
        # Check is this user exists in database
        try:
            invited_user = User.objects.get(username=value)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                f"User with username '{value}' not found."
            )

        # Check thread creation with myself
        if invited_user == self.context["request"].user:
            raise serializers.ValidationError("Cannot create a thread with yourself.")

        return invited_user

    def create(self, validated_data):

        my_user = self.context["request"].user
        invited_user = validated_data["username"]

        # Searching for an existing thread
        thread = (
            Thread.objects.filter(participants=my_user)
            .filter(participants=invited_user)
            .first()
        )
        if thread:
            # Flag to show that we need return 200 status code in ViewSet
            self._existing_thread = True
            return thread

        thread = Thread.objects.create()
        thread.participants.set([my_user, invited_user])

        return thread
