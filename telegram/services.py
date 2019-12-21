import telepot
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from slack.models import Channel
from slack.utils import get_missed_member_telegram_handles


class TelegramService:
    @classmethod
    def get_bot(cls):
        return telepot.Bot(settings.BOT_TOKEN)

    @classmethod
    def send_message_to_conversation(cls, conversation_id: int, message: str):
        bot = cls.get_bot()
        bot.sendMessage(conversation_id, message)

    @classmethod
    def notify_missed_members(cls):
        channels = Channel.objects.filter(members__isnull=False).distinct()

        for channel in channels:
            missed_handles = get_missed_member_telegram_handles(channel)

            if len(missed_handles) > 0:
                text = ', '.join('@{}'.format(handle) for handle in missed_handles)
                text = _('{}: 🥾🥾🥾 repooooorts in slack, ').format(channel.name) + text
            else:
                text = _('{}: Nice! 😎👍').format(channel.name)

            cls.send_message_to_conversation(settings.MENTEE_CHANNEL_ID, str(text))
