#!/bin/bash

shopt -s nullglob
shopt -s dotglob

prefix=".._.._.._nuXmv-2.1.0-linux64_examples_"

cd ../benchmarks/smv || exit 1
# mkdir -p smv

for f in *"$prefix"*.smv; do
  newname="${f#$prefix}"
  mv "$f" "$newname"
done
