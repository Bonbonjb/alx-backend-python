from datetime import datetime
from django.http import HttpResponseForbidden
import time
from django.http import JsonResponse
from django.http import JsonResponse

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # You can customize this to log what you need
        method = request.method
        path = request.get_full_path()
        print(f"[Request] {method} {path}")  # Or use logging module

        response = self.get_response(request)
        return response


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

class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.message_log = {}

    def __call__(self, request):
        # Only monitor POST requests to the messaging endpoint
        if request.method == 'POST' and '/messages/' in request.path:
            ip = self.get_client_ip(request)
            now = time.time()
            time_window = 60  # 60 seconds
            max_messages = 5

            # Initialize message log for the IP
            if ip not in self.message_log:
                self.message_log[ip] = []

            # Remove messages older than time window
            self.message_log[ip] = [t for t in self.message_log[ip] if now - t < time_window]

            # Check if limit is exceeded
            if len(self.message_log[ip]) >= max_messages:
                return JsonResponse(
                    {"error": "Rate limit exceeded. Max 5 messages per minute."},
                    status=429
                )

            # Log current message time
            self.message_log[ip].append(now)

        return self.get_response(request)

    def get_client_ip(self, request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check only specific restricted endpoints, e.g., admin/moderator actions
        if request.path.startswith('/admin-actions/'):  # Adjust this path as needed
            user = request.user
            if not user.is_authenticated:
                return JsonResponse({"error": "Authentication required"}, status=401)

            # Assuming 'role' is a field on your user model
            user_role = getattr(user, 'role', None)
            if user_role not in ['admin', 'moderator']:
                return JsonResponse({"error": "Permission denied. Admin or moderator required."}, status=403)

        return self.get_response(request)

