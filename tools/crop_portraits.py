#!/usr/bin/env python3
"""Crop a folder of photos into square portraits for the site.

    python3 tools/crop_portraits.py <src-dir> <dest-dir>

Same treatment as the mentor headshots: crop around the face detected by
OpenCV YuNet where possible, so an environmental or full-body shot still
reads as a portrait at the size the page renders, and fall back to a centre
crop biased slightly upward. Output is 320x320 JPEG named after the source
file, lowercased with dashes.
"""
import pathlib
import re
import subprocess
import sys
import tempfile

from PIL import Image, ImageOps

MODEL = pathlib.Path(tempfile.gettempdir()) / "yunet.onnx"
MODEL_URL = ("https://raw.githubusercontent.com/opencv/opencv_zoo/main/"
             "models/face_detection_yunet/face_detection_yunet_2023mar.onnx")
SIZE, MARGIN = 320, 2.9


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


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
    """Largest detected face as (cx, cy, w) in image pixels.

    A small or low-resolution photo can put the face below the detector's
    floor, so if nothing is found at working size we retry on an upscaled
    copy before giving up on it.
    """
    if det is None:
        return None
    import cv2
    import numpy as np
    for scale in (1, 2, 3, 4):
        work = im.copy()
        if scale == 1:
            work.thumbnail((640, 640))
        else:
            work = im.resize((im.width * scale, im.height * scale), Image.LANCZOS)
            if max(work.size) > 2000:
                continue
        arr = cv2.cvtColor(np.asarray(work), cv2.COLOR_RGB2BGR)
        det.setInputSize((arr.shape[1], arr.shape[0]))
        try:
            _, faces = det.detect(arr)
        except Exception:
            return None
        if faces is not None and len(faces):
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])[:4]
            k = im.width / work.width
            return ((x + w / 2) * k, (y + h / 2) * k, w * k)
    return None


def square(im, box):
    if box:
        cx, cy, fw = box
        # floor keeps a very small face from being blown up past usefulness
        side = min(min(im.size), max(fw * MARGIN, min(im.size) * 0.35))
        left, top = cx - side / 2, cy - side * 0.42
    else:
        side = min(im.size)
        left, top = (im.width - side) / 2, (im.height - side) * 0.35
    left = max(0, min(left, im.width - side))
    top = max(0, min(top, im.height - side))
    return im.crop((int(left), int(top), int(left + side), int(top + side)))


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    dst.mkdir(parents=True, exist_ok=True)
    det = detector()
    print("  face detection: %s" % ("YuNet" if det else "unavailable — centre crop"))
    for f in sorted(src.iterdir()):
        if f.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
            continue
        im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
        box = face_box(det, im)
        out = dst / ("%s.jpg" % slug(f.stem))
        square(im, box).resize((SIZE, SIZE), Image.LANCZOS).save(
            out, "JPEG", quality=82, optimize=True, progressive=True)
        print("  %-34s %-6s -> %-34s %4.0f KB" % (f.name, "face" if box else "centre",
                                                  out.name, out.stat().st_size / 1024))


if __name__ == "__main__":
    main()
