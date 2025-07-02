import logging
from datetime import datetime
import os

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
