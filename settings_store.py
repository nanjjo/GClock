"""Validated settings beside the executable, independent of working directory."""
import json
import os
import tempfile
import sys
from pathlib import Path

COLORS = ['#df4a42', '#3d8769', '#447db0']


def validate(data):
    result = {}
    if not isinstance(data, dict):
        return result
    if type(data.get('layout_version')) is int and data['layout_version'] in (1, 2, 3, 4):
        result['layout_version'] = data['layout_version']
    seconds = data.get('selected_seconds')
    volume = data.get('volume_percent')
    if type(volume) is int and 0 <= volume <= 100:
        result['volume_percent'] = volume
    if type(seconds) is int and 0 <= seconds <= 3600:
        result['selected_seconds'] = seconds
    for name in ('muted', 'topmost', 'maximized'):
        if type(data.get(name)) is bool:
            result[name] = data[name]
    if data.get('color') in COLORS:
        result['color'] = data['color']
    if isinstance(data.get('mp3_path'), str) and len(data['mp3_path']) <= 32768:
        result['mp3_path'] = data['mp3_path']
    window = data.get('window')
    if isinstance(window, dict) and all(type(window.get(k)) is int for k in ('width', 'height', 'x', 'y')):
        if 440 <= window['width'] <= 8000 and 650 <= window['height'] <= 8000 and all(abs(window[k]) <= 100000 for k in ('x', 'y')):
            result['window'] = dict(window)
    return result


class SettingsStore:
    def __init__(self, path=None):
        base = Path(sys.executable).resolve().parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent
        self.path = None if path is False else Path(path).resolve() if path is not None else base / 'settings.json'

    def load(self):
        if self.path is None:
            return {}
        try:
            return validate(json.loads(self.path.read_text(encoding='utf-8')))
        except (OSError, ValueError):
            return {}

    def save(self, data):
        if self.path is None:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=self.path.parent,
                                             suffix='.tmp', delete=False) as file:
                temp_path = Path(file.name)
                json.dump(validate(data), file, ensure_ascii=False, indent=2)
            os.replace(temp_path, self.path)
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
