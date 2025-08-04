import ntplib
import threading
import time
from typing import List, Optional


class TimeSyncError(Exception):
    """Custom exception for time synchronization errors"""
    pass


class Time:
    _instance: Optional['Time'] = None
    _lock = threading.Lock()
    _DEFAULT_RESYNC_INTERVAL = 600  # 10 minutes

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._init_time_sync()
            self._initialized = True

    def _init_time_sync(self):
        """Initialize time synchronization system"""
        self._ntp_servers = [
            "time.google.com",
            "pool.ntp.org",
            "time.windows.com",
            "time.apple.com",
            "time.cloudflare.com"
        ]
        self._ntp_time_start = time.time()
        self._perf_start = time.perf_counter()
        self._resync_interval = self._DEFAULT_RESYNC_INTERVAL
        self._is_running = True
        self._sync_event = threading.Event()

        self._sync_with_ntp(initial=True)

        self._thread = threading.Thread(
            target=self._resync_loop,
            daemon=True,
            name="TimeSyncThread"
        )
        self._thread.start()

    def _sync_with_ntp(self, initial: bool = False) -> bool:
        """Attempt synchronization with NTP servers"""
        success = False
        client = ntplib.NTPClient()

        for server in self._ntp_servers:
            try:
                response = client.request(server, timeout=2, version=3)

                self._ntp_time_start = response.tx_time
                self._perf_start = time.perf_counter()
                success = True
                break
            except Exception:
                pass  # fail silently

        if not success:
            self._ntp_time_start = time.time()
            self._perf_start = time.perf_counter()
            raise TimeSyncError("Failed to sync with all NTP servers")

        return True

    def _resync_loop(self):
        """Periodic resynchronization loop"""
        while self._is_running:
            try:
                self._sync_with_ntp()
            except Exception:
                pass  # fail silently

            self._sync_event.wait(self._resync_interval)

    @property
    def time_diff(self) -> float:
        """Get current time difference between system and NTP time"""
        return (time.time() - self._ntp_time_start) - \
               (time.perf_counter() - self._perf_start)

    @staticmethod
    def get_time() -> float:
        """Get current synchronized time"""
        instance = Time()
        elapsed = time.perf_counter() - instance._perf_start
        return instance._ntp_time_start + elapsed

    @staticmethod
    def get_formatted_time(iso_format: bool = False) -> str:
        """Get formatted UTC time with microseconds"""
        ts = Time.get_time()
        if iso_format:
            formatted = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(ts))
        else:
            formatted = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ts))

        micros = int((ts % 1) * 1_000_000)
        return f"{formatted}.{micros:06d}Z" if iso_format else f"{formatted}.{micros:06d}"

    def stop(self):
        """Stop synchronization service"""
        if self._is_running:
            self._is_running = False
            self._sync_event.set()
            self._thread.join(timeout=5)
