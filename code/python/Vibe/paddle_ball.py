import tkinter as tk
import random
import math
import time
import sys
import threading
import os

try:
    import winsound as _winsound   # Windows only; None on other platforms
except ImportError:
    _winsound = None  # type: ignore[assignment]

# ── Background music via Windows MCI ─────────────────────────────────────────
_MUSIC_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           '2021-08-30_-_Boss_Time_-_www.FesliyanStudios.com.mp3')

_mci_fn = None
if sys.platform == 'win32':
    try:
        import ctypes as _ct
        _mci_fn = _ct.WinDLL('winmm').mciSendStringW
        _mci_fn.argtypes = [_ct.c_wchar_p, _ct.c_wchar_p, _ct.c_uint, _ct.c_void_p]
        _mci_fn.restype = _ct.c_int
    except Exception:
        pass

def _mci(cmd: str) -> None:
    if _mci_fn is not None:
        try:
            _mci_fn(cmd, None, 0, None)
        except Exception:
            pass


# ── Data classes ─────────────────────────────────────────────────────────────

class Particle:
    __slots__ = ('x', 'y', 'vx', 'vy', 'life', 'decay', 'radius', 'r', 'g', 'b', 'cid')

    def __init__(self, x, y, scale=1.0):
        self.x = x
        self.y = y
        a = random.uniform(0, 2 * math.pi)
        s = random.uniform(2, 7) * scale
        self.vx = math.cos(a) * s
        self.vy = math.sin(a) * s
        self.life = 1.0
        self.decay = random.uniform(0.03, 0.07)
        self.radius = random.uniform(3, 8) * scale
        palettes = [
            (255, random.randint(80, 180), 0),
            (255, random.randint(180, 255), 0),
            (255, random.randint(40, 90), 40),
        ]
        self.r, self.g, self.b = random.choice(palettes)
        self.cid = None


class Ball:
    __slots__ = ('x', 'y', 'vx', 'vy', 'halo_id', 'body_id')

    def __init__(self, x, y, vx, vy):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.halo_id = None
        self.body_id = None


class PowerUp:
    # kind → (symbol, fill, outline, is_positive)
    CATALOG = {
        'split':   ('x2',  '#00ffee', '#008888', True),
        'wide':    ('+W',  '#44ff88', '#22aa44', True),
        'bigball': ('+B',  '#ffaa00', '#995500', True),
        'narrow':  ('-W',  '#ff4455', '#aa1122', False),
    }
    # weighted list used when picking a random kind
    _POOL = (['split'] * 30 + ['wide'] * 30 + ['bigball'] * 25 + ['narrow'] * 8)

    __slots__ = ('x', 'y', 'vy', 'kind', 'ring_id', 'label_id', 'radius')

    def __init__(self, x, y, vy, kind, radius):
        self.x = float(x)
        self.y = float(y)
        self.vy = float(vy)
        self.kind = kind
        self.radius = radius
        self.ring_id = None
        self.label_id = None

    @classmethod
    def random_kind(cls):
        return random.choice(cls._POOL)


# ── Main game ─────────────────────────────────────────────────────────────────

class Game:
    _BASE_W = 800
    _BASE_H = 600
    MILESTONE = 5
    FRAME_MS = 16
    _BEEP_FREQS = (440, 554, 659)   # A4 → C#5 → E5, cycles on every hit

    EFFECT_DUR = 600          # frames ≈ 10 s at 60 fps
    MAX_BALLS = 8
    POWERUP_INTERVAL_LO = 480  # ~8 s
    POWERUP_INTERVAL_HI = 900  # ~15 s

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Paddle Ball")
        self.root.resizable(False, False)

        self.W = self._BASE_W
        self.H = self._BASE_H
        self._fullscreen = False
        self._screen_state = 'title'

        self.canvas = tk.Canvas(root, width=self.W, height=self.H,
                                bg='#080818', highlightthickness=0)
        self.canvas.pack()

        self.best = 0
        self._keys: set = set()
        self._running = False

        # Persistent HUD canvas item IDs
        self._pad_halo = self._pad_body = None
        self._hits_lbl = self._best_lbl = None
        self._flash_lbl = self._status_lbl = None

        # Live collections
        self._particles: list = []
        self._balls: list = []
        self._powerups: list = []

        # Game state
        self._hits = 0
        self._speed = 0.0
        self._flash_life = 0.0
        self._px = float(self._BASE_W // 2)

        # Effect timers (frames remaining; 0 = inactive)
        self._wide_timer = 0
        self._narrow_timer = 0
        self._bigball_timer = 0
        self._powerup_cd = 0    # frames until next spawn attempt

        # Cached render states — only call itemconfig on transition
        self._last_pad_state = 'normal'   # 'normal' | 'wide' | 'narrow'
        self._last_bigball = False

        self._beep_idx = 0

        # Audio state
        self._music_enabled = True
        self._volume = 80          # 0-100
        self._muted = False
        self._vol_flash = 0        # frames remaining for vol indicator
        self._vol_lbl = None       # canvas item id (created in _rebuild_canvas)

        # Maximize / fullscreen button
        self._max_btn = tk.Button(
            root, text='⛶',
            command=self._toggle_fullscreen,
            bg='#0d1a2e', fg='#0088dd',
            activebackground='#1a3a5c', activeforeground='#00ccff',
            relief='flat', bd=0,
            font=('Arial', 13, 'bold'),
            cursor='hand2',
        )
        self._max_btn.place(relx=1.0, rely=0.0, anchor='ne', x=-6, y=6)

        # Music toggle button (headphone icon) — sits left of the fullscreen button
        self._music_btn = tk.Button(
            root, text='🎧',
            command=self._toggle_music,
            bg='#0d1a2e', fg='#44ccff',
            activebackground='#1a3a5c', activeforeground='#00ccff',
            relief='flat', bd=0,
            font=('Arial', 13),
            cursor='hand2',
        )
        self._music_btn.place(relx=1.0, rely=0.0, anchor='ne', x=-44, y=6)

        self.canvas.bind('<Motion>', self._on_mouse)
        self.canvas.bind('<MouseWheel>', self._on_scroll)
        self.root.bind('<KeyPress>', self._key_down)
        self.root.bind('<KeyRelease>', self._key_up)
        self.canvas.bind('<Button-1>', self._on_click)
        self.root.bind('<F11>', lambda _e: self._toggle_fullscreen())
        self.root.bind('<Escape>', lambda _e: self._set_fullscreen(False))

        self._show_title()

    # ── Scale helpers ─────────────────────────────────────────────────────────

    @property
    def _sx(self):
        return self.W / self._BASE_W

    @property
    def _sy(self):
        return self.H / self._BASE_H

    def _sc(self, px):
        return max(1, int(px * self._sx))

    def _font(self, size: int, *styles: str) -> list:
        return ['Courier', self._sc(size), *styles]

    # ── Computed game constants ───────────────────────────────────────────────

    @property
    def _base_pad_w(self): return self._sc(110)
    @property
    def _pad_h(self):      return max(8, self._sc(14))
    @property
    def _pad_y(self):      return int(self.H * (545 / 600))
    @property
    def _base_ball_r(self): return max(6, self._sc(10))
    @property
    def _pad_spd(self):    return 14.0 * self._sx
    @property
    def _base_spd(self):   return 5.0 * self._sx
    @property
    def _spd_per_hit(self): return 0.10 * self._sx
    @property
    def _spd_milestone(self): return 0.75 * self._sx
    @property
    def _pu_radius(self):  return self._sc(18)

    # Effect-modified values
    @property
    def _eff_pad_w(self):
        if self._wide_timer > 0:
            return self._sc(190)
        if self._narrow_timer > 0:
            return self._sc(55)
        return self._base_pad_w

    @property
    def _eff_ball_r(self):
        if self._bigball_timer > 0:
            return max(10, self._sc(22))
        return self._base_ball_r

    # ── Fullscreen ────────────────────────────────────────────────────────────

    def _toggle_fullscreen(self):
        self._set_fullscreen(not self._fullscreen)

    def _set_fullscreen(self, state: bool):
        if state == self._fullscreen:
            return
        old_w, old_h = self.W, self.H
        self._fullscreen = state
        self.root.attributes('-fullscreen', state)
        self.root.update_idletasks()

        new_w = self.root.winfo_width()
        new_h = self.root.winfo_height()
        if new_w < 10 or new_h < 10:
            return

        self.canvas.config(width=new_w, height=new_h)
        sx, sy = new_w / old_w, new_h / old_h

        if self._screen_state in ('playing', 'gameover'):
            self._px *= sx
            for b in self._balls:
                b.x *= sx
                b.y *= sy
                b.vx *= sx
                b.vy *= sx
            self._speed *= sx
            for p in self._particles:
                self.canvas.delete(p.cid)
            self._particles = []
            for pu in self._powerups:
                self.canvas.delete(pu.ring_id)
                self.canvas.delete(pu.label_id)
            self._powerups = []

        self.W, self.H = new_w, new_h
        self._max_btn.config(text='⊡' if self._fullscreen else '⛶')

        if self._screen_state == 'title':
            self._show_title()
        elif self._screen_state == 'playing':
            self._rebuild_canvas()
            self._render()
        else:
            self._rebuild_canvas()
            self._render()
            self._show_game_over()

    # ── Input ────────────────────────────────────────────────────────────────

    def _on_mouse(self, e):
        if self._running:
            half = self._eff_pad_w // 2
            self._px = float(max(half, min(self.W - half, e.x)))

    def _key_down(self, e):
        self._keys.add(e.keysym)
        if e.keysym.lower() == 'm':
            self._toggle_mute()

    def _key_up(self, e):   self._keys.discard(e.keysym)

    def _on_click(self, _e):
        if not self._running:
            self._start()

    # ── Static screens ───────────────────────────────────────────────────────

    def _show_title(self):
        self._screen_state = 'title'
        c = self.canvas
        c.delete('all')
        self._invalidate_ids()
        cy = self.H // 2
        sy = self._sy
        c.create_text(self.W // 2, cy - int(125 * sy),
                      text='PADDLE BALL',
                      font=self._font(50, 'bold'), fill='#00ffcc')
        c.create_text(self.W // 2, cy - int(50 * sy),
                      text='Keep the ball alive!',
                      font=self._font(18), fill='#aaaacc')
        c.create_text(self.W // 2, cy - int(8 * sy),
                      text='Move mouse  •  ← → keys  •  F11 fullscreen',
                      font=self._font(12), fill='#555577')
        # Power-up legend
        legend = '  '.join(
            f'{v[0]} {k}' for k, v in PowerUp.CATALOG.items()
        )
        c.create_text(self.W // 2, cy + int(36 * sy),
                      text=legend,
                      font=self._font(11), fill='#445566')
        self._draw_btn(self.W // 2, cy + int(115 * sy), 'CLICK TO START')

        # ★ NOW WITH SOUND badge — upper-right of title area
        s = min(self._sx, self._sy)
        bx = min(self.W // 2 + int(220 * self._sx), self.W - int(72 * s))
        by = cy - int(148 * self._sy)
        br = int(58 * s)
        c.create_oval(bx - br, by - int(br * 0.68),
                      bx + br, by + int(br * 0.68),
                      fill='#ffdd00', outline='#ff8800', width=max(2, int(3 * s)))
        c.create_text(bx, by, text='★ NOW WITH\n   SOUND! ★',
                      font=['Courier', max(7, int(9 * s)), 'bold'],
                      fill='#553300', justify='center')

    def _show_game_over(self):
        self._screen_state = 'gameover'
        c = self.canvas
        c.create_rectangle(0, 0, self.W, self.H, fill='#000011', stipple='gray50')
        cy = self.H // 2
        sy = self._sy
        c.create_text(self.W // 2, cy - int(128 * sy),
                      text='GAME OVER',
                      font=self._font(54, 'bold'), fill='#ff2244')
        c.create_text(self.W // 2, cy - int(32 * sy),
                      text=f'Hits this round:  {self._hits}',
                      font=self._font(22), fill='#ffffff')
        c.create_text(self.W // 2, cy + int(18 * sy),
                      text=f'Best streak:  {self.best}',
                      font=self._font(22), fill='#ffcc00')
        self._draw_btn(self.W // 2, cy + int(120 * sy), 'PLAY AGAIN')

    def _draw_btn(self, cx, cy, text):
        bw, bh = self._sc(220), self._sc(52)
        c = self.canvas
        c.create_rectangle(cx - bw // 2, cy - bh // 2,
                           cx + bw // 2, cy + bh // 2,
                           fill='#102040', outline='#0088dd', width=2)
        c.create_text(cx, cy, text=text,
                      font=self._font(14, 'bold'), fill='#00aaff')

    def _invalidate_ids(self):
        self._pad_halo = self._pad_body = None
        self._hits_lbl = self._best_lbl = None
        self._flash_lbl = self._status_lbl = None
        self._vol_lbl = None

    # ── Persistent game canvas ────────────────────────────────────────────────

    def _rebuild_canvas(self):
        """Recreate every persistent canvas item at current W/H."""
        c = self.canvas
        c.delete('all')
        self._invalidate_ids()

        step = self._sc(50)
        for x in range(0, self.W + 1, step):
            c.create_line(x, 0, x, self.H, fill='#0d0d25')
        for y in range(0, self.H + 1, step):
            c.create_line(0, y, self.W, y, fill='#0d0d25')

        self._pad_halo = c.create_rectangle(0, 0, 1, 1, fill='#001833', outline='')
        self._pad_body = c.create_rectangle(0, 0, 1, 1,
                                            fill='#0099ee', outline='#55ccff', width=1)

        m = self._sc(14)
        self._hits_lbl = c.create_text(m, m, text=f'HITS  {self._hits}',
                                       font=self._font(16, 'bold'),
                                       fill='#00ffcc', anchor='nw')
        self._best_lbl = c.create_text(self.W - m, m, text=f'BEST  {self.best}',
                                       font=self._font(16, 'bold'),
                                       fill='#ffcc00', anchor='ne')
        self._flash_lbl = c.create_text(self.W // 2, self.H // 2 - self._sc(80),
                                        text='', font=self._font(22, 'bold'),
                                        fill='#ff4400')
        self._status_lbl = c.create_text(self.W // 2, self._sc(40),
                                         text='', font=self._font(11),
                                         fill='#aaaaaa')
        self._vol_lbl = c.create_text(self.W // 2, self._sc(68),
                                      text='', font=self._font(13, 'bold'),
                                      fill='#00eebb')

        # Recreate canvas items for any existing balls
        for ball in self._balls:
            bfill, bout, hfill = self._ball_colors()
            ball.halo_id = c.create_oval(0, 0, 1, 1, fill=hfill, outline='')
            ball.body_id = c.create_oval(0, 0, 1, 1, fill=bfill, outline=bout, width=1)
            c.tag_lower(ball.halo_id, self._hits_lbl)
            c.tag_lower(ball.body_id, self._hits_lbl)

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def _start(self):
        self._screen_state = 'playing'
        self._hits = 0
        self._speed = self._base_spd
        self._flash_life = 0.0
        self._px = float(self.W // 2)
        self._wide_timer = 0
        self._narrow_timer = 0
        self._bigball_timer = 0
        self._powerup_cd = self.POWERUP_INTERVAL_LO
        self._last_pad_state = 'normal'
        self._last_bigball = False
        self._beep_idx = 0

        for p in self._particles:
            self.canvas.delete(p.cid)
        self._particles = []
        for pu in self._powerups:
            self.canvas.delete(pu.ring_id)
            self.canvas.delete(pu.label_id)
        self._powerups = []
        for b in self._balls:
            self.canvas.delete(b.halo_id)
            self.canvas.delete(b.body_id)
        self._balls = []

        # Single starting ball
        angle = random.uniform(math.pi * 0.3, math.pi * 0.7)
        b = Ball(self.W // 2, self.H // 3,
                 math.cos(angle) * self._speed,
                 math.sin(angle) * self._speed)
        self._balls.append(b)
        self._running = True
        self._rebuild_canvas()
        self._music_start()
        self._loop()

    def _end(self):
        self._running = False
        self._music_stop()
        if self._hits > self.best:
            self.best = self._hits
        self._render()
        self._show_game_over()

    # ── Ball management ───────────────────────────────────────────────────────

    def _ball_colors(self) -> tuple[str, str, str]:
        """Returns (body_fill, body_outline, halo_fill) for the current effect state."""
        if self._bigball_timer > 0:
            return '#ffaa00', '#ffdd55', '#885500'
        return '#ff6633', '#ffaa66', '#991100'

    def _register_ball(self, ball: Ball):
        """Add canvas items to a Ball and append it to the list."""
        c = self.canvas
        bfill, bout, hfill = self._ball_colors()
        ball.halo_id = c.create_oval(0, 0, 1, 1, fill=hfill, outline='')
        ball.body_id = c.create_oval(0, 0, 1, 1, fill=bfill, outline=bout, width=1)
        if self._hits_lbl:
            c.tag_lower(ball.halo_id, self._hits_lbl)
            c.tag_lower(ball.body_id, self._hits_lbl)
        self._balls.append(ball)

    def _deregister_ball(self, ball: Ball):
        self.canvas.delete(ball.halo_id)
        self.canvas.delete(ball.body_id)
        if ball in self._balls:
            self._balls.remove(ball)

    def _split_all_balls(self):
        for ball in list(self._balls):
            if len(self._balls) >= self.MAX_BALLS:
                break
            angle = math.atan2(ball.vy, ball.vx)
            spd = math.hypot(ball.vx, ball.vy)
            new_angle = angle + math.radians(28)
            nb = Ball(ball.x, ball.y,
                      math.cos(new_angle) * spd,
                      math.sin(new_angle) * spd)
            # Guarantee new ball travels upward so it doesn't immediately fall off
            if nb.vy > 0:
                nb.vy = -abs(nb.vy)
            self._register_ball(nb)

    # ── Power-ups ─────────────────────────────────────────────────────────────

    def _spawn_powerup(self):
        kind = PowerUp.random_kind()
        lbl, fill, outline, _ = PowerUp.CATALOG[kind]
        r = self._pu_radius
        x = random.uniform(r + self._sc(20), self.W - r - self._sc(20))
        y = float(r)
        vy = 1.2 * self._sx

        pu = PowerUp(x, y, vy, kind, r)
        c = self.canvas
        pu.ring_id = c.create_oval(x - r, y - r, x + r, y + r,
                                   fill=fill, outline=outline,
                                   width=self._sc(2))
        pu.label_id = c.create_text(x, y, text=lbl,
                                    font=self._font(9, 'bold'), fill='#111111')
        if self._hits_lbl:
            c.tag_lower(pu.ring_id, self._hits_lbl)
            c.tag_lower(pu.label_id, self._hits_lbl)
        self._powerups.append(pu)

    def _tick_powerups(self):
        c = self.canvas
        live = []
        br = self._eff_ball_r
        for pu in self._powerups:
            pu.y += pu.vy
            r = pu.radius

            # Ball-to-powerup collision
            collected = any(
                math.hypot(b.x - pu.x, b.y - pu.y) < br + r
                for b in self._balls
            )

            if collected:
                self._apply_powerup(pu.kind)
                _, fill, _, _ = PowerUp.CATALOG[pu.kind]
                self._burst(pu.x, pu.y, n=16, tint=fill)
                c.delete(pu.ring_id)
                c.delete(pu.label_id)
            elif pu.y - r > self.H:
                c.delete(pu.ring_id)
                c.delete(pu.label_id)
            else:
                c.coords(pu.ring_id, pu.x - r, pu.y - r, pu.x + r, pu.y + r)
                c.coords(pu.label_id, pu.x, pu.y)
                live.append(pu)

        self._powerups = live

    def _apply_powerup(self, kind: str):
        if kind == 'split':
            self._split_all_balls()
        elif kind == 'wide':
            self._wide_timer = self.EFFECT_DUR
            self._narrow_timer = 0
        elif kind == 'narrow':
            self._narrow_timer = self.EFFECT_DUR
            self._wide_timer = 0
        elif kind == 'bigball':
            self._bigball_timer = self.EFFECT_DUR

    def _tick_effects(self):
        if self._wide_timer   > 0: self._wide_timer   -= 1
        if self._narrow_timer > 0: self._narrow_timer -= 1
        if self._bigball_timer > 0: self._bigball_timer -= 1
        # Keep paddle inside screen for current effective width
        half = self._eff_pad_w // 2
        self._px = max(float(half), min(float(self.W - half), self._px))

    def _status_text(self) -> str:
        fps = 60
        parts = []
        if self._wide_timer > 0:
            parts.append(f'WIDE {self._wide_timer // fps + 1}s')
        if self._narrow_timer > 0:
            parts.append(f'NARROW {self._narrow_timer // fps + 1}s')
        if self._bigball_timer > 0:
            parts.append(f'BIGBALL {self._bigball_timer // fps + 1}s')
        if len(self._balls) > 1:
            parts.append(f'x{len(self._balls)} balls')
        return '   '.join(parts)

    # ── Particles ────────────────────────────────────────────────────────────

    def _burst(self, x, y, n=24, tint=None):
        c = self.canvas
        for _ in range(n):
            p = Particle(x, y, scale=self._sx)
            if tint:
                try:
                    p.r = int(tint[1:3], 16)
                    p.g = int(tint[3:5], 16)
                    p.b = int(tint[5:7], 16)
                except (ValueError, IndexError):
                    pass
            p.cid = c.create_oval(0, 0, 1, 1, fill='#ff6600', outline='')
            if self._hits_lbl:
                c.tag_lower(p.cid, self._hits_lbl)
            self._particles.append(p)

    def _tick_particles(self):
        c = self.canvas
        grav = 0.28 * self._sx
        live = []
        for p in self._particles:
            p.x += p.vx
            p.y += p.vy
            p.vy += grav
            p.life -= p.decay
            if p.life > 0:
                col = (f'#{int(p.r * p.life):02x}'
                       f'{int(p.g * p.life):02x}'
                       f'{int(p.b * p.life):02x}')
                rad = p.radius * p.life
                c.coords(p.cid, p.x - rad, p.y - rad, p.x + rad, p.y + rad)
                c.itemconfig(p.cid, fill=col)
                live.append(p)
            else:
                c.delete(p.cid)
        self._particles = live

    # ── Audio ────────────────────────────────────────────────────────────────

    def _music_start(self) -> None:
        if not self._music_enabled:
            return
        _mci('close bgm')  # no-op if not open; prevents double-open on restart
        _mci(f'open "{_MUSIC_FILE}" type mpegvideo alias bgm')
        _mci('play bgm repeat')
        self._apply_volume()

    def _music_stop(self) -> None:
        _mci('stop bgm')
        _mci('close bgm')

    def _toggle_music(self) -> None:
        self._music_enabled = not self._music_enabled
        self._music_btn.config(text='🎧' if self._music_enabled else '🔇')
        if self._music_enabled and self._running:
            self._music_start()
        elif not self._music_enabled:
            self._music_stop()

    def _toggle_mute(self) -> None:
        self._muted = not self._muted
        self._apply_volume()
        self._show_vol_flash()

    def _apply_volume(self) -> None:
        vol = 0 if self._muted else self._volume * 10   # MCI range 0-1000
        _mci(f'setaudio bgm volume to {vol}')

    def _on_scroll(self, e) -> None:
        delta = 5 if e.delta > 0 else -5
        self._volume = max(0, min(100, self._volume + delta))
        if self._muted and delta > 0:
            self._muted = False     # scrolling up unmutes automatically
        self._apply_volume()
        self._show_vol_flash()

    def _show_vol_flash(self) -> None:
        self._vol_flash = 90        # ~1.5 s at 60 fps
        if self._vol_lbl:
            icon = '🔇' if self._muted else ('🔈' if self._volume < 40 else '🔊')
            self.canvas.itemconfig(self._vol_lbl, text=f'{icon}  {self._volume}%')

    def _play_beep(self) -> None:
        if _winsound is None:
            return
        freq = self._BEEP_FREQS[self._beep_idx % len(self._BEEP_FREQS)]
        self._beep_idx += 1
        threading.Thread(target=_winsound.Beep, args=(freq, 55), daemon=True).start()

    # ── Main loop ────────────────────────────────────────────────────────────

    def _loop(self):
        if not self._running:
            return
        tick_start = time.perf_counter()

        # Keyboard paddle movement
        half = float(self._eff_pad_w // 2)
        if 'Left' in self._keys:
            self._px = max(half, self._px - self._pad_spd)
        if 'Right' in self._keys:
            self._px = min(self.W - half, self._px + self._pad_spd)

        self._tick_effects()

        br = self._eff_ball_r
        pad_top = self._pad_y - self._pad_h // 2
        to_remove = []

        for ball in self._balls:
            prev_x = ball.x
            prev_y = ball.y
            ball.x += ball.vx
            ball.y += ball.vy

            # Side walls — reflective sweep preserves overshoot at high speed
            if ball.x - br < 0:
                ball.x = br + (br - ball.x)
                ball.vx = abs(ball.vx)
            elif ball.x + br > self.W:
                ball.x = (self.W - br) - (ball.x + br - self.W)
                ball.vx = -abs(ball.vx)

            # Ceiling — same reflective sweep
            if ball.y - br < 0:
                ball.y = br + (br - ball.y)
                ball.vy = abs(ball.vy)

            # ── Sweep-based paddle collision (no tunneling) ──────────────────
            # Check whether the ball's bottom edge crossed pad_top this frame.
            prev_bottom = prev_y + br
            curr_bottom = ball.y + br

            if ball.vy > 0 and prev_bottom < pad_top <= curr_bottom:
                # Fraction of the step at which the crossing happened
                t = (pad_top - prev_bottom) / (curr_bottom - prev_bottom)
                cross_x = prev_x + (ball.x - prev_x) * t

                if abs(cross_x - self._px) <= self._eff_pad_w // 2 + br:
                    # ── Hit! ─────────────────────────────────────────────────
                    ball.x = cross_x
                    ball.y = pad_top - br - 1

                    self._hits += 1
                    self._speed += self._spd_per_hit

                    if self._hits % self.MILESTONE == 0:
                        self._speed += self._spd_milestone
                        self._flash_life = 1.0
                        self.canvas.itemconfig(
                            self._flash_lbl,
                            text=f'SPEED UP!  (hit {self._hits})',
                            fill='#ff8800')

                    # Deflect angle from where on paddle ball lands
                    offset = (ball.x - self._px) / (self._eff_pad_w / 2)
                    offset = max(-1.0, min(1.0, offset))
                    dev = offset * (math.pi / 3)
                    ball.vx = math.sin(dev) * self._speed
                    ball.vy = -abs(math.cos(dev) * self._speed)

                    self._burst(ball.x, pad_top)
                    self._play_beep()

            if ball.y - br > self.H:
                to_remove.append(ball)

        for ball in to_remove:
            self._deregister_ball(ball)

        if not self._balls:
            self._end()
            return

        # Power-up countdown and spawning
        self._powerup_cd -= 1
        if self._powerup_cd <= 0:
            self._spawn_powerup()
            self._powerup_cd = random.randint(self.POWERUP_INTERVAL_LO,
                                              self.POWERUP_INTERVAL_HI)

        # Flash banner decay
        if self._flash_life > 0:
            self._flash_life = max(0.0, self._flash_life - 0.022)
            if self._flash_life == 0.0:
                self.canvas.itemconfig(self._flash_lbl, text='')
            else:
                i = self._flash_life
                col = f'#{int(255 * min(1.0, i * 1.5)):02x}{int(136 * i):02x}00'
                self.canvas.itemconfig(self._flash_lbl, fill=col)

        # Volume indicator decay
        if self._vol_flash > 0:
            self._vol_flash -= 1
            if self._vol_flash == 0 and self._vol_lbl:
                self.canvas.itemconfig(self._vol_lbl, text='')

        self._tick_particles()
        self._tick_powerups()
        self._render()

        spent_ms = (time.perf_counter() - tick_start) * 1000
        self.root.after(max(1, self.FRAME_MS - int(spent_ms)), lambda: self._loop())

    # ── Render ───────────────────────────────────────────────────────────────

    def _render(self):
        c = self.canvas
        halo = self._sc(5)
        bg_halo = self._sc(6)

        # Paddle position
        px, py = self._px, self._pad_y
        hw, hh = self._eff_pad_w // 2, self._pad_h // 2
        c.coords(self._pad_halo,
                 px - hw - halo, py - hh - halo,
                 px + hw + halo, py + hh + halo)
        c.coords(self._pad_body, px - hw, py - hh, px + hw, py + hh)

        # Paddle colour — only on state change
        pad_state = ('wide' if self._wide_timer > 0
                     else 'narrow' if self._narrow_timer > 0
                     else 'normal')
        if pad_state != self._last_pad_state:
            self._last_pad_state = pad_state
            if pad_state == 'wide':
                c.itemconfig(self._pad_body, fill='#22cc66', outline='#66ff99')
                c.itemconfig(self._pad_halo, fill='#003311')
            elif pad_state == 'narrow':
                c.itemconfig(self._pad_body, fill='#dd2222', outline='#ff6666')
                c.itemconfig(self._pad_halo, fill='#330000')
            else:
                c.itemconfig(self._pad_body, fill='#0099ee', outline='#55ccff')
                c.itemconfig(self._pad_halo, fill='#001833')

        # Ball positions
        br = self._eff_ball_r
        for ball in self._balls:
            c.coords(ball.halo_id,
                     ball.x - br - bg_halo, ball.y - br - bg_halo,
                     ball.x + br + bg_halo, ball.y + br + bg_halo)
            c.coords(ball.body_id,
                     ball.x - br, ball.y - br,
                     ball.x + br, ball.y + br)

        # Ball colour — only on bigball state change
        bigball = self._bigball_timer > 0
        if bigball != self._last_bigball:
            self._last_bigball = bigball
            for ball in self._balls:
                if bigball:
                    c.itemconfig(ball.body_id, fill='#ffaa00', outline='#ffdd55')
                    c.itemconfig(ball.halo_id, fill='#885500')
                else:
                    c.itemconfig(ball.body_id, fill='#ff6633', outline='#ffaa66')
                    c.itemconfig(ball.halo_id, fill='#991100')

        # HUD
        c.itemconfig(self._hits_lbl, text=f'HITS  {self._hits}')
        c.itemconfig(self._best_lbl, text=f'BEST  {self.best}')
        c.itemconfig(self._status_lbl, text=self._status_text())
        # tag_raise removed — z-order is managed at creation via tag_lower


def main():
    # On Windows the default timer resolution is ~15 ms, making root.after()
    # fire irregularly even when a shorter delay is requested. Bumping it to
    # 1 ms gives smooth ~60 fps scheduling for the cost of a tiny power draw.
    if sys.platform == 'win32':
        try:
            import ctypes
            ctypes.WinDLL('winmm').timeBeginPeriod(1)
        except Exception:
            pass

    root = tk.Tk()
    Game(root)
    root.mainloop()

    if sys.platform == 'win32':
        try:
            import ctypes
            ctypes.WinDLL('winmm').timeEndPeriod(1)
        except Exception:
            pass


if __name__ == '__main__':
    main()
