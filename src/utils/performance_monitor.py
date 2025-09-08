# logic/performance_monitor.py
"""
Performance monitoring and optimization for ShopQuote Taipy
Tracks application metrics and provides optimization recommendations
"""

import time
import psutil
import threading
from typing import Dict, Any, List
from collections import defaultdict
from datetime import datetime, timedelta
from config import get_config

class PerformanceMonitor:
    """Monitor application performance metrics"""

    def __init__(self):
        self.config = get_config()
        self.metrics = defaultdict(list)
        self.start_time = time.time()
        self.lock = threading.Lock()

        # Start background monitoring if enabled
        if self.config.enable_performance_monitoring:
            self._start_monitoring()

    def _start_monitoring(self):
        """Start background performance monitoring"""
        def monitor_loop():
            while True:
                self._collect_system_metrics()
                time.sleep(60)  # Collect every minute

        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()

    def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'memory_used_mb': psutil.virtual_memory().used / 1024 / 1024,
                'disk_usage_percent': psutil.disk_usage('/').percent,
                'active_connections': len(psutil.net_connections())
            }

            with self.lock:
                for key, value in metrics.items():
                    self.metrics[key].append(value)
                    # Keep only last 1000 measurements
                    if len(self.metrics[key]) > 1000:
                        self.metrics[key] = self.metrics[key][-1000:]

        except Exception as e:
            print(f"Error collecting system metrics: {e}")

    def record_operation_time(self, operation: str, duration: float):
        """Record operation execution time"""
        with self.lock:
            self.metrics[f'operation_{operation}_time'].append(duration)

    def record_request(self, endpoint: str, method: str, duration: float, status_code: int):
        """Record HTTP request metrics"""
        with self.lock:
            key = f'request_{endpoint}_{method}'
            self.metrics[f'{key}_duration'].append(duration)
            self.metrics[f'{key}_status_{status_code}'].append(1)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of performance metrics"""
        with self.lock:
            summary = {
                'uptime_seconds': time.time() - self.start_time,
                'total_requests': 0,
                'avg_response_time': 0,
                'system_metrics': {}
            }

            # Calculate request metrics
            request_times = []
            for key, values in self.metrics.items():
                if key.startswith('request_') and key.endswith('_duration'):
                    request_times.extend(values)
                    summary['total_requests'] += len([v for v in self.metrics.get(key.replace('_duration', '_status_200'), []) if v == 1])

            if request_times:
                summary['avg_response_time'] = sum(request_times) / len(request_times)

            # System metrics (last values)
            system_keys = ['cpu_percent', 'memory_percent', 'disk_usage_percent']
            for key in system_keys:
                if self.metrics[key]:
                    summary['system_metrics'][key] = self.metrics[key][-1]

            return summary

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate detailed performance report"""
        with self.lock:
            report = {
                'generated_at': datetime.now().isoformat(),
                'period_hours': (time.time() - self.start_time) / 3600,
                'metrics': {},
                'recommendations': []
            }

            # Analyze operation performance
            for key, values in self.metrics.items():
                if not values:
                    continue

                if key.startswith('operation_') and key.endswith('_time'):
                    operation_name = key.replace('operation_', '').replace('_time', '')
                    avg_time = sum(values) / len(values)
                    max_time = max(values)
                    report['metrics'][f'{operation_name}_avg_ms'] = avg_time * 1000
                    report['metrics'][f'{operation_name}_max_ms'] = max_time * 1000

                    if avg_time > 5.0:  # More than 5 seconds
                        report['recommendations'].append(f"Consider optimizing {operation_name} (avg: {avg_time:.2f}s)")

            # Analyze system resources
            if self.metrics['cpu_percent']:
                avg_cpu = sum(self.metrics['cpu_percent']) / len(self.metrics['cpu_percent'])
                report['metrics']['avg_cpu_percent'] = avg_cpu
                if avg_cpu > 80:
                    report['recommendations'].append("High CPU usage detected - consider scaling resources")

            if self.metrics['memory_percent']:
                avg_memory = sum(self.metrics['memory_percent']) / len(self.metrics['memory_percent'])
                report['metrics']['avg_memory_percent'] = avg_memory
                if avg_memory > 85:
                    report['recommendations'].append("High memory usage detected - consider increasing RAM")

            return report

    def get_health_status(self) -> Dict[str, Any]:
        """Get application health status"""
        summary = self.get_metrics_summary()

        # Determine health status
        cpu_ok = summary['system_metrics'].get('cpu_percent', 0) < 90
        memory_ok = summary['system_metrics'].get('memory_percent', 0) < 90
        response_ok = summary.get('avg_response_time', 0) < 10  # Less than 10 seconds

        status = "healthy" if all([cpu_ok, memory_ok, response_ok]) else "warning"

        return {
            'status': status,
            'checks': {
                'cpu_usage': 'ok' if cpu_ok else 'high',
                'memory_usage': 'ok' if memory_ok else 'high',
                'response_time': 'ok' if response_ok else 'slow'
            },
            'metrics': summary
        }

# Global performance monitor instance
_performance_monitor = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor

# Performance monitoring decorators
def monitor_operation(operation_name: str):
    """Decorator to monitor operation performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                get_performance_monitor().record_operation_time(operation_name, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                get_performance_monitor().record_operation_time(f"{operation_name}_error", duration)
                raise e
        return wrapper
    return decorator

def monitor_request(endpoint: str, method: str = "GET"):
    """Decorator to monitor HTTP request performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                # Assume 200 status if no exception
                get_performance_monitor().record_request(endpoint, method, duration, 200)
                return result
            except Exception as e:
                duration = time.time() - start_time
                get_performance_monitor().record_request(endpoint, method, duration, 500)
                raise e
        return wrapper
    return decorator