#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f "$SCRIPT_DIR/.env" ]; then
	set -a
	. "$SCRIPT_DIR/.env"
	set +a
fi

URL="${EPG_SOURCE:-}"
OUTPUT="open-epg_series.xml"

exec python3 "$SCRIPT_DIR/epg_add_series.py" --url "$URL" --output "$OUTPUT"


