from django.db import models
from django.utils.translation import gettext_lazy as _


class Channel(models.Model):

    class Type(models.TextChoices):
        MAIN = 'MA', _('Main')
        CUTS = 'CU', _('Cuts')

    id = models.CharField(max_length=24, primary_key=True)
    title = models.CharField(max_length=50)
    type = models.CharField(
        max_length=2,
        choices=Type.choices,
        default='MA'
    )


class Video(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    id = models.CharField(max_length=11, primary_key=True)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=5000)
    category = models.SmallIntegerField()
    tags = models.CharField(max_length=500)
    thumbnail = models.CharField(max_length=100)
    view_count = models.IntegerField()
    like_count = models.IntegerField()
    published = models.DateTimeField()


class VideoStatus(models.Model):

    class Status(models.TextChoices):
        UPLOAD = 'UP', _('Upload')
        DISCARD = 'DI', _('Discard')

    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    uploaded_id = models.CharField(max_length=11, blank=True)
    status = models.CharField(
        max_length=2,
        choices=Status.choices
    )
    published = models.DateTimeField(null=True, blank=True)
    original_video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='original_video', null=True, blank=True)
