# Generated by Django 3.1.1 on 2020-09-23 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('epilepsy', '0002_auto_20200922_2044'),
    ]

    operations = [
        migrations.AddField(
            model_name='triggers',
            name='progress',
            field=models.IntegerField(default=0),
        ),
    ]