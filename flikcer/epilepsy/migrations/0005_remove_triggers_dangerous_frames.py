# Generated by Django 3.1.1 on 2020-09-25 18:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epilepsy', '0004_triggers_dangerous_frames'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='triggers',
            name='dangerous_frames',
        ),
    ]
