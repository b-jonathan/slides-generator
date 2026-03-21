from slides_generator.parse_songs import (
    build_title_to_id_map,
    extract_song_titles,
    match_titles_to_ids,
)


class TestExtractSongTitles:
    def test_basic(self):
        snippet = "Hindsight - Hillsong\nInto the deep - idk"
        assert extract_song_titles(snippet) == ["Hindsight", "Into the deep"]

    def test_numbered(self):
        snippet = "1. Hindsight - Hillsong\n2) Into the deep - idk"
        assert extract_song_titles(snippet) == ["Hindsight", "Into the deep"]

    def test_ignores_urls_and_blank_lines(self):
        snippet = (
            "Hindsight - Hillsong\n"
            "https://open.spotify.com/track/abc\n"
            "\n"
            "Into the deep - idk\n"
        )
        assert extract_song_titles(snippet) == ["Hindsight", "Into the deep"]

    def test_empty(self):
        assert extract_song_titles("") == []


class TestMatchTitlesToIds:
    drive_results = [
        {"Title": "Hindsight", "Presentation ID": "abc123"},
        {"Title": "Other Song", "Presentation ID": "xyz789"},
    ]

    def test_found_and_missing(self):
        titles = ["Hindsight", "Into the deep"]
        matches = match_titles_to_ids(titles, self.drive_results)
        assert matches[0] == {"title": "Hindsight", "id": "abc123"}
        assert matches[1] == {"title": "Into the deep", "id": None}

    def test_case_insensitive(self):
        titles = ["hindsight"]
        matches = match_titles_to_ids(titles, self.drive_results)
        assert matches[0]["id"] == "abc123"


class TestBuildTitleToIdMap:
    def test_basic(self):
        drive_results = [
            {"Title": "Hindsight", "Presentation ID": "abc123"},
        ]
        mapping = build_title_to_id_map(drive_results)
        assert mapping == {"hindsight": "abc123"}
