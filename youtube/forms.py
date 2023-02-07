from django import forms
from django.forms import ModelForm
from .models import Channel, VideoStatus
from django.utils.translation import gettext_lazy as _


class ChannelForm(ModelForm):
    class Meta:
        model = Channel
        fields = ['id', 'title', 'type']
        widgets = {
            'id': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-select'})
        }
        labels = {
            'id': 'ID',
            'title': 'TITLE',
            'type': 'TYPE'
        }
        error_messages = {
            'id': {
                'unique': _("Channel with this Id already exists"),
            }
        }


class VideoStatusForm(ModelForm):
    class Meta:
        model = VideoStatus
        fields = ['video', 'uploaded_id', 'status', 'published', 'original_video']
