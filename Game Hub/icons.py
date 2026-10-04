# ==================================================
# GAMEHUB — CLEAN VECTOR ICON SYSTEM
# ==================================================

from functools import lru_cache
from PIL import Image, ImageDraw, ImageTk
import customtkinter as ctk
import math

ACCENT = "#00ffee"
GREEN = "#00ff88"
_SCALE = 4


def _line(draw, pts, fill, width):
    draw.line(pts, fill=fill, width=width, joint="curve")


def _draw(draw, kind, s, color):
    w = max(3, round(s / 8))
    m = s * 0.20
    cx = s / 2
    cy = s / 2

    if kind == "home":
        _line(draw, [(s*.18, s*.46), (cx, s*.18), (s*.82, s*.46)], color, w)
        draw.rounded_rectangle(
            (s*.27, s*.43, s*.73, s*.82),
            radius=int(s*.05),
            outline=color,
            width=w
        )
        draw.rectangle((s*.45, s*.61, s*.55, s*.82), fill=color)

    elif kind == "logo":
        # GameHub brand mark: a bold G with a subtle play cue.
        draw.arc(
            (s*.18, s*.16, s*.76, s*.84),
            start=38,
            end=320,
            fill=color,
            width=w
        )
        _line(draw, [(s*.48, s*.52), (s*.75, s*.52)], color, w)
        draw.polygon(
            [(s*.54, s*.40), (s*.54, s*.64), (s*.70, s*.52)],
            fill=GREEN
        )

    elif kind == "launcher":
        # Launcher: a game window with a clear play symbol.
        draw.rounded_rectangle(
            (s*.16, s*.18, s*.84, s*.82),
            radius=int(s*.09),
            outline=color,
            width=w
        )
        _line(draw, [(s*.20, s*.32), (s*.80, s*.32)], color, w)
        draw.ellipse((s*.26, s*.24, s*.30, s*.28), fill=GREEN)
        draw.ellipse((s*.33, s*.24, s*.37, s*.28), fill=GREEN)
        draw.polygon(
            [(s*.44, s*.43), (s*.44, s*.67), (s*.66, s*.55)],
            fill=color
        )

    elif kind == "music":
        _line(draw, [(s*.61, s*.20), (s*.61, s*.66)], color, w)
        _line(draw, [(s*.61, s*.20), (s*.80, s*.16)], color, w)
        draw.ellipse((s*.43, s*.60, s*.61, s*.77), fill=color)
        _line(draw, [(s*.61, s*.49), (s*.43, s*.60)], color, w)

    elif kind == "timer":
        draw.ellipse((s*.22, s*.28, s*.78, s*.84), outline=color, width=w)
        _line(draw, [(cx, s*.44), (cx, s*.57), (s*.63, s*.64)], color, w)
        draw.rounded_rectangle((s*.43, s*.16, s*.57, s*.25), radius=int(s*.03), fill=color)

    elif kind == "todo":
        draw.rounded_rectangle(
            (s*.24, s*.18, s*.76, s*.82),
            radius=int(s*.07),
            outline=color,
            width=w
        )
        _line(draw, [(s*.34, s*.51), (s*.44, s*.61), (s*.66, s*.38)], color, w)

    elif kind == "stats":
        # Three clean bars, increasing in height.
        draw.rounded_rectangle((s*.20, s*.56, s*.36, s*.80), radius=int(s*.025), fill=color)
        draw.rounded_rectangle((s*.42, s*.40, s*.58, s*.80), radius=int(s*.025), fill=color)
        draw.rounded_rectangle((s*.64, s*.22, s*.80, s*.80), radius=int(s*.025), fill=color)

    elif kind == "session":
        # Session: unmistakable clock, with a small controller cue.
        draw.ellipse((s*.18, s*.18, s*.78, s*.78), outline=color, width=w)
        _line(draw, [(s*.48, s*.31), (s*.48, s*.50), (s*.61, s*.58)], color, w)
        draw.rounded_rectangle(
            (s*.52, s*.66, s*.86, s*.84),
            radius=int(s*.07),
            outline=color,
            width=w
        )
        _line(draw, [(s*.62, s*.70), (s*.62, s*.79)], color, w)
        _line(draw, [(s*.58, s*.745), (s*.66, s*.745)], color, w)

    elif kind == "settings":
        # Eight short teeth + clear center hole.
        draw.ellipse((s*.27, s*.27, s*.73, s*.73), outline=color, width=w)
        draw.ellipse((s*.43, s*.43, s*.57, s*.57), outline=color, width=w)
        for a in range(0, 360, 45):
            r1, r2 = s*.36, s*.46
            x1 = cx + math.cos(math.radians(a)) * r1
            y1 = cy + math.sin(math.radians(a)) * r1
            x2 = cx + math.cos(math.radians(a)) * r2
            y2 = cy + math.sin(math.radians(a)) * r2
            _line(draw, [(x1, y1), (x2, y2)], color, w)

    elif kind == "search":
        draw.ellipse((s*.20, s*.18, s*.61, s*.59), outline=color, width=w)
        _line(draw, [(s*.53, s*.53), (s*.80, s*.80)], color, w)

    elif kind == "add":
        draw.ellipse((s*.18, s*.18, s*.82, s*.82), outline=color, width=w)
        _line(draw, [(cx, s*.34), (cx, s*.66)], color, w)
        _line(draw, [(s*.34, cy), (s*.66, cy)], color, w)

    elif kind == "refresh":
        draw.arc((s*.20, s*.20, s*.80, s*.80), 35, 305, fill=color, width=w)
        draw.polygon(
            [(s*.73, s*.24), (s*.82, s*.24), (s*.82, s*.33)],
            fill=color
        )

    elif kind == "play":
        draw.rounded_rectangle(
            (s*.18, s*.18, s*.82, s*.82),
            radius=int(s*.10),
            outline=color,
            width=w
        )
        draw.polygon(
            [(s*.44, s*.35), (s*.44, s*.65), (s*.68, cy)],
            fill=color
        )

    elif kind == "edit":
        _line(draw, [(s*.25, s*.73), (s*.34, s*.47), (s*.67, s*.20)], color, w)
        _line(draw, [(s*.37, s*.75), (s*.71, s*.41)], color, w)
        _line(draw, [(s*.24, s*.76), (s*.42, s*.72)], color, w)

    elif kind == "delete":
        draw.rounded_rectangle(
            (s*.30, s*.30, s*.70, s*.79),
            radius=int(s*.04),
            outline=color,
            width=w
        )
        _line(draw, [(s*.23, s*.25), (s*.77, s*.25)], color, w)
        _line(draw, [(s*.42, s*.17), (s*.58, s*.17)], color, w)

    elif kind == "star":
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            r = s*.36 if i % 2 == 0 else s*.16
            pts.append((cx + math.cos(a)*r, cy + math.sin(a)*r))
        draw.polygon(pts, outline=color, width=w)

    elif kind == "quote":
        draw.rounded_rectangle(
            (s*.16, s*.18, s*.84, s*.72),
            radius=int(s*.10),
            outline=color,
            width=w
        )
        _line(draw, [(s*.30, s*.72), (s*.27, s*.86), (s*.45, s*.72)], color, w)
        draw.ellipse((s*.33, s*.39, s*.40, s*.46), fill=color)
        draw.ellipse((s*.51, s*.39, s*.58, s*.46), fill=color)

    elif kind == "monitor":
        draw.rounded_rectangle(
            (s*.16, s*.18, s*.84, s*.68),
            radius=int(s*.06),
            outline=color,
            width=w
        )
        _line(draw, [(cx, s*.68), (cx, s*.82)], color, w)
        _line(draw, [(s*.38, s*.82), (s*.62, s*.82)], color, w)

    else:
        draw.ellipse((s*.25, s*.25, s*.75, s*.75), outline=color, width=w)


def _make_image(kind, size, color):
    size = int(size)
    render_size = max(64, size * _SCALE)
    img = Image.new("RGBA", (render_size, render_size), (0, 0, 0, 0))
    _draw(ImageDraw.Draw(img), kind, render_size, color)
    if render_size != size:
        img = img.resize((size, size), Image.Resampling.LANCZOS)
    return img


@lru_cache(maxsize=64)
def get_icon(kind, size=24, color=ACCENT):
    size = int(size)
    img = _make_image(kind, size, color)
    return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))


@lru_cache(maxsize=16)
def get_tk_icon(kind, size=64, color=ACCENT):
    size = int(size)
    return ImageTk.PhotoImage(_make_image(kind, size, color))
