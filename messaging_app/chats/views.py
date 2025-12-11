"""
Views for the messaging app.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    ConversationListSerializer,
    MessageSerializer
)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing conversations.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = []
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return ConversationListSerializer
        return ConversationSerializer

    def get_queryset(self):
        """Optionally filter conversations by participant."""
        queryset = Conversation.objects.all()
        participant_id = self.request.query_params.get('participant', None)
        if participant_id:
            queryset = queryset.filter(participants__user_id=participant_id)
        return queryset.distinct()

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message to a conversation."""
        conversation = self.get_object()
        serializer = MessageSerializer(
            data={
                'conversation': conversation.conversation_id,
                'sender': request.user.user_id if hasattr(request.user, 'user_id') else None,
                'message_body': request.data.get('message_body')
            }
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing messages.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['message_body']
    ordering_fields = ['sent_at', 'message_body']
    ordering = ['-sent_at']

    def get_queryset(self):
        """Optionally filter messages by conversation."""
        queryset = Message.objects.all()
        conversation_id = self.request.query_params.get('conversation', None)
        if conversation_id:
            queryset = queryset.filter(conversation__conversation_id=conversation_id)
        return queryset

    def perform_create(self, serializer):
        """Set sender to current user if available."""
        if hasattr(self.request.user, 'user_id'):
            serializer.save(sender=self.request.user)
        else:
            serializer.save()

