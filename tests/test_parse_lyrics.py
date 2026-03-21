from slides_generator.parse_lyrics import (
    chunk_lines,
    parse_and_chunk,
    parse_sections,
)


class TestParseSections:
    def test_basic_sections(self):
        lyrics = (
            "[Verse 1]\n"
            "Line one\n"
            "Line two\n"
            "\n"
            "[Chorus]\n"
            "Chorus line\n"
        )
        sections = parse_sections(lyrics)
        assert len(sections) == 2
        assert sections[0]["label"] == "Verse 1"
        assert sections[0]["lines"] == ["Line one", "Line two"]
        assert sections[1]["label"] == "Chorus"
        assert sections[1]["lines"] == ["Chorus line"]

    def test_deduplication(self):
        lyrics = (
            "[Verse 1]\n"
            "Same line\n"
            "[Verse 2]\n"
            "Same line\n"
            "New line\n"
        )
        sections = parse_sections(lyrics)
        # "Same line" appears only in Verse 1
        assert sections[0]["lines"] == ["Same line"]
        assert sections[1]["lines"] == ["New line"]

    def test_chorus_family_merge(self):
        lyrics = (
            "[Pre-Chorus]\n"
            "Pre line\n"
            "[Chorus]\n"
            "Chorus line\n"
        )
        sections = parse_sections(lyrics)
        # Pre-Chorus and Chorus merge into one section
        assert len(sections) == 1
        assert sections[0]["lines"] == ["Pre line", "Chorus line"]

    def test_empty(self):
        assert parse_sections("") == []


class TestChunkLines:
    def test_short_lines_paired(self):
        sections = [{"label": "V1", "lines": ["Short A", "Short B", "Short C"]}]
        chunks = chunk_lines(sections)
        assert chunks == ["Short A\nShort B", "Short C"]

    def test_long_line_split(self):
        sections = [{"label": "V1", "lines": ["This is a really long line that exceeds the limit"]}]
        chunks = chunk_lines(sections)
        assert len(chunks) == 1
        assert "\n" in chunks[0]  # was split


class TestParseAndChunk:
    def test_integration(self):
        lyrics = "[Verse 1]\nLine one\nLine two\n[Chorus]\nChorus line\n"
        chunks = parse_and_chunk(lyrics)
        assert len(chunks) >= 1
        assert "Line one" in chunks[0]
