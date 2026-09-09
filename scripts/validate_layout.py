"""Check assigned photo coverage, page bounds and collage collisions."""
import argparse
import sys
from collections import Counter
from data_utils import read_json, validate_trip, number


def box(item, label, ratio=None, border=None):
    if not isinstance(item, dict) or item.get("side") not in ("left", "right"):
        raise ValueError(f"{label}: side must be left or right")
    x = number(item.get("x"), f"{label}.x")
    z = number(item.get("z"), f"{label}.z")
    w = number(item.get("width"), f"{label}.width", positive=True)
    h = w / ratio if ratio is not None else number(item.get("height"), f"{label}.height", positive=True)
    border = border or {"x": 0, "top": 0, "bottom": 0}
    return (item["side"], x - w / 2 - border["x"], x + w / 2 + border["x"],
            z - h / 2 - border["top"], z + h / 2 + border["bottom"])


def overlaps(a, b):
    eps = 1e-8
    return a[0] == b[0] and a[1] < b[2] - eps and a[2] > b[1] + eps and a[3] < b[4] - eps and a[4] > b[3] + eps


def validate(trip, layouts):
    photos, scenes = validate_trip(trip, published=True)
    if not isinstance(layouts, dict) or not isinstance(layouts.get("spreads"), list):
        raise ValueError("layouts.spreads must be a list")
    bounds, border = layouts.get("bounds", {}), layouts.get("border", {})
    for key in ("left", "right", "top", "bottom"):
        number(bounds.get(key), f"bounds.{key}")
    if bounds["left"] >= bounds["right"] or bounds["top"] >= bounds["bottom"]:
        raise ValueError("Page bounds must have positive width and height")
    for key in ("x", "top", "bottom"):
        number(border.get(key), f"border.{key}", nonnegative=True)
    actual = {sid: [] for sid in scenes}
    errors = []
    for i, spread in enumerate(layouts["spreads"]):
        if not isinstance(spread, dict) or spread.get("scene") not in scenes:
            raise ValueError(f"spread {i}: unknown scene")
        sid = spread["scene"]
        if not isinstance(spread.get("items"), list) or not isinstance(spread.get("reserved", []), list):
            raise ValueError(f"spread {i}: items and reserved must be lists")
        cards = []
        reserved = [box(r, f"spread {i} reserved {j}") for j, r in enumerate(spread.get("reserved", []))]
        for item in spread["items"]:
            if not isinstance(item, dict) or item.get("id") not in photos:
                raise ValueError(f"spread {i}: unknown photo")
            pid = item["id"]
            actual[sid].append(pid)
            rect = box(item, f"{sid}/{pid}", photos[pid]["ratio"], border)
            if rect[1] < bounds["left"] - 1e-8 or rect[2] > bounds["right"] + 1e-8 or rect[3] < bounds["top"] - 1e-8 or rect[4] > bounds["bottom"] + 1e-8:
                errors.append(f"spread {i} {pid}: frame outside page bounds")
            for other_id, other in cards:
                if overlaps(rect, other):
                    errors.append(f"spread {i}: {pid} overlaps {other_id}")
            for j, area in enumerate(reserved):
                if overlaps(rect, area):
                    errors.append(f"spread {i}: {pid} overlaps reserved area {j}")
            cards.append((pid, rect))
        if not spread["items"]:
            errors.append(f"spread {i}: no photos")
    for sid, scene in scenes.items():
        expected, found = Counter(scene["photos"]), Counter(actual[sid])
        if expected != found:
            errors.append(f"{sid}: missing {list((expected - found).elements())}; extra/duplicated {list((found - expected).elements())}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trip", required=True)
    parser.add_argument("--layouts", required=True)
    args = parser.parse_args()
    try:
        trip, layouts = read_json(args.trip), read_json(args.layouts)
        errors = validate(trip, layouts)
        if errors:
            print("Layout invalid:\n- " + "\n- ".join(errors), file=sys.stderr)
            return 1
        print(f"PASS: {len(trip['scenes'])} scenes, {len(layouts['spreads'])} spreads; all assigned photos fit without collisions.")
        return 0
    except (ValueError, OSError, TypeError, AttributeError) as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
