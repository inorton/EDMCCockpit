"""Useful things"""
from typing import Any, Optional
from queue import Queue


def pragma_silence(obj: Any):
    pass


class BufferQueue(Queue):
    """Queue that can't grow bigger than maxsize, the oldest items are discarded"""

    def put(self, item: Any, block: bool = True, timeout: Optional[float] = None) -> None:
        while self.qsize() >= self.maxsize:
            # discard the oldest item
            self.get()
        super(BufferQueue, self).put(item, block=block, timeout=timeout)
