import re

import requests
from django.db.models import Q
from django.utils import timezone
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from slack.models import BotAdmin, Member, Channel, Miss, Excuse


def send_message_to_web_hook(web_hook, text):
    response = requests.post(url=web_hook, json={'text': str(text)})
    return response.status_code


def send_formatted_message_to_web_hook(web_hook, data):
    example = [
        {
            "fallback": "Required plain-text summary of the attachment.",
            "color": "#2eb886",
            "pretext": "",
            "author_name": "",
            "author_link": "",
            "author_icon": "",
            "title": "",
            "title_link": "",
            "text": "",
            "fields": "",
            "image_url": "",
            "thumb_url": "",
            "footer": "",
            "footer_icon": "",
            "ts": 0
        }
    ]

    response = requests.post(url=web_hook, json={'attachments': data})
    return response.status_code


def get_mentioned_people(message):
    p = re.compile(r"@\w+", re.I | re.M)
    return p.findall(message)[1:]


def get_escaped_people(message):
    p = re.compile(r"(\w+\|\w+)", re.I | re.M)
    people = p.findall(message)

    uid_name_pairs = []

    for person in people:
        uid_name = person.split('|')
        entry = {'uid': uid_name[0], 'name': uid_name[1]}
        uid_name_pairs.append(entry)

    return uid_name_pairs


def is_bot_admin(uid):
    return BotAdmin.objects.filter(uid=uid).exists()


def get_random_joke():
    url = 'http://api.icndb.com/jokes/random/'
    response = requests.get(url)
    if response.json()['type'] == 'success':
        return response.json()['value']['joke']
    return _('Come back later')


def get_random_quote():
    url = 'http://quotes.rest/qod.json?category=management'
    response = requests.get(url)
    if response.status_code == 200:
        quote = response.json()['contents']['quotes'][0]['quote']
        author = response.json()['contents']['quotes'][0]['author']
        pic = response.json()['contents']['quotes'][0]['background']
        return {'quote': quote, 'author': author, 'pic': pic, 'author_icon': ''}
    return {
        'quote': str(_('I\'m tired of you')),
        'author': 'Alice',
        'pic': '',
        'author_icon': "https://orig00.deviantart.net/c525/f/2012/302/a/8/mass_effect__edi_by_ruthieee-d4yr023.png"
    }


def create_mentee(uid, channel, response_url, name='none'):
    member, created = Member.objects.update_or_create(uid=uid, defaults={'name': name})

    if member.channels.filter(uid=channel.uid).exists():
        text = _('<@{}> already in the group {}').format(uid, channel.name)
    else:
        member.channels.add(channel)
        text = _('Succesfully added <@{}> to group {}').format(uid, channel.name)
    send_message_to_web_hook(response_url, text)
    end_excuse_period(member, channel)


def end_excuse_period(member, channel):
    active_excuses = Excuse.objects.filter(member=member, channel=channel, until__gte=now())
    if active_excuses.exists():
        active_excuses.last().until = now()
        active_excuses.last().save()

    Excuse.objects.filter(member=member, channel=channel, until__gt=now()).delete()


def update_misses():
    channels = Channel.objects.filter(members__isnull=False).distinct()
    channel_fields = []
    today_date = timezone.localtime().date()

    # remove all today misses to update
    Miss.objects.filter(date=today_date).delete()

    for channel in channels:
        channel_members = channel.members.all()

        # ToDo: same person in different channels should send separate reports
        today_absentees = channel_members.exclude(
            Q(standups__time__date=today_date) & Q(standups__channel=channel)
        )

        uid_mc = []

        for absentee in today_absentees:
            Miss.objects.update_or_create(member=absentee, channel=channel,
                                          date=today_date)
            uid_mc.append((
                absentee.uid,
                Miss.objects.filter(member=absentee, channel=channel).count()
            ))

        name_list = ' '.join(
            '<@{}>: {}'.format(uid, mc) for uid, mc in uid_mc)

        channel_fields.append({
            "title": channel.name,
            "value": '{}/{}: {}'.format(
                channel_members.count() - today_absentees.count(),
                channel_members.count(),
                name_list),
            "short": False
        })
    return channel_fields


def remind_channel_members(channel: Channel):
    miss_member_uids = get_missed_member_uids(channel)
    if len(miss_member_uids) > 0:
        text = ' '.join('<@{}>'.format(uid) for uid in miss_member_uids)
        text = _('Wakey wakey, ') + text
    else:
        text = _('Everyone in this channel is on time :sunglasses:')
    send_message_to_web_hook(channel.web_hook, text)


# ToDo: DRY these two
def get_missed_member_uids(channel: Channel):
    update_misses()
    today_date = timezone.localtime().date()
    miss_member_uids = Miss.objects.filter(date=today_date).filter(
        channel=channel).values_list('member__uid', flat=True).distinct()
    return miss_member_uids


# ToDo: DRY these two
def get_missed_member_telegram_handles(channel: Channel):
    update_misses()
    today_date = timezone.localtime().date()
    miss_member_handles = Miss.objects.filter(date=today_date).filter(
        channel=channel).values_list('member__telegram_handler', flat=True).distinct()
    return miss_member_handles


# TODO: rules for validating standup messages
def report_is_valid(text, channel_stand_up_time):
    if timezone.localtime().time() > channel_stand_up_time:
        status = _("You are late")
        return False, status
    if len(text) < 50:
        status = _('Your report is too short')
        return False, status

    status = _("Standup submitted")
    return True, status
