#!/usr/bin/env python3
"""Publish one line about the meeting that should have been an email.

The entry is a single joke: twelve people sat in a room for an hour to
look at one slide, and the slide was a screenshot of the email. The
meeting literally was the email, projected. The turn lands on the last
word, every word earns its place, and anyone who has sat through a
screenshot-as-slide meeting recognises it at once.

This program holds that line as a constant, checks it against the gate
in the kit's RULES.txt (UTF-8, 1 to 200 characters, not only whitespace,
a single line, no trailing whitespace, no control characters), writes it
byte-for-byte to /output/entry.txt (falling back to ./output-entry.txt
when /output is not writable), re-reads the published file and refuses
if it differs, and prints the line to stdout.

Deterministic: no network, no randomness, no time dependence, no
arguments. Python standard library only.
"""

import os
import sys

LINE = (
    "Twelve people, one hour, one slide \u2014 and the slide was a "
    "screenshot of the email."
)

MAX_CHARS = 200
DESTINATIONS = ("/output/entry.txt", "output-entry.txt")


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


def publish(line):
    """Write the line to the first writable destination; return its path."""
    payload = line.encode("utf-8")
    for path in DESTINATIONS:
        try:
            parent = os.path.dirname(path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(path, "wb") as handle:
                handle.write(payload)
        except OSError:
            continue
        with open(path, "rb") as handle:
            if handle.read() != payload:
                print("error: published bytes differ at %s" % path, file=sys.stderr)
                raise SystemExit(1)
        return path
    print("error: no writable destination among %s" % (DESTINATIONS,), file=sys.stderr)
    raise SystemExit(1)


def main():
    bad = problems_with(LINE)
    if bad:
        print("error: entry is invalid: %s" % "; ".join(bad), file=sys.stderr)
        raise SystemExit(1)
    where = publish(LINE)
    print(LINE)
    print("wrote %d characters to %s" % (len(LINE), where), file=sys.stderr)


if __name__ == "__main__":
    main()
