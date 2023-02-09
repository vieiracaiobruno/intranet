import shutil
from datetime import datetime
import httplib2
import requests
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from pytube import YouTube


def title_adjustment(text):
    return text[0:text.find("|") - 1].strip()


def time_adjustment(time):
    return time.date()


def get_episode(text):
    x = text.find('https://youtu.be/')
    if not x > 0:
        x = text.find('https://www.youtube.com/watch?v=')
        if not x > 0:
            return 'Error'
        else:
            x = x + len('https://www.youtube.com/watch?v=')
    else:
        x = x + len('https://youtu.be/')

    y = x + 11
    return text[x:y].strip()


def get_root_folder():
    return './Projetos/intranet/'


def get_video_folder():
    return './Downloads/intranet/'


def get_client_secret_upload_video():
    return get_root_folder() + 'certificates/client_secret_upload_video.json'


def get_client_secret_upload_thumbnail():
    return get_root_folder() + 'certificates/client_secret_upload_thumbnail.json'


def youtube_authenticated_service(client_secret):
    flow = flow_from_clientsecrets(client_secret,
                                   scope='https://www.googleapis.com/auth/youtube',
                                   message='Missing client secret')

    storage = Storage("%s-oauth2.json" % client_secret)
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage)

    return build('youtube', 'v3',
                 http=credentials.authorize(httplib2.Http()))


def youtube_upload_video(video, upload_date, original_video):
    year = int(upload_date[0:4])
    month = int(upload_date[5:7])
    day = int(upload_date[8:10])
    dt = datetime(year, month, day, 15, 0, 0, 0)
    iso_date = dt.isoformat()

    description = 'Assista ao episódio completo aqui: https://www.youtube.com/watch?v=' + get_episode(video.description) + \
                  '\n\n' + original_video.title

    request_body = {
        'snippet': {
            'title': title_adjustment(video.title) + ' [REUPLOAD]',
            'description': description,
            'categoryId': video.category,
            'tags': [video.tags]
        },
        'status': {
            'privacyStatus': 'private',
            'publishAt': iso_date
        }
    }

    youtube = youtube_authenticated_service(get_client_secret_upload_video())

    file = get_video_folder() + video.channel.id + '/' + video.id + '/video.mp4'
    print("Uploading video...")
    insert_request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=MediaFileUpload(file, chunksize=-1, resumable=True)
    )

    response = None
    try:
        status, response = insert_request.next_chunk()
        if response is not None:
            if 'id' in response:
                return True, response['id']
            else:
                return False, 'UploadErrorNoId'
        else:
            return False, 'UploadError'
    except Exception as err:
        print(err)
        return False, 'UploadErrorTry'


def thumbnail_upload(video, uploaded_video_id):
    print("Uploading thumbnail...")
    file = get_video_folder() + video.channel.id + "/" + video.id + '/thumbnail.jpg'
    youtube = youtube_authenticated_service(get_client_secret_upload_thumbnail())

    try:
        youtube.thumbnails().set(
            videoId=uploaded_video_id,
            media_body=file
        ).execute()
        return True
    except:
        return False


def download_video(video):
    print("Downloading video...")
    folder = get_video_folder() + video.channel.id + "/" + video.id
    link = 'https://www.youtube.com/watch?v=' + str(video.id)
    youtubeObject = YouTube(link)
    youtubeObject = youtubeObject.streams.get_highest_resolution()
    try:
        youtubeObject.download(folder, filename='video.mp4')
        return True
    except:
        return False


def download_thumbnail(video):
    print("Downloading thumbnail...")
    folder = get_video_folder() + video.channel.id + "/" + video.id
    res = requests.get(video.thumbnail, stream=True)
    try:
        with open(folder + '/thumbnail.jpg', 'wb') as f:
            shutil.copyfileobj(res.raw, f)
        return True
    except:
        return False


def delete_files(video):
    print("Deleting files...")
    folder = get_video_folder() + video.channel.id + "/" + video.id
    shutil.rmtree(folder)
    return True
