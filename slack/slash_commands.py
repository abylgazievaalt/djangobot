import datetime

from django.db.models import Count, Q
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from rest_framework.generics import get_object_or_404

from .models import Channel, Member, Excuse
from .utils import (
    send_message_to_web_hook, remind_channel_members,
    get_escaped_people, create_mentee, send_formatted_message_to_web_hook,
)


def add_channel(payload):
    uid = payload['channel_id']

    channel = Channel.objects.filter(uid=uid)
    if not channel.exists():
        name = payload['text']
        if len(name) == 0:
            name = payload['channel_name']
        Channel.objects.create(name=name, uid=uid)

        send_message_to_web_hook(payload['response_url'], str(_('Channel added')))
        return

    send_message_to_web_hook(payload['response_url'], str(_('Channel already in system')))


def add_mentee_slash(payload):
    channel_uid = payload['channel_id']
    channel = get_object_or_404(Channel, uid=channel_uid)
    # response_url = payload['response_url']

    mentees = get_escaped_people(payload['text'])

    for mentee in mentees:
        create_mentee(uid=mentee['uid'], name=mentee['name'],
                      channel=channel, response_url=channel.web_hook)


def remove_mentee_slash(payload):
    channel_uid = payload['channel_id']
    channel = get_object_or_404(Channel, uid=channel_uid)

    mentees = get_escaped_people(payload['text'])

    for mentee in mentees:
        member = Member.objects.filter(uid=mentee['uid']).first()

        if member:
            if member.channels.filter(uid=channel_uid).exists():
                text = _('Removed <@{}> from group {}').format(member.uid,
                                                               channel.name)
                member.channels.remove(channel)
            else:
                text = _('<@{}> is not registered in {}').format(member.uid,
                                                                 channel.name)
        else:
            text = _('<@{}> is not registered in system').format(member.uid,
                                                                 channel.name)

        send_message_to_web_hook(channel.web_hook, text)


def excuse_mentee(payload):
    channel_uid = payload['channel_id']
    channel = get_object_or_404(Channel, uid=channel_uid)

    split_payload = payload['text'].split()
    excuser = '<@{}>'.format(payload['user_id'])

    try:
        mentee = get_escaped_people(payload['text'])[0]
        date_until = datetime.datetime.strptime(split_payload[1], '%d.%m.%Y').date()
        reason = ' '.join(split_payload[2:])

    except IndexError:
        text = _('Usage: `/excuse @name 01.01.2020 Reason for excuse`')
        send_message_to_web_hook(channel.web_hook, text)
        return

    if date_until < now().date():
        text = _('Date for excuse is in the past')
        send_message_to_web_hook(channel.web_hook, text)
        return

    member = Member.objects.filter(uid=mentee['uid']).first()
    if member:
        if member.channels.filter(uid=channel_uid).exists():
            text = _('{} excused <@{}> from group {} until {}. Reason: {}').format(
                excuser, member.uid, channel.name, date_until, reason)
            member.channels.remove(channel)
            Excuse.objects.update_or_create(member=member, channel=channel, reason=reason, until=date_until)
        else:
            text = _('<@{}> is not registered in {}').format(member.uid, channel.name)
    else:
        text = _('<@{}> is not registered in system').format(member.uid, channel.name)

    send_message_to_web_hook(channel.web_hook, text)


def remind_command_handler(payload):
    params = payload['text']

    if 'all' in params:
        channels = Channel.objects.filter(members__isnull=False).distinct()
    else:
        channels = Channel.objects.filter(uid=payload['channel_id'])
    for channel in channels:
        remind_channel_members(channel)


def slackers_list(payload):
    dates = payload['text'].split('-')
    today = datetime.datetime.today()

    try:
        start_date = datetime.datetime.strptime(dates[0], "%d.%m.%y").date()
    except:
        last_monday = today - datetime.timedelta(days=today.weekday())
        start_date = last_monday.date()

    try:
        end_date = datetime.datetime.strptime(dates[1], "%d.%m.%y").date()
    except:
        end_date = today.date()

    slackers = Member.objects.filter(
        Q(misses__date__gte=start_date) &
        Q(misses__date__lte=end_date)).annotate(
        miss_count=Count('misses')
    ).order_by('-miss_count').values_list('uid', 'miss_count')

    fields = []

    for slacker in slackers:
        fields.append(
            {
                "value": '<@{}>: {}'.format(slacker[0], slacker[1]),
                "short": False,
            }
        )

    data = [
        {
            "fallback": "Slackers",
            "color": "#ff0086",
            "pretext": _("Slackers `{}` - `{}`:").format(start_date, end_date),
            "author_name": "",
            "author_link": "",
            "author_icon": "https://orig00.deviantart.net/c525/f/2012/302/a/8/mass_effect__edi_by_ruthieee-d4yr023.png",
            "title": "",
            "title_link": "",
            "text": "",
            "fields": fields,
            "image_url": "",
            "thumb_url": "",
            "footer": "",
            "footer_icon": "",
            "ts": 0
        }
    ]

    try:
        channel = Channel.objects.get(name='general')
        response_url = channel.web_hook
    except Channel.DoesNotExist:
        try:
            channel = Channel.objects.get(uid=payload['channel_id'])
            response_url = channel.web_hook
        except Channel.DoesNotExist:
            response_url = payload['response_url']

    send_formatted_message_to_web_hook(response_url, data)
