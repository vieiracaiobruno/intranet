import json
from .forms import ChannelForm, VideoStatusForm
from django.shortcuts import render, redirect
from .models import Channel, Video, VideoStatus
from .services import *


def home(request):
    return render(request, 'youtube/home.html')


def channel(request):
    list = channel_list()
    if request.method == 'POST':
        form = ChannelForm(request.POST)
        add = channel_add(form)
        if add:
            form = ChannelForm
    else:
        form = ChannelForm

    return render(request, 'youtube/channel.html', {'form': form, 'channel_list': list})


def channel_add(form):
    if form.is_valid():
        try:
            form.save()
            return True
        except:
            return False
    else:
        data = form.errors.as_json()
        print(data)
        return False


def channel_delete(request, id_channel):
    channel = Channel.objects.get(pk=id_channel)
    try:
        channel.delete()
        return redirect('channel')
    except:
        return redirect('channel')


def channel_list():
    list = Channel.objects.all().order_by('title')
    return list


def video(request):
    video_list = video_list_main()
    return render(request, 'youtube/video.html', {'video_list': video_list})


def video_get(id_video):
    video = Video.objects.get(pk=id_video)
    return video


def video_list():
    list = Video.objects.all().filter(videostatus__isnull=True).order_by('published')
    for item in list:
        item.title = title_adjustment(item.title)
        item.published = time_adjustment(item.published)
        if item.channel.type == 'MA':
            item.description = ''
        else:
            item.description = get_episode(item.description)
    return list


def video_list_main():
    list = Video.objects.all().filter(videostatus__isnull=True, channel__type='MA').order_by('published')
    for item in list:
        item.published = time_adjustment(item.published)
    return list


def video_list_cuts(id_video):
    list = Video.objects.all().\
        filter(videostatus__isnull=True, channel__type='CU', description__contains=id_video).\
        order_by('-view_count')
    for item in list:
        item.title = title_adjustment(item.title)
    return list


def video_detail(request, id_video):
    video = video_get(id_video)
    list = video_list_cuts(id_video)
    return render(request, 'youtube/detail.html', {'video': video, 'video_list': list})


def video_detail_discard(request, id_video):
    video_discard_id(id_video)
    return redirect(request.META['HTTP_REFERER'])


def video_discard(request, id_video):
    video_discard_id(id_video)
    video_discard_cuts(id_video)
    video_list = video_list_main()
    return redirect('video')


def video_discard_id(id_video):
    json_string = '{' \
                  '"video": "' + id_video + '", ' \
                  '"status": "DI"' \
                  '}'
    dict_fromjson = json.loads(json_string)
    form = VideoStatusForm(dict_fromjson)
    if form.is_valid():
        form.save()
    else:
        data = form.errors.as_json()
        print("error discard = " + data)


def video_discard_cuts(id_video):
    list = Video.objects.all(). \
        filter(videostatus__isnull=True, channel__type='CU', description__contains=id_video). \
        order_by('-view_count')
    for item in list:
        video_discard_id(item.id)


def video_detail_upload(request, id_video):
    list, video = video_list_cuts(id_video)
    return render(request, 'youtube/upload.html', {'video': video, 'video_list': list})


def video_detail_upload(request, id_video):
    video = Video.objects.get(pk=id_video)
    upload_date = request.GET["uploadDate"]
    original_video = Video.objects.get(pk=request.GET["originalVideo"])
    
    if download_video(video) and download_thumbnail(video):
        status_video, response = youtube_upload_video(video, upload_date, original_video)
        if status_video:
            status_thumbnail = thumbnail_upload(video, response)
            status_delete = delete_files(video)
            json_string = '{' \
                          '"video": "' + id_video + '", ' \
                          '"uploaded_id": "' + response + '", ' \
                          '"status": "UP",' \
                          '"published": "' + upload_date + ' 09:00:00.000000",' \
                          '"original_video": "' + original_video.id + '"' \
                          '}'
            dict_fromjson = json.loads(json_string)
            form = VideoStatusForm(dict_fromjson)
            if form.is_valid():
                print("Updating video status table...")
                form.save()
            else:
                data = form.errors.as_json()
                print("Error updating video = " + data)
        else:
            print("Error uploading = ", response)

    return redirect(request.META['HTTP_REFERER'])


def uploaded(request):
    list = uploaded_list()
    for item in list:
        item.video.title = title_adjustment(item.video.title)
    return render(request, 'youtube/uploaded.html', {'uploaded_list': list})


def uploaded_list():
    list = VideoStatus.objects.exclude(published=None).order_by('-published')
    return list
