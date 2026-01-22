#!/bin/bash

set -euo pipefail

NUXMV="$HOME/bin/nuXmv"
BENCH_DIR="../benchmarks"
SMV_DIR="$BENCH_DIR/smv"
AAG_DIR="$BENCH_DIR/aag"
LOG_DIR="$BENCH_DIR/logs"

JOBS=8
TIMEOUT=600   # seconds

mkdir -p "$AAG_DIR" "$LOG_DIR"

FAIL_LOG="$LOG_DIR/failed.log"
TIMEOUT_LOG="$LOG_DIR/timeout.log"

# Clear old logs
: > "$FAIL_LOG"
: > "$TIMEOUT_LOG"

process_one() {
  smv="$1"
  base=$(basename "$smv" .smv)
  out="$AAG_DIR/$base.aag"

  # Skip if already done
  if [ -f "$out" ]; then
    echo "[SKIP] $base.aag exists"
    return
  fi

  script=$(mktemp)

  cat > "$script" <<EOF
read_model -i $smv
go
build_boolean_model
write_aiger_model -f $AAG_DIR/$base
quit
EOF

  echo "[RUN ] $base"

  # Run nuXmv with timeout
  if timeout "$TIMEOUT" "$NUXMV" -source "$script" >"$LOG_DIR/$base.out" 2>"$LOG_DIR/$base.err"; then
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

  rm -f "$script"
}

export -f process_one
export NUXMV BENCH_DIR SMV_DIR AAG_DIR LOG_DIR TIMEOUT FAIL_LOG TIMEOUT_LOG

find "$SMV_DIR" -type f -name "*.smv" \
  | sort \
  | xargs -n 1 -P "$JOBS" -I {} bash -c 'process_one "$@"' _ {}
