## EPG Series Tagger

Adds a `series` category to `programme` entries that have no categories, infers season/episode from description when possible, and fills empty `xmltv_ns` episode numbers as `0.0.0`. This helps Plex DVR identify items as TV series when recording.

### Requirements
- Python 3.8+
- macOS/Linux shell (or adjust commands for Windows)

### Files
- `epg_add_series.py`: Core script. Downloads or reads XML, updates categories and episode numbers, writes output.
- `run_epg_update.sh`: Convenience wrapper that reads the source URL from `.env`.
- `.gitignore`: Excludes `*.xml` artifacts from git.

### Configuration (.env)
Create a `.env` file in this directory with the source EPG URL:

```bash
EPG_SOURCE="https://www.open-epg.com/app/pdownload.php?file=ksy5SdW4jS.xml"
```

### Quick start
Run with the URL from `.env` and write `open-epg_series.xml` in this directory:

```bash
./run_epg_update.sh
```

If `EPG_SOURCE` is not set, the script will exit with an error explaining how to configure `.env`.

### Direct usage
- Download from URL and write to a custom path:
```bash
python3 epg_add_series.py --url "https://www.open-epg.com/app/pdownload.php?file=abc123456.xml" --output /path/to/open-epg_series.xml
```

- Process a local XMLTV file:
```bash
python3 epg_add_series.py --input /path/to/source.xml --output /path/to/open-epg_series.xml
```

### What it does
- Ensures `programme` entries with no categories receive:
  - `<category lang="en">series</category>`
- Honours any existing categories and never overwrites them
- Ensures empty `xmltv_ns` episode numbers are set to:
  - `<episode-num system="xmltv_ns">0.0.0</episode-num>`
- Leaves existing non-empty `xmltv_ns` values unchanged
 - If description contains a recognizable pattern like `S5 Ep2`, `S05E02`, or `Season 5 Episode 2`, it writes an `xmltv_ns` value (zero-based, e.g., `S5 Ep2` → `4.1.`) when the `xmltv_ns` entry is missing or empty
 - If no season/episode can be inferred, a date-based fallback sets `xmltv_ns` using programme start date as: season = start year, episode = day-of-year (both zero-based in xmltv_ns, e.g., 2025-09-02 → `2024.244.`)

### Cron example
Run daily at 03:30, logging to `/var/log/epg_update.log`:
```bash
30 3 * * * /Users/stevencoutts/Dev/EPG/run_epg_update.sh >/var/log/epg_update.log 2>&1
```

### Notes
- XML files are ignored by git via `.gitignore`.
- A DOCTYPE (if present) is stripped before parsing to avoid external subset issues.
- Output defaults to `open-epg_series.xml` in the working directory if `--output` is not specified.

### Troubleshooting
- Network errors: check connectivity or try `--input` with a local file.
- Parse errors: ensure the input is valid XMLTV. If issues persist, share a sample snippet.


