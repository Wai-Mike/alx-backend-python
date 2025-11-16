"""
Serializers for the messaging app.
"""
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from .models import User, Conversation, Message, ConversationParticipant


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'user_id',
            'first_name',
            'last_name',
            'email',
            'password',
            'phone_number',
            'role',
            'created_at'
        ]
        read_only_fields = ['user_id', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        """Create user with hashed password."""
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model."""
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender',
            'conversation',
            'message_body',
            'sent_at'
        ]
        read_only_fields = ['message_id', 'sent_at']

    def validate_message_body(self, value):
        """Validate message body is not empty."""
        if not value or not value.strip():
            raise ValidationError("Message body cannot be empty.")
        return value


class ConversationParticipantSerializer(serializers.ModelSerializer):
    """Serializer for ConversationParticipant."""
    participant = UserSerializer(read_only=True)

    class Meta:
        model = ConversationParticipant
        fields = ['participant', 'joined_at']
        read_only_fields = ['joined_at']


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model with nested messages."""
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True,
        source='participants'
    )

    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'participant_ids',
            'messages',
            'created_at'
        ]
        read_only_fields = ['conversation_id', 'created_at']

    def validate_participant_ids(self, value):
        """Validate that at least one participant is provided."""
        if not value or len(value) == 0:
            raise ValidationError("At least one participant is required.")
        if len(value) < 2:
            raise ValidationError("A conversation must have at least 2 participants.")
        return value

    def create(self, validated_data):
        """Create conversation and add participants."""
        participants = validated_data.pop('participants', [])
        conversation = Conversation.objects.create(**validated_data)
        for participant in participants:
            ConversationParticipant.objects.create(
                conversation=conversation,
                participant=participant
            )
        return conversation


class ConversationListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing conversations."""
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'last_message',
            'unread_count',
            'created_at'
        ]
        read_only_fields = ['conversation_id', 'created_at']

    def get_last_message(self, obj):
        """Get the last message in the conversation."""
        last_msg = obj.messages.first()
        if last_msg:
            return {
                'message_id': last_msg.message_id,
                'sender': UserSerializer(last_msg.sender).data,
                'message_body': last_msg.message_body,
                'sent_at': last_msg.sent_at
            }
        return None

    def get_unread_count(self, obj):
        """Get unread message count (placeholder)."""
        return 0

