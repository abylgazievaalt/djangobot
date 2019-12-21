from django.core.management import BaseCommand

from telegram.services import TelegramService


class Command(BaseCommand):
    help = 'Send the reminder to submit reports signal to telegram group'

    def handle(self, *args, **options):
        TelegramService.notify_missed_members()
        self.stdout.write(self.style.SUCCESS('Telegram ping sent!'))
