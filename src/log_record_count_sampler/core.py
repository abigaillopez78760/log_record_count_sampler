"""Emit one log record per N occurrences of an identical message template.

The sampler keys on the raw message string. Messages that differ only in
variable data (timestamps, ids) must be normalised by the caller before being
handed to the sampler; doing the normalisation here would require guessing at
log formats and would make the output less predictable.
"""

from __future__ import annotations

from typing import Dict


class CountSampler:
    """Keep a running count per message and emit one record every ``every`` hits.

    The first time a message is seen the count is 1. A record is emitted when
    the count is an exact multiple of ``every``. This means the very first
    occurrence of a message is emitted only when ``every == 1``; with the
    default ``every == 2`` the first record arrives on the second occurrence.
    That ordering is deliberate: it keeps the hot path free of special cases
    and makes the emitted records line up with the multiples of ``every``.

    Args:
        every: Emit one record for every ``every`` occurrences. Must be a
            positive integer.

    Raises:
        ValueError: If ``every`` is not a positive integer.
    """

    __slots__ = ("_every", "_counts")

    def __init__(self, every: int = 2) -> None:
        if isinstance(every, bool) or not isinstance(every, int):
            raise ValueError("every must be an integer")
        if every < 1:
            raise ValueError("every must be at least 1")
        self._every = every
        self._counts: Dict[str, int] = {}

    @property
    def every(self) -> int:
        """The configured emission interval."""
        return self._every

    def count(self, message: str) -> int:
        """Return how many times ``message`` has been seen so far.

        This does not advance the counter; use :meth:`process` for that.
        """
        return self._counts.get(message, 0)

    def process(self, message: str) -> bool:
        """Record one occurrence of ``message`` and report whether to emit.

        Returns:
            ``True`` when the occurrence count for ``message`` is a multiple
            of ``every``, otherwise ``False``.
        """
        seen = self._counts.get(message, 0) + 1
        self._counts[message] = seen
        return seen % self._every == 0

    def reset(self) -> None:
        """Forget every counter. The configured interval is unchanged."""
        self._counts.clear()

    def counts(self) -> Dict[str, int]:
        """Return a copy of the current per-message counts.

        The copy protects the sampler's internal state from callers that would
        otherwise mutate it while iterating.
        """
        return dict(self._counts)
