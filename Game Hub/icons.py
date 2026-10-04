# ==================================================
# 🎨 GAMEHUB ICON SYSTEM
# ==================================================

from functools import lru_cache
from PIL import Image, ImageDraw, ImageTk
import customtkinter as ctk

ACCENT = "#00ffee"
GREEN = "#00ff88"


def _line(draw, pts, fill, width):
    draw.line(pts, fill=fill, width=width, joint="curve")


def _draw(draw, kind, s, color):
    import math
    w = max(2, round(s / 9))
    m = s * 0.18
    cx = s / 2
    cy = s / 2

    if kind == "home":
        _line(draw, [(m, s*.48), (cx, m), (s-m, s*.48)], color, w)
        draw.rectangle((s*.27, s*.46, s*.73, s*.82), outline=color, width=w)
        draw.rectangle((s*.45, s*.61, s*.55, s*.82), outline=color, width=w)

    elif kind in ("launcher", "logo"):
        draw.rounded_rectangle((m, s*.34, s-m, s*.72), radius=int(s*.16), outline=color, width=w)
        draw.ellipse((s*.10, s*.30, s*.34, s*.70), outline=color, width=w)
        draw.ellipse((s*.66, s*.30, s*.90, s*.70), outline=color, width=w)
        _line(draw, [(s*.25, cy), (s*.43, cy)], color, w)
        _line(draw, [(s*.34, s*.41), (s*.34, s*.59)], color, w)
        draw.ellipse((s*.62, s*.47, s*.68, s*.53), fill=GREEN)
        draw.ellipse((s*.72, s*.57, s*.78, s*.63), fill=GREEN)

    elif kind == "music":
        _line(draw, [(s*.60, s*.20), (s*.60, s*.67)], color, w)
        _line(draw, [(s*.60, s*.20), (s*.82, s*.16)], color, w)
        draw.ellipse((s*.25, s*.60, s*.48, s*.80), outline=color, width=w)
        draw.ellipse((s*.49, s*.54, s*.72, s*.74), outline=color, width=w)
        _line(draw, [(s*.37, s*.70), (s*.60, s*.64)], color, w)

    elif kind == "timer":
        draw.ellipse((m, s*.24, s-m, s*.88), outline=color, width=w)
        _line(draw, [(cx, s*.44), (cx, s*.60), (s*.62, s*.67)], color, w)
        _line(draw, [(s*.42, s*.14), (s*.58, s*.14)], color, w)
        _line(draw, [(cx, s*.08), (cx, s*.16)], color, w)

    elif kind == "todo":
        draw.rounded_rectangle((s*.22, s*.16, s*.78, s*.84), radius=int(s*.06), outline=color, width=w)
        _line(draw, [(s*.33,s*.51),(s*.43,s*.61),(s*.67,s*.35)], color, w)

    elif kind == "stats":
        _line(draw, [(s*.22,s*.80),(s*.22,s*.55),(s*.40,s*.55),(s*.40,s*.38),(s*.58,s*.38),(s*.58,s*.22),(s*.78,s*.22)], color, w)

    elif kind == "session":
        _line(draw, [(s*.26,s*.66),(s*.26,s*.38),(s*.46,s*.38),(s*.46,s*.66)], color, w)
        _line(draw, [(s*.54,s*.66),(s*.54,s*.38),(s*.74,s*.38),(s*.74,s*.66)], color, w)
        _line(draw, [(s*.38,s*.76),(s*.62,s*.76)], color, w)

    elif kind == "settings":
        draw.ellipse((s*.28,s*.28,s*.72,s*.72), outline=color, width=w)
        draw.ellipse((s*.43,s*.43,s*.57,s*.57), outline=color, width=w)
        for a in range(0,360,60):
            x1=cx+math.cos(math.radians(a))*s*.30
            y1=cy+math.sin(math.radians(a))*s*.30
            x2=cx+math.cos(math.radians(a))*s*.44
            y2=cy+math.sin(math.radians(a))*s*.44
            _line(draw,[(x1,y1),(x2,y2)],color,w)

    elif kind == "search":
        draw.ellipse((s*.22,s*.20,s*.62,s*.60), outline=color, width=w)
        _line(draw,[(s*.54,s*.54),(s*.80,s*.80)],color,w)

    elif kind == "add":
        draw.ellipse((s*.18,s*.18,s*.82,s*.82), outline=color, width=w)
        _line(draw,[(cx,s*.34),(cx,s*.66)],color,w)
        _line(draw,[(s*.34,cy),(s*.66,cy)],color,w)

    elif kind == "refresh":
        draw.arc((s*.20,s*.20,s*.80,s*.80), 20, 300, fill=color, width=w)
        _line(draw,[(s*.76,s*.40),(s*.76,s*.22),(s*.58,s*.22)],color,w)
        _line(draw,[(s*.24,s*.60),(s*.24,s*.78),(s*.42,s*.78)],color,w)

    elif kind == "play":
        draw.rounded_rectangle((s*.18,s*.18,s*.82,s*.82),radius=int(s*.10),outline=color,width=w)
        draw.polygon([(s*.43,s*.34),(s*.43,s*.66),(s*.68,s*.50)],outline=color)

    elif kind == "edit":
        _line(draw,[(s*.26,s*.72),(s*.34,s*.48),(s*.66,s*.20)],color,w)
        _line(draw,[(s*.37,s*.75),(s*.70,s*.42)],color,w)
        _line(draw,[(s*.24,s*.76),(s*.42,s*.72)],color,w)

    elif kind == "delete":
        draw.rectangle((s*.30,s*.30,s*.70,s*.78),outline=color,width=w)
        _line(draw,[(s*.24,s*.25),(s*.76,s*.25)],color,w)
        _line(draw,[(s*.42,s*.17),(s*.58,s*.17)],color,w)

    elif kind == "star":
        pts=[]
        for i in range(10):
            a=-math.pi/2+i*math.pi/5
            rad=s*.34 if i%2==0 else s*.14
            pts.append((cx+math.cos(a)*rad,cy+math.sin(a)*rad))
        draw.polygon(pts,outline=color)

    elif kind == "quote":
        draw.rounded_rectangle((s*.16,s*.18,s*.84,s*.74),radius=int(s*.10),outline=color,width=w)
        _line(draw,[(s*.34,s*.74),(s*.30,s*.88),(s*.48,s*.74)],color,w)
        draw.ellipse((s*.31,s*.42,s*.38,s*.49),fill=color)
        draw.ellipse((s*.47,s*.42,s*.54,s*.49),fill=color)

    elif kind == "monitor":
        draw.rounded_rectangle((s*.16,s*.18,s*.84,s*.68),radius=int(s*.06),outline=color,width=w)
        _line(draw,[(s*.38,s*.82),(s*.62,s*.82)],color,w)
        _line(draw,[(cx,s*.68),(cx,s*.82)],color,w)

    else:
        draw.ellipse((s*.25,s*.25,s*.75,s*.75),outline=color,width=w)


@lru_cache(maxsize=64)
def get_icon(kind, size=24, color=ACCENT):
    size = int(size)
    img = Image.new("RGBA", (size, size), (0,0,0,0))
    _draw(ImageDraw.Draw(img), kind, size, color)
    return ctk.CTkImage(light_image=img, dark_image=img, size=(size,size))


@lru_cache(maxsize=16)
def get_tk_icon(kind, size=64, color=ACCENT):
    size = int(size)
    img = Image.new("RGBA", (size, size), (0,0,0,0))
    _draw(ImageDraw.Draw(img), kind, size, color)
    return ImageTk.PhotoImage(img)
