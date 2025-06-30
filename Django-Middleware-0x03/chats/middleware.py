from datetime import datetime
from django.http import HttpResponseForbidden


class RestrictAccessByTimeMiddleware:
    """
    Middleware to restrict chat access based on time.
    Only allows access during allowed hours (e.g., 8 AM to 6 PM).
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_start_hour = 8   # 8 AM
        self.allowed_end_hour = 18   # 6 PM

    def __call__(self, request):
        current_hour = datetime.now().hour
        if request.path.startswith("/messages/"):
            if not (self.allowed_start_hour <= current_hour < self.allowed_end_hour):
                return HttpResponseForbidden("Chat access is restricted during this time.")
        return self.get_response(request)
