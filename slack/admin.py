from django.contrib import admin

from .models import Channel, Member, BotAdmin, Standup, Miss, Excuse


class MissInline(admin.StackedInline):
    model = Miss
    readonly_fields = ('member',)
    extra = 0


class MembershipInline(admin.StackedInline):
    model = Member.channels.through
    extra = 0


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'uid', 'stand_up_time', 'web_hook')
    inlines = (MembershipInline,)


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    inlines = (MembershipInline, MissInline,)
    exclude = ('channels',)
    list_display = ('uid', 'name', 'telegram_handler')
    list_filter = ('channels',)
    list_editable = ('telegram_handler',)


@admin.register(BotAdmin)
class BotAdminAdmin(admin.ModelAdmin):
    list_display = ('uid', 'name')


@admin.register(Standup)
class StandupAdmin(admin.ModelAdmin):
    list_display = ('member', 'channel', 'time')
    list_filter = ('channel', 'time', 'member')
    date_hierarchy = 'time'


@admin.register(Miss)
class MissAdmin(admin.ModelAdmin):
    list_display = ('member', 'date', 'channel')
    list_filter = ('date', 'channel', 'member')
    date_hierarchy = 'date'
    search_fields = ('member__name',)


@admin.register(Excuse)
class MissAdmin(admin.ModelAdmin):
    list_display = ('member', 'until', 'channel', 'reason', 'created')
    list_filter = ('until', 'channel', 'member')
    date_hierarchy = 'created'
    search_fields = ('member__name',)
