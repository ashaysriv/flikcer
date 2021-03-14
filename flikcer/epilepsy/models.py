from django.db import models
from django.contrib.postgres.fields import ArrayField

class Triggers(models.Model):
    uuid = models.CharField(max_length=64)
    url = models.CharField(max_length=512)
    num_triggers = models.IntegerField(default=0)
    status = models.CharField(max_length=16, default='loading') # downloading, processing, done
    num_frames = models.IntegerField(default=0)
    video_title = models.CharField(max_length=512, default='')
    progress = models.IntegerField(default=0)
    dangerous_frames = ArrayField(models.CharField(max_length=64), default=list)
    frames_to_remove = ArrayField(models.IntegerField(default=0), default=list)


class SafeVideo(models.Model):
    status = models.CharField(max_length=16, default='loading') # downloading, processing, done
    uuid = models.CharField(max_length=64)
    download_url = models.CharField(max_length=1024)
    frames_to_remove = ArrayField(models.IntegerField(default=0), default=list)
    safe_video_url = models.CharField(max_length=1024)
