from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from slack.bot_mentions import (
    record_standup,
    general_report, tell_joke, tell_quote)
from slack.models import Channel
from slack.slash_commands import (
    add_channel, add_mentee_slash, slackers_list, remind_command_handler,
    remove_mentee_slash, excuse_mentee
)
from slack.utils import is_bot_admin, send_message_to_web_hook


class UrlVerification(APIView):
    def post(self, request):
        challenge = request.data['challenge']
        return Response({"challenge": challenge}, status=status.HTTP_200_OK)


class BotMentionAPIView(APIView):
    def post(self, request):
        standart = {
            "token": "ZZZZZZWSxiZZZ2yIvs3peJ",
            "team_id": "T061EG9R6",
            "api_app_id": "A0MDYCDME",
            "event": {
                "type": "app_mention",
                "user": "U061F7AUR",
                "text": "What is the hour of the pearl, <@U0LAN0Z89>?",
                "ts": "1515449522.000016",
                "channel": "C0LAN2Q65",
                "event_ts": "1515449522000016"
            },
            "type": "event_callback",
            "event_id": "Ev0LAN670R",
            "event_time": 1515449522000016,
            "authed_users": [
                "U0LAN0Z89"
            ]
        }

        # print(request.data)
        event = request.data['event']

        channel_uid = event['channel']
        channel = get_object_or_404(Channel, uid=channel_uid)

        user = event['user']
        text = event['text']

        if 'standup' in text:
            record_standup(text, channel, user)

        elif 'report' in text and is_bot_admin(user):
            general_report(channel)

        # elif 'addMentee' in text and is_bot_admin(user):
        #     add_mentees(text, channel)

        # elif 'removeMentee' in text and is_bot_admin(user):
        #     remove_mentees(text, channel)

        # MISC #

        elif 'joke' in text:
            tell_joke(channel)

        elif 'quote' in text:
            tell_quote(channel)

        return Response(status=status.HTTP_200_OK)


class SlashAPIView(APIView):
    def post(self, request):
        standart = {
            "token": "i9Mi4jAcWv11Vg8HoMCTBz0K",
            "team_id": "TAG60J5JS",
            "team_domain": "neobis",
            "channel_id": "GBJA5CCQK",
            "channel_name": "privategroup",
            "user_id": "UAGC8SK7Z",
            "user_name": "aaurub",
            "command": "/addchannel",
            "text": "Backend Mentors",
            "response_url":
                "https://hooks.slack.com/commands/TAG60J5JS/485000801506/Ya2ICriWKLBZRxNgOqw4dLuy",
            "trigger_id":
                "484396273889.356204617638.170d452289f49c089a46d1c10f8ac6e4"
        }

        # print(request.data)

        payload = request.data
        command = payload['command']
        user = payload['user_id']

        if command == '/slackers':
            slackers_list(payload)

        elif command == '/ping':
            remind_command_handler(payload)

        if is_bot_admin(user):
            if command == '/addchannel':
                add_channel(payload)

            elif command == '/addmentee':
                add_mentee_slash(payload)

            elif command == '/removementee':
                remove_mentee_slash(payload)

            elif command == '/excuse':
                excuse_mentee(payload)

        else:
            text = str(_('Not enough permissions to execute command'))
            send_message_to_web_hook(payload['response_url'], text)

        return Response(status=status.HTTP_200_OK)
