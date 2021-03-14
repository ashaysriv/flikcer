import numpy as np
import os
import pafy
from math import ceil
from .models import Triggers
from .models import SafeVideo

def get_worst(video):
    index = 0
    for i, stream in enumerate(video.streams):
        if stream.get_filesize() < video.streams[0].get_filesize():
            index = i
    return video.streams[index]

def download_video(url, trigger):
    import cv2
    # original = [] # Stores the original video for downloading
    frames = [] # Stores the new video for processing

    if "youtu" in url:

        vPafy = pafy.new(url)
        play = get_worst(vPafy)

        trigger.status = 'downloading'
        trigger.video_title = play.title
        trigger.save()

        size_check = play.get_filesize()

        sample = play.url

        if size_check > 52428800:
            sample = ""
            trigger.video_title = 'exceeded'
            trigger.save()

    else:
        sample = url
        trigger.status = 'downloading'
        trigger.video_title = "Uploaded Video"
        trigger.save()

    compiled_table = []

    vid = cv2.VideoCapture(sample)
    fps = vid.get(cv2.CAP_PROP_FPS) # Get video fps

    total_frames = vid.get(cv2.CAP_PROP_FRAME_COUNT)
    trigger.num_frames = total_frames
    trigger.save()

    while(vid.isOpened()):
        rtrn, frame = vid.read()
        if rtrn == False:
            break
        # original.append(frame)
        frame_res = cv2.resize(frame, (160,120), interpolation = cv2.INTER_AREA) # Change video resolution
        frames.append(frame_res)

        current_frame = vid.get(cv2.CAP_PROP_POS_FRAMES)

        print (f'{current_frame} / {total_frames}')
        if current_frame % 89 == 0:
            trigger.progress = current_frame
            trigger.save()

        if len(frames) >= 250:
            triggers = run(np.array(frames))
            compiled_table = np.concatenate((compiled_table, triggers))
            frames = []

    triggers = run(np.array(frames))
    compiled_table = np.concatenate((compiled_table, triggers))

    trigger.status = 'downloaded'
    trigger.progress = total_frames
    trigger.save()
#     cv2.destroyAllWindows()
    vid.release()
    return fps, compiled_table

def run(frames):
    avg_lum_frames = 413.435*(0.002745 * frames.mean(axis=3) + 0.0189623)**2.2
    change_lum = np.delete(avg_lum_frames, 0, 0) - np.delete(avg_lum_frames, -1, 0)

    pos_lum = change_lum.copy().reshape(change_lum.shape[0], -1)
    pos_lum[pos_lum < 0] = 0
    pos_lum.sort(axis=1)
    pos_lum = np.flip(pos_lum, axis=1)

    neg_lum = -change_lum.copy().reshape(change_lum.shape[0], -1)
    neg_lum[neg_lum < 0] = 0
    neg_lum.sort(axis=1)
    neg_lum = np.flip(neg_lum, axis=1)

    QUARTER = ceil(pos_lum.shape[1] / 4)

    p_avgL = pos_lum[:,:QUARTER].mean(axis=1)
    n_avgL = neg_lum[:,:QUARTER].mean(axis=1)

    table = p_avgL - n_avgL
    table[table > 0] = p_avgL[table > 0]
    table[table <= 0] = -n_avgL[table <= 0]

    return table

def get_fin_frame(table):
    def getSign(x):
        if x > 0 :
            sign = "pos"
        else:
            sign = "neg"
        return sign

    fin = []
    fin_frames = []

    cum = table[0]
    fin_frame = 1

    for change in range(len(table)-1):
        if getSign(table[change]) == getSign(table[change + 1]):
            cum += table[change + 1]
            fin_frame += 1
        else:
            fin.append(cum)
            fin_frames.append(fin_frame)
            cum = table[change + 1]
            fin_frame = change + 2
    return fin_frames, fin

def get_ep_and_rm_frm(fin_frames, fin):
    ep_frm = []
    rem_frm = []

    prev = 0
    for x in range(len(fin)) :
        if abs(fin[x]) >= 20 :
            frame_inc = fin_frames[x] - prev
            prev = fin_frames[x]
            rem_frm.append(fin_frames[x])
            ep_frm.append(frame_inc)
    return ep_frm, rem_frm

def possible_triggers(ep_frm, fps, rem_frm):
    ext = 0
    dangerous_frames = []
    score = 0
    hits = 0
    for a in range(len(ep_frm)):
        if score < fps:
            score += ep_frm[a]
            hits += 1
        else:
            if hits > 3 :
                ext += 1
                dangerous_frames.append(rem_frm[a-3])
            score = 0
            hits = 0
    frames_to_remove = dangerous_frames
    dangerous_frames = np.array(dangerous_frames)
    dangerous_frames = dangerous_frames/fps
    return ext, dangerous_frames,  frames_to_remove

def get_times(dangerous_frames):
    time_stamps = []
    for x in dangerous_frames:
        if x > 60:
            minutes = (x) // 60
        else:
            minutes = 0
        seconds = x % 60
        milliseconds = (x*100) % 100
        timestamp = "%d:%02d:%02d" % (minutes, seconds, milliseconds)
        time_stamps.append(timestamp)
    return time_stamps

def clean_video(frames, fps):
    fin_frames, fin = get_fin_frame(frames)
    ep_frm, rem_frm = get_ep_and_rm_frm(fin_frames, fin)
    num_triggers, dangerous_frames, frames_to_remove = possible_triggers(ep_frm, fps, rem_frm)
    dangerous_frames_times = get_times(dangerous_frames)
    return num_triggers, dangerous_frames_times, frames_to_remove

def num_triggers_in_url(url, trigger):
    fps, frames = download_video(url, trigger)

    trigger.status = 'analyzing'

    num_triggers, dangerous_frames_times, frames_to_remove = clean_video(frames, fps)

    trigger.status = 'done'
    trigger.dangerous_frames = dangerous_frames_times
    trigger.frames_to_remove = frames_to_remove
    trigger.num_triggers = num_triggers
    trigger.save()

    safe_video_object, is_new = SafeVideo.objects.get_or_create(uuid=trigger.uuid)
    if is_new:
        safe_video_object.status = 'ready'
        safe_video_object.download_url = url
        safe_video_object.frames_to_remove = frames_to_remove
        safe_video_object.save()

    return num_triggers
