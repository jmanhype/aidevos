"""
Metrics collection and instrumentation for AIDevOS.

This module provides utilities for collecting and exposing metrics from
AIDevOS components for monitoring purposes.
"""

import time
import functools
import logging
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, TypeVar, cast

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("aidevos.monitoring.metrics")

# Type variables for generic function annotations
F = TypeVar('F', bound=Callable[..., Any])
T = TypeVar('T')


class MetricType(Enum):
    """Types of metrics supported by the AIDevOS monitoring system."""
    
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class MetricsRegistry:
    """
    Registry for AIDevOS metrics.
    
    This class provides a central registry for all metrics collected by AIDevOS
    components, ensuring that metrics are properly registered and exposed.
    """
    
    def __init__(self):
        """Initialize the metrics registry."""
        self._metrics: Dict[str, Dict[str, Any]] = {
            MetricType.COUNTER.value: {},
            MetricType.GAUGE.value: {},
            MetricType.HISTOGRAM.value: {},
            MetricType.SUMMARY.value: {},
        }
        
        # Initialize default metrics
        self._init_default_metrics()
        
        logger.info("Metrics registry initialized")
    
    def _init_default_metrics(self) -> None:
        """Initialize default metrics for AIDevOS components."""
        # System metrics
        self.create_gauge(
            name="system_memory_usage_bytes",
            description="Memory usage in bytes",
            labels=["component", "instance"],
        )
        
        self.create_gauge(
            name="system_cpu_usage_percent",
            description="CPU usage percentage",
            labels=["component", "instance"],
        )
        
        # Request metrics
        self.create_counter(
            name="http_requests_total",
            description="Total number of HTTP requests",
            labels=["component", "method", "path", "status"],
        )
        
        self.create_histogram(
            name="http_request_duration_seconds",
            description="HTTP request duration in seconds",
            labels=["component", "method", "path"],
            buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0],
        )
        
        # Durable Objects metrics
        self.create_counter(
            name="durable_object_creations_total",
            description="Total number of Durable Object creations",
            labels=["object_type"],
        )
        
        self.create_counter(
            name="durable_object_updates_total",
            description="Total number of Durable Object updates",
            labels=["object_type"],
        )
        
        self.create_gauge(
            name="durable_objects_active",
            description="Number of active Durable Objects",
            labels=["object_type"],
        )
        
        # Event metrics
        self.create_counter(
            name="events_published_total",
            description="Total number of events published",
            labels=["event_type"],
        )
        
        self.create_counter(
            name="events_consumed_total",
            description="Total number of events consumed",
            labels=["event_type", "consumer"],
        )
    
    def create_counter(self, name: str, description: str, labels: List[str] = None) -> Any:
        """
        Create a new counter metric.
        
        Args:
            name: Name of the metric
            description: Description of the metric
            labels: Labels for the metric
            
        Returns:
            The created counter metric
        """
        labels = labels or []
        
        # In a real implementation, this would create a Prometheus counter
        # For this example, we'll just create a simple dictionary
        counter = {
            "name": name,
            "description": description,
            "labels": labels,
            "type": MetricType.COUNTER.value,
            "value": 0,
        }
        
        self._metrics[MetricType.COUNTER.value][name] = counter
        logger.info(f"Created counter metric: {name}")
        return counter
    
    def create_gauge(self, name: str, description: str, labels: List[str] = None) -> Any:
        """
        Create a new gauge metric.
        
        Args:
            name: Name of the metric
            description: Description of the metric
            labels: Labels for the metric
            
        Returns:
            The created gauge metric
        """
        labels = labels or []
        
        # In a real implementation, this would create a Prometheus gauge
        # For this example, we'll just create a simple dictionary
        gauge = {
            "name": name,
            "description": description,
            "labels": labels,
            "type": MetricType.GAUGE.value,
            "value": 0,
        }
        
        self._metrics[MetricType.GAUGE.value][name] = gauge
        logger.info(f"Created gauge metric: {name}")
        return gauge
    
    def create_histogram(
        self, name: str, description: str, labels: List[str] = None, buckets: List[float] = None
    ) -> Any:
        """
        Create a new histogram metric.
        
        Args:
            name: Name of the metric
            description: Description of the metric
            labels: Labels for the metric
            buckets: Histogram buckets
            
        Returns:
            The created histogram metric
        """
        labels = labels or []
        buckets = buckets or [0.1, 0.5, 1.0, 5.0, 10.0]
        
        # In a real implementation, this would create a Prometheus histogram
        # For this example, we'll just create a simple dictionary
        histogram = {
            "name": name,
            "description": description,
            "labels": labels,
            "type": MetricType.HISTOGRAM.value,
            "buckets": buckets,
            "values": {bucket: 0 for bucket in buckets},
            "sum": 0,
            "count": 0,
        }
        
        self._metrics[MetricType.HISTOGRAM.value][name] = histogram
        logger.info(f"Created histogram metric: {name}")
        return histogram
    
    def create_summary(
        self, name: str, description: str, labels: List[str] = None, quantiles: List[float] = None
    ) -> Any:
        """
        Create a new summary metric.
        
        Args:
            name: Name of the metric
            description: Description of the metric
            labels: Labels for the metric
            quantiles: Summary quantiles
            
        Returns:
            The created summary metric
        """
        labels = labels or []
        quantiles = quantiles or [0.5, 0.9, 0.95, 0.99]
        
        # In a real implementation, this would create a Prometheus summary
        # For this example, we'll just create a simple dictionary
        summary = {
            "name": name,
            "description": description,
            "labels": labels,
            "type": MetricType.SUMMARY.value,
            "quantiles": quantiles,
            "values": {quantile: 0 for quantile in quantiles},
            "sum": 0,
            "count": 0,
        }
        
        self._metrics[MetricType.SUMMARY.value][name] = summary
        logger.info(f"Created summary metric: {name}")
        return summary
    
    def get_metric(self, name: str, metric_type: MetricType) -> Optional[Any]:
        """
        Get a metric by name and type.
        
        Args:
            name: Name of the metric
            metric_type: Type of the metric
            
        Returns:
            The metric if found, None otherwise
        """
        return self._metrics[metric_type.value].get(name)
    
    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all registered metrics.
        
        Returns:
            All registered metrics grouped by type
        """
        return self._metrics
    
    def increment_counter(self, name: str, value: float = 1, labels: Dict[str, str] = None) -> None:
        """
        Increment a counter metric.
        
        Args:
            name: Name of the counter
            value: Value to increment by
            labels: Labels for the counter
        """
        counter = self.get_metric(name, MetricType.COUNTER)
        if counter:
            # In a real implementation, this would increment a Prometheus counter
            # For this example, we'll just increment the value
            counter["value"] += value
        else:
            logger.warning(f"Counter metric not found: {name}")
    
    def set_gauge(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """
        Set a gauge metric value.
        
        Args:
            name: Name of the gauge
            value: Value to set
            labels: Labels for the gauge
        """
        gauge = self.get_metric(name, MetricType.GAUGE)
        if gauge:
            # In a real implementation, this would set a Prometheus gauge
            # For this example, we'll just set the value
            gauge["value"] = value
        else:
            logger.warning(f"Gauge metric not found: {name}")
    
    def observe_histogram(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """
        Observe a value for a histogram metric.
        
        Args:
            name: Name of the histogram
            value: Value to observe
            labels: Labels for the histogram
        """
        histogram = self.get_metric(name, MetricType.HISTOGRAM)
        if histogram:
            # In a real implementation, this would observe a value in a Prometheus histogram
            # For this example, we'll just update the relevant buckets
            histogram["sum"] += value
            histogram["count"] += 1
            
            for bucket in sorted(histogram["buckets"]):
                if value <= bucket:
                    histogram["values"][bucket] += 1
        else:
            logger.warning(f"Histogram metric not found: {name}")
    
    def observe_summary(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """
        Observe a value for a summary metric.
        
        Args:
            name: Name of the summary
            value: Value to observe
            labels: Labels for the summary
        """
        summary = self.get_metric(name, MetricType.SUMMARY)
        if summary:
            # In a real implementation, this would observe a value in a Prometheus summary
            # For this example, we'll just update the sum and count
            summary["sum"] += value
            summary["count"] += 1
            
            # Note: This is a simplistic implementation, in practice you'd need a more
            # sophisticated algorithm to compute accurate quantiles
        else:
            logger.warning(f"Summary metric not found: {name}")


# Create a global registry instance
registry = MetricsRegistry()


def timed(name: str, labels: Dict[str, str] = None) -> Callable[[F], F]:
    """
    Decorator to time a function and record the duration in a histogram.
    
    Args:
        name: Name of the histogram to record the duration
        labels: Labels for the histogram
        
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            labels_dict = labels or {}
            start_time = time.time()
            try:
                return func(*args, **kwargs)
            finally:
                duration = time.time() - start_time
                registry.observe_histogram(name, duration, labels_dict)
        return cast(F, wrapper)
    return decorator


def counted(name: str, labels: Dict[str, str] = None) -> Callable[[F], F]:
    """
    Decorator to count function calls.
    
    Args:
        name: Name of the counter to increment
        labels: Labels for the counter
        
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            labels_dict = labels or {}
            try:
                return func(*args, **kwargs)
            finally:
                registry.increment_counter(name, 1, labels_dict)
        return cast(F, wrapper)
    return decorator


class MetricsMiddleware:
    """
    Middleware for collecting HTTP request metrics.
    
    This class provides middleware for FastAPI (or other ASGI-compatible frameworks)
    to collect metrics for HTTP requests.
    """
    
    def __init__(self, app: Any, component: str = "unknown"):
        """
        Initialize the metrics middleware.
        
        Args:
            app: The ASGI application
            component: Component name to use in metrics labels
        """
        self.app = app
        self.component = component
    
    async def __call__(self, scope, receive, send):
        """ASGI middleware implementation."""
        if scope["type"] != "http":
            # Pass through non-HTTP requests
            await self.app(scope, receive, send)
            return
        
        # Get request details
        method = scope.get("method", "UNKNOWN")
        path = scope.get("path", "/")
        
        # Start timing the request
        start_time = time.time()
        
        # Modified send function to capture response status
        status_code = [None]
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code[0] = message["status"]
            await send(message)
        
        try:
            # Process the request
            await self.app(scope, receive, send_wrapper)
        finally:
            # Record metrics
            if status_code[0] is not None:
                # Record request count
                registry.increment_counter(
                    "http_requests_total",
                    1,
                    {
                        "component": self.component,
                        "method": method,
                        "path": path,
                        "status": str(status_code[0]),
                    },
                )
                
                # Record request duration
                duration = time.time() - start_time
                registry.observe_histogram(
                    "http_request_duration_seconds",
                    duration,
                    {"component": self.component, "method": method, "path": path},
                )


def instrument_fastapi(app: Any, component: str = "fastapi") -> Any:
    """
    Instrument a FastAPI application with metrics collection.
    
    Args:
        app: FastAPI application to instrument
        component: Component name to use in metrics labels
        
    Returns:
        Instrumented FastAPI application
    """
    from fastapi import FastAPI
    from prometheus_client import make_asgi_app
    
    assert isinstance(app, FastAPI), "App must be a FastAPI instance"
    
    # Add metrics middleware
    app.add_middleware(MetricsMiddleware, component=component)
    
    # Mount metrics endpoint
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)
    
    return app