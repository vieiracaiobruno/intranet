from django.urls import path
from youtube.views import home, channel, video, channel_delete, video_discard, video_detail_upload, video_detail, \
    video_detail_discard, uploaded

urlpatterns = [
    path('', home, name='youtube-home'),
    path('channel/', channel, name='channel'),
    path('channel/delete/<id_channel>', channel_delete, name='channel-delete'),
    path('video/', video, name='video'),
    path('video/discard/<id_video>', video_discard, name='video-discard'),
    path('video/detail/<id_video>', video_detail, name='video-detail'),
    path('video/detail/upload/<id_video>', video_detail_upload, name='video-detail-upload'),
    path('video/detail/discard/<id_video>', video_detail_discard, name='video-detail-discard'),
    path('uploaded', uploaded, name='uploaded')
]
