#!/bin/sh
#Usage: dedrm.sh <kindle_serial> <file> <outdir>

SCRIPT="/root/drm/DeDRM_Windows_Application/DeDRM_App/DeDRM_lib/lib/k4mobidedrm.py"

if [ "$3" = "" ]; then
    echo "Usage: dedrm.sh <kindle_serial> <file> <outdir>"
    exit 1
fi

python "$SCRIPT" -s "$1" "$2" "$3"
