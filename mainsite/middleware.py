import datetime
import logging
import os
import psutil

from django import http
from django.conf import settings

error_logger = logging.getLogger('watchtower-error-logger')

class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == getattr(settings, "HEALTH_CHECK_URL", "/health/"):
            output = {
                "status": "200 OK",
                "timestamp": datetime.datetime.now().isoformat(),
            }
            return http.JsonResponse(output)
        return self.get_response(request)


class MemoryUsageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.process = psutil.Process(os.getpid())

    def __call__(self, request):
        mem_before = self.process.memory_info().rss / (1024 * 1024)  # MB
        
        response = self.get_response(request)
        
        mem_after = self.process.memory_info().rss / (1024 * 1024)   # MB
        mem_diff = mem_after - mem_before
        
        # Log requests that increase RSS memory by more than 50 MB
        # (adjust threshold as needed)
        if mem_diff > 10:
            error_logger.warning(
                f"HIGH MEMORY REQUEST: {request.method} {request.path} | "
                f"Before: {mem_before:.2f}MB | After: {mem_after:.2f}MB | "
                f"Delta: +{mem_diff:.2f}MB"
            )
            
        return response