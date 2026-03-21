"""
Parse raw lyrics text into deduplicated sections and chunk into slide-sized pieces.

Supports section headers like:
    Verse 1, V1, [Verse 1], Chorus, Pre-Chorus, Bridge, Outro, Tag, Interlude, etc.
"""

import re
from typing import List

# Matches section headers: "Verse 1", "V1", "[Chorus]", "Pre-Chorus", "(Bridge)", etc.
_SECTION_RE = re.compile(
    r"^\s*"
    r"[\[\(]?\s*"  # optional opening bracket/paren
    r"(verse|v|chorus|pre[- ]?chorus|post[- ]?chorus|bridge|outro|tag|intro|interlude|ending|vamp|hook)"
    r"(?:\s*\d+)?"  # optional number
    r"\s*[\]\)]?"   # optional closing bracket/paren
    r"\s*:?\s*$",   # optional colon, end of line
    re.IGNORECASE,
)


def _normalize_label(raw_label: str) -> str:
    """Normalize a section label for comparison.

    'Verse 1', 'V1', and '[Verse 1]' all become 'verse 1', etc.
    Pre-Chorus / Post-Chorus normalize to 'chorus' so they merge with Chorus.
    """
    label = raw_label.strip().strip("[]():").strip().lower()
    # Expand shorthand: V1 -> verse 1, V2 -> verse 2
    label = re.sub(r"^v(\d+)$", r"verse \1", label)
    # Collapse pre-chorus / post-chorus into chorus
    label = re.sub(r"^(pre|post)[- ]?chorus", "chorus", label)
    # Normalize whitespace
    label = re.sub(r"\s+", " ", label)
    return label


def _is_chorus_family(raw_label: str) -> bool:
    """Return True if the label is chorus, pre-chorus, or post-chorus."""
    return _normalize_label(raw_label).startswith("chorus")


def parse_sections(raw_lyrics: str) -> list[dict]:
    """Parse raw lyrics into a list of {'label': str, 'lines': list[str]}.

    Step 1: Dedupe — walk every line, keep only the first occurrence of each
            unique line (compared case-insensitively). Section headers are not
            deduped, only lyric lines.
    Step 2: Group — collect the surviving lines under their section headers,
            normalizing labels (V1 → Verse 1, Pre-Chorus → Chorus, etc.) and
            merging adjacent chorus-family sections.
    """
    # --- Step 1: collect unique lines, preserving order and section markers ---
    seen_lines: set[str] = set()
    # Build list of (label_or_none, line_or_none) tuples
    # label_or_none is set when we hit a header; line_or_none for lyric lines
    tagged: list[tuple[str | None, str | None]] = []

    current_label = ""
    for raw_line in raw_lyrics.splitlines():
        line = raw_line.strip()
        if _SECTION_RE.match(line):
            current_label = line.strip("[](): \t")
            tagged.append((current_label, None))
        elif line:
            key = line.lower()
            if key not in seen_lines:
                seen_lines.add(key)
                tagged.append((None, line))
            # duplicate lines are silently dropped

    # --- Step 2: group into sections, merge chorus family ---
    sections: list[dict] = []
    current_label = ""
    current_lines: list[str] = []

    def flush():
        if current_lines:
            norm = _normalize_label(current_label) if current_label else ""
            display = "Chorus" if _is_chorus_family(current_label) else current_label
            # Merge into previous section if both are chorus-family
            if (
                sections
                and _is_chorus_family(current_label)
                and _is_chorus_family(sections[-1]["label"])
            ):
                sections[-1]["lines"].extend(current_lines)
            else:
                sections.append({"label": display, "lines": list(current_lines)})

    for label, line in tagged:
        if label is not None:
            flush()
            current_label = label
            current_lines = []
        elif line is not None:
            current_lines.append(line)

    flush()
    return sections


def _split_at_midpoint(line: str) -> str:
    """Split a long line into two at the word boundary closest to the middle."""
    mid = len(line) // 2
    # Search outward from the midpoint for the nearest space
    best = None
    for offset in range(len(line)):
        for candidate in (mid + offset, mid - offset):
            if 0 <= candidate < len(line) and line[candidate] == " ":
                best = candidate
                break
        if best is not None:
            break
    if best is None:
        return line
    return line[:best] + "\n" + line[best + 1:]


# Max characters that fit on one visual line of the slide
# (Comfortaa 36pt in a 674 PT text box ≈ 35 chars before wrapping)
_MAX_LINE_LEN = 35


def chunk_lines(sections: list[dict]) -> list[str]:
    """Split each section's lines into slide-sized chunks.

    - Short lines (≤ _MAX_LINE_LEN) are paired two per slide
    - Long lines (> _MAX_LINE_LEN) get their own slide, split at the
      word boundary nearest the midpoint
    - Chunks never cross section boundaries
    """
    chunks: list[str] = []
    for section in sections:
        pending = None  # a short line waiting for a partner
        for line in section["lines"]:
            if len(line) > _MAX_LINE_LEN:
                # Flush any pending short line on its own
                if pending is not None:
                    chunks.append(pending)
                    pending = None
                chunks.append(_split_at_midpoint(line))
            else:
                if pending is not None:
                    chunks.append(pending + "\n" + line)
                    pending = None
                else:
                    pending = line
        # Flush leftover at section boundary
        if pending is not None:
            chunks.append(pending)
            pending = None
    return chunks


def parse_and_chunk(raw_lyrics: str) -> list[str]:
    """Convenience: parse → dedupe → chunk."""
    sections = parse_sections(raw_lyrics)
    return chunk_lines(sections)
