"""
Round 2 landing page assets — JAS-13
Generates:
  public/textures/parchment-bg.jpg      (~60-80KB, subtle warm paper texture)
  public/illustrations/book-mockup-b1.jpg  (~80-120KB, Book 1 coming-soon placeholder)
"""

import os
import random
import math
from PIL import Image, ImageDraw, ImageFilter, ImageFont

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# Palette anchors — JAS-9 / V4 reference
AMBER_WARM = (212, 155, 74)
FOREST_GREEN = (62, 92, 54)
CREAM_LIGHT = (245, 238, 218)
DUSK_PURPLE = (98, 82, 120)
PARCHMENT_BASE = (232, 218, 185)
PARCHMENT_DARK = (195, 178, 140)
PARCHMENT_LIGHT = (248, 240, 215)


# ─────────────────────────────────────────────
# 1. PARCHMENT BACKGROUND TEXTURE
# ─────────────────────────────────────────────

def lerp(a, b, t):
    return a + (b - a) * t

def smoothstep(t):
    return t * t * (3 - 2 * t)

def value_noise(w, h, scale, seed_offset=0):
    """Simple tileable value-noise field."""
    rng = random.Random(RANDOM_SEED + seed_offset)
    cells_x = max(2, w // scale + 2)
    cells_y = max(2, h // scale + 2)
    grid = [[rng.random() for _ in range(cells_x)] for _ in range(cells_y)]

    result = []
    for y in range(h):
        row = []
        for x in range(w):
            gx = x / scale
            gy = y / scale
            x0 = int(gx) % (cells_x - 1)
            y0 = int(gy) % (cells_y - 1)
            x1 = (x0 + 1) % (cells_x - 1)
            y1 = (y0 + 1) % (cells_y - 1)
            fx = smoothstep(gx - int(gx))
            fy = smoothstep(gy - int(gy))
            v = lerp(
                lerp(grid[y0][x0], grid[y0][x1], fx),
                lerp(grid[y1][x0], grid[y1][x1], fx),
                fy
            )
            row.append(v)
        result.append(row)
    return result

def gen_parchment(w=1920, h=1080, out_path="public/textures/parchment-bg.jpg"):
    print(f"  Generating parchment texture {w}×{h}...")

    # Base warm parchment color
    img = Image.new("RGB", (w, h), PARCHMENT_BASE)
    px = img.load()

    # Layer 1: large value noise (broad paper unevenness)
    noise_large = value_noise(w, h, scale=180, seed_offset=0)
    # Layer 2: medium grain
    noise_med   = value_noise(w, h, scale=40,  seed_offset=1)
    # Layer 3: fine paper grain
    noise_fine  = value_noise(w, h, scale=8,   seed_offset=2)

    br, bg, bb = PARCHMENT_BASE
    dr, dg, db = PARCHMENT_DARK
    lr, lg, lb = PARCHMENT_LIGHT

    for y in range(h):
        for x in range(w):
            nl = noise_large[y][x]
            nm = noise_med[y][x]
            nf = noise_fine[y][x]

            # Combine noise layers with weights
            v = nl * 0.55 + nm * 0.30 + nf * 0.15

            # Map to parchment range: dark=0.0, light=1.0
            if v < 0.5:
                t = v * 2.0
                r = int(lerp(dr, br, t))
                g = int(lerp(dg, bg, t))
                b = int(lerp(db, bb, t))
            else:
                t = (v - 0.5) * 2.0
                r = int(lerp(br, lr, t))
                g = int(lerp(bg, lg, t))
                b = int(lerp(bb, lb, t))

            # Very subtle warm amber tint on light spots
            if v > 0.75:
                tint = (v - 0.75) / 0.25 * 0.06
                r = min(255, int(r + (AMBER_WARM[0] - r) * tint))
                g = min(255, int(g + (AMBER_WARM[1] - g) * tint))

            px[x, y] = (
                max(0, min(255, r)),
                max(0, min(255, g)),
                max(0, min(255, b)),
            )

    # Slight Gaussian blur to smooth pixelation
    img = img.filter(ImageFilter.GaussianBlur(radius=0.8))

    # Vignette: darken corners very slightly for depth
    vignette = Image.new("RGB", (w, h), (0, 0, 0))
    draw = ImageDraw.Draw(vignette)
    cx, cy = w / 2, h / 2
    max_d = math.sqrt(cx**2 + cy**2)
    vpx = vignette.load()
    for y in range(h):
        for x in range(w):
            d = math.sqrt((x - cx)**2 + (y - cy)**2) / max_d
            # Only applies at edges (d > 0.6), max darkening 12%
            if d > 0.6:
                strength = ((d - 0.6) / 0.4) ** 2 * 0.12
                vpx[x, y] = (int(255 * strength),) * 3

    # Blend vignette (subtract)
    result_px = img.load()
    vig_px = vignette.load()
    for y in range(h):
        for x in range(w):
            r, g, b = result_px[x, y]
            v_dark = vig_px[x, y][0]
            result_px[x, y] = (
                max(0, r - v_dark),
                max(0, g - v_dark),
                max(0, b - v_dark),
            )

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "JPEG", quality=82, optimize=True)
    size_kb = os.path.getsize(out_path) // 1024
    print(f"  Saved: {out_path} ({size_kb}KB)")
    return out_path


# ─────────────────────────────────────────────
# 2. BOOK 1 "COMING SOON" PLACEHOLDER MOCKUP
# ─────────────────────────────────────────────

def gen_book_mockup(w=600, h=900, out_path="public/illustrations/book-mockup-b1.jpg"):
    """
    Typographic placeholder — styled in series palette.
    No AI generation: pure PIL drawing.
    Communicates: cozy fantasy, Jason Krebs, Book 1, coming soon.
    """
    print(f"  Generating book mockup {w}×{h}...")

    img = Image.new("RGB", (w, h), (40, 32, 24))  # very dark warm brown bg
    draw = ImageDraw.Draw(img)

    # ── Background gradient (sky-like, warm dark) ──
    for y in range(h):
        t = y / h
        # Top: dark forest green tint → bottom: deep amber-brown
        r = int(lerp(30, 55, t))
        g = int(lerp(28, 38, t))
        b = int(lerp(22, 18, t))
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # ── Atmospheric glow — warm amber orb (inn window suggestion) ──
    glow_cx, glow_cy = w // 2, int(h * 0.52)
    glow_r = 110
    for step in range(60, 0, -1):
        radius = int(glow_r * step / 60)
        alpha_frac = (1 - step / 60) ** 1.8 * 0.35
        fill_r = int(lerp(40, AMBER_WARM[0], alpha_frac * 3))
        fill_g = int(lerp(30, AMBER_WARM[1], alpha_frac * 3))
        fill_b = int(lerp(18, AMBER_WARM[2], alpha_frac * 3))
        draw.ellipse(
            [glow_cx - radius, glow_cy - radius, glow_cx + radius, glow_cy + radius],
            fill=(
                min(255, fill_r),
                min(255, fill_g),
                min(255, fill_b),
            )
        )

    # ── Silhouette: inn outline ──
    def draw_inn_silhouette(draw, cx, base_y, scale=1.0):
        s = scale
        # Main building body
        body = [
            (cx - int(70*s), base_y),
            (cx - int(70*s), base_y - int(90*s)),
            (cx + int(70*s), base_y - int(90*s)),
            (cx + int(70*s), base_y),
        ]
        draw.polygon(body, fill=(22, 28, 20))

        # Roof
        roof = [
            (cx - int(80*s), base_y - int(90*s)),
            (cx, base_y - int(145*s)),
            (cx + int(80*s), base_y - int(90*s)),
        ]
        draw.polygon(roof, fill=(18, 24, 16))

        # Chimney
        draw.rectangle([cx + int(30*s), base_y - int(165*s), cx + int(45*s), base_y - int(105*s)], fill=(18, 24, 16))

        # Windows — warm amber glow
        win_color = (AMBER_WARM[0] - 20, AMBER_WARM[1] - 30, 30)
        for wx in [cx - int(45*s), cx - int(10*s), cx + int(25*s)]:
            wy_top = base_y - int(75*s)
            wy_bot = base_y - int(45*s)
            draw.rectangle([wx, wy_top, wx + int(18*s), wy_bot], fill=win_color)

        # Door
        draw.rectangle([cx - int(12*s), base_y - int(40*s), cx + int(12*s), base_y], fill=(50, 30, 15))

    draw_inn_silhouette(draw, w // 2, int(h * 0.72), scale=1.0)

    # ── Ground / rolling hills ──
    hill_color = (28, 42, 24)
    points = [(0, int(h * 0.73))]
    for xi in range(0, w + 20, 20):
        yi = int(h * 0.73) + int(12 * math.sin(xi / 60.0)) + int(6 * math.sin(xi / 20.0))
        points.append((xi, yi))
    points.extend([(w, h), (0, h)])
    draw.polygon(points, fill=hill_color)

    # ── Stars ──
    rng = random.Random(99)
    for _ in range(55):
        sx = rng.randint(20, w - 20)
        sy = rng.randint(18, int(h * 0.38))
        brightness = rng.randint(160, 240)
        sr = rng.randint(1, 2)
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(brightness, brightness, int(brightness * 0.9)))

    # ── Fireflies / small lights ──
    for _ in range(18):
        fx = rng.randint(40, w - 40)
        fy = rng.randint(int(h * 0.55), int(h * 0.75))
        draw.ellipse([fx - 2, fy - 2, fx + 2, fy + 2], fill=(AMBER_WARM[0], AMBER_WARM[1], 80))

    # ── Border frame ──
    border_color = (AMBER_WARM[0] - 30, AMBER_WARM[1] - 40, 30)
    border_w = 6
    draw.rectangle([border_w, border_w, w - border_w, h - border_w], outline=border_color, width=2)
    # Inner border (decorative double)
    draw.rectangle([border_w + 8, border_w + 8, w - border_w - 8, h - border_w - 8], outline=border_color, width=1)

    # ── Typography ──
    # Series label — top
    series_text = "THE CROSSROADS INN"
    # Title placeholder
    title_text = "BOOK ONE"
    coming_text = "COMING SOON"
    author_text = "JASON KREBS"

    try:
        # Try system fonts in order of preference
        font_paths = [
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
            "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
        ]
        font_regular_paths = [
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        ]
        bold_font = None
        regular_font = None
        for fp in font_paths:
            if os.path.exists(fp):
                bold_font = fp
                break
        for fp in font_regular_paths:
            if os.path.exists(fp):
                regular_font = fp
                break

        f_series  = ImageFont.truetype(regular_font or bold_font, 18) if (regular_font or bold_font) else ImageFont.load_default()
        f_title   = ImageFont.truetype(bold_font or regular_font, 52) if (bold_font or regular_font) else ImageFont.load_default()
        f_coming  = ImageFont.truetype(regular_font or bold_font, 22) if (regular_font or bold_font) else ImageFont.load_default()
        f_author  = ImageFont.truetype(bold_font or regular_font, 26) if (bold_font or regular_font) else ImageFont.load_default()
    except Exception:
        f_series = f_title = f_coming = f_author = ImageFont.load_default()

    def centered_text(draw, text, y, font, color):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        x = (w - text_w) // 2
        draw.text((x, y), text, font=font, fill=color)

    gold_text = (AMBER_WARM[0] + 20, AMBER_WARM[1] + 10, 80)
    cream_text = CREAM_LIGHT
    dim_text = (180, 165, 130)

    # Series label
    centered_text(draw, series_text, 30, f_series, dim_text)

    # Thin ornamental rule below series label
    rule_y = 60
    draw.line([(w // 4, rule_y), (3 * w // 4, rule_y)], fill=border_color, width=1)
    # Small diamond center
    draw.polygon([
        (w // 2, rule_y - 4),
        (w // 2 + 5, rule_y),
        (w // 2, rule_y + 4),
        (w // 2 - 5, rule_y),
    ], fill=border_color)

    # "BOOK ONE" — large
    centered_text(draw, title_text, 76, f_title, gold_text)

    # Rule below title
    rule2_y = 140
    draw.line([(w // 4, rule2_y), (3 * w // 4, rule2_y)], fill=border_color, width=1)

    # "COMING SOON" — below title, above scene
    centered_text(draw, coming_text, int(h * 0.78) + 18, f_coming, cream_text)

    # Author name at bottom
    centered_text(draw, author_text, h - 55, f_author, gold_text)

    # Rule above author
    draw.line([(w // 4, h - 65), (3 * w // 4, h - 65)], fill=border_color, width=1)

    img = img.filter(ImageFilter.GaussianBlur(radius=0.3))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "JPEG", quality=85, optimize=True)
    size_kb = os.path.getsize(out_path) // 1024
    print(f"  Saved: {out_path} ({size_kb}KB)")
    return out_path


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print("Round 2 asset generation — JAS-13")
    print("Working dir:", os.getcwd())
    gen_parchment()
    gen_book_mockup()
    print("Done.")
