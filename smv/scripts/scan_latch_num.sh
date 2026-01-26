#!/bin/bash
# Scan through all .blif files and count inputs and latches

count_inputs() {
    awk '
    BEGIN { count=0; in_inputs=0 }
    /^\.inputs/ {
        in_inputs=1
        sub(/^\.inputs[ \t]*/, "")
    }
    in_inputs {
        line=$0
        cont = (line ~ /\\$/)
        gsub(/\\/, "", line)
        n = split(line, a, /[ \t]+/)
        for (i=1; i<=n; i++)
            if (a[i] != "") count++
        if (!cont) in_inputs=0
    }
    END { print count }
    ' "$1"
}

for f in ../benchmarks/blif/*.blif; do
    latch_cnt=$(grep -c '^\.latch' "$f")
    input_cnt=$(count_inputs "$f")
    printf "%s: inputs=%d latches=%d\n" "$f" "$input_cnt" "$latch_cnt"
done
