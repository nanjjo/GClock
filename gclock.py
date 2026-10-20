"""Windows visual timer with buffered miniaudio playback."""
import math
import time
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from audio_player import AudioPlayer
import sys
from PIL import ImageTk
from dial_renderer import DialRenderer
from display_support import enable_dpi_awareness, system_dpi
from settings_store import SettingsStore
import ctypes
from tkinter import font as tkfont
from pathlib import Path
from volume_control import VolumeBar
from translations import TEXT

VERSION = '2.3'


class TimerState:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.selected = 1500
        self.remaining = 1500.0
        self.deadline = None

    def set_minutes(self, minutes):
        self.selected = round(max(0, min(60, minutes)) * 60)
        self.reset()

    def start(self):
        if self.deadline is None and self.remaining > 0:
            self.deadline = self.clock() + self.remaining

    def tick(self):
        if self.deadline is None:
            return False
        self.remaining = max(0, self.deadline - self.clock())
        if self.remaining == 0:
            self.deadline = None
            return True
        return False

    def pause(self):
        self.tick()
        self.deadline = None

    def reset(self):
        self.remaining = float(self.selected)
        self.deadline = None


class GClock:
    COLORS = ['#df4a42', '#3d8769', '#447db0']

    def __init__(self, root, settings_path=None):
        self.root = root
        self.settings = SettingsStore(settings_path)
        saved = self.settings.load()
        self.language = saved.get('language', 'ko')
        self.status_key = 'intro'
        self.status_detail = ''
        self.save_id = None
        self.layout_id = None
        self.completion_started = None
        self.animation_id = None
        self.normal_window = saved.get('window')
        dpi = system_dpi()
        self.display_scale = dpi / 96
        self.dial_gap = round(8*self.display_scale)
        root.tk.call('tk', 'scaling', dpi / 72)
        self.renderer = DialRenderer()
        self.dial_image = None
        self.state = TimerState()
        self.state.set_minutes(saved.get('selected_seconds', 1500) / 60)
        self.color = saved.get('color', self.COLORS[0])
        self.muted = tk.BooleanVar(value=saved.get('muted', False))
        self.topmost = tk.BooleanVar(value=saved.get('topmost', False))
        self.wheel_remainder = 0
        self.audio = AudioPlayer()
        self.volume = tk.IntVar(value=saved.get('volume_percent', 100))
        self.audio.set_volume(self.volume.get()/100)
        self.mp3_path = tk.StringVar(value=saved.get('mp3_path', ''))
        self.last_drawing = None
        self.last_layout = None
        root.title(f'GClock · 시각 타이머 · v{VERSION}')
        root.geometry(f'{round(512*self.display_scale)}x{round(560*self.display_scale)}')
        root.minsize(round(440*self.display_scale), round(500*self.display_scale))
        if self.normal_window:
            window = self.normal_window
            if saved.get('layout_version', 1) < 2:
                # Enlarge the former default once; subsequent user resizes persist.
                window = dict(window, width=max(520, window['width']), height=max(720, window['height']))
            if saved.get('layout_version', 1) < 3:
                # Keep the dial size when adding 20 px to each side margin.
                window = dict(window, width=min(8000, window['width']+40))
            if saved.get('layout_version', 1) < 4:
                window = dict(window, width=max(440, window['width']-48),
                              height=max(650, window['height']-16))
            width = round(window['width']*self.display_scale)
            if saved.get('layout_version', 1) < 5:
                window = dict(window, height=max(500, window['height']-144))
            height = round(window['height']*self.display_scale)
            x, y = window['x'], window['y']
            # Restore only if part of the caption can still be reached.
            user32 = ctypes.windll.user32
            vx, vy = user32.GetSystemMetrics(76), user32.GetSystemMetrics(77)
            vw, vh = user32.GetSystemMetrics(78), user32.GetSystemMetrics(79)
            if x+width > vx+80 and x < vx+vw-80 and vy <= y < vy+vh-40:
                root.geometry(f'{width}x{height}{x:+d}{y:+d}')
        root.attributes('-topmost', self.topmost.get())
        root.protocol('WM_DELETE_WINDOW', self.close)
        root.configure(bg='#f5f3ed')
        style = ttk.Style(root)
        style.theme_use('clam')
        style.configure('TFrame', background='#f5f3ed')
        style.configure('TLabel', background='#f5f3ed', font=('맑은 고딕', 11))
        style.configure('TButton', font=('맑은 고딕', 11), padding=round(8*self.display_scale))
        style.configure('TCheckbutton', background='#f5f3ed', font=('맑은 고딕', 11))
        main = ttk.Frame(root, padding=(round(6*self.display_scale), 0,
                                        round(6*self.display_scale), round(4*self.display_scale)))
        self.main = main
        main.pack(fill='both', expand=True)
        header = ttk.Frame(main)
        header.pack(fill='x')
        self.heading = ttk.Label(header, text='GClock', font=('맑은 고딕', 23, 'bold'))
        self.heading.pack(side='left')
        options = ttk.Frame(header)
        options.pack(side='right')
        self.language_choice = tk.StringVar(value='한국어' if self.language == 'ko' else 'English')
        self.language_combo = ttk.Combobox(options, state='readonly', width=7,
                                          textvariable=self.language_choice, values=('한국어', 'English'),
                                          font=('맑은 고딕', 11))
        self.language_combo.pack(side='left', padx=(0, 4))
        self.language_combo.bind('<<ComboboxSelected>>', self.change_language)
        self.topmost_button = ttk.Checkbutton(options, variable=self.topmost,
                        command=self.topmost_changed)
        self.topmost_button.pack(side='left', padx=6)
        for index, color in enumerate(self.COLORS):
            tk.Button(options, bg=color, activebackground=color, width=2,
                      relief='flat', command=lambda c=color: self.change_color(c)).pack(
                          side='left', padx=(4, 0 if index == len(self.COLORS)-1 else 4))
        self.status = ttk.Label(main, text='당신의 시간을 가볍게')
        self.status.pack(pady=(8, tkfont.Font(root=root, font=('맑은 고딕', 11)).metrics('linespace')))
        dial_row = ttk.Frame(main)
        self.dial_row = dial_row
        dial_row.pack(fill='x')
        self.canvas = tk.Canvas(dial_row, width=1, height=1, background='#f5f3ed',
                                highlightthickness=0, takefocus=True)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.bind('<Configure>', lambda _: self.resize_dial())
        self.canvas.bind('<Button-1>', self.pointer)
        self.canvas.bind('<B1-Motion>', self.pointer)
        root.bind('<MouseWheel>', self.wheel)
        self.time_label = ttk.Label(dial_row, font=('Consolas', 36))
        self.guide = ttk.Label(main)
        self.guide.pack()
        self.slider = tk.Scale(dial_row, from_=60, to=0, orient='vertical',
                               resolution=1, bg='#f5f3ed', highlightthickness=0,
                               width=round(30*self.display_scale), font=('맑은 고딕', 14),
                               command=self.from_slider)
        self.slider.set(self.state.selected/60)
        self.presets = ttk.Frame(dial_row)
        self.preset_buttons = []
        for minutes in [10, 30, 50]:
            button = ttk.Button(self.presets, width=4, command=lambda m=minutes: self.select(m))
            button.pack(pady=6)
            self.preset_buttons.append((minutes, button))
        controls = ttk.Frame(main)
        controls.pack(pady=12)
        self.reset_button = ttk.Button(controls, command=self.reset)
        self.reset_button.pack(side='left', padx=6)
        self.play = ttk.Button(controls, text='시작', command=self.toggle)
        self.play.pack(side='left', padx=6)
        self.settings_button = ttk.Button(controls, command=self.show_audio_settings)
        self.settings_button.pack(side='left', padx=6)
        # Keep one non-modal dialog so variables/traces are never duplicated.
        self.audio_dialog = tk.Toplevel(root)
        self.audio_dialog.withdraw()
        self.audio_dialog.transient(root)
        self.audio_dialog.configure(bg='#f5f3ed')
        self.audio_dialog.geometry(f'{round(640*self.display_scale)}x{round(200*self.display_scale)}')
        self.audio_dialog.minsize(round(540*self.display_scale), round(200*self.display_scale))
        self.audio_dialog.protocol('WM_DELETE_WINDOW', self.hide_audio_settings)
        self.audio_dialog.bind('<Escape>', lambda _: self.hide_audio_settings())
        audio_panel = ttk.Frame(self.audio_dialog, padding=round(12*self.display_scale))
        audio_panel.pack(fill='both', expand=True)
        audio_heading = ttk.Frame(audio_panel)
        audio_heading.pack(fill='x', pady=(12, 4))
        self.audio_title = ttk.Label(audio_heading, text='종료 시 재생할 MP3')
        self.audio_title.pack(side='left', anchor='center')
        self.mute_button = ttk.Checkbutton(audio_heading, text='무음', variable=self.muted,
                                          command=self.mute_changed)
        self.volume_slider = VolumeBar(audio_heading, self.volume, self.volume_changed,
                                        scale=self.display_scale)
        self.volume_slider.pack(side='right', anchor='center', padx=(round(10*self.display_scale), 0))
        self.mute_button.pack(side='right', anchor='center', padx=(8, 0))
        audio_row = ttk.Frame(audio_panel)
        audio_row.pack(fill='x')
        self.path_entry = ttk.Entry(audio_row, textvariable=self.mp3_path)
        original_font = tkfont.Font(root=root, font=self.path_entry.cget('font'))
        self.path_entry.configure(font=('맑은 고딕', abs(original_font.actual('size'))*2))
        self.path_entry.pack(side='left', fill='both', expand=True)
        self.browse_button = ttk.Button(audio_row, text='찾기', width=4, command=self.browse_mp3)
        self.browse_button.pack(side='left', padx=(6, 0))
        audio_controls = ttk.Frame(audio_panel)
        audio_controls.pack(pady=(6, 0))
        self.preview_button = ttk.Button(audio_controls, command=self.preview_audio)
        self.preview_button.pack(side='left', padx=4)
        self.stop_button = ttk.Button(audio_controls, command=self.stop_audio)
        self.stop_button.pack(side='left', padx=4)
        self.dialog_close_button = ttk.Button(audio_controls, command=self.hide_audio_settings)
        self.dialog_close_button.pack(side='left', padx=4)
        root.bind('<space>', lambda e: self.shortcut(e, self.toggle))
        root.bind('<Escape>', lambda e: self.shortcut(e, self.reset))
        self.apply_language()
        self.tick_id = root.after(100, self.tick)
        for variable in (self.muted, self.topmost, self.mp3_path):
            variable.trace_add('write', lambda *_: self.queue_save())
        root.bind('<Configure>', self.window_changed, add='+')
        if saved.get('maximized'):
            root.state('zoomed')

    def tr(self, key, **values):
        return TEXT[self.language][key].format(**values)

    def set_status(self, key, detail=''):
        self.status_key, self.status_detail = key, detail
        text = self.tr(key)
        if detail:
            text += ': ' + self.error_text(detail)
        self.status.config(text=text)

    def error_text(self, error):
        text = str(error)
        for key in ('invalid_mp3', 'decode_error'):
            text = text.replace(TEXT['ko'][key], self.tr(key))
        return text

    def apply_language(self):
        self.root.title(f'GClock · {self.tr("title")} · v{VERSION}')
        for widget, key in ((self.topmost_button, 'topmost'), (self.guide, 'guide'),
                            (self.reset_button, 'reset'), (self.audio_title, 'audio_title'),
                            (self.settings_button, 'audio_settings'), (self.dialog_close_button, 'close'),
                            (self.mute_button, 'mute'), (self.browse_button, 'browse'),
                            (self.preview_button, 'preview'), (self.stop_button, 'stop_audio')):
            widget.config(text=self.tr(key))
        self.audio_dialog.title(self.tr('audio_settings'))
        self.browse_button.config(width=6 if self.language == 'en' else 4)
        for minutes, button in self.preset_buttons:
            button.config(text=self.tr('preset', minutes=minutes), width=6 if self.language == 'en' else 4)
        self.set_status(self.status_key, self.status_detail)
        self.refresh()
        if self.layout_id is not None:
            self.root.after_cancel(self.layout_id)
        self.layout_id = self.root.after_idle(self.language_layout)

    def language_layout(self):
        self.layout_id = None
        self.resize_dial()

    def change_language(self, _event=None):
        self.language = 'en' if self.language_choice.get() == 'English' else 'ko'
        self.apply_language()
        self.queue_save()

    def window_changed(self, event):
        if event.widget == self.root:
            self.queue_save()
            self.resize_dial()

    def shortcut(self, event, action):
        if event.widget in (self.root, self.canvas):
            action()
            return 'break'

    def resize_dial(self):
        if not hasattr(self, 'presets'):
            return
        gap = self.presets.winfo_reqwidth()/5
        side = max(self.slider.winfo_reqwidth()+gap, self.presets.winfo_reqwidth()+gap)
        other_height = 0
        for child in self.main.pack_slaves():
            if child == self.dial_row:
                continue
            raw_padding = child.pack_info()['pady']
            padding = (raw_padding,) if isinstance(raw_padding, (int, float)) else self.root.tk.splitlist(raw_padding)
            other_height += child.winfo_reqheight() + (2*float(padding[0]) if len(padding) == 1 else sum(map(float, padding)))
        available = self.main.winfo_height()-4*self.display_scale-other_height
        wanted = self.canvas.winfo_width()-2*side+self.time_label.winfo_reqheight()+gap
        height = max(80, round(min(wanted, available)))
        if int(self.canvas.cget('height')) != height:
            self.canvas.configure(height=height)
        self.draw()

    def volume_changed(self, value):
        self.audio.set_volume(float(value)/100)
        self.queue_save()

    def queue_save(self):
        if self.save_id is not None:
            self.root.after_cancel(self.save_id)
        self.save_id = self.root.after(500, self.save_settings)

    def save_settings(self):
        self.save_id = None
        if self.root.state() == 'normal' and self.root.winfo_width() > 1:
            self.normal_window = dict(width=max(440, round(self.root.winfo_width()/self.display_scale)),
                                      height=max(500, round(self.root.winfo_height()/self.display_scale)),
                                      x=self.root.winfo_x(), y=self.root.winfo_y())
        data = dict(selected_seconds=self.state.selected, color=self.color,
                    muted=self.muted.get(), topmost=self.topmost.get(),
                    mp3_path=self.mp3_path.get(), window=self.normal_window,
                    volume_percent=self.volume.get(),
                    layout_version=5,
                    language=self.language,
                    maximized=self.root.state() == 'zoomed')
        try:
            self.settings.save(data)
        except OSError:
            self.set_status('save_error')

    def change_color(self, color):
        self.color = color
        self.draw()
        self.queue_save()

    def browse_mp3(self):
        self.path_entry.focus_set()
        self.wheel_remainder = 0
        path = filedialog.askopenfilename(parent=self.audio_dialog, title=self.tr('choose_mp3'),
                                         filetypes=[(self.tr('mp3_files'), '*.mp3')])
        if path:
            self.mp3_path.set(path)

    def show_audio_settings(self):
        was_hidden = self.audio_dialog.state() == 'withdrawn'
        self.audio_dialog.deiconify()
        if was_hidden:
            self.audio_dialog.update_idletasks()
            w, h = self.audio_dialog.winfo_width(), self.audio_dialog.winfo_height()
            user32 = ctypes.windll.user32
            vx, vy = user32.GetSystemMetrics(76), user32.GetSystemMetrics(77)
            vw, vh = user32.GetSystemMetrics(78), user32.GetSystemMetrics(79)
            x = max(vx, min(self.root.winfo_x()+(self.root.winfo_width()-w)//2, vx+vw-w))
            y = max(vy, min(self.root.winfo_y()+(self.root.winfo_height()-h)//2, vy+vh-h))
            self.audio_dialog.geometry(f'{x:+d}{y:+d}')
        self.audio_dialog.lift()
        self.audio_dialog.attributes('-topmost', self.topmost.get())
        self.path_entry.focus_set()

    def topmost_changed(self):
        self.root.attributes('-topmost', self.topmost.get())
        self.audio_dialog.attributes('-topmost', self.topmost.get())

    def hide_audio_settings(self):
        self.stop_audio()
        self.audio_dialog.withdraw()
        self.canvas.focus_set()

    def audio_path(self):
        path = Path(self.mp3_path.get().strip().strip('"')).expanduser()
        if not path.is_absolute():
            path = (self.settings.path.parent if self.settings.path else Path(__file__).parent) / path
        return str(path)

    def preview_audio(self):
        try:
            self.audio.play(self.audio_path())
        except (ValueError, RuntimeError, OSError) as error:
            messagebox.showerror(self.tr('play_error'), self.error_text(error), parent=self.audio_dialog)

    def stop_audio(self):
        try:
            self.audio.stop()
        except RuntimeError as error:
            messagebox.showerror(self.tr('stop_error'), self.error_text(error), parent=self.root)

    def mute_changed(self):
        if self.muted.get():
            self.stop_audio()

    def close(self):
        self.stop_completion()
        self.root.after_cancel(self.tick_id)
        if self.layout_id is not None:
            self.root.after_cancel(self.layout_id)
        if self.save_id is not None:
            self.root.after_cancel(self.save_id)
        self.save_settings()
        try:
            self.audio.stop()
        finally:
            self.root.destroy()

    def from_slider(self, value):
        # Tk calls this asynchronously, so avoid resetting on programmatic sync.
        if round(float(value) * 60) != self.state.selected:
            self.select(float(value), sync=False)

    def select(self, minutes, sync=True):
        if self.completion_started is not None:
            self.stop_audio()
            self.stop_completion()
        self.state.set_minutes(minutes)
        if sync:
            self.slider.set(round(minutes))
        self.set_status('ready')
        self.refresh()

        self.queue_save()

    def pointer(self, event):
        x, y, radius = self.geometry()
        dx, dy = event.x-x, event.y-y
        if math.hypot(dx, dy) > radius:
            return
        self.canvas.focus_set()
        self.wheel_remainder = 0
        if self.completion_started is not None:
            self.reset()
            return
        if math.hypot(dx, dy) < radius * .13:
            return
        angle = math.atan2(-dx, -dy) % math.tau
        self.select(round(angle / math.tau * 60))

    def wheel(self, event):
        if self.root.focus_get() != self.canvas or getattr(event, 'widget', self.canvas) != self.canvas:
            return None
        self.wheel_remainder += event.delta
        steps = math.trunc(self.wheel_remainder / 120)
        self.wheel_remainder -= steps * 120
        if steps:
            self.select(max(0, min(60, self.state.selected / 60 + steps)))
        return 'break'

    def toggle(self):
        if self.completion_started is not None:
            self.stop_audio()
            self.stop_completion()
            self.state.reset()
        if self.state.deadline is None:
            self.state.start()
        else:
            self.state.pause()
        self.set_status('running' if self.state.deadline else 'pause')
        self.refresh()

    def reset(self):
        self.stop_audio()
        self.stop_completion()
        self.state.reset()
        self.set_status('reset_ready')
        self.refresh()

    def tick(self):
        self.root.after_cancel(self.tick_id)
        if self.state.tick():
            self.set_status('completed')
            self.start_completion()
            if not self.muted.get():
                if self.mp3_path.get().strip():
                    try:
                        self.audio.play(self.audio_path())
                    except (ValueError, RuntimeError, OSError) as error:
                        self.set_status('play_error', error)
                        self.play_default_alarm()
                else:
                    self.play_default_alarm()
        self.refresh()
        self.tick_id = self.root.after(100, self.tick)

    def play_default_alarm(self):
        try:
            self.audio.play_chime()
        except (ValueError, RuntimeError, OSError) as error:
            self.set_status('play_error', error)

    def refresh(self):
        seconds = math.ceil(self.state.remaining)
        self.time_label.config(text=f'{seconds // 60:02}:{seconds % 60:02}')
        completed = self.completion_started is not None
        self.guide.config(text=self.tr('completed_guide' if completed else 'guide'))
        self.reset_button.config(text=self.tr('acknowledge' if completed else 'reset'))
        self.play.config(text=self.tr('restart' if completed else 'pause' if self.state.deadline else 'start'),
                         state='normal' if seconds or completed else 'disabled')
        self.draw()

    def start_completion(self):
        self.stop_completion()
        self.completion_started = time.monotonic()
        self.animate_completion()

    def stop_completion(self):
        if self.animation_id is not None:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None
        self.completion_started = None
        self.canvas.delete('completion')

    def draw_completion(self):
        if self.completion_started is None:
            return
        x, y, radius = self.geometry()
        elapsed = time.monotonic() - self.completion_started
        rgb = tuple(int(self.color[i:i+2], 16) for i in (1, 3, 5))
        # Only lightweight Canvas rings animate; the high-DPI dial stays cached.
        for index in range(3):
            phase = (elapsed / 2.4 + index / 3) % 1
            r = radius * (.12 + .86 * phase)
            alpha = .85 * (1-phase)
            color = '#' + ''.join(f'{round(238+(channel-238)*alpha):02x}' for channel in rgb)
            tag = f'wave{index}'
            if not self.canvas.find_withtag(tag):
                self.canvas.create_oval(0, 0, 0, 0, tags=('completion', tag))
            self.canvas.coords(tag, x-r, y-r, x+r, y+r)
            self.canvas.itemconfigure(tag, outline=color, width=max(2, round(radius*.018)))
        self.canvas.tag_raise('completion')

    def animate_completion(self):
        self.animation_id = None
        if self.completion_started is not None:
            self.draw_completion()
            self.animation_id = self.root.after(33, self.animate_completion)

    def geometry(self):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        button_width = self.presets.winfo_reqwidth()
        self.dial_gap = button_width/5
        side = max(self.slider.winfo_reqwidth()+self.dial_gap, button_width+self.dial_gap)
        radius = max(1, min((w-2*side)/2, (h-self.time_label.winfo_reqheight()-self.dial_gap)/2))
        return w/2, radius, radius

    def draw(self):
        canvas = self.canvas
        x, y, radius = self.geometry()
        layout = (x, y, radius)
        if layout != self.last_layout and hasattr(self, 'presets'):
            # Slider sits beside the physical dial, with exactly its height.
            self.slider.place(x=x-radius-self.dial_gap, y=y-radius, anchor='ne', height=2*radius)
            gap = self.presets.winfo_reqwidth() / 5
            self.presets.place(x=x+radius+gap, y=y, anchor='w')
            self.time_label.place(x=x, y=y+radius+gap, anchor='n')
            self.slider.lift()
            self.presets.lift()
            self.last_layout = layout
        # The digital display updates once a second. Avoid expensive 4K
        # supersampling on every 100ms state tick for a subpixel dial change.
        drawing = (layout, self.color, math.ceil(self.state.remaining))
        if drawing == self.last_drawing:
            return
        self.last_drawing = drawing
        canvas.delete('all')
        rendered = self.renderer.render(round(2*radius), self.color, self.state.remaining)
        self.dial_image = ImageTk.PhotoImage(rendered, master=self.root)
        canvas.create_image(x, y, image=self.dial_image)
        self.draw_completion()


def run_smoke_test(root):
    """Exercise the packaged app; always release timers, audio and windows."""
    app = None
    callback_errors = []
    root.report_callback_exception = lambda *error: callback_errors.append(str(error[1]))
    try:
        app = GClock(root, settings_path=False)
        root.update()
        app.select(60)
        app.toggle()
        root.update()
        assert app.state.deadline is not None
        assert app.dial_image is not None and app.dial_image.width() > 0
        deadline = app.state.deadline
        app.language_choice.set('English')
        app.change_language()
        root.update()
        assert app.play.cget('text') == 'Pause'
        assert app.state.deadline == deadline
        app.language_choice.set('한국어')
        app.change_language()
        app.reset()
        assert app.state.remaining == 3600
        assert app.audio_dialog.state() == 'withdrawn'
        # Native window mapping can finish after update() on a busy desktop.
        root.deiconify()
        app.show_audio_settings()
        mapping_deadline = time.monotonic() + 2
        while not app.path_entry.winfo_ismapped() and time.monotonic() < mapping_deadline:
            root.update()
            time.sleep(.01)
        if not app.path_entry.winfo_ismapped():
            raise RuntimeError('Sound settings did not become visible within 2 seconds')
        app.hide_audio_settings()
        root.withdraw()
        app.muted.set(True)
        app.state.deadline = app.state.clock()-1
        app.tick()
        assert len(app.canvas.find_withtag('completion')) == 3
        assert app.animation_id is not None
        app.toggle()
        assert app.animation_id is None and app.state.deadline is not None
        app.reset()
        # Verify bundled native decoder and the 50 ms device request size.
        import io
        import wave
        import miniaudio
        wav_data = io.BytesIO()
        with wave.open(wav_data, 'wb') as wav:
            wav.setnchannels(2)
            wav.setsampwidth(2)
            wav.setframerate(44100)
            wav.writeframes(b'\0' * 44100 * 4)
        stream = miniaudio.stream_memory(wav_data.getvalue(), frames_to_read=32768)
        assert len(stream.send(2205)) == 4410
        stream.close()
        from audio_player import chime_wav
        stream = miniaudio.stream_memory(chime_wav(), frames_to_read=32768)
        assert any(stream.send(2205))
        stream.close()
        if callback_errors:
            raise RuntimeError('; '.join(callback_errors))
    finally:
        if app is not None:
            app.close()
        else:
            root.destroy()


def smoke_main(report_path):
    """Return a failing exit code plus a report instead of a windowed traceback."""
    import json
    import traceback
    report = {'ok': False, 'version': VERSION}
    try:
        run_smoke_test(tk.Tk())
        report['ok'] = True
    except Exception:
        report['error'] = traceback.format_exc()
    try:
        Path(report_path).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    except OSError:
        return 1
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    enable_dpi_awareness()
    if '--smoke-test' in sys.argv:
        report_path = Path(sys.executable if getattr(sys, 'frozen', False) else __file__).with_name('GClock-smoke-test.json')
        if '--smoke-report' in sys.argv:
            report_path = sys.argv[sys.argv.index('--smoke-report')+1]
        sys.exit(smoke_main(report_path))
    else:
        root = tk.Tk()
        GClock(root)
        root.mainloop()
