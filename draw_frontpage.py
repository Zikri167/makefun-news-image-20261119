#!/usr/bin/env python3
"""
Deterministic newspaper‑style layout generator.
Creates /home/hatch/workspace/makefun/news-image-20261119/entry.png
and prints its size and dimensions.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageColor

# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------
WIDTH, HEIGHT = 1024, 1024
BG_COLOR = "#f7f3ea"
INK_COLOR = "#111111"
RED_COLOR = "#b91c1c"
NAVY_COLOR = "#1e3a5f"
TEAL_COLOR = "#0f766e"

# Font files (DejaVu family must exist on the system)
FONT_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def text_bbox(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont):
    """Return (width, height) of the given text using textbbox."""
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return right - left, bottom - top


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont,
              max_width: int) -> list[str]:
    """Wrap text to fit max_width. Returns list of lines (no truncation)."""
    words = text.split()
    lines = []
    current = ""
    for w in words:
        trial = f"{current} {w}".strip()
        w_width, _ = text_bbox(draw, trial, font)
        if w_width <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def fit_text(draw: ImageDraw.ImageDraw, text: str, font_path: str,
             start_size: int, max_width: int,
             max_lines: int, max_total_height: int = None) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    """
    Find the largest font size (starting from start_size and decreasing)
    that lets the wrapped text fit within max_width and max_lines.
    If max_total_height is given, also enforce that total height fits.
    Returns the font and the wrapped lines.
    """
    size = start_size
    while size > 5:
        font = load_font(font_path, size)
        lines = wrap_text(draw, text, font, max_width)
        if len(lines) <= max_lines:
            line_h = int(size * 1.25)
            total_h = line_h * len(lines)
            if (max_total_height is None) or (total_h <= max_total_height):
                return font, lines
        size -= 1
    # Fallback – use smallest size and whatever lines we got
    font = load_font(font_path, size)
    lines = wrap_text(draw, text, font, max_width)[:max_lines]
    return font, lines


def draw_wrapped(draw: ImageDraw.ImageDraw, x: int, y: int,
                 text: str, font_path: str, start_size: int,
                 max_width: int, max_lines: int,
                 line_spacing: float = 1.25,
                 fill=INK_COLOR) -> int:
    """
    Draw wrapped text and return the y‑coordinate just below the drawn block.
    """
    font, lines = fit_text(draw, text, font_path, start_size,
                           max_width, max_lines)
    line_h = int(font.size * line_spacing)
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_h
    return y


def draw_kicker_chip(draw: ImageDraw.ImageDraw, x: int, y: int,
                     text: str, font_path: str, size: int,
                     bg_color=RED_COLOR, txt_color="#ffffff",
                     hpad: int = 8, vpad: int = 4) -> int:
    """Draw a rectangular chip with red background and return bottom y."""
    font = load_font(font_path, size)
    txt_w, txt_h = text_bbox(draw, text, font)
    rect_w = txt_w + 2 * hpad
    rect_h = txt_h + 2 * vpad
    draw.rectangle([x, y, x + rect_w, y + rect_h], fill=bg_color)
    draw.text((x + hpad, y + vpad), text, font=font, fill=txt_color)
    return y + rect_h


def draw_rule(draw: ImageDraw.ImageDraw, y: int, color=INK_COLOR, thickness: int = 1):
    draw.line([(0, y), (WIDTH, y)], fill=color, width=thickness)


def vertical_gradient(draw: ImageDraw.ImageDraw, bbox, top_color, bottom_color):
    """Draw a simple vertical gradient inside bbox."""
    top_rgb = ImageColor.getrgb(top_color)
    bot_rgb = ImageColor.getrgb(bottom_color)
    x0, y0, x1, y1 = bbox
    height = y1 - y0
    for i in range(height):
        ratio = i / max(height - 1, 1)
        r = int(top_rgb[0] * (1 - ratio) + bot_rgb[0] * ratio)
        g = int(top_rgb[1] * (1 - ratio) + bot_rgb[1] * ratio)
        b = int(top_rgb[2] * (1 - ratio) + bot_rgb[2] * ratio)
        draw.line([(x0, y0 + i), (x1, y0 + i)], fill=(r, g, b))


def draw_star(draw: ImageDraw.ImageDraw, cx, cy, radius, fill="#ffffff"):
    """Draw a simple 5‑point star."""
    points = []
    for i in range(10):
        angle = i * 3.14159265 / 5
        r = radius if i % 2 == 0 else radius / 2
        x = cx + r * ImageDraw.math.cos(angle)
        y = cy + r * ImageDraw.math.sin(angle)
        points.append((x, y))
    draw.polygon(points, fill=fill)


# ----------------------------------------------------------------------
# Main drawing routine
# ----------------------------------------------------------------------
def main():
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # ------------------------------------------------------------------
    # 1. Masthead
    # ------------------------------------------------------------------
    draw_rule(draw, 8, INK_COLOR)
    draw_rule(draw, 112, INK_COLOR)

    # Kicker centered
    kicker_font = load_font(FONT_SANS_BOLD, 20)
    kicker_txt = "THE WORLD IN ONE PAGE"
    w, _ = text_bbox(draw, kicker_txt, kicker_font)
    draw.text(((WIDTH - w) / 2, 28), kicker_txt, font=kicker_font, fill=INK_COLOR)

    # Title
    title_font = load_font(FONT_SERIF_BOLD, 72)
    title_txt = "THE WORLD"
    w, _ = text_bbox(draw, title_txt, title_font)
    draw.text(((WIDTH - w) / 2, 40), title_txt, font=title_font, fill=INK_COLOR)

    # Date line
    date_left = "THURSDAY 19 NOVEMBER 2026"
    date_right = "EIGHT STORIES THAT DEFINED THE DAY"
    date_font_size = 20
    while True:
        date_font = load_font(FONT_SANS_BOLD, date_font_size)
        left_w, _ = text_bbox(draw, date_left, date_font)
        right_w, _ = text_bbox(draw, date_right, date_font)
        if WIDTH - left_w - right_w >= 24:
            break
        date_font_size -= 1
    draw.text((32, 122), date_left, font=date_font, fill=INK_COLOR)
    draw.text((WIDTH - 32 - right_w, 122), date_right, font=date_font, fill=INK_COLOR)

    draw_rule(draw, 152, INK_COLOR)
    draw_rule(draw, 156, RED_COLOR)

    # ------------------------------------------------------------------
    # 2. Lead story (left column)
    # ------------------------------------------------------------------
    left_x0, left_x1 = 32, 600
    col_width = left_x1 - left_x0
    cur_y = 164

    # Red kicker chip
    cur_y = draw_kicker_chip(draw, left_x0, cur_y,
                             "GTA VI IS HERE", FONT_SANS_BOLD, 20)

    cur_y += 10  # gap after chip

    # Headline – exactly 3 lines, serif bold 44pt
    headline = "AFTER 13 YEARS, VICE CITY OPENS ITS DOORS"
    cur_y = draw_wrapped(draw, left_x0, cur_y,
                         headline, FONT_SERIF_BOLD, 44,
                         col_width, max_lines=3)

    cur_y += 12  # gap before subhead

    # Subhead – corrected text, at most 2 lines, 23pt
    subhead = ("GTA VI launches worldwide at midnight; pre-orders top $1.5 billion, "
               "critics score 99/100.")
    cur_y = draw_wrapped(draw, left_x0, cur_y,
                         subhead, FONT_SANS, 23,
                         col_width, max_lines=2)

    # ------------------------------------------------------------------
    # Lead illustration (right panel)
    # ------------------------------------------------------------------
    ill_x0, ill_x1 = 624, 992
    ill_y0, ill_y1 = 164, 464
    # Gradient background
    vertical_gradient(draw, (ill_x0, ill_y0, ill_x1, ill_y1),
                      "#2d1b4e", "#ec4899")

    # Black skyline silhouette (simple rectangle at bottom)
    skyline_h = 40
    draw.rectangle([ill_x0, ill_y1 - skyline_h, ill_x1, ill_y1],
                   fill=INK_COLOR)

    # White "VI" in serif bold, placed upper right
    vi_font = load_font(FONT_SERIF_BOLD, 120)
    vi_w, vi_h = text_bbox(draw, "VI", vi_font)
    vi_x = ill_x1 - vi_w - 20
    vi_y = ill_y0 + 20
    draw.text((vi_x, vi_y), "VI", font=vi_font, fill="#ffffff")

    # Orange sun disc (fully inside panel, clear of the white "VI")
    sun_center = (900, 360)
    sun_radius = 60
    sun_bbox = [sun_center[0] - sun_radius, sun_center[1] - sun_radius,
                sun_center[0] + sun_radius, sun_center[1] + sun_radius]
    draw.ellipse(sun_bbox, fill="#ff8800")

    # Three small white stars in upper sky
    star_coords = [(ill_x0 + 80, ill_y0 + 60),
                   (ill_x0 + 150, ill_y0 + 30),
                   (ill_x0 + 220, ill_y0 + 80)]
    for cx, cy in star_coords:
        draw_star(draw, cx, cy, 8, fill="#ffffff")

    # ------------------------------------------------------------------
    # 3. Second row – two panels
    # ------------------------------------------------------------------
    row_y0, row_y1 = 484, 734
    divider_x = 512
    draw.line([(divider_x, row_y0), (divider_x, row_y1)], fill=INK_COLOR, width=1)

    panel_width = 464
    panel_height = row_y1 - row_y0

    # ---- Left panel -------------------------------------------------
    left_panel_x0 = 32
    cur_y = row_y0 + 10

    cur_y = draw_kicker_chip(draw, left_panel_x0, cur_y,
                             "SHENZHEN SUMMIT", FONT_SANS_BOLD, 20)

    cur_y += 10
    left_headline = "TRUMP, XI AND PUTIN MEET IN SHENZHEN"
    # Measure-fit so no line crosses the divider at x=512
    head_font, left_headline_lines = fit_text(
        draw, left_headline, FONT_SERIF_BOLD, 30, panel_width, 2)
    line_h = int(head_font.size * 1.25)
    for line in left_headline_lines:
        draw.text((left_panel_x0, cur_y), line, font=head_font, fill=INK_COLOR)
        cur_y += line_h

    cur_y += 10
    left_sub = "The first trilateral of the three leaders opens in China."
    cur_y = draw_wrapped(draw, left_panel_x0, cur_y,
                         left_sub, FONT_SANS, 19,
                         panel_width, max_lines=2)

    # Illustration band (45px tall approx)
    band_top = cur_y + 10
    band_bottom = min(band_top + 45, row_y1)
    draw.rectangle([left_panel_x0, band_top, left_panel_x0 + panel_width, band_bottom],
                   fill="#e0f7ff")  # pale blue

    # Navy skyline silhouette (simple rectangles)
    skyline_h = 30
    draw.rectangle([left_panel_x0, band_bottom - skyline_h,
                    left_panel_x0 + panel_width, band_bottom],
                   fill=NAVY_COLOR)

    # Red sun disc behind towers
    sun_center = (left_panel_x0 + panel_width // 2, band_top + 20)
    sun_radius = 25
    draw.ellipse([sun_center[0] - sun_radius, sun_center[1] - sun_radius,
                  sun_center[0] + sun_radius, sun_center[1] + sun_radius],
                 fill=RED_COLOR)

    # Three flagpoles
    flagpole_x = [left_panel_x0 + 80, left_panel_x0 + 200, left_panel_x0 + 320]
    for fx in flagpole_x:
        draw.line([(fx, band_top), (fx, band_bottom - skyline_h)], fill=INK_COLOR, width=2)
    # Flags (simple rectangles)
    # China (red)
    draw.rectangle([flagpole_x[0] + 2, band_top + 5,
                    flagpole_x[0] + 22, band_top + 15], fill=RED_COLOR)
    # Russia (white‑blue‑red stripes)
    flag_w = 20
    stripe_h = 4
    for i, col in enumerate(["#ffffff", "#0000ff", "#ff0000"]):
        draw.rectangle([flagpole_x[1] + 2, band_top + 5 + i * stripe_h,
                        flagpole_x[1] + 2 + flag_w, band_top + 5 + (i + 1) * stripe_h],
                       fill=col)
    # USA (red‑white stripes with blue canton)
    draw.rectangle([flagpole_x[2] + 2, band_top + 5,
                    flagpole_x[2] + 2 + flag_w, band_top + 15],
                   fill=RED_COLOR)
    draw.rectangle([flagpole_x[2] + 2, band_top + 5,
                    flagpole_x[2] + 2 + 10, band_top + 10],
                   fill="#0000ff")  # blue canton

    # ---- Right panel ------------------------------------------------
    right_panel_x0 = 528
    cur_y = row_y0 + 10

    cur_y = draw_kicker_chip(draw, right_panel_x0, cur_y,
                             "U.S. CONGRESS", FONT_SANS_BOLD, 20)

    cur_y += 10
    right_headline = "JEFFRIES SET TO BE FIRST BLACK SPEAKER"
    right_head_font, right_headline_lines = fit_text(
        draw, right_headline, FONT_SERIF_BOLD, 30, panel_width, 2)
    right_line_h = int(right_head_font.size * 1.25)
    for line in right_headline_lines:
        draw.text((right_panel_x0, cur_y), line, font=right_head_font, fill=INK_COLOR)
        cur_y += right_line_h

    cur_y += 10
    right_sub = "Democrats pick Hakeem Jeffries to lead the House."
    cur_y = draw_wrapped(draw, right_panel_x0, cur_y,
                         right_sub, FONT_SANS, 19,
                         panel_width, max_lines=2)

    # Illustration band
    band_top = cur_y + 10
    band_bottom = min(band_top + 45, row_y1)
    draw.rectangle([right_panel_x0, band_top,
                    right_panel_x0 + panel_width, band_bottom],
                   fill="#f0f0f0")  # pale background

    # Capitol dome silhouette (simple arch)
    dome_center = (right_panel_x0 + panel_width // 2, band_top + 20)
    dome_radius = 30
    draw.pieslice([dome_center[0] - dome_radius, dome_center[1] - dome_radius,
                   dome_center[0] + dome_radius, dome_center[1] + dome_radius],
                  start=180, end=360, fill=NAVY_COLOR)
    # Small flag on top
    flag_x = dome_center[0]
    draw.line([(flag_x, band_top), (flag_x, band_top - 15)], fill=INK_COLOR, width=2)
    draw.rectangle([flag_x - 5, band_top - 15,
                    flag_x + 5, band_top - 5], fill=RED_COLOR)

    # Thin red base line
    draw.line([(right_panel_x0, band_bottom),
               (right_panel_x0 + panel_width, band_bottom)],
              fill=RED_COLOR, width=2)

    # ------------------------------------------------------------------
    # 4. Third row – three columns
    # ------------------------------------------------------------------
    third_y0, third_y1 = 754, 934
    col_div1, col_div2 = 352, 672

    # Column definitions: (x0, x1, kicker, headline, body, icon_drawer)
    columns = [
        (32, 336,
         "GULF",
         "U.S. AND IRAN TRADE FIRE AGAIN",
         "Iran widens attacks to Kuwait and Bahrain.",
         "warship"),
        (368, 656,
         "VOYAGER 1",
         "ONE LIGHT-DAY FROM HOME",
         "NASA's probe is now one light-day away.",
         "spacecraft"),
        (688, 992,
         "CYCLONE AKVAN",
         "STORM BEARS DOWN ON INDIA",
         "Cyclone Akvan heads for the coast between Machilipatnam and Puri.",
         "cyclone")
    ]

    for x0, x1, kicker, headline, body, icon_type in columns:
        cur_y = third_y0 + 10
        # Kicker chip
        cur_y = draw_kicker_chip(draw, x0, cur_y, kicker,
                                 FONT_SANS_BOLD, 20)

        # Headline – exactly 2 lines, serif bold 26pt
        head_font = load_font(FONT_SERIF_BOLD, 26)
        # Force wrap into two lines as per spec
        # Simple split at first space after roughly half width
        max_w = x1 - x0
        words = headline.split()
        # naive two‑line split
        split_idx = len(words) // 2
        line1 = " ".join(words[:split_idx])
        line2 = " ".join(words[split_idx:])
        # Ensure they fit; if not, shrink font
        while True:
            w1, _ = text_bbox(draw, line1, head_font)
            w2, _ = text_bbox(draw, line2, head_font)
            if w1 <= max_w and w2 <= max_w:
                break
            head_font = load_font(FONT_SERIF_BOLD, head_font.size - 1)

        line_h = int(head_font.size * 1.25)
        draw.text((x0, cur_y), line1, font=head_font, fill=INK_COLOR)
        cur_y += line_h
        draw.text((x0, cur_y), line2, font=head_font, fill=INK_COLOR)
        cur_y += line_h

        cur_y += 10
        # Body – at most 2 lines, sans 17pt
        cur_y = draw_wrapped(draw, x0, cur_y,
                             body, FONT_SANS, 17,
                             max_w, max_lines=2)

        # Icon – placed at top‑right of column, aligned with kicker chip top
        icon_size = 40
        icon_x = x1 - icon_size - 4
        icon_y = third_y0 + 10  # same as kicker top
        if icon_type == "warship":
            # grey hull rectangle + small mast
            draw.rectangle([icon_x, icon_y + 20,
                            icon_x + 30, icon_y + 30],
                           fill="#777777")
            draw.line([icon_x + 15, icon_y + 20,
                       icon_x + 15, icon_y + 10],
                      fill="#777777", width=2)
        elif icon_type == "spacecraft":
            # gold circle dish + antenna
            draw.ellipse([icon_x, icon_y,
                          icon_x + 30, icon_y + 30],
                         fill="#ffd700")
            draw.line([icon_x + 15, icon_y,
                       icon_x + 15, icon_y - 10],
                      fill="#ffd700", width=2)
        elif icon_type == "cyclone":
            # teal spiral (two arcs)
            draw.arc([icon_x, icon_y,
                      icon_x + 30, icon_y + 30],
                     start=0, end=270, fill=TEAL_COLOR, width=3)
            draw.arc([icon_x + 5, icon_y + 5,
                      icon_x + 25, icon_y + 25],
                     start=0, end=270, fill=TEAL_COLOR, width=3)

    # ------------------------------------------------------------------
    # 5. Bottom strip (corrected spec)
    # ------------------------------------------------------------------
    draw_rule(draw, 936, INK_COLOR)

    label_font = load_font(FONT_SANS_BOLD, 18)
    label_txt = "ALSO TODAY"
    draw.text((32, 944), label_txt, font=label_font, fill=RED_COLOR)

    # First item on same line after label
    item1 = ("EU PROPOSES 45 BILLION EURO UKRAINE LOAN — to be repaid from "
             "Russian reparations.")
    # Compute start x after label plus a space
    label_w, _ = text_bbox(draw, label_txt, label_font)
    item1_x = 32 + label_w + 8
    # Ensure it fits within width
    max_w = WIDTH - item1_x - 32
    item1_font, item1_lines = fit_text(draw, item1, FONT_SANS,
                                       18, max_w, max_lines=1)
    draw.text((item1_x, 944), item1_lines[0], font=item1_font, fill=INK_COLOR)

    # Second item on next line
    item2 = ("NVIDIA'S NEW ERA — acting chief promises earlier pay rises "
             "after Huang quits.")
    draw.text((32, 966), item2, font=label_font, fill=INK_COLOR)

    # ------------------------------------------------------------------
    # 6. Footer (corrected spec)
    # ------------------------------------------------------------------
    draw_rule(draw, 992, INK_COLOR)

    footer_y = 998
    left_footer = ("Wire reports from 19 November 2026 — gaming, Shenzhen, "
                   "Washington, Gulf, space, India.")
    left_font = load_font(FONT_SANS, 14)
    draw.text((32, footer_y), left_footer, font=left_font, fill=INK_COLOR)

    right_footer = "THE WORLD IN ONE PAGE"
    right_font = load_font(FONT_SANS_BOLD, 14)
    right_w, _ = text_bbox(draw, right_footer, right_font)
    draw.text((WIDTH - 32 - right_w, footer_y),
              right_footer, font=right_font, fill=RED_COLOR)

    # ------------------------------------------------------------------
    # Save and report
    # ------------------------------------------------------------------
    out_path = Path("/home/hatch/workspace/makefun/news-image-20261119/entry.png")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="PNG")
    size_bytes = out_path.stat().st_size
    print(f"{size_bytes} bytes, {WIDTH}x{HEIGHT}")

if __name__ == "__main__":
    main()
