import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from gclock import TimerState, smoke_main


class TimerTests(unittest.TestCase):
    def test_smoke_failure_returns_nonzero_and_preserves_diagnostic_report(self):
        with tempfile.TemporaryDirectory(dir='.build-temp') as folder:
            report = Path(folder) / 'smoke.json'
            with patch('gclock.tk.Tk'), patch('gclock.run_smoke_test', side_effect=AssertionError('dialog mapping')):
                self.assertEqual(smoke_main(report), 1)
            result = json.loads(report.read_text(encoding='utf-8'))
            self.assertFalse(result['ok'])
            self.assertIn('AssertionError: dialog mapping', result['error'])

    def test_delayed_completion_once(self):
        now = [0.0]
        timer = TimerState(lambda: now[0])
        timer.set_minutes(1)
        timer.start()
        now[0] = 47
        self.assertFalse(timer.tick())
        self.assertEqual(timer.remaining, 13)
        now[0] = 90
        self.assertTrue(timer.tick())
        self.assertFalse(timer.tick())

    def test_pause_resume_reset(self):
        now = [0.0]
        timer = TimerState(lambda: now[0])
        timer.start()
        now[0] = 300
        timer.pause()
        now[0] = 900
        timer.start()
        now[0] = 1020
        timer.tick()
        self.assertEqual(timer.remaining, 1080)
        timer.reset()
        self.assertEqual(timer.remaining, 1500)
        timer.set_minutes(90)
        self.assertEqual(timer.remaining, 3600)


if __name__ == '__main__':
    unittest.main()
