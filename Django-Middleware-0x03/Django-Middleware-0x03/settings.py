import logging
import time
from datetime import datetime
import os
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from collections import defaultdict
from threading import Lock

# Set up logging to a file
logger = logging.getLogger(__name__)
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'requests.log')
handler = logging.FileHandler(log_file)
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_entry = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_entry)
        return self.get_response(request)

class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_time = datetime.now().time()
        restricted_start = time(21, 0)  # 9:00 PM
        restricted_end = time(18, 0)    # 6:00 PM

        # Block access if outside allowed window
        if current_time >= restricted_start or current_time <= restricted_end:
            return HttpResponseForbidden("Access to the chat is restricted during this time.")

        return self.get_response(request)

class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.ip_log = defaultdict(list)  # {ip: [timestamps]}
        self.lock = Lock()

    def __call__(self, request):
        if request.method == 'POST' and request.path.startswith('/chats/'):
            ip = self.get_client_ip(request)
            now = time.time()

            with self.lock:
                timestamps = self.ip_log[ip]
                # Remove timestamps older than 60 seconds
                timestamps = [t for t in timestamps if now - t < 60]
                timestamps.append(now)
                self.ip_log[ip] = timestamps

                if len(timestamps) > 5:
                    return JsonResponse({
                        'error': 'Rate limit exceeded. You can only send 5 messages per minute.'
                    }, status=429)

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        restricted_paths = ['/chats/delete/', '/chats/manage/']  # Customize as needed

        if request.path in restricted_paths:
            user = getattr(request, 'user', None)
            if not user or not user.is_authenticated:
                return JsonResponse({'error': 'Authentication required.'}, status=403)

            user_role = getattr(user, 'role', None)  # assumes user.role exists

            if user_role not in ['admin', 'moderator']:
                return JsonResponse({'error': 'Permission denied. Admin or moderator only.'}, status=403)

        return self.get_response(request)
