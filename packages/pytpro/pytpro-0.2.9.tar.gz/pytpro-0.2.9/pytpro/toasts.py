import html as html_escape
import time

# Dictionary mapping toast types to (background, text) colors
_TOAST_STYLES = {
    "red":   ("#fdecea", "#b00020"),
    "green": ("#e8f5e9", "#2e7d32"),
    "blue":  ("#e3f2fd", "#1976d2"),
    "black": ("#b5b5b5", "#212121"),
    "pink":  ("#fce4ec", "#c2185b"),
    "white": ("#ffffff", "#4A4A4A"),
    "yellow": ("#fffde7", "#ff9800"),
    "orange": ("#fff3e0", "#f57c00"),
    "purple": ("#f4e1ff", "#954dff"),
    "brown": ("#efebe9", "#795548"),
    "gray":  ("#f9f9f9", "#9e9e9e"),
    "teal":  ("#e0f2f1", "#009688"),
    "lime":  ("#f9fbe7", "#7cb342"),
    "indigo": ("#e8f5e9", "#304ffe"),
    "cyan":  ("#e0f2f1", "#00bcd4"),
    "magenta": ("#fde7e6", "#d50000"),
    "olive": ("#fde7e6", "#8d6e63"),
    "navy":  ("#fde7e6", "#0062cc"),
    "maroon": ("#fde7e6", "#7f0000"),
}

def toast(text, color="white", duration=5):
    """Display a toast message in the given color (disappears after 5 seconds default)."""
    try:
        from .main import write  # adjust import if needed
        safe_text = html_escape.escape(str(text))
        bg_color, text_color = _TOAST_STYLES[color]

        html = f"""
        <div style='
            text-align: center;
            position: fixed;
            top: 2%;
            right: 2%;
            background-color: {bg_color};
            color: {text_color};
            padding-top: 16px;
            padding-bottom: 16px;
            padding-right: 50px;
            padding-left: 50px;
            border-radius: 4px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            font-family: sans-serif;
            z-index: 9999;
            animation: fadeout {duration}s forwards;
        '>
            {safe_text}
        </div>
        <style>
        @keyframes fadeout {{
            0% {{ opacity: 1; }}
            70% {{ opacity: 1; }}
            100% {{ opacity: 0; }}
        }}
        </style>
        """
        write(html)
    except KeyError:
        from main import errorbox
        errorbox("Invalid color. Please choose from the available colors or use py.toast_custom()")
def toast_custom(text, color="white", text_color="black", duration=5):
    """Display a custom HTML toast message in the given color (disappears after 5 seconds default)."""
    from .main import write  # adjust import if needed

    html = f"""
    <div style='
        text-align: center;
        position: fixed;
        top: 2%;
        right: 2%;
        background-color: {color};
        color: {text_color};
        padding-top: 16px;
        padding-bottom: 16px;
        padding-right: 50px;
        padding-left: 50px;
        border-radius: 4px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        font-family: sans-serif;
        z-index: 9999;
        animation: fadeout {duration}s forwards;
    '>
        {text}
    </div>
    <style>
    @keyframes fadeout {{
        0% {{ opacity: 1; }}
        70% {{ opacity: 1; }}
        100% {{ opacity: 0; }}
    }}
    </style>
    """
    write(html)