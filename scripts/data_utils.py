"""Shared validation for scrapbook manifests; standard library only."""
import json
import math
import re
from pathlib import Path


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def number(value, label, positive=False, nonnegative=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label}: expected a finite number")
    if positive and value <= 0 or nonnegative and value < 0:
        raise ValueError(f"{label}: invalid value {value}")
    return value


def identifier(value, label):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", value):
        raise ValueError(f"{label}: use a nonempty string of letters, digits, _ or -")
    return value


def id_list(values, label, known):
    if not isinstance(values, list):
        raise ValueError(f"{label}: expected a list")
    ids = [identifier(v, label) for v in values]
    if len(set(ids)) != len(ids):
        raise ValueError(f"{label}: duplicate photo IDs")
    missing = set(ids) - known
    if missing:
        raise ValueError(f"{label}: unknown photo IDs {sorted(missing)}")
    return ids


def validate_trip(trip, published=False):
    if not isinstance(trip, dict) or not isinstance(trip.get("photos"), list) or not trip["photos"]:
        raise ValueError("trip.photos must be a nonempty list")
    photos = {}
    for p in trip["photos"]:
        if not isinstance(p, dict):
            raise ValueError("Each photo must be an object")
        pid = identifier(p.get("id"), "photo.id")
        if pid in photos:
            raise ValueError(f"Duplicate photo ID: {pid}")
        if published:
            w = number(p.get("width"), f"{pid}.width", positive=True)
            h = number(p.get("height"), f"{pid}.height", positive=True)
            ratio = number(p.get("ratio"), f"{pid}.ratio", positive=True)
            if not math.isclose(ratio, w / h, rel_tol=1e-6):
                raise ValueError(f"{pid}: ratio differs from width / height")
        elif not isinstance(p.get("source"), str) or not p["source"]:
            raise ValueError(f"{pid}: source path required")
        photos[pid] = p
    if not isinstance(trip.get("scenes"), list):
        raise ValueError("trip.scenes must be a list")
    scenes, assigned = {}, set()
    for scene in trip["scenes"]:
        if not isinstance(scene, dict):
            raise ValueError("Each scene must be an object")
        sid = identifier(scene.get("id"), "scene.id")
        if sid in scenes:
            raise ValueError(f"Duplicate scene ID: {sid}")
        ids = id_list(scene.get("photos"), f"{sid}.photos", set(photos))
        if not ids:
            raise ValueError(f"{sid}: scene needs at least one photo")
        scenes[sid] = scene
        assigned.update(ids)
    unassigned = set(id_list(trip.get("unassigned", []), "unassigned", set(photos)))
    if assigned & unassigned:
        raise ValueError(f"Assigned and unassigned overlap: {sorted(assigned & unassigned)}")
    forgotten = set(photos) - assigned - unassigned
    if forgotten:
        raise ValueError(f"Photos need a scene or explicit unassigned status: {sorted(forgotten)}")
    return photos, scenes
