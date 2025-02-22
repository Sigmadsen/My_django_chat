from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from rest_framework import serializers

from chat_app.models import Thread, Message


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


class ThreadMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    text = serializers.CharField()
    created = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Message
        fields = ["id", "sender", "text", "is_read", "created"]

    def validate_is_read(self, value):
        sender = self.context["sender"]
        if self.instance and self.instance.sender == sender and value is True:
            raise serializers.ValidationError(
                "You cannot mark your own message as read."
            )
        if self.instance and value is False:
            raise serializers.ValidationError(
                "Mark a message as not read are not allowed."
            )
        return value

    def validate(self, data):
        thread_id = self.context.get("thread_id")
        thread = Thread.objects.filter(id=thread_id).first()
        if not thread:
            raise serializers.ValidationError(
                {"detail": f"Thread with id {thread_id} does not exist."}
            )

        if self.context.get("sender") not in thread.participants.all():
            raise serializers.ValidationError(
                {"detail": "Sender must be a participant of the thread."}
            )

        return data

    def create(self, validated_data):
        # Always set is_read=False on creation to prevent set up is_read=False on message creation
        # and allow to set is_read=True with PATCH request
        validated_data["is_read"] = False
        thread_id = self.context.get("thread_id")
        thread = Thread.objects.filter(id=thread_id).first()
        sender = self.context.get("sender")
        message = Message.objects.create(thread=thread, sender=sender, **validated_data)
        return message
