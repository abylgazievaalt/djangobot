# Generated by Django 3.0 on 2019-12-21 08:10

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('slack', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('busy_from_date', models.DateField(null=True)),
                ('busy_to_date', models.DateField(null=True)),
                ('busyness_points', models.IntegerField(default=0)),
                ('activity_points', models.IntegerField(default=0)),
                ('reports_points', models.IntegerField(default=0)),
                ('mentorship_points', models.IntegerField(default=0)),
                ('total_points', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name_plural': 'Messages',
            },
        ),
        migrations.CreateModel(
            name='Message1',
            fields=[
                ('update_id', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('text', models.CharField(max_length=255)),
                ('date', models.DateTimeField(default=datetime.datetime.utcnow)),
                ('chat_id', models.IntegerField(default=0)),
                ('sender_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='slack.User')),
            ],
        ),
    ]
