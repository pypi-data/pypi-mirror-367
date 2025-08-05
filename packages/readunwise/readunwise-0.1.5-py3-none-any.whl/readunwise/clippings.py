from collections import defaultdict
from readunwise.highlight import Highlight
from typing import List

CLIPPING_DELIMITER = "=========="


def parse_clippings_file(clippings_file: str) -> dict[str, list[Highlight]]:
    with open(clippings_file, "r+", encoding="utf8") as f:
        clippings = f.read().split(CLIPPING_DELIMITER)

    return _load_highlights(clippings)


def _load_highlights(clippings: List[str]) -> dict[str, list[Highlight]]:
    highlights = defaultdict(list)
    prev_highlight = Highlight()

    for clipping in clippings:
        highlight = Highlight.create(clipping)

        if highlight is None:
            continue

        if highlight.is_related(prev_highlight):
            highlights[prev_highlight.book].pop()

        highlights[highlight.book].append(highlight)
        prev_highlight = highlight

    return highlights
