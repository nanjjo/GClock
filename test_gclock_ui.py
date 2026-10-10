import tkinter as tk
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from gclock import GClock
from pathlib import Path


class InteractionTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.callback_errors = []
        self.root.report_callback_exception = lambda *error: self.callback_errors.append(error)
        self.app = GClock(self.root, settings_path=False)
        self.root.update()

    def tearDown(self):
        self.app.close()
        self.assertEqual(self.callback_errors, [])

    def test_compact_body_and_volume_fill(self):
        bottom = self.app.time_label.winfo_y()+self.app.time_label.winfo_height()
        self.assertAlmostEqual(self.app.canvas.winfo_height(), bottom, delta=2)
        bar = self.app.volume_slider
        self.app.volume.set(40)
        self.root.update()
        self.assertAlmostEqual(bar.coords('filled')[2], bar.winfo_width()*.4, delta=1)
        self.assertFalse(any(bar.type(item) == 'text' for item in bar.find_all()))
        for widget in (self.app.audio_title, self.app.mute_button):
            self.assertAlmostEqual(widget.winfo_y()+widget.winfo_height()/2,
                                   bar.winfo_y()+bar.winfo_height()/2, delta=1)
        self.assertEqual(self.app.path_entry.winfo_height(), self.app.browse_button.winfo_height())
        self.assertEqual(self.app.heading.winfo_rooty(), self.root.winfo_rooty())
        self.assertEqual(self.app.heading.winfo_rootx(), self.app.path_entry.winfo_rootx())
        self.assertEqual(self.app.audio_title.winfo_rootx(), self.app.path_entry.winfo_rootx())
        right = self.app.browse_button.winfo_rootx()+self.app.browse_button.winfo_width()
        self.assertEqual(bar.winfo_rootx()+bar.winfo_width(), right)
        options = self.app.heading.master.pack_slaves()[1]
        last_color = options.pack_slaves()[-1]
        self.assertEqual(last_color.winfo_rootx()+last_color.winfo_width(), right)
        bar.pointer(SimpleNamespace(x=bar.winfo_width()*.6))
        self.assertEqual(self.app.volume.get(), 60)
        self.assertAlmostEqual(self.app.audio.volume, .6)

    def test_browse_keeps_timer_and_wheel_over_other_controls_is_ignored(self):
        self.app.select(30)
        self.app.state.start()
        deadline = self.app.state.deadline
        self.app.canvas.focus_force()
        self.root.update()
        with patch('gclock.filedialog.askopenfilename', return_value='C:/music/alarm.mp3'):
            self.app.browse_mp3()
        self.root.update()
        self.assertEqual(self.app.state.selected, 1800)
        self.assertEqual(self.app.state.deadline, deadline)
        self.app.canvas.focus_force()
        self.root.update()
        self.app.wheel(SimpleNamespace(delta=120, widget=self.app.volume_slider))
        self.assertEqual(self.app.state.selected, 1800)
        self.app.shortcut(SimpleNamespace(widget=self.app.path_entry), self.app.reset)
        self.assertEqual(self.app.state.deadline, deadline)

    def test_preview_relative_path_uses_settings_folder(self):
        self.app.settings.path = Path('dist/settings.json').resolve()
        self.app.mp3_path.set('music/alarm.mp3')
        self.app.audio = Mock()
        self.app.preview_audio()
        self.app.audio.play.assert_called_once_with(str(self.app.settings.path.parent/'music/alarm.mp3'))
        self.app.settings.path = None

    def test_resize_scales_dial(self):
        small = self.app.geometry()[2]
        self.root.geometry('800x1000')
        self.root.update()
        large = self.app.geometry()[2]
        self.assertGreater(large, small)
        x, y, radius = self.app.geometry()
        self.assertAlmostEqual(self.app.slider.winfo_height(), 2*radius, delta=2)
        self.assertAlmostEqual(self.app.slider.winfo_y(), y-radius, delta=2)
        self.assertAlmostEqual(self.app.slider.winfo_x()+self.app.slider.winfo_width(), x-radius-self.app.dial_gap, delta=2)
        gap = self.app.presets.winfo_reqwidth() / 5
        self.assertAlmostEqual(self.app.presets.winfo_x(), x+radius+gap, delta=2)
        self.assertAlmostEqual(self.app.time_label.winfo_y(), y+radius+gap, delta=2)
        self.root.geometry('400x650')
        self.root.update()
        self.assertLess(self.app.geometry()[2], large)
        self.assertTrue(self.app.play.winfo_ismapped())

    def test_mp3_completion_and_mute(self):
        self.app.audio = Mock()
        self.app.mp3_path.set('C:/music/alarm.mp3')
        self.app.state.set_minutes(1)
        self.app.state.deadline = self.app.state.clock() - 1
        self.app.tick()
        self.app.audio.play.assert_called_once_with(str(Path('C:/music/alarm.mp3')))
        self.app.audio.reset_mock()
        self.app.muted.set(True)
        self.app.state.deadline = self.app.state.clock() - 1
        self.app.tick()
        self.app.audio.play.assert_not_called()

    def test_mp3_failure_falls_back_to_alert(self):
        self.app.audio = Mock()
        self.app.audio.play.side_effect = ValueError('missing file')
        self.app.mp3_path.set('missing.mp3')
        self.app.state.deadline = self.app.state.clock() - 1
        with patch('gclock.winsound.PlaySound') as alert:
            self.app.tick()
            alert.assert_called_once()
        self.assertIn('MP3 재생 실패', self.app.status.cget('text'))

    def test_wheel_focus_limits_and_partial_deltas(self):
        self.app.canvas.focus_force()
        self.root.update()
        self.app.select(25)
        self.app.wheel(SimpleNamespace(delta=60))
        self.assertEqual(self.app.state.selected, 1500)
        self.app.wheel(SimpleNamespace(delta=60))
        self.assertEqual(self.app.state.selected, 1560)
        self.app.wheel(SimpleNamespace(delta=-120))
        self.assertEqual(self.app.state.selected, 1500)
        self.app.select(60)
        self.app.wheel(SimpleNamespace(delta=120))
        self.assertEqual(self.app.state.selected, 3600)
        self.app.select(0)
        self.app.wheel(SimpleNamespace(delta=-120))
        self.assertEqual(self.app.state.selected, 0)
        self.app.slider.focus_force()
        self.root.update()
        self.app.wheel(SimpleNamespace(delta=120))
        self.assertEqual(self.app.state.selected, 0)


if __name__ == '__main__':
    unittest.main()
