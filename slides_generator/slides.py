import datetime
import uuid
from typing import Dict, List


def _uid() -> str:
    return str(uuid.uuid4()).replace("-", "")[:24]


def _bg_request(slide_id: str, bg_url: str) -> dict:
    """Build a single request to set a slide's background image."""
    return {
        "updatePageProperties": {
            "objectId": slide_id,
            "pageProperties": {
                "pageBackgroundFill": {
                    "stretchedPictureFill": {"contentUrl": bg_url}
                }
            },
            "fields": "pageBackgroundFill",
        }
    }


def _title_slide_requests(slide_id: str, bg_url: str, title_text: str) -> List[dict]:
    """Build batchUpdate requests for the title slide (background + overlay + title + lines)."""
    cream_id = _uid()
    taupe_id = _uid()
    title_id = _uid()
    top_line_id = _uid()
    left_line_id = _uid()
    right_line_id = _uid()
    bl_line_id = _uid()
    br_line_id = _uid()

    return [
        # 1. Background image
        _bg_request(slide_id, bg_url),
        # 2. Cream rectangle (bottom band)
        {
            "createShape": {
                "objectId": cream_id,
                "shapeType": "RECTANGLE",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {
                        "width": {"magnitude": 720, "unit": "PT"},
                        "height": {"magnitude": 261, "unit": "PT"},
                    },
                    "transform": {
                        "scaleX": 1,
                        "scaleY": 1,
                        "translateX": 0,
                        "translateY": 144,
                        "unit": "PT",
                    },
                },
            }
        },
        {
            "updateShapeProperties": {
                "objectId": cream_id,
                "shapeProperties": {
                    "shapeBackgroundFill": {
                        "solidFill": {
                            "color": {
                                "rgbColor": {"red": 0.961, "green": 0.914, "blue": 0.851}
                            },
                            "alpha": 0.55,
                        }
                    },
                    "outline": {"propertyState": "NOT_RENDERED"},
                },
                "fields": "shapeBackgroundFill,outline",
            }
        },
        # 3. Taupe rectangle (center overlay)
        {
            "createShape": {
                "objectId": taupe_id,
                "shapeType": "RECTANGLE",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {
                        "width": {"magnitude": 484, "unit": "PT"},
                        "height": {"magnitude": 174, "unit": "PT"},
                    },
                    "transform": {
                        "scaleX": 1,
                        "scaleY": 1,
                        "translateX": 119,
                        "translateY": 115,
                        "unit": "PT",
                    },
                },
            }
        },
        {
            "updateShapeProperties": {
                "objectId": taupe_id,
                "shapeProperties": {
                    "shapeBackgroundFill": {
                        "solidFill": {
                            "color": {
                                "rgbColor": {"red": 0.682, "green": 0.639, "blue": 0.561}
                            },
                            "alpha": 0.85,
                        }
                    },
                    "outline": {"propertyState": "NOT_RENDERED"},
                },
                "fields": "shapeBackgroundFill,outline",
            }
        },
        # 4. Title text box
        {
            "createShape": {
                "objectId": title_id,
                "shapeType": "TEXT_BOX",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {
                        "width": {"magnitude": 400, "unit": "PT"},
                        "height": {"magnitude": 80, "unit": "PT"},
                    },
                    "transform": {
                        "scaleX": 1,
                        "scaleY": 1,
                        "translateX": 160,
                        "translateY": 162,
                        "unit": "PT",
                    },
                },
            }
        },
        {
            "insertText": {
                "objectId": title_id,
                "insertionIndex": 0,
                "text": title_text,
            }
        },
        {
            "updateTextStyle": {
                "objectId": title_id,
                "textRange": {"type": "ALL"},
                "style": {
                    "fontFamily": "Lora",
                    "fontSize": {"magnitude": 60, "unit": "PT"},
                    "foregroundColor": {
                        "opaqueColor": {
                            "rgbColor": {"red": 0.322, "green": 0.275, "blue": 0.192}
                        }
                    },
                    "bold": False,
                },
                "fields": "fontFamily,fontSize,foregroundColor,bold",
            }
        },
        {
            "updateParagraphStyle": {
                "objectId": title_id,
                "textRange": {"type": "ALL"},
                "style": {"alignment": "CENTER"},
                "fields": "alignment",
            }
        },
        {
            "updateShapeProperties": {
                "objectId": title_id,
                "shapeProperties": {
                    "shapeBackgroundFill": {"propertyState": "NOT_RENDERED"},
                    "outline": {"propertyState": "NOT_RENDERED"},
                    "contentAlignment": "MIDDLE",
                },
                "fields": "shapeBackgroundFill,outline,contentAlignment",
            }
        },
        # 5. Decorative lines (frame with open bottom)
        {
            "createLine": {
                "objectId": top_line_id,
                "lineCategory": "STRAIGHT",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {
                        "width": {"magnitude": 596, "unit": "PT"},
                        "height": {"magnitude": 0, "unit": "PT"},
                    },
                    "transform": {
                        "scaleX": 1,
                        "scaleY": 1,
                        "translateX": 62,
                        "translateY": 88,
                        "unit": "PT",
                    },
                },
            }
        },
        {
            "createLine": {
                "objectId": left_line_id,
                "lineCategory": "STRAIGHT",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {
                        "width": {"magnitude": 0, "unit": "PT"},
                        "height": {"magnitude": 71, "unit": "PT"},
                    },
                    "transform": {
                        "scaleX": 1,
                        "scaleY": 1,
                        "translateX": 61,
                        "translateY": 87,
                        "unit": "PT",
                    },
                },
            }
        },
        {
            "createLine": {
                "objectId": right_line_id,
                "lineCategory": "STRAIGHT",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {
                        "width": {"magnitude": 0, "unit": "PT"},
                        "height": {"magnitude": 69, "unit": "PT"},
                    },
                    "transform": {
                        "scaleX": 1,
                        "scaleY": 1,
                        "translateX": 658,
                        "translateY": 87,
                        "unit": "PT",
                    },
                },
            }
        },
        {
            "createLine": {
                "objectId": bl_line_id,
                "lineCategory": "STRAIGHT",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {
                        "width": {"magnitude": 50, "unit": "PT"},
                        "height": {"magnitude": 0, "unit": "PT"},
                    },
                    "transform": {
                        "scaleX": 1,
                        "scaleY": 1,
                        "translateX": 62,
                        "translateY": 156,
                        "unit": "PT",
                    },
                },
            }
        },
        {
            "createLine": {
                "objectId": br_line_id,
                "lineCategory": "STRAIGHT",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {
                        "width": {"magnitude": 50, "unit": "PT"},
                        "height": {"magnitude": 0, "unit": "PT"},
                    },
                    "transform": {
                        "scaleX": 1,
                        "scaleY": 1,
                        "translateX": 610,
                        "translateY": 155,
                        "unit": "PT",
                    },
                },
            }
        },
        *[
            {
                "updateLineProperties": {
                    "objectId": line_id,
                    "lineProperties": {
                        "lineFill": {
                            "solidFill": {
                                "color": {
                                    "rgbColor": {"red": 1.0, "green": 1.0, "blue": 1.0}
                                },
                                "alpha": 1.0,
                            }
                        },
                        "weight": {"magnitude": 3, "unit": "PT"},
                    },
                    "fields": "lineFill,weight",
                }
            }
            for line_id in (top_line_id, left_line_id, right_line_id, bl_line_id, br_line_id)
        ],
    ]


def _create_slides_requests(count: int):
    """Generate createSlide requests for *count* blank slides appended after slide 0.

    Returns (requests, slide_ids).
    """
    requests = []
    slide_ids = []
    for i in range(count):
        sid = _uid()
        slide_ids.append(sid)
        requests.append({
            "createSlide": {
                "objectId": sid,
                "insertionIndex": i + 1,  # after title slide (index 0)
            }
        })
    return requests, slide_ids


def _lyric_slide_requests(slide_id: str, lyric_text: str) -> List[dict]:
    """Build batchUpdate requests for a single lyric slide's text box."""
    tb_id = _uid()
    return [
        # Create text box
        {
            "createShape": {
                "objectId": tb_id,
                "shapeType": "TEXT_BOX",
                "elementProperties": {
                    "pageObjectId": slide_id,
                    "size": {
                        "width": {"magnitude": 674, "unit": "PT"},
                        "height": {"magnitude": 133, "unit": "PT"},
                    },
                    "transform": {
                        "scaleX": 1,
                        "scaleY": 1,
                        "translateX": 16,
                        "translateY": 12,
                        "unit": "PT",
                    },
                },
            }
        },
        # Insert lyric text
        {
            "insertText": {
                "objectId": tb_id,
                "insertionIndex": 0,
                "text": lyric_text,
            }
        },
        # Style the text
        {
            "updateTextStyle": {
                "objectId": tb_id,
                "textRange": {"type": "ALL"},
                "style": {
                    "fontFamily": "Comfortaa",
                    "fontSize": {"magnitude": 36, "unit": "PT"},
                    "foregroundColor": {
                        "opaqueColor": {
                            "rgbColor": {"red": 0.0, "green": 0.0, "blue": 0.0}
                        }
                    },
                    "bold": False,
                    "backgroundColor": {
                        "opaqueColor": {
                            "rgbColor": {"red": 1.0, "green": 1.0, "blue": 1.0}
                        }
                    },
                },
                "fields": "fontFamily,fontSize,foregroundColor,bold,backgroundColor",
            }
        },
        # Paragraph style: center, 140% line spacing
        {
            "updateParagraphStyle": {
                "objectId": tb_id,
                "textRange": {"type": "ALL"},
                "style": {
                    "alignment": "CENTER",
                    "lineSpacing": 140,
                },
                "fields": "alignment,lineSpacing",
            }
        },
        # Shape properties: transparent bg, no outline, vertical center, autofit
        {
            "updateShapeProperties": {
                "objectId": tb_id,
                "shapeProperties": {
                    "shapeBackgroundFill": {"propertyState": "NOT_RENDERED"},
                    "outline": {"propertyState": "NOT_RENDERED"},
                    "contentAlignment": "MIDDLE",
                },
                "fields": "shapeBackgroundFill,outline,contentAlignment",
            }
        },
    ]


def build_lyric_presentation_requests(
    title_slide_id: str,
    lyric_chunks: List[str],
    bg_url: str,
    song_title: str,
    placeholder_ids: List[str] | None = None,
) -> List[dict]:
    """Orchestrate all requests to populate a blank presentation with lyrics.

    0. Delete default placeholder elements on the title slide
    1. Create slides (one per chunk)
    2. Title slide styling (background + overlay + title + decorative lines)
    3. Background on all lyric slides
    4. Lyric text boxes on each slide
    """
    requests: List[dict] = []

    # 0. Remove default title/subtitle placeholders
    for obj_id in (placeholder_ids or []):
        requests.append({"deleteObject": {"objectId": obj_id}})

    # 1. Create lyric slides
    slide_reqs, lyric_slide_ids = _create_slides_requests(len(lyric_chunks))
    requests.extend(slide_reqs)

    # 2. Title slide styling
    requests.extend(_title_slide_requests(title_slide_id, bg_url, song_title))

    # 3. Background on lyric slides
    for sid in lyric_slide_ids:
        requests.append(_bg_request(sid, bg_url))

    # 4. Lyric text boxes
    for sid, chunk in zip(lyric_slide_ids, lyric_chunks):
        requests.extend(_lyric_slide_requests(sid, chunk))

    return requests


def create_presentation(slides_service, title: str | None = None) -> Dict:
    """Create a new Google Slides presentation and return metadata + URL.

    If *title* is not provided, defaults to the closest Sunday after today.
    """
    if title is None:
        title = next_sunday_title()
    body = {"title": title}
    pres = slides_service.presentations().create(body=body).execute()

    pres_id = pres["presentationId"]
    pres_url = f"https://docs.google.com/presentation/d/{pres_id}/edit"

    return {
        "id": pres_id,
        "title": pres.get("title"),
        "url": pres_url,
    }


def next_sunday() -> datetime.date:
    """Return the date of the next Sunday."""
    today = datetime.date.today()
    weekday = today.weekday()
    days_ahead = (6 - weekday + 7) % 7
    if days_ahead == 0:
        days_ahead = 7
    return today + datetime.timedelta(days=days_ahead)


def next_sunday_title() -> str:
    """Return the next Sunday's date as MM/DD/YYYY."""
    return next_sunday().strftime("%m/%d/%Y")


def apply_backgrounds(
    slides_service, presentation_id: str, bg_url: str, title_text: str
):
    """Apply background to all slides: title template on slide 1, image-only on the rest."""
    pres = slides_service.presentations().get(presentationId=presentation_id).execute()
    slides = pres.get("slides", [])
    if not slides:
        print("No slides found in presentation.")
        return

    requests = []

    # First slide: full title template
    first_slide_id = slides[0]["objectId"]
    requests.extend(_title_slide_requests(first_slide_id, bg_url, title_text))

    # Remaining slides: background only
    for slide in slides[1:]:
        requests.append(_bg_request(slide["objectId"], bg_url))

    slides_service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={"requests": requests},
    ).execute()
    print(f"Applied background to {len(slides)} slide(s).")
