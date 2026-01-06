#!/bin/bash

OUTDIR="fraig"
LOGDIR="logs"

mkdir -p "$OUTDIR" "$LOGDIR"

for f in *.blif; do
    base=$(basename "$f" .blif)
    out="$OUTDIR/${base}_fraig.blif"
    log="$LOGDIR/${base}.log"

    echo "Fraiging $f → $out"

    ../../abc/abc -c "
        read $f;
        strash;
        fraig;
        print_stats;
        write_blif $out
    " > "$log"
done
