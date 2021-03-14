from uuid import uuid4
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from celery.decorators import task
from celery import shared_task
from .models import Triggers, SafeVideo
from .utils import num_triggers_in_url
from .safevideo import generate_safe_video

@shared_task(name='calculate_triggers')
def calculate_triggers(url, uuid):
    trigger, _ = Triggers.objects.get_or_create(uuid=uuid)
    trigger.url = url
    trigger.status = 'loading'
    trigger.save()
    try: 
        num_triggers = num_triggers_in_url(url, trigger)
        print('Done creating object')
        return num_triggers
    except Exception as e:
        print ("I am error", e)
        trigger.status = 'error'
        trigger.save() 
        return -1


def get_response(data):
    response = JsonResponse(data, safe=False)

    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    return response


@api_view(['GET'])
def poll_number_of_triggers(request):
    try:
        if request.GET.get('password', '') != 'featherx':
            raise Exception("You don't have access to this resource")
        uuid = request.GET.get('uuid', None)
        if not uuid:
            raise Exception('You need to pass in a UUID')
        existing = Triggers.objects.filter(uuid=uuid).first()
        data = {
            'status': 'not found',
            'value': None,
        }
        if existing:
            data = {
                'status': existing.status,
                'num_triggers': existing.num_triggers,
                'url': existing.url,
                'video_title': existing.video_title,
                'num_frames': existing.num_frames,
                'progress': existing.progress,
                'dangerous_frames': existing.dangerous_frames,
                'uuid': existing.uuid,
            }

        return get_response(data)

    except Exception as e:
        return JsonResponse({'data': [], 'error': str(e)}, safe=False, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
def get_number_of_triggers(request):
    try:
        if request.GET.get('password', '') != 'featherx':
            raise Exception("You don't have access to this resource")
        url = request.GET.get('url', 'https://www.youtube.com/watch?v=ZktraWpXuso')
        existing = Triggers.objects.filter(url=url).first()

        data = {}

        if existing:
            data = {
                'status': existing.status,
                'num_triggers': existing.num_triggers,
                'url': existing.url,
                'video_title': existing.video_title,
                'num_frames': existing.num_frames,
                'progress': existing.progress,
                'dangerous_frames': existing.dangerous_frames,
                'uuid': existing.uuid,
            }
            if existing.status == 'done':
                data['state'] = 'cached'
                return get_response(data)
            elif existing.status != 'error':
                data['state'] = 'in_progress'
                return get_response(data)

        # Either error'ed last time or haven't started yet

        uuid = existing.uuid if existing else uuid4()
        calculate_triggers.delay(url, uuid)
        data = {
            'state': 'loading',
            'uuid': uuid,
        }
        # else: Already processing

        return get_response(data)

    except Exception as e:
        return JsonResponse({'data': [], 'error': str(e)}, safe=False, status=status.HTTP_403_FORBIDDEN)


# SAFE VIDEO VIEWS


@shared_task(name='make_safe_video')
def make_safe_video(uuid, level):
    safevideo = SafeVideo.objects.get(uuid=uuid)
    try:
        print ("Generating safe video")
        generate_safe_video(safevideo, level)
        print('Done creating object')
        return safevideo
    except Exception as e:
        print ("I am error", e)
        safevideo.status = 'error'
        safevideo.save()
        return -1


def get_response(data):
    response = JsonResponse(data, safe=False)

    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    return response


@api_view(['GET'])
def poll_safe_video(request):
    try:
        if request.GET.get('password', '') != 'featherx':
            raise Exception("You don't have access to this resource")
        uuid = request.GET.get('uuid', None)
        if not uuid:
            raise Exception('You need to pass in a UUID')
        existing = SafeVideo.objects.filter(uuid=uuid).first()
        data = {
            'status': 'not found',
            'value': None,
        }
        if existing:
            data = {
                'status': existing.status,
                'download_url': existing.download_url,
                'safe_video_url': existing.safe_video_url,
                'frames_to_remove': existing.frames_to_remove,
                'uuid': existing.uuid,
            }

        return get_response(data)

    except Exception as e:
        return JsonResponse({'data': [], 'error': str(e)}, safe=False, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
def get_safe_video(request):
    try:
        if request.GET.get('password', '') != 'featherx':
            raise Exception("You don't have access to this resource")
        uuid = request.GET.get('uuid', 'abcdefghijklmnopqrstuvwxyz')
        level = request.GET.get('level', 0)
        existing = SafeVideo.objects.filter(uuid=uuid).first()

        if not existing:
            raise Exception("This video has not been processed yet")

        data = {
            'status': existing.status,
            'download_url': existing.download_url,
            'safe_video_url': existing.safe_video_url,
            'frames_to_remove': existing.frames_to_remove,
            'uuid': existing.uuid,
            'state': 'in_progress'
        }

        if existing.status == 'done':
            data['state'] = 'cached'

        if existing.status in ['ready', 'error']:
            uuid = existing.uuid
            existing.status = 'loading'
            existing.save()
            make_safe_video.delay(uuid, level)

        return get_response(data)

    except Exception as e:
        return JsonResponse({'data': [], 'error': str(e)}, safe=False, status=status.HTTP_403_FORBIDDEN)

