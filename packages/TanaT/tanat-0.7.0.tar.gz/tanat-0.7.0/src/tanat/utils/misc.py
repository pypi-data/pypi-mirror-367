#!/usr/bin/env python3
"""
Miscellaneous utility functions.
"""


def chunks_from_generator(generator, chunk_size):
    """Create chunks from a generator without loading everything into memory."""
    iterator = iter(generator)
    while True:
        chunk = []
        try:
            for _ in range(chunk_size):
                chunk.append(next(iterator))
            yield tuple(chunk)
        except StopIteration:
            if chunk:
                yield tuple(chunk)
            break
