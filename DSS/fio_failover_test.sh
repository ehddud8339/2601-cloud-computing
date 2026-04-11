#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

TARGET_NODE="${1:-node1}"
MOUNT_POINT="${MOUNT_POINT:-/mnt/gv0/test}"
RUNTIME="${RUNTIME:-60}"
FAIL_AT="${FAIL_AT:-15}"
FILE_SIZE="${FILE_SIZE:-1G}"
JOB_NAME="${JOB_NAME:-gluster-failover}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
TEST_DIR="$MOUNT_POINT/fio-failover-$TIMESTAMP"
FIO_FILE="$TEST_DIR/testfile"
LOG_DIR="$SCRIPT_DIR/logs"
FIO_OUTPUT="$LOG_DIR/fio-$TARGET_NODE-$TIMESTAMP.json"

mkdir -p "$LOG_DIR"

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "missing required command: $1" >&2
    exit 1
  fi
}

cleanup() {
  set +e
  if mountpoint -q "$MOUNT_POINT"; then
    rm -rf "$TEST_DIR"
  fi
}

trap cleanup EXIT

require_cmd fio
require_cmd vagrant
require_cmd timeout

if [ "$FAIL_AT" -ge "$RUNTIME" ]; then
  echo "FAIL_AT must be smaller than RUNTIME" >&2
  exit 1
fi

mkdir -p "$TEST_DIR"

echo "starting fio failover test"
echo "  target node : $TARGET_NODE"
echo "  mount point : $MOUNT_POINT"
echo "  runtime     : ${RUNTIME}s"
echo "  fail at     : ${FAIL_AT}s"
echo "  fio output  : $FIO_OUTPUT"

timeout --foreground "$((RUNTIME + 90))" \
  fio \
  --name="$JOB_NAME" \
  --filename="$FIO_FILE" \
  --rw=randrw \
  --rwmixread=50 \
  --bs=4k \
  --size="$FILE_SIZE" \
  --ioengine=libaio \
  --iodepth=16 \
  --direct=1 \
  --numjobs=1 \
  --time_based=1 \
  --runtime="$RUNTIME" \
  --group_reporting=1 \
  --status-interval=1 \
  --output-format=json \
  --output="$FIO_OUTPUT" &
FIO_PID=$!

sleep "$FAIL_AT"

echo "stopping $TARGET_NODE at $(date '+%F %T')"
vagrant halt "$TARGET_NODE" --force

FIO_STATUS=0
if ! wait "$FIO_PID"; then
  FIO_STATUS=$?
fi

echo "fio exit status: $FIO_STATUS"

if [ "$FIO_STATUS" -eq 0 ]; then
  echo "result: PASS"
  echo "fio completed despite shutting down $TARGET_NODE"
  exit 0
fi

if [ "$FIO_STATUS" -eq 124 ]; then
  echo "result: FAIL"
  echo "fio exceeded timeout and likely hung after node failure" >&2
  exit 1
fi

echo "result: FAIL"
echo "fio exited with an error after node failure" >&2
exit 1
