from datetime import datetime

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        path = request.path
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_entry = f"{timestamp} - User: {user} - Path: {path}\n"

        with open("requests.log", "a") as logfile:
            logfile.write(log_entry)

        return self.get_response(request)
