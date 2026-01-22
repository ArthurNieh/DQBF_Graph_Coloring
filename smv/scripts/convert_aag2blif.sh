#!/bin/bash

set -euo pipefail

AIGTOBLIF="$HOME/bin/aigtoblif"
BENCH_DIR="../benchmarks"
AAG_DIR="$BENCH_DIR/aag"
BLIF_DIR="$BENCH_DIR/blif"
LOG_DIR="$BENCH_DIR/logs"

JOBS=4
TIMEOUT=60   # seconds

mkdir -p "$BLIF_DIR" "$LOG_DIR"

FAIL_LOG="$LOG_DIR/aag2blif_failed.log"
TIMEOUT_LOG="$LOG_DIR/aag2blif_timeout.log"

# Clear old logs
: > "$FAIL_LOG"
: > "$TIMEOUT_LOG"

process_one() {
  aag="$1"
  base=$(basename "$aag" .aag)
  out="$BLIF_DIR/$base.blif"

  # Skip if already done
  if [ -f "$out" ]; then
    echo "[SKIP] $base.blif exists"
    return
  fi

  echo "[RUN ] $base.aag"

  if timeout "$TIMEOUT" "$AIGTOBLIF" -s "$aag" "$out" \
       >"$LOG_DIR/$base.aag2blif.out" \
       2>"$LOG_DIR/$base.aag2blif.err"; then
    echo "[OK  ] $base"
  else
    status=$?
    if [ "$status" -eq 124 ]; then
      echo "[TIME] $base"
      echo "$base" >> "$TIMEOUT_LOG"
    else
      echo "[FAIL] $base (exit=$status)"
      echo "$base" >> "$FAIL_LOG"
    fi
  fi
}

export -f process_one
export AIGTOBLIF BENCH_DIR AAG_DIR BLIF_DIR LOG_DIR TIMEOUT FAIL_LOG TIMEOUT_LOG

find "$AAG_DIR" -type f -name "*.aag" \
  | sort \
  | xargs -n 1 -P "$JOBS" -I {} bash -c 'process_one "$@"' _ {}
