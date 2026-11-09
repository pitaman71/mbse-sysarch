#!/bin/sh
# Copies the canonical skill into the implementation's package, so agents in projects that install mbse-sysarch find
# it next to the code. SKL-01 checks that the copy is current.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
for target in "$here/../python3/mbse/Architecture/Systems/skill"; do
  rm -rf "$target"
  mkdir -p "$target"
  cp -R "$here/mbse-sysarch/." "$target/"
done
