from django.utils.timezone import now

from slack.models import Excuse
from slack.utils import create_mentee


class ExcuseService:
    @classmethod
    def check_expiring_excuses_add_mentees(cls) -> int:
        expiring_excuses = Excuse.objects.filter(until=now()).prefetch_related('member', 'channel')
        for excuse in expiring_excuses:
            create_mentee(excuse.member.uid, excuse.channel, excuse.channel.web_hook, excuse.member.name)
        return expiring_excuses.count()
