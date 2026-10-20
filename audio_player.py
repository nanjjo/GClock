"""Buffered MP3 playback using the MIT-licensed miniaudio engine."""
from pathlib import Path
from array import array
from functools import lru_cache
import io
import math
import wave
import miniaudio


@lru_cache(maxsize=1)
def chime_wav():
    """Original bell-like G5/E5 chime, stereo signed16 at 44100 Hz."""
    rate = 44100
    samples = array('h')
    for frequency, duration in ((783.990872, .42), (659.255114, .65)):
        count = round(rate * duration)
        for frame in range(count):
            t = frame / rate
            envelope = min(1, t/.008) * min(1, (count-1-frame)/(rate*.015)) * math.exp(-5*t/duration)
            angle = math.tau * frequency * t
            tone = .78*math.sin(angle) + .16*math.sin(2*angle) + .06*math.sin(3*angle)
            sample = round(24000 * envelope * tone)
            samples.extend((sample, sample))
        samples.extend([0] * (round(rate*.04)*2))
    output = io.BytesIO()
    with wave.open(output, 'wb') as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(samples.tobytes())
    return output.getvalue()


class AudioPlayer:
    def __init__(self):
        self.device = None
        self.stream = None
        self.volume = 1.0

    def set_volume(self, value):
        self.volume = max(0.0, min(1.0, float(value)))

    def volume_stream(self, source):
        try:
            frames = yield b''
            while True:
                try:
                    samples = source.send(frames)
                except StopIteration:
                    return
                volume = self.volume
                if volume != 1.0:
                    samples = array('h', (round(sample * volume) for sample in samples))
                frames = yield samples
        finally:
            source.close()

    def play(self, path):
        file = Path(path.strip().strip('"')).expanduser().resolve()
        if file.suffix.lower() != '.mp3' or not file.is_file():
            raise ValueError('존재하는 MP3 파일의 경로를 입력하세요.')
        self.play_data(file.read_bytes())

    def play_chime(self):
        self.play_data(chime_wav())

    def play_data(self, data):
        self.stop()
        try:
            # Keep compressed bytes in memory; no repeated disk access or
            # Windows codec dependency in the audio callback.
            source = miniaudio.stream_memory(data, frames_to_read=32768)
            self.stream = self.volume_stream(source)
            next(self.stream)
            # Two 50 ms periods target about 100 ms of queued audio.
            self.device = miniaudio.PlaybackDevice(buffersize_msec=50, callback_periods=2)
            self.device.start(self.stream)
        except (miniaudio.DecodeError, miniaudio.MiniaudioError) as error:
            self.stop()
            raise RuntimeError(f'MP3 재생 오류: {error}') from error

    def stop(self):
        if self.device is not None:
            self.device.close()
            self.device = None
        if self.stream is not None:
            self.stream.close()
            self.stream = None
