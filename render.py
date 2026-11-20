#!/usr/bin/env python3
"""Render the 20 November 2026 world-news front page as a 1024x1024 PNG.

Everything is drawn procedurally with PIL: masthead, headline panels,
simple flag/icon illustrations and a briefs ticker. No randomness and no
clock reads, so the same bytes come out on every run.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024

PAPER = (247, 243, 234)
INK = (20, 33, 61)
RED = (178, 34, 52)
GOLD = (176, 141, 32)
TEAL = (13, 110, 110)
GRAY = (90, 90, 90)
RULE = (180, 174, 158)
PANEL_BG = (255, 255, 255)
SKY = (27, 38, 74)

FONT_CANDIDATES = {
    "serif_bold": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    ],
    "serif": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    ],
    "sans_bold": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ],
    "sans": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ],
}


def font(kind, size):
    for path in FONT_CANDIDATES[kind]:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    raise FileNotFoundError("no font found for " + kind)


def wrap(draw, text, fnt, max_width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_text_block(draw, x, y, text, fnt, fill, max_width, leading=4):
    for line in wrap(draw, text, fnt, max_width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + leading
    return y


def panel(draw, box, fill=PANEL_BG):
    draw.rectangle(box, fill=fill, outline=RULE, width=2)


def kicker(draw, x, y, text, color):
    fnt = font("sans_bold", 17)
    tw = draw.textlength(text, font=fnt)
    draw.rectangle([x, y, x + tw + 16, y + 26], fill=color)
    draw.text((x + 8, y + 4), text, font=fnt, fill=(255, 255, 255))
    return y + 34


# ---------------------------------------------------------------- icons

def flag_us(draw, x, y, w, h):
    stripe = h / 7
    for i in range(7):
        c = (178, 34, 52) if i % 2 == 0 else (255, 255, 255)
        draw.rectangle([x, y + i * stripe, x + w, y + (i + 1) * stripe], fill=c)
    draw.rectangle([x, y, x + w * 0.42, y + stripe * 4], fill=(30, 40, 110))
    for r in range(3):
        for cix in range(4):
            cx = x + 6 + cix * (w * 0.42 - 10) / 3
            cy = y + 6 + r * (stripe * 4 - 10) / 2
            draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(255, 255, 255))
    draw.rectangle([x, y, x + w, y + h], outline=(120, 120, 120), width=1)


def flag_cn(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    # one large star (drawn as a filled 5-point star) + four small dots
    cx, cy, r = x + w * 0.22, y + h * 0.28, h * 0.16
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    draw.polygon(pts, fill=(255, 222, 0))
    for dx, dy in [(0.42, 0.12), (0.47, 0.26), (0.47, 0.42), (0.42, 0.55)]:
        sx, sy = x + w * dx, y + h * dy
        draw.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(255, 222, 0))
    draw.rectangle([x, y, x + w, y + h], outline=(120, 120, 120), width=1)


def flag_ru(draw, x, y, w, h):
    third = h / 3
    draw.rectangle([x, y, x + w, y + third], fill=(255, 255, 255))
    draw.rectangle([x, y + third, x + w, y + 2 * third], fill=(0, 57, 166))
    draw.rectangle([x, y + 2 * third, x + w, y + h], fill=(213, 43, 30))
    draw.rectangle([x, y, x + w, y + h], outline=(120, 120, 120), width=1)


def icon_scales(draw, cx, cy, s, color):
    # central post
    draw.line([cx, cy - s, cx, cy + s * 0.9], fill=color, width=4)
    draw.line([cx - s * 0.8, cy - s * 0.75, cx + s * 0.8, cy - s * 0.75],
              fill=color, width=4)
    draw.ellipse([cx - 5, cy - s - 5, cx + 5, cy - s + 5], fill=color)
    draw.line([cx - s * 0.45, cy + s * 0.9, cx + s * 0.45, cy + s * 0.9],
              fill=color, width=5)
    for side in (-1, 1):
        px = cx + side * s * 0.8
        draw.line([px, cy - s * 0.75, px - s * 0.28, cy - s * 0.1],
                  fill=color, width=2)
        draw.line([px, cy - s * 0.75, px + s * 0.28, cy - s * 0.1],
                  fill=color, width=2)
        draw.arc([px - s * 0.3, cy - s * 0.35, px + s * 0.3, cy + s * 0.25],
                 start=15, end=165, fill=color, width=4)


def icon_calendar(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255),
                   outline=INK, width=3)
    draw.rectangle([x, y, x + w, y + h * 0.3], fill=RED)
    for fx in (0.25, 0.75):
        rx = x + w * fx
        draw.rectangle([rx - 4, y - 8, rx + 4, y + 10], fill=INK)
    f1 = font("sans_bold", 30)
    f2 = font("sans_bold", 22)
    t1 = "JAN 1"
    draw.text((x + (w - draw.textlength(t1, font=f1)) / 2, y + h * 0.36),
              t1, font=f1, fill=INK)
    t2 = "2027"
    draw.text((x + (w - draw.textlength(t2, font=f2)) / 2, y + h * 0.68),
              t2, font=f2, fill=RED)


def icon_cyclone(draw, cx, cy, r, color):
    w_out = max(3, r // 4)
    w_in = max(2, r // 5)
    for i in range(3):
        start = i * 120
        draw.arc([cx - r, cy - r, cx + r, cy + r], start=start,
                 end=start + 200, fill=color, width=w_out)
        draw.arc([cx - r * 0.62, cy - r * 0.62, cx + r * 0.62, cy + r * 0.62],
                 start=start + 60, end=start + 260, fill=color, width=w_in)
    draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=color)


def icon_bridge(draw, x, y, w, h):
    deck_y = y + h * 0.55
    draw.line([x, deck_y, x + w, deck_y], fill=INK, width=5)
    for fx in (0.3, 0.7):
        tx = x + w * fx
        draw.line([tx, y, tx, y + h], fill=INK, width=5)
        draw.line([tx - w * 0.28, deck_y, tx, y + 6], fill=INK, width=2)
        draw.line([tx + w * 0.28, deck_y, tx, y + 6], fill=INK, width=2)
    # broken span marker
    mx = x + w * 0.5
    draw.line([mx - 10, deck_y - 14, mx + 10, deck_y + 14], fill=RED, width=5)
    draw.line([mx + 10, deck_y - 14, mx - 10, deck_y + 14], fill=RED, width=5)
    for i in range(4):
        wy = y + h * 0.74 + i * (h * 0.06)
        draw.arc([x + i * 14, wy - 5, x + i * 14 + 26, wy + 5], start=0,
                 end=180, fill=TEAL, width=2)


def icon_voyager(draw, x, y, w, h):
    # Earth
    er = max(9, int(h * 0.26))
    ex, ey = x + er + 4, y + h - er - 2
    draw.ellipse([ex - er, ey - er, ex + er, ey + er], fill=(52, 110, 200))
    draw.ellipse([ex - er * 0.55, ey - er * 0.7, ex + er * 0.1, ey - er * 0.1],
                 fill=(90, 180, 90))
    draw.ellipse([ex + er * 0.1, ey + er * 0.2, ex + er * 0.75, ey + er * 0.7],
                 fill=(90, 180, 90))
    # spacecraft: dish + body + boom
    sx, sy = x + w - 40, y + 4
    draw.pieslice([sx - 24, sy - 6, sx + 24, sy + 26], start=200, end=340,
                  fill=(230, 230, 230), outline=INK, width=2)
    draw.rectangle([sx - 6, sy + 15, sx + 6, sy + 28], fill=(200, 170, 60),
                   outline=INK, width=1)
    draw.line([sx, sy + 28, sx - 26, sy + 46], fill=INK, width=2)
    draw.line([sx, sy + 28, sx + 22, sy + 42], fill=INK, width=2)
    # dashed signal path
    steps = 14
    for i in range(steps):
        t0, t1 = i / steps, (i + 0.55) / steps
        p0 = (ex + (sx - ex) * t0, ey + (sy + 10 - ey) * t0)
        p1 = (ex + (sx - ex) * t1, ey + (sy + 10 - ey) * t1)
        draw.line([p0, p1], fill=GOLD, width=3)


# ---------------------------------------------------------------- layout

def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # outer frame
    d.rectangle([10, 10, W - 11, H - 11], outline=INK, width=3)

    # ---- masthead
    d.rectangle([22, 22, W - 23, 122], fill=INK)
    title = "THE WORLD TODAY"
    tf = font("serif_bold", 52)
    tw = d.textlength(title, font=tf)
    d.text(((W - tw) / 2, 28), title, font=tf, fill=(255, 255, 255))
    date_line = "FRIDAY  ·  20 NOVEMBER 2026"
    df = font("sans_bold", 25)
    dw = d.textlength(date_line, font=df)
    d.text(((W - dw) / 2, 88), date_line, font=df, fill=(255, 214, 90))
    d.text((34, 38), "make.fun", font=font("sans_bold", 16),
           fill=(255, 255, 255))
    d.text((34, 58), "daily news", font=font("sans", 14),
           fill=(200, 205, 220))
    ed = "No. 2026-11-20"
    ef = font("sans", 14)
    d.text((W - 34 - d.textlength(ed, font=ef), 38), ed, font=ef,
           fill=(200, 205, 220))

    # ---- lead story
    lx0, ly0, lx1, ly1 = 22, 134, W - 23, 430
    panel(d, [lx0, ly0, lx1, ly1])
    y = kicker(d, lx0 + 16, ly0 + 14, "SHENZHEN, CHINA — APEC SUMMIT", RED)
    headline = "TRUMP, XI AND PUTIN HOLD FIRST-EVER THREE-WAY SUMMIT"
    hf = font("serif_bold", 39)
    y = draw_text_block(d, lx0 + 16, y + 2, headline, hf, INK, 600, leading=2)
    sub = ("The three nuclear powers' leaders met for 81 minutes on arms "
           "control and Ukraine. No breakthrough — the meeting itself "
           "was the message.")
    y = draw_text_block(d, lx0 + 16, y + 4, sub, font("sans", 20), GRAY, 600)
    # stat strip under the lead text
    d.rectangle([lx0 + 16, 390, lx0 + 616, 418], outline=RULE, width=2,
                fill=(252, 250, 244))
    strip = "81 MINUTES  ·  90% OF WORLD NUKES  ·  NO DEAL ANNOUNCED"
    sf2 = font("sans_bold", 16)
    sw2 = d.textlength(strip, font=sf2)
    d.text((lx0 + 16 + (600 - sw2) / 2, 396), strip, font=sf2, fill=INK)
    # flags + table graphic on the right of the lead panel
    gx = lx0 + 636
    flag_us(d, gx, ly0 + 44, 104, 58)
    flag_cn(d, gx + 122, ly0 + 44, 104, 58)
    flag_ru(d, gx + 244, ly0 + 44, 104, 58)
    for fx in (gx + 52, gx + 174, gx + 296):
        d.line([fx, ly0 + 102, fx, ly0 + 176], fill=INK, width=3)
    d.ellipse([gx + 34, ly0 + 176, gx + 314, ly0 + 228], fill=(120, 84, 50),
              outline=INK, width=2)
    cap = "Three flags, one round table"
    cf = font("sans", 15)
    d.text((gx + (348 - d.textlength(cap, font=cf)) / 2, ly0 + 236), cap,
           font=cf, fill=GRAY)

    # ---- second row: ICJ + Iran
    ry0, ry1 = 442, 684
    # ICJ panel
    panel(d, [22, ry0, 506, ry1])
    y = kicker(d, 38, ry0 + 12, "THE HAGUE — WORLD COURT", INK)
    y = draw_text_block(d, 38, y + 2,
                        "UN COURT: MYANMAR COMMITTED GENOCIDE",
                        font("serif_bold", 27), INK, 330, leading=2)
    y = draw_text_block(
        d, 38, y + 4,
        "First state ever held responsible for genocide. Reparations "
        "ordered for the Rohingya.",
        font("sans", 19), GRAY, 330)
    icon_scales(d, 440, ry0 + 128, 52, GOLD)
    # Iran panel
    panel(d, [518, ry0, W - 23, ry1])
    y = kicker(d, 534, ry0 + 12, "WASHINGTON — IRAN WAR", RED)
    y = draw_text_block(d, 534, y + 2,
                        "TRUMP PUSHES IRAN DECISION TO 2027",
                        font("serif_bold", 27), INK, 330, leading=2)
    y = draw_text_block(
        d, 534, y + 4,
        "\"We'll see what happens after January 1,\" Trump told Fox News "
        "during his China trip. No decision before the new year.",
        font("sans", 19), GRAY, 330)
    icon_calendar(d, 884, ry0 + 70, 96, 116)

    # ---- third row: Voyager / Cyclone / Kerch
    ty0, ty1 = 696, 896
    col_w = (W - 44 - 24) // 3
    # Voyager
    x0 = 22
    panel(d, [x0, ty0, x0 + col_w, ty1])
    y = kicker(d, x0 + 12, ty0 + 10, "SPACE — NASA", TEAL)
    y = draw_text_block(d, x0 + 12, y + 2,
                        "VOYAGER 1: ONE LIGHT-DAY AWAY",
                        font("serif_bold", 23), INK, col_w - 24, leading=2)
    y = draw_text_block(
        d, x0 + 12, y + 4,
        "First human-made object 16 billion miles out. Signals take a "
        "full day to reach Earth.",
        font("sans", 18), GRAY, col_w - 24)
    icon_voyager(d, x0 + 16, ty1 - 46, col_w - 32, 38)
    # Cyclone
    x0 = 22 + col_w + 12
    panel(d, [x0, ty0, x0 + col_w, ty1])
    y = kicker(d, x0 + 12, ty0 + 10, "INDIA — CYCLONE AKVAN", RED)
    y = draw_text_block(d, x0 + 12, y + 2,
                        "CYCLONE AKVAN NEARS ODISHA",
                        font("serif_bold", 23), INK, col_w - 24, leading=2)
    y = draw_text_block(
        d, x0 + 12, y + 4,
        "Landfall expected today near Gopalpur. Over 300,000 evacuated; "
        "winds to 110 km/h.",
        font("sans", 18), GRAY, col_w - 24)
    icon_cyclone(d, x0 + col_w // 2, ty1 - 22, 18, TEAL)
    # Kerch bridge
    x0 = 22 + 2 * (col_w + 12)
    panel(d, [x0, ty0, x0 + col_w, ty1])
    y = kicker(d, x0 + 12, ty0 + 10, "UKRAINE WAR", INK)
    y = draw_text_block(d, x0 + 12, y + 2,
                        "KERCH BRIDGE HIT A THIRD TIME",
                        font("serif_bold", 23), INK, col_w - 24, leading=2)
    y = draw_text_block(
        d, x0 + 12, y + 4,
        "Rail link to Crimea halted again. Europe says it is ready for "
        "talks with Russia.",
        font("sans", 18), GRAY, col_w - 24)
    icon_bridge(d, x0 + 20, ty1 - 34, col_w - 40, 26)

    # ---- briefs ticker
    by0, by1 = 908, 968
    d.rectangle([22, by0, W - 23, by1], fill=INK)
    d.text((36, by0 + 6), "ALSO TODAY", font=font("sans_bold", 16),
           fill=(255, 214, 90))
    briefs = ("Japan's Hayabusa2 — engine trouble ends asteroid landing "
              "plan · Sensex jumps 1.2% · Nicholls century as NZ reach "
              "243/5 vs India · Anthropic reportedly valued at $1.5 "
              "trillion")
    bf = font("sans", 15)
    lines = wrap(d, briefs, bf, W - 90)
    ly = by0 + 27
    for line in lines[:2]:
        d.text((36, ly), line, font=bf, fill=(240, 240, 240))
        ly += 17

    # ---- footer
    foot = ("Sources: Reuters · CNN · BBC · NASA · UN News · The Hindu · "
            "Le Monde — all reported 20 November 2026")
    ff = font("sans", 15)
    fw = d.textlength(foot, font=ff)
    d.text(((W - fw) / 2, 976), foot, font=ff, fill=GRAY)
    sig = "One image, one day: Friday 20 November 2026"
    sf = font("sans_bold", 16)
    sw = d.textlength(sig, font=sf)
    d.text(((W - sw) / 2, 994), sig, font=sf, fill=INK)

    return img


def render(dest):
    img = build()
    img.save(dest, "PNG", optimize=True)


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    render(os.path.join(here, "entry.png"))
    print("entry.png written")
