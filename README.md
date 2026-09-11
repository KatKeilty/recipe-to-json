# Mealie Text-to-JSON Converter

## Script
`mealie_text_to_json.py`

## Usage
```
python mealie_text_to_json.py input.txt -o output.json
python mealie_text_to_json.py input.txt          # prints to stdout instead
```

## Parsing rules
- A header line (`Breakfast:`, `Lunch:`, `Dinner:`, `Snack:`, `Vegetarian option:`) starts a new entry.
- A line of three or more dashes ends the current entry.
- Wrapped lines with no comma are joined with a space (same ingredient, split across lines by word wrap).
- A comma marks the boundary between two separate ingredients.
- `name` and `description` are both set to the first two ingredients joined with `, `, since the source text has no separate title or description field.

## Known limitation
`Vegetarian option:` blocks parse as their own entry with `type: vegetarian_option`, not linked back to the lunch entry above them. If you want it tied to the parent meal (e.g. as an alt/variant field on the lunch entry), the parser needs a small change to track "last real meal type" and attach rather than treat it as standalone.

## Next up
Bulk import tooling, to be scoped separately.