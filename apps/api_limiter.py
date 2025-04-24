# -*- encoding: utf-8 -*-
"""
API Security Module - Rate Limiting for Flask
"""

from flask import request, jsonify
import time
from functools import wraps
import threading

class RateLimiter:
    """
    Rate limiter for Flask API endpoints
    Similar to express-rate-limit but for Flask applications
    """
    def __init__(self, window_ms=15 * 60 * 1000, max_requests=100, message="Too many requests from this IP, please try again later."):
        """
        Initialize rate limiter
        
        :param window_ms: Time window in milliseconds
        :param max_requests: Maximum number of requests per IP in the time window
        :param message: Message to return when rate limit is exceeded
        """
        self.window_ms = window_ms
        self.max_requests = max_requests
        self.message = message
        
        # Store IP requests with timestamps
        self.requests = {}
        
        # Lock for thread safety
        self.lock = threading.Lock()
        
        # Clean expired entries periodically
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """Start a thread to clean up expired entries periodically"""
        def cleanup():
            while True:
                time.sleep(self.window_ms / 2000)  # Half the window time in seconds
                self._cleanup_expired()
        
        thread = threading.Thread(target=cleanup, daemon=True)
        thread.start()
    
    def _cleanup_expired(self):
        """Remove expired entries from the requests dictionary"""
        now = time.time() * 1000
        with self.lock:
            for ip in list(self.requests.keys()):
                # Filter timestamps that haven't expired yet
                valid_timestamps = [ts for ts in self.requests[ip] 
                                  if now - ts < self.window_ms]
                
                if valid_timestamps:
                    self.requests[ip] = valid_timestamps
                else:
                    del self.requests[ip]
    
    def _get_ip(self):
        """Get the client's IP address"""
        # Try to get IP from X-Forwarded-For header for proxies
        if 'X-Forwarded-For' in request.headers:
            return request.headers['X-Forwarded-For'].split(',')[0].strip()
        return request.remote_addr
    
    def limit(self, f):
        """
        Decorator to limit requests to an endpoint
        
        Usage:
        @rate_limiter.limit
        @app.route('/api/endpoint')
        def endpoint():
            return jsonify({"data": "response"})
        """
        @wraps(f)
        def wrapper(*args, **kwargs):
            ip = self._get_ip()
            now = time.time() * 1000
            
            with self.lock:
                if ip not in self.requests:
                    self.requests[ip] = []
                
                # Add current timestamp
                self.requests[ip].append(now)
                
                # Clean up expired timestamps for this IP
                self.requests[ip] = [ts for ts in self.requests[ip] 
                                  if now - ts < self.window_ms]
                
                # Check if the number of requests exceeds the limit
                if len(self.requests[ip]) > self.max_requests:
                    return jsonify({"error": self.message}), 429
            
            return f(*args, **kwargs)
        
        return wrapper

# Create a default rate limiter instance
rate_limiter = RateLimiter() 