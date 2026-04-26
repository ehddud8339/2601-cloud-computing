#!/usr/bin/env python3
"""Verify that anonymous access to private-bucket is denied."""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ENDPOINT_URL = "http://127.0.0.1:9101"
PRIVATE_BUCKET = "private-bucket"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Attempt anonymous read access to private-bucket and print the denial response."
    )
    parser.add_argument(
        "image",
        type=Path,
        help="Local file path used only for the object name lookup in private-bucket.",
    )
    return parser.parse_args()


def build_object_url(image: Path) -> str:
    object_name = urllib.parse.quote(image.name)
    return f"{ENDPOINT_URL}/{PRIVATE_BUCKET}/{object_name}"


def main() -> int:
    args = parse_args()
    url = build_object_url(args.image)

    print(f"[INFO] anonymous GET {url}")

    try:
        with urllib.request.urlopen(url) as response:
            body = response.read().decode("utf-8", errors="replace")
            print(f"[ERROR] anonymous access unexpectedly succeeded: HTTP {response.status}")
            print(body)
            return 1
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"[INFO] HTTP status: {exc.code}")
        print(body)
        if exc.code == 403 and "AccessDenied" in body:
            print("[OK] anonymous access to private-bucket was denied as expected")
            return 0
        print("[ERROR] anonymous access failed, but not with the expected AccessDenied response")
        return 1
    except urllib.error.URLError as exc:
        print(f"[ERROR] request failed: {exc.reason}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
