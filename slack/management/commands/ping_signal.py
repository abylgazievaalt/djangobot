from django.core.management import BaseCommand

from slack.slash_commands import remind_command_handler


class Command(BaseCommand):
    help = 'Send the reminder to submit reports signal to slack channel'

    def handle(self, *args, **options):
        payload = {'text': 'all'}
        remind_command_handler(payload)
        self.stdout.write(self.style.SUCCESS('Ping sent!'))
