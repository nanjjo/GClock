"""Compact volume control: the filled part shows the saved volume."""
import tkinter as tk


class VolumeBar(tk.Canvas):
    def __init__(self, parent, variable, command, scale=1):
        super().__init__(parent, width=round(110*scale), height=round(15*scale),
                         bg='#f5f3ed', highlightthickness=0, takefocus=True,
                         cursor='hand2')
        self.variable = variable
        self.command = command
        self.scale = scale
        self.trace = variable.trace_add('write', self.changed)
        self.bind('<Configure>', lambda _: self.redraw())
        self.bind('<Button-1>', self.pointer)
        self.bind('<B1-Motion>', self.pointer)
        self.bind('<Left>', lambda _: self.adjust(-5))
        self.bind('<Right>', lambda _: self.adjust(5))
        self.bind('<Home>', lambda _: self.set_value(0))
        self.bind('<End>', lambda _: self.set_value(100))
        self.bind('<MouseWheel>', lambda e: self.adjust(5 if e.delta > 0 else -5))
        self.bind('<Destroy>', self.cleanup)

    def cleanup(self, event):
        if event.widget == self:
            self.variable.trace_remove('write', self.trace)

    def changed(self, *_):
        self.redraw()
        self.command(self.variable.get())

    def redraw(self):
        self.delete('all')
        width, height = self.winfo_width(), self.winfo_height()
        self.create_rectangle(0, 0, width, height, fill='#d7d8d2', outline='')
        self.create_rectangle(0, 0, width*self.variable.get()/100, height,
                              fill='#3d8769', outline='', tags='filled')
        if self.focus_get() == self:
            self.create_rectangle(1, 1, width-1, height-1, outline='#447db0')

    def set_value(self, value):
        self.variable.set(max(0, min(100, round(value))))
        return 'break'

    def adjust(self, delta):
        return self.set_value(self.variable.get()+delta)

    def pointer(self, event):
        self.focus_set()
        return self.set_value(event.x/max(1, self.winfo_width())*100)
