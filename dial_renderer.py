"""Antialiased dial at the current physical pixel size; no upscaled bitmap."""
import math
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


class DialRenderer:
    def __init__(self):
        self.key = None
        self.base = None
        self.overlay = None

    def render(self, diameter, color, remaining):
        diameter = max(2, int(diameter))
        scale = 2
        side = diameter * scale
        radius = side / 2
        center = (radius, radius)
        if self.key != (diameter, color):
            self.key = (diameter, color)
            self.base = Image.new('RGBA', (side, side), color)
            draw = ImageDraw.Draw(self.base)
            r = radius * .94
            draw.ellipse((radius-r, radius-r, radius+r, radius+r), fill='#fcfcf8')
            self.overlay = Image.new('RGBA', (side, side))
            ink = ImageDraw.Draw(self.overlay)
            font_path = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts/arialbd.ttf'
            size = max(8 * scale, round(radius * .10))
            try:
                font = ImageFont.truetype(str(font_path), size)
            except OSError:
                font = ImageFont.load_default(size=size)
            for minute in range(60):
                angle = -math.pi/2 - minute*math.tau/60
                major = minute % 5 == 0
                def point(factor):
                    return (center[0]+math.cos(angle)*radius*factor,
                            center[1]+math.sin(angle)*radius*factor)
                ink.line((point(.71), point(.78 if major else .75)), fill='#414943',
                         width=max(scale, round(radius*(.012 if major else .006))))
                if major:
                    ink.text(point(.86), str(minute), font=font, fill='#343d37', anchor='mm')
            knob = radius * .115
            ink.ellipse((radius-knob, radius-knob, radius+knob, radius+knob),
                        fill='#e3e7dc', outline='#ccd1c7', width=2*scale)
        image = self.base.copy()
        draw = ImageDraw.Draw(image)
        disk = radius * .68
        box = (radius-disk, radius-disk, radius+disk, radius+disk)
        draw.ellipse(box, fill='#eeeee8')
        extent = max(0, min(360, remaining/3600*360))
        if extent >= 359.999:
            draw.ellipse(box, fill=color)
        elif extent > 0:
            draw.pieslice(box, 270-extent, 270, fill=color)
        image = Image.alpha_composite(image, self.overlay)
        return image.resize((diameter, diameter), Image.Resampling.LANCZOS)
