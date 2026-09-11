#!/usr/bin/env python3
"""
mealie_text_to_json.py

Converts plain-text meal plan blocks into JSON entries usable for Mealie import.

Input format expected:
    Breakfast:
    Cereal and fresh
    berries
    -----------------
    Lunch:
    Tomato chickpea
    basil soup with
    cheese bread,
    steamed carrots on
    the side,
    pineapple
    ----------

Rules:
    - A header line (Breakfast:, Lunch:, Dinner:, Snack:) starts a new entry.
    - A "Vegetarian option:" line does NOT start a new entry. It attaches to
      the meal entry right before it: that entry gets a "vegetarian" tag and
      a "vegetarian_alternative" field holding the alt ingredients.
    - Lines of 3+ dashes end the current entry.
    - Wrapped lines with no comma are joined with a space (same item).
    - A comma marks a boundary between separate ingredients.
    - name and description are both set to the first two ingredients
      joined with ", " (no separate title/desc exists in the source text).

Usage:
    python mealie_text_to_json.py input.txt -o output.json
    python mealie_text_to_json.py input.txt        # prints to stdout
"""

import argparse
import json
import re
import sys

MEAL_HEADER_RE = re.compile(r"^(breakfast|lunch|dinner|snack)\s*:\s*$", re.IGNORECASE)
VEG_HEADER_RE = re.compile(r"^vegetarian option\s*:\s*$", re.IGNORECASE)
SEPARATOR_RE = re.compile(r"^-{3,}$")


def lines_to_ingredients(lines):
    joined = " ".join(lines)
    return [item.strip() for item in joined.split(",") if item.strip()]


def flush_meal_entry(entry_type, lines):
    """Turn collected lines into one meal entry dict, or None if empty."""
    if not entry_type or not lines:
        return None

    ingredients = lines_to_ingredients(lines)
    if not ingredients:
        return None

    name_desc = ", ".join(ingredients[:2])

    return {
        "type": entry_type.lower(),
        "name": name_desc,
        "description": name_desc,
        "ingredients": ingredients,
        "tags": [],
    }


def parse_text(text):
    entries = []
    current_type = None      # meal type currently being collected, or "vegetarian" marker
    current_lines = []
    last_entry = None        # most recently flushed meal entry, for attaching veg options

    def flush_pending():
        nonlocal current_type, current_lines, last_entry
        if current_type == "vegetarian":
            veg_ingredients = lines_to_ingredients(current_lines)
            if veg_ingredients and last_entry is not None:
                if "vegetarian" not in last_entry["tags"]:
                    last_entry["tags"].append("vegetarian")
                last_entry["vegetarian_alternative"] = veg_ingredients
        else:
            entry = flush_meal_entry(current_type, current_lines)
            if entry:
                entries.append(entry)
                last_entry = entry
        current_type = None
        current_lines = []

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        if SEPARATOR_RE.match(line):
            flush_pending()
            continue

        if MEAL_HEADER_RE.match(line):
            flush_pending()
            current_type = MEAL_HEADER_RE.match(line).group(1)
            continue

        if VEG_HEADER_RE.match(line):
            flush_pending()
            current_type = "vegetarian"
            continue

        current_lines.append(line)

    flush_pending()

    return entries


def main():
    parser = argparse.ArgumentParser(description="Convert meal plan text to JSON.")
    parser.add_argument("input", help="Path to the input text file")
    parser.add_argument("-o", "--output", help="Path to write JSON output (default: stdout)")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        text = f.read()

    entries = parse_text(text)
    output = json.dumps(entries, indent=2, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Wrote {len(entries)} entries to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()