#!/usr/bin/env python3
"""Publish one line about the meeting that should have been an email.

The entry is a single joke: twelve people sat in a room for an hour to
look at one slide, and the slide was a screenshot of the email. The
meeting literally was the email, projected. The turn lands on the last
word, every word earns its place, and anyone who has sat through a
screenshot-as-slide meeting recognises it at once.

This program builds the line from one function, checks it against the
gate in the kit's RULES.txt (UTF-8, 1 to 200 characters, not only
whitespace, a single line, no trailing whitespace, no control
characters), writes it byte-for-byte to the first writable destination,
re-reads the published file as UTF-8 and refuses with a clear error if
it differs by even one byte, and prints the line to stdout.

Deterministic: no network, no randomness, no time dependence, no
arguments, no environment dependence beyond the write destination.
Python standard library only.
"""

import os
import sys

# The entry line. The em dash is U+2014; the line is 81 characters.
ENTRY = (
    "Twelve people, one hour, one slide \u2014 and the slide was a "
    "screenshot of the email."
)

MAX_CHARS = 200
DESTINATIONS = ("/output/entry.txt", "output/entry.txt")


def entry_line():
    """Return the entry line."""
    return ENTRY


def problems_with(line):
    """Return a list of gate violations for the line, empty when valid."""
    found = []
    if not 1 <= len(line) <= MAX_CHARS:
        found.append("length %d, must be 1 to %d characters" % (len(line), MAX_CHARS))
    if not line.strip():
        found.append("must not be only whitespace")
    if "\n" in line or "\r" in line:
        found.append("must be a single line")
    if line != line.rstrip():
        found.append("must not end with trailing whitespace")
    if any(ord(ch) < 0x20 for ch in line):
        found.append("must not contain control characters")
    return found


def write_entry(path, line):
    """Write the line as UTF-8 bytes to path, creating parents as needed."""
    payload = line.encode("utf-8")
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(payload)
    return payload


def verify_written(path, expected_bytes):
    """Re-read path as UTF-8 and refuse unless it matches byte-for-byte.

    A mismatch means the gate would fail on the published file, so fail
    loudly here instead of silently leaving a bad entry behind.
    """
    with open(path, "rb") as handle:
        actual = handle.read()
    if actual != expected_bytes:
        raise SystemExit(
            "error: gate would fail: published bytes at %s differ from "
            "the entry line (%d bytes written, %d expected)"
            % (path, len(actual), len(expected_bytes))
        )
    decoded = actual.decode("utf-8")
    if decoded != entry_line():
        raise SystemExit(
            "error: gate would fail: published text at %s differs from "
            "the entry line" % path
        )
    return True


def publish(line):
    """Write the line to the first writable destination; return its path."""
    for path in DESTINATIONS:
        try:
            payload = write_entry(path, line)
            verify_written(path, payload)
        except OSError as exc:
            print("warning: cannot write %s: %s" % (path, exc), file=sys.stderr)
            continue
        return path
    raise SystemExit("error: no writable destination among %s" % (DESTINATIONS,))


def main():
    """Validate, publish, and echo the entry line. Return an exit code."""
    line = entry_line()
    bad = problems_with(line)
    if bad:
        print("error: entry is invalid: %s" % "; ".join(bad), file=sys.stderr)
        return 1
    where = publish(line)
    print(line)
    print("wrote %d characters to %s" % (len(line), where), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
