import io
import wave
import unittest
from array import array
from unittest.mock import patch
import tempfile
from pathlib import Path
import miniaudio
from audio_player import AudioPlayer, chime_wav


class AudioTests(unittest.TestCase):
    def test_chime_has_sol_then_mi_and_uses_live_volume(self):
        with wave.open(io.BytesIO(chime_wav()), 'rb') as wav:
            self.assertEqual((wav.getnchannels(), wav.getsampwidth(), wav.getframerate()), (2, 2, 44100))
            pcm = array('h', wav.readframes(wav.getnframes()))[::2]
        for offset, frequency in ((.04, 783.990872), (.50, 659.255114)):
            part = pcm[round(offset*44100):round((offset+.1)*44100)]
            crossings = sum(a <= 0 < b for a, b in zip(part, part[1:]))
            self.assertAlmostEqual(crossings, frequency*.1, delta=2)
        self.assertEqual(pcm[0], 0)
        self.assertEqual(pcm[-1], 0)
        with patch('audio_player.miniaudio.PlaybackDevice', autospec=True):
            player = AudioPlayer()
            player.play_chime()
            self.assertTrue(any(player.stream.send(2205)))
            player.set_volume(0)
            self.assertTrue(all(sample == 0 for sample in player.stream.send(2205)))
            player.stop()

    def test_preview_with_real_decoder_and_supported_device_api(self):
        data = io.BytesIO()
        with wave.open(data, 'wb') as wav:
            wav.setnchannels(2)
            wav.setsampwidth(2)
            wav.setframerate(44100)
            wav.writeframes(array('h', [1000, -1000]*44100).tobytes())
        with tempfile.TemporaryDirectory(dir='.build-temp') as folder:
            path = Path(folder)/'decoder-fixture.mp3'
            # The decoder detects the content; use PCM to test exact gain.
            path.write_bytes(data.getvalue())
            with patch('audio_player.miniaudio.PlaybackDevice', autospec=True) as device:
                player = AudioPlayer()
                player.set_volume(.5)
                player.play(str(path))
                device.assert_called_once_with(buffersize_msec=50, callback_periods=2)
                device.return_value.start.assert_called_once_with(player.stream)
                samples = player.stream.send(2205)
                self.assertEqual(len(samples), 4410)
                self.assertEqual(samples[:2], array('h', [500, -500]))
                player.set_volume(0)
                self.assertTrue(all(sample == 0 for sample in player.stream.send(2205)))
                player.stop()
                device.return_value.close.assert_called_once()

    def test_half_second_buffer_is_supported(self):
        data = io.BytesIO()
        with wave.open(data, 'wb') as wav:
            wav.setnchannels(2)
            wav.setsampwidth(2)
            wav.setframerate(44100)
            wav.writeframes(b'\0' * 44100 * 4)
        stream = miniaudio.stream_memory(data.getvalue(), frames_to_read=32768)
        self.assertEqual(len(stream.send(22050)), 44100)
        stream.close()

    def test_missing_file_and_idle_stop(self):
        player = AudioPlayer()
        with self.assertRaises(ValueError):
            player.play('does-not-exist.mp3')
        player.stop()


if __name__ == '__main__':
    unittest.main()
