"""Prepare the screenshots for the comparison page.

Reads the original screenshots from oud/ and nieuw/, applies the agreed edits
and writes cropped images (form area only, 1707 x 860) to site/img/.

Edits on the new screenshots:
  - tab "Tabblad" is renamed to "Bestanden" (glyphs copied from an old screenshot)
  - the "Prognosecategorie" row is removed from Algemene informatie (test environment only)

Run from the repository root:  python3 tools/prepare_images.py
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site" / "img"
W, H = 1707, 860

# Full browser-window screenshots: the form area starts here
WIN_X, WIN_Y = 200, 167

# Tab bar band in window coordinates
TAB_Y0, TAB_Y1 = 372, 407


def load(rel):
    return Image.open(ROOT / rel).convert("RGB")


def gray(img):
    return np.asarray(img.convert("L")).astype(float)


def ink_columns(img, x0, x1, y0, y1, thresh=170):
    """First and last column (inclusive) in the box that contain dark text pixels."""
    a = gray(img)[y0:y1, x0:x1]
    cols = np.where((a < thresh).any(axis=0))[0]
    return x0 + cols[0], x0 + cols[-1]


# Glyph sources
_tab_src = load("nieuw/nieuwe-klant/01-algemene-informatie.png")
_tx0, _tx1 = ink_columns(_tab_src, 1140, 1240, TAB_Y0, TAB_Y1)
TABBLAD = gray(_tab_src)[TAB_Y0:TAB_Y1, _tx0:_tx1 + 1]

_best_src = load("oud/verlenging/01-algemene-informatie.png")
_bx0, _bx1 = ink_columns(_best_src, 1225, 1330, TAB_Y0, TAB_Y1)
# Include the anti-aliased fringe on both sides of the word
BESTANDEN = _best_src.crop((_bx0 - 1, TAB_Y0, _bx1 + 3, TAB_Y1))


def find_tabblad(img):
    """Locate the "Tabblad" label in the tab bar; returns its left x or None."""
    a = gray(img)[TAB_Y0:TAB_Y1]
    t = TABBLAD
    tw = t.shape[1]
    tn = (t - t.mean()) / (t.std() + 1e-6)
    best = (0.0, None)
    for x in range(900, 1500 - tw):
        p = a[:, x:x + tw]
        pn = (p - p.mean()) / (p.std() + 1e-6)
        score = (pn * tn).mean()
        if score > best[0]:
            best = (score, x)
    return best[1] if best[0] > 0.9 else None


def rename_tabblad(img):
    x = find_tabblad(img)
    if x is None:
        return img, False
    x -= 1
    tw = TABBLAD.shape[1] + 3  # label plus its anti-aliased fringe
    bw = BESTANDEN.width
    delta = bw - tw
    span = 170  # covers "Gerelateerd" and its chevron, stays clear of side panels
    img = img.copy()
    # Shift what follows the label (e.g. "Gerelateerd") to make room
    right = img.crop((x + tw, TAB_Y0, x + tw + span, TAB_Y1))
    bg = img.getpixel((x - 6, (TAB_Y0 + TAB_Y1) // 2))
    patch = BESTANDEN
    if bg != (255, 255, 255):
        # Dimmed by an overlay: map white and text colour linearly onto the dimmed tones
        a = np.asarray(patch).astype(float)
        bgv = np.array(bg, dtype=float)
        dark_orig = TABBLAD.min()
        dark_dim = gray(img)[TAB_Y0:TAB_Y1, x:x + tw].min()
        k = (bgv.mean() - dark_dim) / (255 - dark_orig)
        a = bgv - (255 - a) * k
        patch = Image.fromarray(np.clip(a, 0, 255).astype("uint8"))
    img.paste(Image.new("RGB", (tw + span + max(delta, 0), TAB_Y1 - TAB_Y0), bg), (x, TAB_Y0))
    img.paste(right, (x + tw + delta, TAB_Y0))
    img.paste(patch, (x, TAB_Y0))
    return img, True


def remove_rows(img, y0, y1, x0=WIN_X, x1=WIN_X + 586):
    """Remove the horizontal band [y0, y1) in the left form column and close the gap."""
    img = img.copy()
    h = y1 - y0
    below = img.crop((x0, y1, x1, img.height))
    img.paste(below, (x0, y0))
    bg = img.getpixel((x0 + 2, img.height - 2))
    img.paste(Image.new("RGB", (x1 - x0, h), bg), (x0, img.height - h))
    return img


def crop_window(img, x=WIN_X, y=WIN_Y):
    return img.crop((x, y, x + W, y + H))


def crop_aligned(img, ref):
    """Crop a hand-cut screenshot so its command bar lines up with the reference."""
    a = gray(img)
    best = None
    for dy in range(-6, 7):
        for dx in range(-6, 8):
            if 10 + dy < 0:
                continue
            p = a[10 + dy:60 + dy, 210 + dx:700 + dx]
            if p.shape != ref.shape:
                continue
            d = np.abs(p - ref).mean()
            if best is None or d < best[0]:
                best = (d, dx, dy)
    _, dx, dy = best
    x0, y0 = 198 + dx, max(0, dy)
    return img.crop((x0, y0, x0 + W, y0 + H))


def main():
    (OUT / "oud").mkdir(parents=True, exist_ok=True)
    (OUT / "nieuw").mkdir(parents=True, exist_ok=True)

    ref = gray(load("oud/nieuwe-klant/01-algemene-informatie.png"))[10:60, 210:700]
    for f in sorted((ROOT / "oud" / "nieuwe-klant").glob("*.png")):
        crop_aligned(load(f), ref).save(OUT / "oud" / f"nk-{f.name}", optimize=True)
    for f in sorted((ROOT / "oud" / "verlenging").glob("*.png")):
        crop_window(load(f)).save(OUT / "oud" / f"vl-{f.name}", optimize=True)

    # Band of the Prognosecategorie row, in window coordinates
    prognose = {
        "nieuwe-klant/01-algemene-informatie.png": (779, 827),
        "verlenging/01-algemene-informatie.png": (731, 779),
    }
    # The product dialog sits further left than the form; keep it whole
    special_x = {"nieuwe-klant/03-fase-1-deel-product-toevoegen.png": 96}
    prefix = {"nieuwe-klant": "nk", "verlenging": "vl", "contract": "contract"}

    for f in sorted((ROOT / "nieuw").glob("*/*.png")):
        rel = f"{f.parent.name}/{f.name}"
        img = load(f)
        img, renamed = rename_tabblad(img)
        if rel in prognose:
            img = remove_rows(img, *prognose[rel])
        img = crop_window(img, x=special_x.get(rel, WIN_X))
        name = f"{prefix[f.parent.name]}-{f.name}"
        img.save(OUT / "nieuw" / name, optimize=True)
        print(f"{rel:55s} tab hernoemd: {'ja' if renamed else 'nee'}"
              f"{'  prognose verwijderd' if rel in prognose else ''}")


if __name__ == "__main__":
    main()
