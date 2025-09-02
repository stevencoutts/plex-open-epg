#!/usr/bin/env python3
import argparse
import sys
import re
import urllib.request
from pathlib import Path
from typing import Optional
import xml.etree.ElementTree as ET


def download_url(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "EPGSeriesAdder/1.0 (+https://open-epg.com)",
        },
    )
    with urllib.request.urlopen(request) as response:
        return response.read()


def read_input_source(url: Optional[str], input_path: Optional[Path]) -> bytes:
    if input_path is not None:
        return input_path.read_bytes()
    if url is None:
        raise ValueError("Either --url or --input must be provided")
    return download_url(url)


def strip_doctype(xml_bytes: bytes) -> bytes:
    # Many XMLTV feeds include a DOCTYPE; ElementTree may choke on external subsets.
    # Remove any DOCTYPE declaration defensively before parsing.
    text = xml_bytes.decode("utf-8", errors="replace")
    text = re.sub(r"<!DOCTYPE[^>]*>", "", text, flags=re.IGNORECASE)
    return text.encode("utf-8")


def tag_with_namespace(root_tag: str, local_name: str) -> str:
    if root_tag.startswith("{"):
        namespace = root_tag.split("}")[0][1:]
        return f"{{{namespace}}}{local_name}"
    return local_name


def ensure_series_category(tree: ET.ElementTree) -> int:
    root = tree.getroot()
    programme_tag = tag_with_namespace(root.tag, "programme")
    category_tag = tag_with_namespace(root.tag, "category")

    added_count = 0
    for programme in root.findall(f".//{programme_tag}"):
        categories = programme.findall(category_tag)
        # Only add 'series' if there are no existing category tags
        if len(categories) == 0:
            new_cat = ET.Element(category_tag)
            new_cat.set("lang", "en")
            new_cat.text = "series"
            programme.append(new_cat)
            added_count += 1
    return added_count


def ensure_xmltv_ns_episode_nums(tree: ET.ElementTree) -> int:
    root = tree.getroot()
    episode_num_tag = tag_with_namespace(root.tag, "episode-num")

    updated_count = 0
    for ep in root.findall(f".//{episode_num_tag}"):
        if (ep.get("system") or "").strip().lower() == "xmltv_ns":
            current_text = (ep.text or "").strip()
            if current_text == "":
                ep.text = "0.0.0"
                updated_count += 1
    return updated_count


def main() -> int:
    parser = argparse.ArgumentParser(description="Download/modify XMLTV to ensure category 'series' on each programme")
    parser.add_argument("--url", help="Source URL to download XMLTV")
    parser.add_argument("--input", type=Path, help="Local XMLTV input file instead of URL")
    parser.add_argument("--output", type=Path, default=Path("open-epg_series.xml"), help="Output XML file path")
    args = parser.parse_args()

    try:
        raw_bytes = read_input_source(args.url, args.input)
    except Exception as ex:
        print(f"Failed to read input: {ex}", file=sys.stderr)
        return 1

    try:
        cleaned = strip_doctype(raw_bytes)
        parser = ET.XMLParser()
        root = ET.fromstring(cleaned, parser=parser)
        tree = ET.ElementTree(root)
    except Exception as ex:
        print(f"Failed to parse XML: {ex}", file=sys.stderr)
        return 1

    added_series = ensure_series_category(tree)
    updated_eps = ensure_xmltv_ns_episode_nums(tree)

    try:
        # Pretty-print for readability (Python 3.9+)
        try:
            ET.indent(tree, space="  ")  # type: ignore[attr-defined]
        except Exception:
            pass
        args.output.parent.mkdir(parents=True, exist_ok=True)
        tree.write(args.output, encoding="utf-8", xml_declaration=True)
    except Exception as ex:
        print(f"Failed to write output: {ex}", file=sys.stderr)
        return 1

    print(
        f"Wrote {args.output} (added 'series' to {added_series} programme(s); "
        f"set xmltv_ns episode-num to 0.0.0 on {updated_eps} element(s))"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())


