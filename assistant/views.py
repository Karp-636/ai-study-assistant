# assistant/views.py
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


from .models import Document, DocumentChunk, Conversation, Message
from .serializers import (
    DocumentSerializer,
    DocumentCreateSerializer,
    AskQuestionSerializer,
    ConversationSerializer,
    MessageSerializer,
)
from .chunking import chunk_text
from .embeddings import generate_embeddings_batch

from .rag import (
    retrieve_relevant_chunks,
    generate_rag_response,
    ask_with_rag,
)

@api_view(["GET", "POST"])
def document_list(request):
    """List all documents or upload a new one."""
    if request.method == "GET":
        documents = Document.objects.all().order_by("-created_at")
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)

    # POST: Create a new document, chunk it, and generate embeddings
    serializer = DocumentCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # Save the document
    doc = serializer.save()

    # Chunk the content
    chunks = chunk_text(doc.content)
    print("CONTENT:", repr(doc.content))
    print("CHUNKS:", chunks)

    if not chunks:
        return Response(
            DocumentSerializer(doc).data,
            status=status.HTTP_201_CREATED,
        )

    # Generate embeddings for all chunks in one batch call
    embeddings = generate_embeddings_batch(chunks)

    # Create chunk objects
    chunk_objects = [
        DocumentChunk(
            document=doc,
            chunk_text=text,
            chunk_index=idx,
            embedding=emb,
        )
        for idx, (text, emb) in enumerate(zip(chunks, embeddings))
    ]
    DocumentChunk.objects.bulk_create(chunk_objects)

    return Response(
        DocumentSerializer(doc).data,
        status=status.HTTP_201_CREATED,
    )



@api_view(["POST"])
def ask_question(request):
    """RAG endpoint: retrieve relevant chunks, then generate an answer."""
    serializer = AskQuestionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    question = serializer.validated_data["question"]

    # Check that we have documents to search
    if not DocumentChunk.objects.exists():
        return Response({
            "answer": "No study materials have been uploaded yet. Please upload documents first.",
            "sources": [],
        })

    # Steps 1 & 2: Retrieve relevant chunks
    chunks = retrieve_relevant_chunks(question, top_k=5)

    # Step 3: Generate answer using retrieved context
    answer = generate_rag_response(question, chunks)

    return Response({
        "answer": answer,
        "sources": [
            {
                "document": chunk["document_title"],
                "text_preview": chunk["chunk_text"][:200] + "..."
                    if len(chunk["chunk_text"]) > 200
                    else chunk["chunk_text"],
                "relevance_score": round(1 - chunk["distance"], 3),
            }
            for chunk in chunks
        ],
    })


@api_view(["GET", "POST"])
def conversation_list(request):
    """List conversations or create a new conversation."""
    if request.method == "GET":
        conversations = Conversation.objects.all()
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)

    serializer = ConversationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    conversation = serializer.save()

    return Response(
        serializer.data,
        status=status.HTTP_201_CREATED,
    )

@api_view(["GET"])
def conversation_detail(request, pk):
    """Get one conversation with all of its messages."""
    try:
        conversation = Conversation.objects.get(pk=pk)
    except Conversation.DoesNotExist:
        return Response(
            {"detail": "Conversation not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = ConversationSerializer(conversation)
    return Response(serializer.data)


@api_view(["POST"])
def conversation_ask(request, pk):
    """Ask a question within a conversation using RAG and conversation history."""
    try:
        conversation = Conversation.objects.get(pk=pk)
    except Conversation.DoesNotExist:
        return Response(
            {"detail": "Conversation not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = AskQuestionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    question = serializer.validated_data["question"]

    if not DocumentChunk.objects.exists():
        return Response({
            "answer": "No study materials have been uploaded yet. Please upload documents first.",
            "sources": [],
        })

    try:
        answer, chunks = ask_with_rag(question, conversation)
    except ValueError as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return Response({
        "answer": answer,
        "sources": [
            {
                "document": chunk["document_title"],
                "text_preview": chunk["chunk_text"][:200] + "..."
                    if len(chunk["chunk_text"]) > 200
                    else chunk["chunk_text"],
                "relevance_score": round(
                    1 - float(chunk["distance"]),
                    3,
                ),
            }
            for chunk in chunks
        ],
    })

@api_view(["GET", "POST"])
def message_list(request):
    """List messages or create a new message."""
    if request.method == "GET":
        messages = Message.objects.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    serializer = MessageSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    message = serializer.save()

    return Response(
        serializer.data,
        status=status.HTTP_201_CREATED,
    )

@api_view(["DELETE"])
def document_detail(request, pk):
    """Delete a document and all of its chunks."""
    try:
        document = Document.objects.get(pk=pk)
    except Document.DoesNotExist:
        return Response(
            {"detail": "Document not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    document.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)