from moviepy.editor import *
from itertools import groupby, count
from .models import SafeVideo
import pafy
import os
from google.cloud import storage
from firebase import firebase

def get_worst(video):
    index = 0
    for i, stream in enumerate(video.streams):
        if stream.get_filesize() < video.streams[0].get_filesize():
            index = i
    return video.streams[index]

def get_download_url(url):
    if "youtu" in url:
        vPafy = pafy.new(url)
        play = get_worst(vPafy)
        url = play.url
    return url

def intervals(data, fps):
    out = []
    counter = count()

    for key, group in groupby(data, key = lambda x: x-next(counter)):
        block = list(group)
        out.append([(block[0] / fps ), (block[-1] / fps)])
    return out

def generate_safe_video(safevideo, level):
    frames_to_remove = safevideo.frames_to_remove
    safevideo.status = 'downloading'

    url = get_download_url(safevideo.download_url)

    video = VideoFileClip(url)

    fps = video.fps

    video_frames = []

    extend_fps = int(fps * int(level) * 0.5)

    extend_frame = 0

    for i in range(len(frames_to_remove)):
        if (frames_to_remove[i] > extend_frame):
            video_frames.extend([frames_to_remove[i] + c for c in range(extend_fps)])
            extend_frame = frames_to_remove[i] + extend_fps - 1

    audio_frames = intervals(video_frames, fps)
    audio_frames.reverse()

    safevideo.status = 'analysing'

    for cut in range(len(audio_frames)):
        t1 = audio_frames[cut][0]
        t2 = audio_frames[cut][1]
        video = video.cutout(t1, t2)

    output_url = f'{safevideo.uuid}.mp4'

    video.write_videofile(output_url,
                        codec='libx264',
                        audio_codec='aac',
                        temp_audiofile='temp-audio.m4a',
                        remove_temp=True
                        )

    safevideo.status = 'uploading'
    safevideo.save()

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "flikcer-224d7-2bb64541d88a.json"
    client = storage.Client()
    bucket = client.get_bucket('flikcer-224d7.appspot.com')
    blob = bucket.blob('downloads/ ' + output_url)
    blob.upload_from_filename(filename = output_url)

    safevideo.status = 'done'
    safevideo.safe_video_url = output_url
    safevideo.save()

    return output_url