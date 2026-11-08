"""Best-effort frontend action reports; no SQL, field values or patient data are sent."""
import contextvars
import functools
import json
import queue
import re
import threading
import time
import urllib.request
import uuid
from pathlib import Path

_depth = contextvars.ContextVar("frontend_action_depth", default=0)


class Reporter:
    def __init__(self, folder, application, database):
        self.settings = Path(folder) / "gateway-telemetry.json"
        self.application, self.database = application, database
        self.session = str(uuid.uuid4())
        self.pending = queue.Queue(maxsize=512)
        threading.Thread(target=self._work, daemon=True, name="frontend-telemetry").start()

    def report(self, action, screen, status="reported", duration_ms=None, session=None):
        def safe(value):
            return re.sub(r"[^\w./: -]", "", str(value))[:120] or "unknown"
        try:
            chosen_session = str(uuid.UUID(session)) if session else self.session
            self.pending.put_nowait({"eventId": str(uuid.uuid4()), "sessionId": chosen_session,
                "database": self.database, "application": self.application, "action": safe(action),
                "screen": safe(screen), "status": status, "durationMs": duration_ms})
        except (ValueError, queue.Full):
            pass

    def wrap(self, callback, screen="frontend"):
        if callback is None or not callable(callback) or getattr(callback, "_frontend_reported", False):
            return callback
        @functools.wraps(callback)
        def run(*args, **kwargs):
            nested = _depth.get()
            token = _depth.set(nested + 1)
            start, status = time.perf_counter(), "completed"
            try:
                return callback(*args, **kwargs)
            except BaseException:
                status = "failed"
                raise
            finally:
                _depth.reset(token)
                if not nested:
                    self.report(getattr(callback, "__qualname__", "callback"), screen, status,
                                (time.perf_counter() - start) * 1000)
        run._frontend_reported = True
        return run

    def _work(self):
        while True:
            item = self.pending.get()
            try:
                config = json.loads(self.settings.read_text(encoding="utf-8-sig"))
                if not config.get("enabled", True):
                    continue
                body = json.dumps(item).encode("utf-8")
                for attempt in range(3):
                    try:
                        request = urllib.request.Request(config["endpoint"], data=body,
                            headers={"Content-Type": "application/json", "Authorization": "Bearer " + config["token"]})
                        with urllib.request.urlopen(request, timeout=3) as response:
                            response.read(4096)
                        break
                    except Exception:
                        if attempt < 2:
                            time.sleep(0.5)
            except Exception:
                pass  # Telemetry must never interrupt the prototype itself.
            finally:
                self.pending.task_done()


def install_tk(folder, application, database):
    import customtkinter as ctk
    import tkinter
    reporter = Reporter(folder, application, database)
    for cls in (ctk.CTkButton, ctk.CTkOptionMenu, ctk.CTkCheckBox, ctk.CTkRadioButton,
                ctk.CTkSwitch, ctk.CTkSegmentedButton, ctk.CTkTabview):
        if getattr(cls, "_frontend_instrumented", False):
            continue
        original_init, original_configure = cls.__init__, cls.configure
        def init(self, *args, _original=original_init, _name=cls.__name__, **kwargs):
            if "command" in kwargs:
                kwargs["command"] = reporter.wrap(kwargs["command"], _name)
            return _original(self, *args, **kwargs)
        def configure(self, *args, _original=original_configure, _name=cls.__name__, **kwargs):
            if "command" in kwargs:
                kwargs["command"] = reporter.wrap(kwargs["command"], _name)
            return _original(self, *args, **kwargs)
        cls.__init__, cls.configure, cls._frontend_instrumented = init, configure, True
    original_bind = tkinter.Misc.bind
    def bind(self, sequence=None, func=None, add=None):
        if sequence in ("<Return>", "<KP_Enter>"):
            func = reporter.wrap(func, "keyboard_submit")
        return original_bind(self, sequence, func, add)
    tkinter.Misc.bind = bind
    reporter.report("app_started", "application")
    return reporter
