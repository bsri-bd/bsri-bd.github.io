#!/usr/bin/env python3
"""Download mentor headshots from Drive and crop them to square portraits.

The Drive files are private Google Form uploads, so this only works while the
two Form "File responses" folders are shared as "anyone with the link can
view". Revoke that again afterwards — the images live in the repo from then on.

    python3 tools/fetch_headshots.py

Several mentors submitted environmental or full-body photos, so a plain centre
crop leaves the face tiny at the 72px size the site renders. Where OpenCV's
YuNet detector is available this crops around the detected face instead, with
enough margin to keep it a portrait rather than a tight face shot. Without the
model it falls back to a centre crop biased slightly upward.

Ids come from data/headshot-sources.local.json, which is gitignored: a Drive
id is a capability, not a label.
"""
import json
import pathlib
import subprocess
import sys
import tempfile

from PIL import Image, ImageOps

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "headshot-sources.local.json"
OUT = ROOT / "assets" / "img" / "mentors"
MODEL = pathlib.Path(tempfile.gettempdir()) / "yunet.onnx"
MODEL_URL = ("https://raw.githubusercontent.com/opencv/opencv_zoo/main/"
             "models/face_detection_yunet/face_detection_yunet_2023mar.onnx")
SIZE = 320
MARGIN = 2.9   # square side as a multiple of face width — portrait, not mugshot


def slug(name):
    import re
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def detector():
    try:
        import cv2
    except ImportError:
        return None
    if not MODEL.exists() or MODEL.stat().st_size < 100_000:
        try:
            subprocess.run(["curl", "-sL", MODEL_URL, "-o", str(MODEL)], check=True, timeout=60)
        except Exception:
            return None
    try:
        return cv2.FaceDetectorYN.create(str(MODEL), "", (320, 320))
    except Exception:
        return None


def face_box(det, im):
    """Largest detected face as (cx, cy, w), in image pixels."""
    if det is None:
        return None
    import cv2
    import numpy as np
    small = im.copy()
    small.thumbnail((640, 640))
    arr = cv2.cvtColor(np.asarray(small), cv2.COLOR_RGB2BGR)
    det.setInputSize((arr.shape[1], arr.shape[0]))
    try:
        _, faces = det.detect(arr)
    except Exception:
        return None
    if faces is None or len(faces) == 0:
        return None
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])[:4]
    k = im.width / small.width
    return ((x + w / 2) * k, (y + h / 2) * k, w * k)


def square(im, box):
    if box:
        cx, cy, fw = box
        side = min(min(im.size), max(fw * MARGIN, min(im.size) * 0.25))
        top = cy - side * 0.42          # a little headroom, shoulders below
        left = cx - side / 2
    else:
        side = min(im.size)
        left = (im.width - side) / 2
        top = (im.height - side) * 0.35
    left = max(0, min(left, im.width - side))
    top = max(0, min(top, im.height - side))
    return im.crop((int(left), int(top), int(left + side), int(top + side)))


def main():
    if not SRC.exists():
        sys.exit("missing %s" % SRC)
    sources = json.loads(SRC.read_text(encoding="utf-8"))["sources"]
    OUT.mkdir(parents=True, exist_ok=True)
    det = detector()
    print("  face detection: %s" % ("YuNet" if det else "unavailable — centre crop"))

    ok = faces = skipped = 0
    for name, fid in sources.items():
        tmp = pathlib.Path(tempfile.mkstemp()[1])
        subprocess.run(["curl", "-sL",
                        "https://drive.usercontent.google.com/download?id=%s&export=download" % fid,
                        "-o", str(tmp)], check=False)
        try:
            im = ImageOps.exif_transpose(Image.open(tmp)).convert("RGB")
        except Exception:
            print("  SKIP  %-34s not an image (folder still private?)" % name)
            tmp.unlink(missing_ok=True)
            skipped += 1
            continue
        box = face_box(det, im)
        dst = OUT / ("%s.jpg" % slug(name))
        square(im, box).resize((SIZE, SIZE), Image.LANCZOS).save(
            dst, "JPEG", quality=82, optimize=True, progressive=True)
        print("  ok    %-34s %-5s %5.0f KB" % (name, "face" if box else "centre",
                                               dst.stat().st_size / 1024))
        ok += 1
        faces += 1 if box else 0
        tmp.unlink(missing_ok=True)

    print("\n  %d saved (%d face-centred, %d centre-cropped), %d skipped" %
          (ok, faces, ok - faces, skipped))
    if ok:
        print("  now run: python3 tools/build_mentors.py")


if __name__ == "__main__":
    main()
