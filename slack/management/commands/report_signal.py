from django.core.management import BaseCommand

from slack.bot_mentions import general_report
from slack.models import Channel


class Command(BaseCommand):
    help = 'Send the report signal to slack channel'

    def handle(self, *args, **options):
        try:
            channel = Channel.objects.get(name='general')
            general_report(channel)
            self.stdout.write(self.style.SUCCESS('Signal sent!'))
        except Channel.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('No channel with name general in database'))
