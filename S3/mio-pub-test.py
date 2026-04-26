#!/usr/bin/env python3
"""Read from private-bucket and read/write public-bucket as pub-user."""

from __future__ import annotations

import argparse
import mimetypes
import sys
import webbrowser
from pathlib import Path

DEFAULT_ACCESS_KEY = "pub-user"
DEFAULT_SECRET_KEY = "pub-pass123"
ENDPOINT_URL = "http://127.0.0.1:9101"
REGION = "us-east-1"
PRIVATE_BUCKET = "private-bucket"
PUBLIC_BUCKET = "public-bucket"


def build_client(access_key: str, secret_key: str):
    import boto3
    from botocore.client import Config

    return boto3.client(
        "s3",
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=REGION,
        config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
    )


def ensure_file(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"image file not found: {resolved}")
    return resolved


def validate_credentials(client, access_key: str, bucket: str) -> None:
    from botocore.exceptions import ClientError

    try:
        client.head_bucket(Bucket=bucket)
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        raise RuntimeError(
            f"credential check failed for '{access_key}' on bucket '{bucket}': {code}. "
            "Check access key, secret key, bucket policy, and endpoint."
        ) from exc


def upload_image(client, path: Path, bucket: str, key: str) -> None:
    content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    client.upload_file(
        str(path),
        bucket,
        key,
        ExtraArgs={"ContentType": content_type},
    )


def presigned_get_url(client, bucket: str, key: str) -> str:
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=300,
    )


def open_image(client, bucket: str, key: str, label: str) -> None:
    url = presigned_get_url(client, bucket, key)
    print(f"[OPEN] {label}: {url}")
    webbrowser.open(url)


def expect_access_denied(action, label: str) -> None:
    from botocore.exceptions import ClientError

    try:
        action()
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        if code in {"AccessDenied", "AllAccessDisabled"}:
            print(f"[DENIED] {label}: {code}")
            return
        raise
    raise RuntimeError(f"{label}: expected AccessDenied, but request succeeded")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload/read public images and read, but not write, private images with pub-user credentials."
    )
    parser.add_argument(
        "pub_image",
        type=Path,
        help="Local image file to upload to public-bucket.",
    )
    parser.add_argument(
        "priv_image",
        type=Path,
        help="Local image file name expected in private-bucket. The basename is used as the object key.",
    )
    parser.add_argument(
        "--access-key",
        default=DEFAULT_ACCESS_KEY,
        help="S3 access key for public-bucket access and private-bucket read access.",
    )
    parser.add_argument(
        "--secret-key",
        default=DEFAULT_SECRET_KEY,
        help="S3 secret key for public-bucket access and private-bucket read access.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        pub_image = ensure_file(args.pub_image)
        priv_image = ensure_file(args.priv_image)
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    client = build_client(args.access_key, args.secret_key)
    print(
        f"[INFO] public bucket={PUBLIC_BUCKET}, private bucket={PRIVATE_BUCKET}, "
        f"access_key={args.access_key}"
    )
    validate_credentials(client, args.access_key, PUBLIC_BUCKET)

    public_key = pub_image.name
    private_key = priv_image.name
    denied_key = f"pub-write-attempt/{pub_image.name}"

    upload_image(client, pub_image, PUBLIC_BUCKET, public_key)
    print(f"[OK] uploaded s3://{PUBLIC_BUCKET}/{public_key}")
    open_image(client, PUBLIC_BUCKET, public_key, "public image")

    open_image(client, PRIVATE_BUCKET, private_key, "private image read by pub-user")

    expect_access_denied(
        lambda: upload_image(client, pub_image, PRIVATE_BUCKET, denied_key),
        f"upload to s3://{PRIVATE_BUCKET}/{denied_key}",
    )
    print("[OK] private-bucket upload attempt failed as expected")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
