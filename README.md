## EPG Series Enhancer

Enhances XMLTV data so Plex DVR recognises series and displays consistent season/episode numbers.

### Features
- Adds a `series` category to `programme` entries that have no categories
- Fills missing `xmltv_ns` episode numbers using a strict precedence order
- Pretty-prints and writes a clean XML file

### How episode numbers are determined (precedence)
1. Keep existing non-empty `<episode-num system="xmltv_ns">…</episode-num>` as-is
2. Else, parse season/episode from `<desc>` when it matches common patterns:
   - `S5 Ep2`, `S05E02`, `Season 5 Episode 2`, `Series 5 Episode 2`, or leading `X/Y` (e.g., `27/30.` means season 27, episode 30)
   - Converted to zero-based `xmltv_ns` (e.g., `S5 Ep2` → `4.1.`)
3. Else, date-based fallback from `programme@start` date:
   - season = start year, episode = day-of-year
   - Stored zero-based in `xmltv_ns` (e.g., 2025‑09‑02 → `2024.244.`)
4. Else, set any remaining empty `xmltv_ns` to `0.0.0`

Notes:
- Plex displays S/E using 1-based numbers, but `xmltv_ns` is zero-based. `4.1.` means S5 E2 in Plex.
- Existing categories are never overwritten; `series` is only added if no categories exist.

### Requirements
- Python 3.8+
- macOS/Linux shell (or adjust commands for Windows)

### Repository layout
- `epg_add_series.py`: Core script. Downloads or reads XML, updates categories and episode numbers, writes output.
- `run_epg_update.sh`: Wrapper that reads the source URL from `.env` and runs the script.
- `.gitignore`: Excludes `*.xml` artifacts and `.env` from git.

### Configuration (.env)
Create `.env` in this directory with your XMLTV source URL:

```bash
EPG_SOURCE="https://www.open-epg.com/app/pdownload.php?file=ksy5SdW4jS.xml"
```

Override per-run without editing `.env`:

```bash
EPG_SOURCE="https://example.com/feed.xml" ./run_epg_update.sh
```

### Quick start
Generate `open-epg_series.xml` from the URL in `.env`:

```bash
./run_epg_update.sh
```

### Direct usage (without the wrapper)
- Download from URL and write to a custom path:
```bash
python3 epg_add_series.py --url "https://www.open-epg.com/app/pdownload.php?file=abc123456.xml" --output /path/to/open-epg_series.xml
```

- Process a local XMLTV file:
```bash
python3 epg_add_series.py --input /path/to/source.xml --output /path/to/open-epg_series.xml
```

### What Plex shows
- Title: from `<title>`
- Episode title (details): from `<sub-title>` if present
- Channel: from your Plex channel mapping
- Time: converted from `start`/`stop` (UTC) to local time
- Series detection: presence of `<category lang="en">series</category>`
- S/E mapping: from `xmltv_ns` (Plex converts zero-based to 1-based)

### Examples
- Description contains S/E:
  - `… S5 Ep2` ⇒ `xmltv_ns = 4.1.`
- Description starts with `X/Y` (series count pattern):
  - `27/30. …` ⇒ `xmltv_ns = 26.29.` (season 27, episode 30)
- No S/E in description, `start="20250902140000 +0000"`:
  - season = 2025, episode = day‑of‑year(2025‑09‑02)=245 ⇒ `xmltv_ns = 2024.244.`

### Cron example
Run daily at 03:30, logging to `/var/log/epg_update.log`:
```bash
30 3 * * * /Users/stevencoutts/Dev/EPG/run_epg_update.sh >/var/log/epg_update.log 2>&1
```

### Troubleshooting
- Download errors: set `EPG_SOURCE` correctly or use `--input` with a local file
- Parse errors: ensure the feed is valid XMLTV; share a sample snippet if issues persist
- Unexpected S/E in Plex: Plex can also use other episode tags or online metadata; `xmltv_ns` is the most deterministic

### Development
- Run locally with a sample XML using `--input`
- Keep changes small and readable; script is lint-clean

