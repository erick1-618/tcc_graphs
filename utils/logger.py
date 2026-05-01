import logging
import time
from contextlib import contextmanager


class IndentLogger:
    def __init__(self, level=logging.DEBUG):

        self.depth = 0

        self.logger = logging.getLogger("bmssp")
        self.logger.setLevel(level)
        self.logger.propagate = False

        # remove handlers antigos
        if self.logger.handlers:
            self.logger.handlers.clear()

        handler = logging.StreamHandler()
        handler.setLevel(level)

        formatter = logging.Formatter(
            "%(levelname)s | %(message)s"
        )

        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _prefix(self):
        return "│   " * self.depth

    def debug(self, msg):
        self.logger.debug(self._prefix() + msg)

    def info(self, msg):
        self.logger.info(self._prefix() + msg)

    def warning(self, msg):
        self.logger.warning(self._prefix() + msg)

    @contextmanager
    def section(self, title):
        self.debug(f"┌─ {title}")
        self.depth += 1

        start = time.perf_counter()

        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            self.depth -= 1
            self.debug(f"└─ fim ({elapsed:.4f}s)")