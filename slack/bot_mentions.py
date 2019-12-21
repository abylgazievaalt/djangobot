import datetime

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .models import Member, Standup, Channel
from .utils import (
    send_message_to_web_hook, get_mentioned_people,
    send_formatted_message_to_web_hook, get_random_joke,
    create_mentee, report_is_valid, get_random_quote, update_misses)


def add_mentees(text, channel):
    mentees = get_mentioned_people(text)

    for mentee in mentees:
        uid = mentee[1:]
        create_mentee(uid=uid, channel=channel, response_url=channel.web_hook)


def remove_mentees(text, channel):
    mentees = get_mentioned_people(text)

    for mentee in mentees:
        uid = mentee[1:]
        member = Member.objects.filter(uid=uid).first()
        if member:
            if member.channels.filter(uid=channel.uid).exists():
                text = _('Removed <@{}> from group {}').format(uid,
                                                               channel.name)
                member.channels.remove(channel)
            else:
                text = _('<@{}> is not registered in {}').format(uid,
                                                                 channel.name)
        else:
            text = _('<@{}> is not registered in system').format(uid,
                                                                 channel.name)

        send_message_to_web_hook(channel.web_hook, text)


def record_standup(message, channel, user):
    member = Member.objects.filter(uid=user).first()
    if member:
        if not member.channels.filter(uid=channel.uid).exists():
            text = _("You are not registered for standups in this channel")
            send_message_to_web_hook(channel.web_hook, str(text))
            return

        is_valid, text = report_is_valid(message, channel.stand_up_time)
        if is_valid:
            today_min = datetime.datetime.combine(datetime.date.today(),
                                                  datetime.time.min)
            today_max = datetime.datetime.combine(datetime.date.today(),
                                                  datetime.time.max)

            obj, created = Standup.objects.update_or_create(
                member=member, channel=channel,
                time__range=(today_min, today_max),
                defaults={'text': message}
            )
            if not created:
                text = _('<@{}> has edited own report').format(member.uid)
    else:
        text = _('<@{}> is not registered in system').format(member.uid,
                                                             channel.name)

    send_message_to_web_hook(channel.web_hook, str(text))


def general_report(current_channel):
    try:
        current_channel = Channel.objects.get(name='general')
    except Channel.DoesNotExist:
        text = _('Please specify channel for reports in admin')
        send_message_to_web_hook(current_channel.web_hook, str(text))

    channel_fields = update_misses()

    data = [
        {
            "fallback": "Daily report",
            "color": "#2eb886",
            "pretext": _("#report {}:").format(timezone.localtime().date()),
            "author_name": "",
            "author_link": "",
            "author_icon": "https://orig00.deviantart.net/c525/f/2012/302/a/8/mass_effect__edi_by_ruthieee-d4yr023.png",
            "title": "",
            "title_link": "",
            "text": "",
            "fields": channel_fields,
            "image_url": "",
            "thumb_url": "",
            "footer": "",
            "footer_icon": "",
            "ts": 0
        }
    ]

    send_formatted_message_to_web_hook(current_channel.web_hook, data)


def tell_joke(current_channel):
    joke = get_random_joke()
    send_message_to_web_hook(current_channel.web_hook, str(joke))


def tell_quote(current_channel):
    quote_dict = get_random_quote()
    data = [
        {
            "fallback": "Bit of quotes.",
            "color": "#aabca6",
            "pretext": "",
            "author_name": quote_dict['author'],
            "author_link": "",
            "author_icon": quote_dict['author_icon'],
            "title": "",
            "title_link": "",
            "text": quote_dict['quote'],
            "fields": "",
            "image_url": quote_dict['pic'],
            "thumb_url": "",
            "footer": '',
            "footer_icon": "",
            "ts": 0
        }
    ]
    send_formatted_message_to_web_hook(current_channel.web_hook, data)
