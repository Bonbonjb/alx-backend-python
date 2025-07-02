import logging
from datetime import datetime
import os
from django.http import HttpResponseForbidden

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
