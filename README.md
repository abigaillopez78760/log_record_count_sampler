# log_record_count_sampler

Emit one record for every N occurrences of an identical message template, discarding the rest while keeping a running count.

```python
from log_record_count_sampler import CountSampler

sampler = CountSampler(every=3)

for message in [
    "disk full",
    "disk full",
    "disk full",
    "disk full",
    "disk full",
]:
    if sampler.process(message):
        print(f"{message} (seen {sampler.count(message)} times)")

# prints:
# disk full (seen 3 times)
```

## Why this exists

Log pipelines drown in repeated lines. A single failing dependency can produce
thousands of identical records per second, and shipping every one of them costs
bandwidth and buries the signal. Sampling by count is the cheapest filter: keep
a counter per message and forward only every Nth hit. The trade-off is that the
sampler is stateful and keyed on the exact message string, so messages that
differ only in timestamps or request ids are counted separately. Normalise the
template before calling `process` if that matters to you; guessing a
normalisation scheme inside the library would make the output unpredictable.

## Awkward edge

The first occurrence of a message is emitted only when `every == 1`. With the
default `every == 2` the first record arrives on the second occurrence, because
emission happens when the running count is an exact multiple of `every`. If you
need the first line immediately, construct the sampler with `every=1` and do
your own rate limiting downstream.

## API

- `CountSampler(every=2)` — `every` must be a positive integer, otherwise
  `ValueError` is raised. `bool` is explicitly rejected even though it is an
  `int` subclass.
- `sampler.process(message) -> bool` — record one occurrence and return `True`
  when a record should be emitted.
- `sampler.count(message) -> int` — occurrences seen so far; does not advance
  the counter.
- `sampler.counts() -> dict[str, int]` — a copy of all counters.
- `sampler.reset() -> None` — clear all counters; the interval is unchanged.
- `sampler.every` — the configured interval.
