from datetime import datetime
from typing import Dict, Optional
import time

class MonitoringService:
    """Track enhanced metrics: request count, uptime, response times"""

    def __init__(self, db_session=None):
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        self.response_times = []  # List of response times in ms
        self.db = db_session

    def incrementRequestCount(self, response_time_ms: Optional[float] = None):
        """Increment total request count and track response time"""
        self.request_count += 1
        if response_time_ms is not None:
            self.response_times.append(response_time_ms)
            # Keep only last 1000 response times
            if len(self.response_times) > 1000:
                self.response_times = self.response_times[-1000:]

    def incrementErrorCount(self):
        """Increment error count"""
        self.error_count += 1

    def getUptime(self) -> float:
        """Get uptime in seconds"""
        delta = datetime.now() - self.start_time
        return delta.total_seconds()

    def getMetrics(self) -> Dict:
        """Get current metrics"""
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0

        return {
            "uptime_seconds": self.getUptime(),
            "request_count": self.request_count,
            "error_count": self.error_count,
            "success_rate": (self.request_count - self.error_count) / max(self.request_count, 1),
            "avg_response_time_ms": avg_response_time
        }

    def getDetailedMetrics(self) -> Dict:
        """Get detailed metrics for admin dashboard"""
        metrics = self.getMetrics()

        # Add cache info if available
        try:
            from ..data.cache_manager import CacheManager
            cache = CacheManager()
            metrics["cache_size"] = len(cache.cache)
        except:
            metrics["cache_size"] = 0

        return metrics

    def saveMetricSnapshot(self):
        """Persist current metrics to database (called periodically)"""
        if self.db:
            from ..data.database import Metric
            metrics = self.getDetailedMetrics()
            snapshot = Metric(
                timestamp=datetime.now(),
                request_count=self.request_count,
                error_count=self.error_count,
                success_rate=metrics["success_rate"],
                cache_size=metrics.get("cache_size", 0),
                response_time_avg=metrics.get("avg_response_time_ms", 0)
            )
            self.db.add(snapshot)
            self.db.commit()

    def reset(self):
        """Reset all metrics"""
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        self.response_times = []

