## EPG Series Tagger

Adds a `series` category to every `programme` in an XMLTV file and fills empty `xmltv_ns` episode numbers as `0.0.0`. This helps Plex DVR identify items as TV series when recording.

### Requirements
- Python 3.8+
- macOS/Linux shell (or adjust commands for Windows)

### Files
- `epg_add_series.py`: Core script. Downloads or reads XML, updates categories and episode numbers, writes output.
- `run_epg_update.sh`: Convenience wrapper to run the script with the default Open-EPG URL.
- `.gitignore`: Excludes `*.xml` artifacts from git.

### Quick start
Run with the default Open-EPG URL and write `open-epg_series.xml` in this directory:

```bash
./run_epg_update.sh
```

### Direct usage
- Download from URL and write to a custom path:
```bash
python3 epg_add_series.py --url "https://www.open-epg.com/app/pdownload.php?file=ksy5SdW4jS.xml" --output /path/to/open-epg_series.xml
```

- Process a local XMLTV file:
```bash
python3 epg_add_series.py --input /path/to/source.xml --output /path/to/open-epg_series.xml
```

### What it does
- Ensures every `programme` includes:
  - `<category lang="en">series</category>` if missing
- Ensures empty `xmltv_ns` episode numbers are set to:
  - `<episode-num system="xmltv_ns">0.0.0</episode-num>`
- Leaves existing non-empty `xmltv_ns` values unchanged

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


