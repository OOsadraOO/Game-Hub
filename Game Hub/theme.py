from config import RGB_COLORS

rgb_index = 0

def animate_rgb(app):
    global rgb_index
    color = RGB_COLORS[rgb_index]
    app.sidebar.configure(border_color=color)
    rgb_index += 1
    if rgb_index >= len(RGB_COLORS):
        rgb_index = 0
    app.after(700, lambda: animate_rgb(app))

def apply_theme(widget, theme):
    widget.configure(fg_color=theme["bg"])
