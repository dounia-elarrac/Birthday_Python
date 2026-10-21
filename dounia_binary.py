"""12 November 2026"""
import math
import random
import threading
import tkinter as tk
import tempfile
import wave
import struct
from datetime import datetime
from tkinter import font as tkfont


COLS, ROWS = 88, 28
CELL_W, CELL_H = 10, 16
LEFT, TOP = 30, 20
BG = "#2b1b2e"
BLACK = "#000000"
PINK = "#ff4f9a"
LIGHT_PINK = "#ffd5e5"
WHITE = "#fff8fc"
PURPLE = "#b27cff"
MAUVE = "#d05acb"
GOLD = "#ffd15c"


class DouniaBirthday:
    def __init__(self, root):
        self.root = root
        root.title("Dounia · 20 ans · 12/11")
        root.configure(bg=BG, cursor="heart")
        root.geometry("980x740")
        root.resizable(False, False)
        self.mono = self.choose_mono()
        self.busy = False
        self.finished = False
        self.candles_out = 0
        self.flicker = 0
        self.heart_cells = []
        self.particles = []

        tk.Label(root, text="DOUNIA  ·   20ans", bg=BG, fg=LIGHT_PINK,
                 font=(self.mono, 15, "bold")).pack(pady=(10, 2))
        self.timer = tk.Label(root, text="", bg=BG, fg=WHITE,
                              font=(self.mono, 11, "bold"))
        self.timer.pack(pady=(0, 3))
        self.canvas = tk.Canvas(root, width=940, height=500, bg=BG,
                                highlightthickness=0, cursor="heart")
        self.canvas.pack(padx=18, pady=3)
        self.message = tk.Label(root, text="", bg=BG, fg=PINK,
                                font=("Segoe UI", 24, "bold"), height=1)
        self.message.pack(pady=(5, 0))
        self.button = tk.Button(root, text="♡   OUVRIR LE CŒUR   ♡",
                                command=self.activate, bg=PINK, fg="#35132b",
                                activebackground="#ffc2dc", relief="flat",
                                padx=30, pady=10, font=(self.mono, 11, "bold"),
                                cursor="heart")
        self.button.pack(pady=(5, 2))
        tk.Label(root, text="Clique sur le bouton rose · le son démarre avec la surprise ♥",
                 bg=BG, fg="#bd99b7", font=(self.mono, 8)).pack(pady=(1, 7))
        root.bind("<Return>", lambda _event: self.activate())
        root.bind("<space>", lambda _event: self.activate())
        self.canvas.bind("<Button-1>", lambda _event: self.activate())
        self.draw_heart()
        self.update_timer()

    @staticmethod
    def choose_mono():
        families = set(tkfont.families())
        for family in ("Cascadia Mono", "Consolas", "DejaVu Sans Mono", "Courier New"):
            if family in families:
                return family
        return "Courier"

    @staticmethod
    def blank_grid():
        return [[None for _ in range(COLS)] for _ in range(ROWS)]

    @staticmethod
    def put(grid, x, y, bit, color):
        if 0 <= x < COLS and 0 <= y < ROWS:
            grid[y][x] = (bit, color)

    def render(self, grid):
        self.canvas.delete("all")
        for y, row in enumerate(grid):
            for x, item in enumerate(row):
                if item:
                    bit, color = item
                    self.canvas.create_text(LEFT + x*CELL_W, TOP + y*CELL_H,
                                            text=bit, fill=color,
                                            font=(self.mono, 12, "bold"))

    def update_timer(self):
        now = datetime.now()
        birthday = datetime(2026, 11, 12)
        if now >= birthday:
            label = "JOYEUX ANNIVERSAIRE DOUNIA · 20 ANS"
        else:
            seconds = int((birthday-now).total_seconds())
            days, seconds = divmod(seconds, 86400)
            hours, seconds = divmod(seconds, 3600)
            minutes, seconds = divmod(seconds, 60)
            label = f"12.11.2026  ·  {days:03d} J  {hours:02d} H  {minutes:02d} M  {seconds:02d} S"
        self.timer.configure(text=label)
        self.root.after(1000, self.update_timer)

    @staticmethod
    def in_heart(x, y):
        return (x*x + y*y - 1) ** 3 - x*x*y**3 <= 0

    def draw_heart(self):
        grid = self.blank_grid()
        self.heart_cells.clear()
        cx, cy = 44, 14
        for y in range(3, 26):
            for x in range(17, 72):
                nx = (x-cx) / 23 * 1.52
                ny = (cy-y) / 8.6
                if self.in_heart(nx, ny):
                    edge = any(not self.in_heart(nx+dx, ny+dy)
                               for dx, dy in ((.07, 0), (-.07, 0), (0, .12), (0, -.12)))
                    bit = "0" if (x+y) % 2 else "1"
                    color = BLACK if edge else (PINK if (x+y) % 5 == 0 else LIGHT_PINK)
                    self.put(grid, x, y, bit, color)
                    self.heart_cells.append((x, y, bit, color))
        self.render(grid)

    def play_music(self):
        def play():
            try:
                import winsound
                # A clean, gentle piano-like Happy Birthday tune, synthesized
                # locally so the app needs no downloaded audio or extra package.
                sr = 22050
                quarter = .36
                melody = [
                    (261.63,1),(261.63,1),(293.66,2),(261.63,2),(349.23,2),(329.63,3),
                    (261.63,1),(261.63,1),(293.66,2),(261.63,2),(392.00,2),(349.23,3),
                    (261.63,1),(261.63,1),(523.25,2),(440.00,2),(349.23,2),(329.63,2),(293.66,3),
                    (466.16,1),(466.16,1),(440.00,2),(349.23,2),(392.00,2),(349.23,4),
                ]
                audio = []
                for index, (freq, beats) in enumerate(melody):
                    dur = quarter * beats
                    count = int(sr * dur)
                    # Soft chord underneath each note, with a plucked/piano envelope.
                    chord = freq * (1.25 if index % 3 == 0 else 1.5)
                    for n in range(count):
                        t = n / sr
                        attack = min(1.0, t / .018)
                        release = min(1.0, (dur - t) / .075)
                        env = max(0.0, min(attack, release)) * math.exp(-2.0*t/dur)
                        fundamental = (math.sin(2*math.pi*freq*t)
                                       + .24*math.sin(4*math.pi*freq*t)
                                       + .08*math.sin(6*math.pi*freq*t))
                        harmony = .18 * math.sin(2*math.pi*chord*t)
                        audio.append((fundamental + harmony) * env * .42)
                    audio.extend([0.0] * int(sr * .035))
                with tempfile.NamedTemporaryFile(prefix="dounia_birthday_", suffix=".wav", delete=False) as tmp:
                    wav_path = tmp.name
                with wave.open(wav_path, "wb") as wav:
                    wav.setnchannels(1)
                    wav.setsampwidth(2)
                    wav.setframerate(sr)
                    wav.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, s))*32767)) for s in audio))
                self._music_path = wav_path
                winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except Exception:
                try:
                    self.root.after(0, self.root.bell)
                except tk.TclError:
                    pass
        threading.Thread(target=play, daemon=True).start()

    def activate(self):
        if self.busy:
            return
        if self.finished:
            self.finished = False
            self.candles_out = 0
            self.message.configure(text="")
            self.button.configure(text="♡   OUVRIR LE CŒUR   ♡")
            self.draw_heart()
        self.busy = True
        self.button.configure(state="disabled", text="0101  ·  SURPRISE EN COURS  ·  1010")
        self.message.configure(text="")
        self.play_music()
        self.explode(0)

    def explode(self, frame):
        if frame == 0:
            self.particles = [(x, y, x-44, y-14, bit, color)
                              for x, y, bit, color in self.heart_cells]
        grid = self.blank_grid()
        spread = frame / 12 * 1.35
        for x, y, dx, dy, bit, color in self.particles:
            xx, yy = round(x + dx*spread), round(y + dy*spread)
            if 0 <= xx < COLS and 0 <= yy < ROWS:
                self.put(grid, xx, yy, bit, random.choice((color, PINK, PURPLE, MAUVE, GOLD)))
        self.render(grid)
        if frame < 12:
            self.root.after(65, lambda: self.explode(frame+1))
        else:
            self.root.after(120, lambda: self.assemble(0))

    def draw_balloon(self, grid, cx, cy, rx, ry, color):
        for y in range(cy-ry, cy+ry+1):
            for x in range(cx-rx, cx+rx+1):
                nx = (x-cx) / max(rx, 1)
                ny = (y-cy) / max(ry, 1)
                if nx*nx + ny*ny <= 1:
                    edge = any((nx+dx/rx)**2 + ny**2 > 1 for dx in (-1, 1))
                    edge = edge or any(nx**2 + (ny+dy/ry)**2 > 1 for dy in (-1, 1))
                    bit = "0" if (x+y) % 2 else "1"
                    self.put(grid, x, y, bit, BLACK if edge else color)
        for row in range(cy+ry+1, min(cy+ry+4, ROWS)):
            self.put(grid, cx, row, "0" if row % 2 else "1", PURPLE)

    def draw_fireworks(self, grid, stage):
        # Two mirrored, compact binary starbursts; no loose confetti bits.
        radius_max = min(4, 1 + stage//3)
        for cx, cy, base in ((14, 18, MAUVE), (73, 18, PURPLE)):
            for radius in range(1, radius_max+1):
                rays = ((0, -radius), (radius, 0), (0, radius), (-radius, 0),
                        (radius, -radius), (-radius, -radius),
                        (radius, radius), (-radius, radius))
                for i, (dx, dy) in enumerate(rays):
                    bit = "0" if (radius+i) % 2 else "1"
                    color = (PINK, GOLD, base, LIGHT_PINK)[(radius+i) % 4]
                    self.put(grid, cx+dx, cy+dy, bit, color)

    def draw_tier(self, grid, left, right, top, bottom, reveal, icing):
        rows = max(0, min(bottom-top+1, int((bottom-top+1)*reveal)))
        if rows < 1:
            return
        visible_top = bottom-rows+1
        for y in range(visible_top, bottom+1):
            for x in range(left, right+1):
                edge = y in (visible_top, bottom) or x in (left, right)
                bit = "0" if (x+y) % 2 else "1"
                if edge:
                    color = BLACK
                elif y == visible_top+1 or y == bottom-1:
                    color = icing
                else:
                    color = WHITE
                self.put(grid, x, y, bit, color)

    def cake_grid(self, stage, candles_out, flicker):
        grid = self.blank_grid()
        scale = min(1, .45 + stage*.055)
        for args in ((7, 6, 4, 3, MAUVE), (19, 4, 3, 2, PURPLE),
                     (69, 4, 3, 2, MAUVE), (81, 6, 4, 3, PURPLE)):
            cx, cy, rx, ry, color = args
            self.draw_balloon(grid, cx, cy, max(2, round(rx*scale)),
                              max(1, round(ry*scale)), color)
        self.draw_fireworks(grid, stage)

        # Wider layers at the bottom make an unmistakable binary birthday cake.
        tiers = ((20, 67, 21, 26, PINK),
                 (27, 60, 16, 20, MAUVE),
                 (34, 53, 11, 15, "#ff91bf"))
        progress = min(1, stage/10)
        for index, (left, right, top, bottom, icing) in enumerate(tiers):
            reveal = min(1, max(0, progress*3-index))
            self.draw_tier(grid, left, right, top, bottom, reveal, icing)

        if stage >= 7:
            candle_x = (37, 40, 43, 46, 49, 52)
            for i, x in enumerate(candle_x):
                for dy in (0, 1, 2):
                    self.put(grid, x, 10+dy, "0" if (i+dy) % 2 else "1", PINK)
        return grid

    def render_cake(self, stage, candles_out, flicker):
        self.render(self.cake_grid(stage, candles_out, flicker))
        if stage >= 7:
            candle_x = (37, 40, 43, 46, 49, 52)
            # Each little flame is a distinct eight-point star made only of bits.
            rays = ((0, -14), (-8, -8), (8, -8), (-13, 0), (0, 0), (13, 0),
                    (-8, 8), (8, 8), (0, 14))
            for i, x in enumerate(candle_x):
                if i >= candles_out:
                    cx, cy = LEFT+x*CELL_W, TOP+9*CELL_H
                    for j, (dx, dy) in enumerate(rays):
                        bit = "0" if (i+j+flicker) % 2 else "1"
                        tint = GOLD if j % 2 == 0 else LIGHT_PINK
                        self.canvas.create_text(cx+dx, cy+dy, text=bit, fill=tint,
                                                font=(self.mono, 12, "bold"))

    def assemble(self, stage):
        self.flicker += 1
        self.render_cake(stage, self.candles_out, self.flicker)
        if stage < 10:
            self.root.after(110, lambda: self.assemble(stage+1))
        else:
            self.type_message(0)
            self.root.after(550, lambda: self.extinguish(0))

    def type_message(self, index):
        text = "HAPPY BIRTHDAY DOUNIA · 20 ANS"
        self.message.configure(text=text[:index], fg=PINK)
        if index < len(text):
            self.root.after(55, lambda: self.type_message(index+1))

    def extinguish(self, count):
        self.candles_out = count
        self.flicker += 1
        self.render_cake(10, count, self.flicker)
        if count < 6:
            self.root.after(750, lambda: self.extinguish(count+1))
        else:
            self.final_scene()

    def final_scene(self):
        self.render_cake(10, 6, self.flicker)
        self.message.configure(text="HAPPY BIRTHDAY DOUNIA · 20 ANS", fg=LIGHT_PINK)
        self.button.configure(state="normal", text="↻   REJOUER LA SURPRISE   ♡")
        self.busy = False
        self.finished = True


def main():
    root = tk.Tk()
    DouniaBirthday(root)
    root.mainloop()


if __name__ == "__main__":
    main()
