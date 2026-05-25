#!/bin/sh
set -eu

COMMIT=6019056
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
TARGET="$ROOT/third_party/lattice-estimator"

if [ ! -d "$TARGET/.git" ]; then
    mkdir -p "$ROOT/third_party"
    git clone https://github.com/malb/lattice-estimator.git "$TARGET"
fi

git -C "$TARGET" fetch --quiet origin
git -C "$TARGET" checkout "$COMMIT"
echo "lattice-estimator ready at $TARGET ($(git -C "$TARGET" rev-parse --short HEAD))"
