import tkinter as tk
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from gclock import GClock
from pathlib import Path
from tkinter import font as tkfont


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

    def test_language_switch_preserves_running_timer_and_audio(self):
        self.assertEqual(self.app.language, 'ko')
        self.app.show_audio_settings()
        self.root.update()
        self.app.select(30)
        self.app.toggle()
        deadline = self.app.state.deadline
        self.app.audio = Mock()
        self.app.language_choice.set('English')
        self.app.language_combo.event_generate('<<ComboboxSelected>>')
        self.root.update()
        self.assertEqual(self.app.language, 'en')
        self.assertEqual(self.app.play.cget('text'), 'Pause')
        self.assertEqual(self.app.browse_button.cget('text'), 'Browse')
        self.assertEqual(self.app.mute_button.cget('text'), 'Mute')
        self.assertIn('Visual Timer', self.root.title())
        self.assertEqual(self.app.state.selected, 1800)
        self.assertEqual(self.app.state.deadline, deadline)
        self.app.audio.play.assert_not_called()
        self.app.audio.stop.assert_not_called()
        self.assertLess(self.app.language_combo.winfo_rootx(), self.app.topmost_button.winfo_rootx())
        self.assertEqual(self.app.path_entry.winfo_height(), self.app.browse_button.winfo_height())
        font = tkfont.Font(root=self.root, font=self.app.path_entry.cget('font'))
        original = tkfont.nametofont('TkTextFont', root=self.root)
        self.assertEqual(font.actual('size'), original.actual('size')*2)
        self.app.language_choice.set('한국어')
        self.app.change_language()
        self.root.update()
        self.assertEqual(self.app.play.cget('text'), '일시정지')
        self.assertEqual(self.app.state.deadline, deadline)

    def test_english_dialog_and_completion_strings(self):
        self.app.language_choice.set('English')
        self.app.change_language()
        self.root.update()
        with patch('gclock.filedialog.askopenfilename', return_value='') as dialog:
            self.app.browse_mp3()
        self.assertEqual(dialog.call_args.kwargs['title'], 'Choose MP3 alarm')
        self.app.audio = Mock()
        self.app.audio.play.side_effect = ValueError('존재하는 MP3 파일의 경로를 입력하세요.')
        with patch('gclock.messagebox.showerror') as error:
            self.app.preview_audio()
        self.assertEqual(error.call_args.args, ('MP3 playback failed', 'Enter the path to an existing MP3 file.'))
        self.app.muted.set(True)
        self.app.state.deadline = self.app.state.clock()-1
        self.app.tick()
        self.assertEqual(self.app.status.cget('text'), 'Time is up! Take a short break.')

    def test_compact_body_and_volume_fill(self):
        bottom = self.app.time_label.winfo_y()+self.app.time_label.winfo_height()
        self.assertAlmostEqual(self.app.canvas.winfo_height(), bottom, delta=2)
        self.app.show_audio_settings()
        self.root.update()
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
        self.assertEqual(self.app.audio_title.winfo_rootx(), self.app.path_entry.winfo_rootx())
        right = self.app.browse_button.winfo_rootx()+self.app.browse_button.winfo_width()
        self.assertEqual(bar.winfo_rootx()+bar.winfo_width(), right)
        bar.pointer(SimpleNamespace(x=bar.winfo_width()*.6))
        self.assertEqual(self.app.volume.get(), 60)
        self.assertAlmostEqual(self.app.audio.volume, .6)

    def test_browse_keeps_timer_and_wheel_over_other_controls_is_ignored(self):
        self.app.show_audio_settings()
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

    def test_audio_settings_hidden_reused_and_non_modal(self):
        self.assertEqual(self.app.audio_dialog.state(), 'withdrawn')
        self.assertFalse(self.app.path_entry.winfo_ismapped())
        self.assertTrue(self.app.settings_button.winfo_ismapped())
        self.app.select(10)
        self.app.toggle()
        deadline = self.app.state.deadline
        dialog = self.app.audio_dialog
        self.app.audio = Mock()
        for _ in range(3):
            self.app.settings_button.invoke()
            self.root.update()
            self.assertIs(self.app.audio_dialog, dialog)
            self.assertTrue(self.app.path_entry.winfo_ismapped())
            self.assertIsNone(self.root.grab_current())
            self.app.mp3_path.set('C:/music/alarm.mp3')
            self.app.volume.set(42)
            self.app.hide_audio_settings()
            self.root.update()
            self.assertEqual(dialog.state(), 'withdrawn')
            self.assertEqual(self.app.state.deadline, deadline)
            self.assertEqual(self.app.volume.get(), 42)
        self.assertEqual(len([w for w in self.root.winfo_children() if isinstance(w, tk.Toplevel)]), 1)

    def test_muted_completion_animates_until_acknowledged_and_can_restart(self):
        self.app.audio = Mock()
        self.app.muted.set(True)
        self.app.select(10)
        self.app.state.deadline = self.app.state.clock()-1
        self.app.tick()
        self.app.audio.play.assert_not_called()
        self.assertEqual(self.app.time_label.cget('text'), '00:00')
        self.assertEqual(self.app.reset_button.cget('text'), '확인')
        self.assertEqual(len(self.app.canvas.find_withtag('completion')), 3)
        first = self.app.canvas.coords('wave0')
        with patch('gclock.time.monotonic', return_value=self.app.completion_started + .6):
            self.app.draw_completion()
        self.assertNotEqual(self.app.canvas.coords('wave0'), first)
        image = self.app.dial_image
        self.app.tick()
        self.assertIs(self.app.dial_image, image)
        self.assertEqual(len(self.app.canvas.find_withtag('completion')), 3)
        self.app.language_choice.set('English')
        self.app.change_language()
        self.root.update()
        self.assertEqual(self.app.play.cget('text'), 'Restart')
        self.root.geometry('700x800')
        self.root.update()
        x, y, radius = self.app.geometry()
        for item in self.app.canvas.find_withtag('completion'):
            left, top, right, bottom = self.app.canvas.coords(item)
            self.assertAlmostEqual((left+right)/2, x)
            self.assertAlmostEqual((top+bottom)/2, y)
            self.assertLessEqual((right-left)/2, radius)
        self.app.reset_button.invoke()
        self.assertIsNone(self.app.animation_id)
        self.assertFalse(self.app.canvas.find_withtag('completion'))
        self.assertEqual(self.app.state.remaining, 600)
        self.assertIsNone(self.app.state.deadline)
        self.app.state.deadline = self.app.state.clock()-1
        self.app.tick()
        self.app.play.invoke()
        self.assertIsNone(self.app.completion_started)
        self.assertIsNotNone(self.app.state.deadline)
        self.assertEqual(self.app.state.selected, 600)

    def test_completion_clears_on_new_preset_and_close_cancels_animation(self):
        self.app.muted.set(True)
        self.app.state.deadline = self.app.state.clock()-1
        self.app.tick()
        animation = self.app.animation_id
        self.app.select(30)
        self.assertIsNone(self.app.animation_id)
        self.assertNotIn(animation, self.root.tk.call('after', 'info'))
        self.assertFalse(self.app.canvas.find_withtag('completion'))
        self.app.start_completion()
        self.assertIsNotNone(self.app.animation_id)
        # tearDown closes during an active animation and collects callback errors.

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
