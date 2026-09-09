"""Import photos without changing sources. Requires Pillow. See --help."""
import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from data_utils import read_json, validate_trip


def run(args):
    try:
        from PIL import Image, ImageOps
    except ImportError as exc:
        raise ValueError("Pillow is required. Use a Python runtime with Pillow installed.") from exc
    if args.full_size <= 0 or args.thumb_size <= 0:
        raise ValueError("Image sizes must be positive")
    manifest = Path(args.manifest).resolve()
    trip = read_json(manifest)
    photos, _ = validate_trip(trip)
    out = Path(args.out).resolve()
    sources = {}
    for pid, p in photos.items():
        source = Path(p["source"])
        if not source.is_absolute():
            source = manifest.parent / source
        source = source.resolve(strict=True)
        if not source.is_file():
            raise ValueError(f"{pid}: source is not a file")
        sources[pid] = source
    names = ["trip.json", "photo-metadata.js"]
    for pid in photos:
        names.extend([f"assets/photos/{pid}.jpg", f"assets/thumbs/{pid}.jpg"])
    destinations = [(out / name).resolve() for name in names]
    if manifest in destinations or set(sources.values()) & set(destinations):
        raise ValueError("Output would replace an input file; select another output directory")
    for dest in destinations:
        if dest.exists() and not args.overwrite:
            raise ValueError(f"Output already exists: {dest}. Use --overwrite only for intentional regeneration.")
    out.mkdir(parents=True, exist_ok=True)
    # All images must decode successfully before any generated file is replaced.
    with tempfile.TemporaryDirectory(prefix=".photo-import-", dir=out) as temporary:
        stage = Path(temporary)
        metadata = []
        for pid, p in photos.items():
            with Image.open(sources[pid]) as source:
                upright = ImageOps.exif_transpose(source)
                if "A" in upright.getbands() or "transparency" in upright.info:
                    rgba = upright.convert("RGBA")
                    image = Image.new("RGB", rgba.size, "white")
                    image.paste(rgba, mask=rgba.getchannel("A"))
                else:
                    image = upright.convert("RGB")
                # Retain a valid existing color profile, but never EXIF/GPS metadata.
                save_options = {"icc_profile": source.info["icc_profile"]} if source.info.get("icc_profile") and source.mode in ("RGB", "RGBA") else {}
                size = None
                for folder, maximum in [("photos", args.full_size), ("thumbs", args.thumb_size)]:
                    scaled = image.copy()
                    scaled.thumbnail((maximum, maximum), Image.Resampling.LANCZOS)
                    dest = stage / "assets" / folder / f"{pid}.jpg"
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    scaled.save(dest, "JPEG", quality=92 if folder == "photos" else 86, optimize=True, **save_options)
                    if folder == "photos":
                        size = scaled.size
                width, height = size
                entry = {"id": pid, "src": f"assets/photos/{pid}.jpg", "thumb": f"assets/thumbs/{pid}.jpg",
                         "width": width, "height": height, "ratio": width / height,
                         "orientation": "landscape" if width > height else "portrait" if height > width else "square"}
                if "caption" in p:
                    entry["caption"] = p["caption"]
                metadata.append(entry)
        published = {**trip, "photos": metadata}
        validate_trip(published, published=True)
        (stage / "trip.json").write_text(json.dumps(published, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (stage / "photo-metadata.js").write_text("export const photoMetadata = " + json.dumps(metadata, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")
        for name in names:
            dest = out / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            os.replace(stage / name, dest)
    print(f"Imported {len(metadata)} photos into {out}; source files unchanged.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--full-size", type=int, default=2048)
    parser.add_argument("--thumb-size", type=int, default=640)
    parser.add_argument("--overwrite", action="store_true")
    try:
        run(parser.parse_args())
    except (ValueError, OSError) as exc:
        print(f"Import failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
