#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR"

URL="https://www.open-epg.com/app/pdownload.php?file=ksy5SdW4jS.xml"
OUTPUT="open-epg_series.xml"

exec python3 "$SCRIPT_DIR/epg_add_series.py" --url "$URL" --output "$OUTPUT"


