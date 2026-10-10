import tempfile
from pathlib import Path
import tkinter as tk
import unittest
import os
import sys
from unittest.mock import patch
from gclock import GClock
from settings_store import SettingsStore, validate


class SettingsTests(unittest.TestCase):
    def test_frozen_settings_location_ignores_working_directory(self):
        executable = Path('dist/GClock.exe').resolve()
        original = Path.cwd()
        try:
            with patch.object(sys, 'frozen', True, create=True), patch.object(sys, 'executable', str(executable)):
                os.chdir(self.path.parent)
                self.assertEqual(SettingsStore().path, executable.parent/'settings.json')
        finally:
            os.chdir(original)

    def setUp(self):
        Path('.build-temp').mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir='.build-temp')
        self.path = Path(self.temp.name) / 'settings.json'

    def tearDown(self):
        self.temp.cleanup()

    def test_roundtrip_unicode_and_atomic_file(self):
        store = SettingsStore(self.path)
        data = dict(selected_seconds=1800, muted=True, topmost=False,
                    color='#3d8769', mp3_path='C:/음악/노래.mp3')
        store.save(data)
        self.assertEqual(store.load(), data)
        self.assertEqual(list(self.path.parent.glob('*.tmp')), [])

    def test_corrupt_and_invalid_values_fall_back(self):
        self.path.write_text('{broken', encoding='utf-8')
        self.assertEqual(SettingsStore(self.path).load(), {})
        self.assertEqual(validate(dict(selected_seconds=99999, muted='true', color='invalid', window=[])), {})

    def test_restart_restores_preferences_without_starting_timer(self):
        root = tk.Tk()
        app = GClock(root, settings_path=self.path)
        root.update()
        app.select(50)
        app.change_color('#447db0')
        app.mp3_path.set('C:/음악/노래.mp3')
        app.muted.set(True)
        app.topmost.set(True)
        app.volume.set(37)
        app.state.start()
        app.close()
        root = tk.Tk()
        app = GClock(root, settings_path=self.path)
        try:
            root.update()
            self.assertEqual(app.state.selected, 3000)
            self.assertEqual(app.state.remaining, 3000)
            self.assertIsNone(app.state.deadline)
            self.assertEqual(app.color, '#447db0')
            self.assertTrue(app.muted.get())
            self.assertTrue(app.topmost.get())
            self.assertEqual(app.volume.get(), 37)
            self.assertAlmostEqual(app.audio.volume, .37)
            self.assertEqual(app.mp3_path.get(), 'C:/음악/노래.mp3')
        finally:
            app.close()


if __name__ == '__main__':
    unittest.main()
