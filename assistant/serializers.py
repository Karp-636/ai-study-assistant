# assistant/serializers.py
from rest_framework import serializers
from .models import Document, Conversation, Message

class DocumentSerializer(serializers.ModelSerializer):
    chunk_count = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ["id", "title", "content", "chunk_count", "created_at"]
        read_only_fields = ["chunk_count", "created_at"]

    def get_chunk_count(self, obj):
        return obj.chunks.count()


class DocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["title", "content"]


class AskQuestionSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=2000)



class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "conversation", "role", "content", "created_at"]
        read_only_fields = ["id", "created_at"]


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ["id", "title", "created_at", "messages"]
        read_only_fields = ["id", "created_at", "messages"]