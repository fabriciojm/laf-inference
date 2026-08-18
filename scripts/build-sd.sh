#!/usr/bin/env bash
set -euo pipefail

PREFIX=${1:-/usr/local/bin}

mkdir -p "$PREFIX"

git clone --recursive \
  https://github.com/leejet/stable-diffusion.cpp \
  /tmp/stable-diffusion.cpp

cmake -B /tmp/stable-diffusion.cpp/build \
  -G Ninja \
  -S /tmp/stable-diffusion.cpp \
  -DCMAKE_BUILD_TYPE=Release \
  -DGGML_OPENBLAS=ON

cmake --build /tmp/stable-diffusion.cpp/build

mkdir -p "$PREFIX/"

cp \
  /tmp/stable-diffusion.cpp/build/bin/sd-cli \
  "$PREFIX/"
