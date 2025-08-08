from .formatter import CustomLogger
import inspect


class _SmartLogger:
    def __init__(self):
        self._loggers = {}

    def _get_caller_name(self):
        try:
            frame = inspect.currentframe()
            caller_frame = frame.f_back.f_back.f_back
            if caller_frame:
                name = caller_frame.f_globals.get('__name__', '__main__')
            else:
                name = '__main__'
        except Exception:
            name = '__main__'
        finally:
            if 'frame' in locals():
                del frame
        return name

    def _get_logger(self):
        caller_name = self._get_caller_name()
        if caller_name not in self._loggers:
            self._loggers[caller_name] = CustomLogger(caller_name)
        return self._loggers[caller_name]

    def __getattr__(self, name):
        return getattr(self._get_logger(), name)


logger = _SmartLogger()

__all__ = ["logger"]
