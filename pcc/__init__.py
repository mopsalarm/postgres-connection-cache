import threading
import time
from contextlib import contextmanager

import psycopg2

__all__ = ["RefreshingConnectionCache"]


class ReferenceCountedConnection(object):
    def __init__(self, *args, **kwargs):
        self._lock = threading.Lock()
        self.conn = psycopg2.connect(*args, **kwargs)
        self.count = 1

    def borrow(self):
        with self._lock:
            if self.count == 0:
                raise ValueError("reference reached zero")

            self.count += 1

    def release(self):
        with self._lock:
            if self.count == 0:
                raise ValueError("reference already reached zero")

            self.count -= 1

        if self.count == 0:
            self._close()

    def _close(self):
        # noinspection PyBroadException
        try:
            self.conn.close()
        except:
            pass


class RefreshingConnectionCache(object):
    def __init__(self, lifetime, **kwargs):
        self._kwargs = kwargs
        self._lifetime = lifetime
        self._active = None
        self._active_deadline = 0
        self._lock = threading.RLock()

    @contextmanager
    def active(self):
        with self._lock:
            now = time.time()
            if not self._active or now > self._active_deadline:
                # first try to close the current connection
                if self._active:
                    self._active.release()
                    self._active = None

                # and create a new one
                active = ReferenceCountedConnection(**self._kwargs)
                self._active = active
                self._active_deadline = time.time() + self._lifetime

            else:
                active = self._active

            # get a reference to this new connection
            active.borrow()

        try:
            yield active.conn
        finally:
            with self._lock:
                # release the connection
                active.release()

    @contextmanager
    def tx(self):
        with self.active() as conn, conn:
            yield conn
