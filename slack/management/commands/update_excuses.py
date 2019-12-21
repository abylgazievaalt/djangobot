from django.core.management import BaseCommand

from slack.services import ExcuseService


class Command(BaseCommand):
    help = 'Check the end of excuses for current day and add mentees to channels'

    def handle(self, *args, **options):
        count = ExcuseService.check_expiring_excuses_add_mentees()
        self.stdout.write(self.style.SUCCESS('{} excuses updated!'.format(count)))
