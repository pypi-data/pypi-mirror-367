from html.parser import HTMLParser
import html
import re

HTML_COLOR_MAP = {
    "black": "000000",
    "white": "FFFFFF",
    "red": "FF0000",
    "green": "008000",
    "blue": "0000FF",
    "yellow": "FFFF00",
    "gray": "808080",
    "cyan": "00FFFF",
    "magenta": "FF00FF",
}


def css_color_to_rgb(color):
    color = color.strip().lower()
    if color.startswith("#"):
        hex_val = color.lstrip("#")
        if len(hex_val) == 3:
            hex_val = "".join([c * 2 for c in hex_val])
        return "FF" + hex_val.upper()
    elif color in HTML_COLOR_MAP:
        return "FF" + HTML_COLOR_MAP[color].upper()
    elif color.startswith("rgb("):
        match = re.match(r"rgb\((\d+),\s*(\d+),\s*(\d+)\)", color)
        if match:
            r, g, b = map(int, match.groups())
            return f"FF{r:02X}{g:02X}{b:02X}"
    return None


class RichTextParser(HTMLParser):
    def __init__(self, fontfamily, base_fontsize):
        super().__init__()
        self.runs = []
        self.style_stack = []
        self.current_text = ""
        self.fontfamily = fontfamily
        self.base_fontsize = float(base_fontsize)

    def feed(self, cell_text, cell_style):
        cell_text = cell_text.strip()
        if cell_style.get("font-weight", "") == "bold":
            cell_text = f"<b>{cell_text}</b>"
        if cell_style.get("font-style", "") == "italic":
            cell_text = f"<i>{cell_text}</i>"
        if cell_style.get("text-decoration", "") == "underline":
            cell_text = f"<u>{cell_text}</u>"
        if (color := cell_style.get("color", "")):
            cell_text = f"<font color=#{css_color_to_rgb(color)[2:]}>{cell_text}</font>"
        return super().feed(cell_text)

    def _get_current_style(self):
        return self.style_stack[-1] if self.style_stack else {}

    def _flush_current_text(self):
        if not self.current_text:
            return
        style = self._get_current_style()
        rPr = [f'<rFont val="{self.fontfamily}"/>']
        rPr.append(f'<sz val="{style.get("fontsize", self.base_fontsize)}"/>')
        if style.get("bold"):
            rPr.append("<b/>")
        if style.get("italic"):
            rPr.append("<i/>")
        if style.get("underline"):
            rPr.append("<u/>")
        if style.get("color"):
            rPr.append(f'<color rgb="{style["color"]}"/>')

        self.runs.append(
            "<r>"
            f"<rPr>{''.join(rPr)}</rPr>"
            f'<t xml:space="preserve">{html.escape(self.current_text)}</t>'
            "</r>"
        )
        self.current_text = ""

    def handle_starttag(self, tag, attrs):
        self._flush_current_text()
        style = self._get_current_style().copy()
        tag = tag.lower()

        if tag == "b":
            style["bold"] = True
        elif tag == "i":
            style["italic"] = True
        elif tag == "u":
            style["underline"] = True
        elif tag == "br":
            self._flush_current_text()
            self.runs.append("<br/>")
        elif tag == "font":
            for name, value in attrs:
                if name == "size":
                    try:
                        if value.startswith("+"):
                            style["fontsize"] = str(self.base_fontsize + int(value[1:]))
                        elif value.startswith("-"):
                            style["fontsize"] = str(self.base_fontsize - int(value[1:]))
                        else:
                            style["fontsize"] = value
                    except Exception:
                        pass
                elif name == "color":
                    rgb = css_color_to_rgb(value)
                    if rgb:
                        style["color"] = rgb
        self.style_stack.append(style)

    def handle_endtag(self, tag):
        self._flush_current_text()
        if self.style_stack:
            self.style_stack.pop()

    def handle_data(self, data):
        self.current_text += data

    def handle_entityref(self, name):
        self.current_text += html.unescape(f"&{name};")

    def handle_charref(self, name):
        self.current_text += html.unescape(f"&#{name};")

    def get_runs(self):
        self._flush_current_text()
        return self.runs
