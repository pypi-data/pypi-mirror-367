import dataclasses
import logging
from time import perf_counter
import traceback

import sqlalchemy as sa

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class LongTransactionDetector:
    timeout: float
    capture_stack_on_begin: bool = dataclasses.field(default=False)
    info_key: str = dataclasses.field(default="sqlalchemy_boltons.slow")

    def register(self, engine):
        sa.event.listen(engine, "begin", self.on_begin)
        sa.event.listen(engine, "rollback", self.on_end)
        sa.event.listen(engine, "commit", self.on_end)

    @staticmethod
    def _now():
        return perf_counter()

    def capture_stack(self):
        return traceback.extract_stack()

    def format_stack(self, stack_info):
        return traceback.format_list(stack_info)

    def on_begin(self, conn: sa.Connection):
        d = {"t": self._now()}
        if self.capture_stack_on_begin:
            d["stack_info"] = self.capture_stack()
        conn.info[self.info_key] = d

    def on_end(self, conn: sa.Connection):
        if not (d := conn.info.pop(self.info_key, None)):
            return

        elapsed = self._now() - d["t"]
        if elapsed <= self.timeout:
            return

        message = [f"slow transaction ({elapsed:.3f}s) at:\n\n"]
        if not (stack_info := d.get("stack_info")):
            stack_info = self.capture_stack()
        message += self.format_stack(stack_info)

        logger.warning("".join(message))
