import unittest
from unittest.mock import patch
import tkinter as tk
from dial_renderer import DialRenderer
from gclock import GClock


class DisplayTests(unittest.TestCase):
    def test_dial_is_rendered_at_requested_resolution(self):
        renderer = DialRenderer()
        for pixels in (300, 600, 1200):
            image = renderer.render(pixels, '#df4a42', 900)
            self.assertEqual(image.size, (pixels, pixels))
            # 15-minute sector occupies the upper-left quarter.
            left = image.getpixel((int(pixels*.35), int(pixels*.35)))
            right = image.getpixel((int(pixels*.65), int(pixels*.35)))
            self.assertEqual(left[:3], (223, 74, 66))
            self.assertEqual(right[:3], (238, 238, 232))

    def test_100_150_200_percent_layout(self):
        for dpi in (96, 144, 192):
            with self.subTest(dpi=dpi), patch('gclock.system_dpi', return_value=dpi):
                root = tk.Tk()
                app = GClock(root, settings_path=False)
                try:
                    root.update()
                    self.assertEqual(app.slider.cget('width'), round(30*dpi/96))
                    self.assertGreater(app.dial_image.width(), 100)
                    self.assertAlmostEqual(float(root.tk.call('tk', 'scaling')), dpi/72, delta=.02)
                    self.assertTrue(app.play.winfo_ismapped())
                    app.language_choice.set('English')
                    app.change_language()
                    root.update()
                    self.assertEqual(app.heading.winfo_width(), app.heading.winfo_reqwidth())
                    self.assertLessEqual(app.heading.winfo_rootx()+app.heading.winfo_width(),
                                         app.language_combo.winfo_rootx())
                    self.assertEqual(app.path_entry.winfo_height(), app.browse_button.winfo_height())
                finally:
                    app.close()


if __name__ == '__main__':
    unittest.main()
