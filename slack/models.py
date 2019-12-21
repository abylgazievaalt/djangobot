import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _


class BotAdmin(models.Model):
    uid = models.CharField(max_length=20, verbose_name=_('User unique ID'))
    name = models.CharField(max_length=75, verbose_name=_('Name'))

    def __str__(self):
        return self.uid


# TODO: rework channel-member relation
class Channel(models.Model):
    name = models.CharField(max_length=30, verbose_name=_('Channel name'))
    uid = models.CharField(max_length=20, verbose_name=_('Channel unique ID'))
    web_hook = models.URLField(verbose_name=_('Incoming webhook'), blank=True)
    stand_up_time = models.TimeField(verbose_name=_('Stand up time'),
                                     default=datetime.time(11, 0))

    def __str__(self):
        return self.name


class Member(models.Model):
    uid = models.CharField(max_length=20, verbose_name=_('User unique ID'),
                           unique=True)
    telegram_handler = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=75, verbose_name=_('Name'))
    channels = models.ManyToManyField(Channel,
                                      verbose_name=_('Linked channels'),
                                      related_name='members',
                                      blank=True)

    def __str__(self):
        return '{}: {}'.format(self.name, self.uid)

    class Meta:
        verbose_name_plural = _('Members')


class Standup(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE,
                               verbose_name=_('Standup author'),
                               related_name='standups')
    channel = models.ForeignKey(Channel, on_delete=models.PROTECT,
                                verbose_name=_('Linked channel'),
                                related_name='standups')
    time = models.DateTimeField(auto_now_add=True,
                                verbose_name=_('Standup submitted time'))
    text = models.TextField(verbose_name=_('Standup content'))

    def __str__(self):
        return str(self.member)


class Miss(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE,
                               verbose_name=_('mentee'),
                               related_name='misses')
    channel = models.ForeignKey(Channel, on_delete=models.PROTECT,
                                verbose_name=_('Linked channel'),
                                related_name='misses')
    date = models.DateField(verbose_name=_('Missed day'))

    def __str__(self):
        return str(self.member)

    class Meta:
        unique_together = ('member', 'channel', 'date',)
        verbose_name_plural = _('Misses')
        ordering = ('-date', 'channel')


class Excuse(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE,
                               verbose_name=_('mentee'), related_name='excuses')
    channel = models.ForeignKey(Channel, on_delete=models.PROTECT,
                                verbose_name=_('Linked channel'),
                                related_name='excuses')
    reason = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    until = models.DateField()

    def __str__(self):
        return str(self.member)

    class Meta:
        unique_together = ('member', 'channel', 'until',)
        verbose_name_plural = _('Excuses')
        ordering = ('-until', 'channel')

class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    busy_from_date = models.DateField(null=True)
    busy_to_date = models.DateField(null=True)

    busyness_points = models.IntegerField(default=0)
    activity_points = models.IntegerField(default=0)
    reports_points = models.IntegerField(default=0)
    mentorship_points = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)

    def __str__(self):
        return "<User(FirstName='{}', LastName='{}')>".format(self.first_name, self.last_name)

    class Meta:
        verbose_name_plural = _('Messages')


class Message1(models.Model):
    __tablename__ = 'message'
    update_id = models.IntegerField(primary_key=True, unique=True)
    text = models.CharField(max_length=255)
    date = models.DateTimeField(default=datetime.datetime.utcnow)
    sender_id = models.ForeignKey(User, on_delete=models.CASCADE) #ondelete="CASCADE"
    chat_id = models.IntegerField(default=0)

    def __str__(self):
        return "<Message(text='{}', date='{}', sender_id='{}')>" \
            .format(self.text, self.date, self.sender_id)


# import datetime
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime, Boolean, func
# from sqlalchemy.orm import relationship
#
# Base = declarative_base()

# class User(Base):
#     __tablename__ = 'user'
#     id = Column(Integer, unique=True, primary_key=True)
#     first_name = Column(String)
#     last_name = Column(String)
#     messages = relationship("Message1")
#
#     busy_from_date = Column(Date, default=None)
#     busy_to_date = Column(Date, default=None)
#
#     busyness_points = Column(Integer, default=0)
#     activity_points = Column(Integer, default=0)
#     reports_points = Column(Integer, default=0)
#     mentorship_points = Column(Integer, default=0)
#     total_points = Column(Integer, default=0)
#
#     def __repr__(self):
#         return "<User(FirstName='{}', LastName='{}')>" \
#             .format(self.first_name, self.last_name)
#
#
# class Message1(Base):
#     __tablename__ = 'message'
#     update_id = Column(Integer, primary_key=True, unique=True)
#     text = Column(String)
#     date = Column(DateTime, default=datetime.datetime.utcnow)
#     sender_id = Column(Integer, ForeignKey('user.id')) #ondelete="CASCADE"
#     chat_id = Column(Integer)
#     def __repr__(self):
#         return "<Message(text='{}', date='{}', sender_id='{}')>" \
#             .format(self.first_name, self.last_name, self.sender_id)
