from django.urls import path

from . import views

# You will add your endpoints here during the lesson.
urlpatterns = [
   path("documents/", views.document_list, name="document-list"),  
   path("documents/<int:pk>/", views.document_detail, name="document-detail"),

   path("ask/", views.ask_question, name="ask-question"),
  
   path("messages/", views.message_list, name="message-list"),
   
   path("conversations/", views.conversation_list, name="conversation-list"),
   path("conversations/<int:pk>/", views.conversation_detail, name="conversation-detail"),
   path("conversations/<int:pk>/ask/", views.conversation_ask, name="conversation-ask"),
]
