from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^verify/', views.UrlVerification.as_view()),
    #url(r'^bot_mention/', views.UrlVerification.as_view()),
    url(r'^bot_mention/', views.BotMentionAPIView.as_view()),
    url(r'^slash_commands/', views.SlashAPIView.as_view()),
]
