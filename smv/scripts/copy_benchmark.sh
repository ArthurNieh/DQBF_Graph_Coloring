#!/bin/bash
# Copy all .smv files from benchmark1 directory to benchmark directory

origin_dir="../../../nuXmv-2.1.0-linux64/examples/"
target_dir="../benchmarks/smv/"

mkdir -p "$target_dir"
find "$origin_dir" -type f -path "*/QF_BV/*.smv" | while read f; do
  newname=$(echo "$f" | sed 's|/|_|g')
  cp "$f" "$target_dir/$newname"
done
