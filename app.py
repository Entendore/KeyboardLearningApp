#!/usr/bin/env python3
"""
Keyboard Learning App — Learn to type fast and accurately on multiple layouts.
Supports: QWERTY, AZERTY, DVORAK, Colemak
Platforms: Desktop (Windows/Linux/Mac) and Android

Requirements:
  pip install kivy plyer

Android Build:
  buildozer android debug
"""

import time, random, json, os, sys, math, struct, wave
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.properties import (
    StringProperty, NumericProperty, BooleanProperty, ListProperty
)
from kivy.metrics import dp, sp
from kivy.animation import Animation
from kivy.utils import platform

# ─── Platform Detection ───────────────────────────────────────────────────────
IS_ANDROID = platform == 'android'
IS_IOS = platform == 'ios'
IS_MOBILE = IS_ANDROID or IS_IOS

HAS_VIBRATOR = False
if IS_ANDROID:
    try:
        from plyer import vibrator
        HAS_VIBRATOR = True
    except ImportError:
        pass

# ─── Responsive Sizing ────────────────────────────────────────────────────────
def _sw():
    """Scale factor based on screen width."""
    w = Window.width if Window.width else 800
    if w < 500: return 0.85
    if w < 800: return 0.95
    return 1.0

def key_h():   return dp(48 if IS_MOBILE else 42) * _sw()
def key_fs(l): return sp(13 if len(l) <= 2 else 10) * _sw()
def btn_h():   return dp(52 if IS_MOBILE else 48)
def typing_h():return dp(160 if IS_MOBILE else 150)

# ─── Theme System ─────────────────────────────────────────────────────────────
THEMES = {
    'dark': {
        'BG':(0.08,0.08,0.12,1), 'CARD':(0.14,0.15,0.20,1),
        'CARD2':(0.20,0.21,0.27,1), 'CARD3':(0.25,0.26,0.32,1),
        'ACCENT':(0.28,0.56,1.0,1), 'GREEN':(0.22,0.88,0.42,1),
        'RED':(0.92,0.26,0.26,1), 'YELLOW':(1.0,0.86,0.20,1),
        'ORANGE':(1.0,0.55,0.15,1), 'TXT':(0.93,0.93,0.97,1),
        'DIM':(0.44,0.44,0.52,1),
    },
    'midnight': {
        'BG':(0.04,0.04,0.09,1), 'CARD':(0.09,0.10,0.17,1),
        'CARD2':(0.15,0.16,0.23,1), 'CARD3':(0.20,0.22,0.30,1),
        'ACCENT':(0.45,0.45,1.0,1), 'GREEN':(0.20,0.90,0.60,1),
        'RED':(0.95,0.20,0.30,1), 'YELLOW':(1.0,0.90,0.30,1),
        'ORANGE':(1.0,0.60,0.20,1), 'TXT':(0.90,0.90,0.98,1),
        'DIM':(0.40,0.40,0.55,1),
    },
    'ocean': {
        'BG':(0.04,0.07,0.12,1), 'CARD':(0.08,0.13,0.20,1),
        'CARD2':(0.12,0.18,0.28,1), 'CARD3':(0.16,0.24,0.34,1),
        'ACCENT':(0.15,0.75,0.90,1), 'GREEN':(0.20,0.85,0.65,1),
        'RED':(0.90,0.30,0.35,1), 'YELLOW':(0.95,0.88,0.25,1),
        'ORANGE':(0.95,0.60,0.20,1), 'TXT':(0.92,0.95,0.98,1),
        'DIM':(0.35,0.45,0.55,1),
    },
    'warm': {
        'BG':(0.12,0.08,0.06,1), 'CARD':(0.18,0.14,0.10,1),
        'CARD2':(0.24,0.20,0.16,1), 'CARD3':(0.30,0.26,0.22,1),
        'ACCENT':(0.95,0.65,0.25,1), 'GREEN':(0.45,0.85,0.35,1),
        'RED':(0.90,0.30,0.25,1), 'YELLOW':(0.98,0.88,0.25,1),
        'ORANGE':(0.95,0.55,0.20,1), 'TXT':(0.95,0.92,0.88,1),
        'DIM':(0.50,0.42,0.36,1),
    },
}

_theme_name = 'dark'

def T(key):
    return THEMES[_theme_name].get(key, (0.5,0.5,0.5,1))

def set_theme(name):
    global _theme_name
    if name in THEMES:
        _theme_name = name

FINGER_COLS = [
    (0.85,0.30,0.30),(0.90,0.55,0.20),(0.88,0.82,0.22),(0.28,0.78,0.32),
    (0.20,0.76,0.82),(0.30,0.46,0.92),(0.58,0.30,0.82),(0.82,0.30,0.70),
    (0.50,0.50,0.56),
]
FINGER_NAMES = [
    "Left Pinky","Left Ring","Left Middle","Left Index",
    "Right Index","Right Middle","Right Ring","Right Pinky","Thumb"
]

# ─── Sound System ─────────────────────────────────────────────────────────────
def _gen_wav(path, freq=800, dur=0.04, vol=0.2):
    sr = 22050; n = int(sr * dur); frames = []
    for i in range(n):
        fade = 1.0 - (i / n)
        v = int(vol * 32767 * math.sin(2*math.pi*freq*i/sr) * fade)
        frames.append(struct.pack('<h', max(-32768, min(32767, v))))
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
        wf.writeframes(b''.join(frames))

class SoundManager:
    def __init__(self):
        self.enabled = True
        self.sounds = {}
        self._ready = False

    def init(self, data_dir):
        try:
            from kivy.core.audio import SoundLoader
            sd = os.path.join(data_dir, 'sounds')
            os.makedirs(sd, exist_ok=True)
            for name, freq, dur in [('click',880,0.035),('error',280,0.07),('done',1100,0.12)]:
                p = os.path.join(sd, f'{name}.wav')
                if not os.path.exists(p):
                    _gen_wav(p, freq, dur, 0.18)
                s = SoundLoader.load(p)
                if s:
                    s.volume = 0.5
                    self.sounds[name] = s
            self._ready = True
        except Exception as e:
            print(f"Sound init skipped: {e}")

    def play(self, name):
        if not self.enabled or not self._ready or name not in self.sounds:
            return
        try:
            s = self.sounds[name]
            if s:
                s.stop(); s.play()
        except: pass

sound_mgr = SoundManager()

def vibrate(ms=30):
    if HAS_VIBRATOR:
        try: vibrator.vibrate(time=ms/1000.0)
        except: pass

# ─── Settings Manager ─────────────────────────────────────────────────────────
DEFAULT_SETTINGS = {
    'layout': 'QWERTY', 'lesson': 'home_row', 'theme': 'dark',
    'sound': True, 'vibration': True, 'mode': 'completion', 'timer_secs': 60,
}

class SettingsManager:
    def __init__(self):
        self.data = dict(DEFAULT_SETTINGS)
        self._path = None

    def init(self, data_dir):
        self._path = os.path.join(data_dir, 'kb_settings.json')
        self.load()

    def load(self):
        if self._path and os.path.exists(self._path):
            try:
                with open(self._path, 'r') as f:
                    saved = json.load(f)
                    self.data.update(saved)
            except: pass
        set_theme(self.data.get('theme', 'dark'))
        sound_mgr.enabled = self.data.get('sound', True)

    def save(self):
        if self._path:
            try:
                with open(self._path, 'w') as f:
                    json.dump(self.data, f)
            except: pass

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()
        if key == 'theme': set_theme(value)
        if key == 'sound': sound_mgr.enabled = value

settings_mgr = SettingsManager()

# ─── Keyboard Layouts ─────────────────────────────────────────────────────────
LAYOUTS = {
    'QWERTY': {
        'display': 'QWERTY (Standard)',
        'rows': [
            [('`',1),('1',1),('2',1),('3',1),('4',1),('5',1),('6',1),('7',1),('8',1),('9',1),('0',1),('-',1),('=',1)],
            [('Q',1),('W',1),('E',1),('R',1),('T',1),('Y',1),('U',1),('I',1),('O',1),('P',1),('[',1),(']',1),('\\',1)],
            [('A',1),('S',1),('D',1),('F',1),('G',1),('H',1),('J',1),('K',1),('L',1),(';',1),("'",1)],
            [('⇧',1.5),('Z',1),('X',1),('C',1),('V',1),('B',1),('N',1),('M',1),(',',1),('.',1),('/',1),('⇧',1.5)],
            [('SPACE',7)]
        ],
        'offsets': [0, 0.25, 0.5, 0.75, 2.5],
        'home_keys': ['F','D','S','A','J','K','L',';'],
    },
    'AZERTY': {
        'display': 'AZERTY (French)',
        'rows': [
            [('²',1),('&',1),('é',1),('"',1),("'",1),('(',1),('-',1),('è',1),('_',1),('ç',1),('à',1),(')',1),('=',1)],
            [('A',1),('Z',1),('E',1),('R',1),('T',1),('Y',1),('U',1),('I',1),('O',1),('P',1),('^',1),('$',1),('*',1)],
            [('Q',1),('S',1),('D',1),('F',1),('G',1),('H',1),('J',1),('K',1),('L',1),('M',1),('ù',1)],
            [('⇧',1.5),('W',1),('X',1),('C',1),('V',1),('B',1),('N',1),(',',1),(';',1),(':',1),('!',1),('⇧',1.5)],
            [('SPACE',7)]
        ],
        'offsets': [0, 0.25, 0.5, 0.75, 2.5],
        'home_keys': ['F','D','S','Q','J','K','L','M'],
    },
    'DVORAK': {
        'display': 'DVORAK (Ergonomic)',
        'rows': [
            [('`',1),('1',1),('2',1),('3',1),('4',1),('5',1),('6',1),('7',1),('8',1),('9',1),('0',1),('[',1),(']',1)],
            [("'",1),(',',1),('.',1),('P',1),('Y',1),('F',1),('G',1),('C',1),('R',1),('L',1),('/',1),('=',1)],
            [('A',1),('O',1),('E',1),('U',1),('I',1),('D',1),('H',1),('T',1),('N',1),('S',1),('-',1)],
            [('⇧',1.5),(';',1),('Q',1),('J',1),('K',1),('X',1),('B',1),('M',1),('W',1),('V',1),('Z',1),('⇧',1.5)],
            [('SPACE',7)]
        ],
        'offsets': [0, 0.25, 0.5, 0.75, 2.5],
        'home_keys': ['E','U','I','A','H','T','N','S'],
    },
    'COLEMAK': {
        'display': 'Colemak (Modern)',
        'rows': [
            [('`',1),('1',1),('2',1),('3',1),('4',1),('5',1),('6',1),('7',1),('8',1),('9',1),('0',1),('-',1),('=',1)],
            [('Q',1),('W',1),('F',1),('P',1),('G',1),('J',1),('L',1),('U',1),('Y',1),(';',1),('[',1),(']',1),('\\',1)],
            [('A',1),('R',1),('S',1),('T',1),('D',1),('H',1),('N',1),('E',1),('I',1),('O',1),("'",1)],
            [('⇧',1.5),('Z',1),('X',1),('C',1),('V',1),('B',1),('K',1),('M',1),(',',1),('.',1),('/',1),('⇧',1.5)],
            [('SPACE',7)]
        ],
        'offsets': [0, 0.25, 0.5, 0.75, 2.5],
        'home_keys': ['T','S','R','A','N','E','I','O'],
    },
}

def get_finger(layout_name, key_char):
    if key_char in (' ', 'SPACE'): return 8
    layout = LAYOUTS[layout_name]
    ku = key_char.upper()
    for row in layout['rows']:
        for ci, (lbl, _) in enumerate(row):
            if lbl.upper() == ku or lbl == key_char:
                if ci <= 0: return 0
                if ci == 1: return 1
                if ci == 2: return 2
                if ci <= 4: return 3
                if ci <= 6: return 4
                if ci == 7: return 5
                if ci == 8: return 6
                return 7
    return 8

def find_key_label(layout_name, char):
    if char == ' ': return 'SPACE'
    for row in LAYOUTS[layout_name]['rows']:
        for lbl, _ in row:
            if lbl == char or lbl.lower() == char or lbl.upper() == char:
                return lbl
    return None

# ─── Lesson Generation ────────────────────────────────────────────────────────
WORDS = [
    "the","be","to","of","and","a","in","that","have","it","for","not","on",
    "with","he","as","you","do","at","this","but","his","by","from","they",
    "we","say","her","she","or","an","will","my","one","all","would","there",
    "their","what","so","up","out","if","about","who","get","which","go","me",
    "when","make","can","like","time","no","just","him","know","take","into",
    "year","your","good","some","could","them","see","other","than","then",
    "now","look","only","come","its","over","think","also","back","after",
    "use","two","how","our","work","first","well","way","even","new","want",
    "because","any","these","give","day","most","us","great","between","need",
    "large","often","hand","high","place","find","here","thing","many","home",
    "still","world","long","right","small","part","through","each","much",
    "before","line","end","turn","move","play","run","read","write","learn",
    "type","fast","key","home","row","top","bottom","finger","practice",
]
SENTENCES = [
    "The quick brown fox jumps over the lazy dog.",
    "Pack my box with five dozen liquor jugs.",
    "How vexingly quick daft zebras jump.",
    "The five boxing wizards jump quickly.",
    "Sphinx of black quartz judge my vow.",
    "Two driven jocks help fax my big quiz.",
    "Practice makes perfect when learning to type.",
    "Keep your fingers on the home row keys.",
    "Accuracy is more important than speed at first.",
    "Try to type without looking at the keyboard.",
    "Each finger has its own set of keys to press.",
    "The shift key is used to type capital letters.",
    "Good posture helps you type faster and avoid strain.",
    "Take short breaks to rest your hands and eyes.",
    "Consistent daily practice leads to rapid improvement.",
]

def gen_lesson(layout_name, lesson_type, length=140):
    layout = LAYOUTS[layout_name]
    if lesson_type == 'custom':
        return ''
    if lesson_type == 'home_row':
        keys = [k.lower() for k in layout['home_keys']]
        t = ''.join(random.choice(keys) + (' ' if random.random()<0.18 else '') for _ in range(length))
        return t.strip()
    if lesson_type == 'top_row':
        keys = [lbl.lower() for lbl,_ in layout['rows'][1] if len(lbl)==1 and lbl.isalpha()]
        t = ''.join(random.choice(keys) + (' ' if random.random()<0.18 else '') for _ in range(length))
        return t.strip()
    if lesson_type == 'bottom_row':
        keys = [lbl.lower() for lbl,_ in layout['rows'][3] if len(lbl)==1 and lbl.isalpha()]
        t = ''.join(random.choice(keys) + (' ' if random.random()<0.18 else '') for _ in range(length))
        return t.strip()
    if lesson_type == 'all_letters':
        keys = []
        for row in layout['rows'][1:4]:
            keys += [lbl.lower() for lbl,_ in row if len(lbl)==1 and lbl.isalpha()]
        t = ''.join(random.choice(keys) + (' ' if random.random()<0.18 else '') for _ in range(length))
        return t.strip()
    if lesson_type == 'common_words':
        return ' '.join(random.choices(WORDS, k=24))
    if lesson_type == 'sentences':
        return ' '.join(random.sample(SENTENCES, min(3, len(SENTENCES))))
    if lesson_type == 'numbers':
        keys = [lbl for lbl,_ in layout['rows'][0] if len(lbl)==1]
        t = ''.join(random.choice(keys) + (' ' if random.random()<0.15 else '') for _ in range(length))
        return t.strip()
    return gen_lesson(layout_name, 'common_words', length)

LESSON_TYPES = [
    ('home_row',    '🏠  Home Row',     'Master the home row keys'),
    ('top_row',     '⬆️  Top Row',      'Practice the top letter row'),
    ('bottom_row',  '⬇️  Bottom Row',   'Practice the bottom letter row'),
    ('all_letters', '🔤  All Letters',   'All letter keys combined'),
    ('common_words','📝  Common Words',  'Frequently used English words'),
    ('sentences',   '📖  Sentences',     'Full sentences for real practice'),
    ('numbers',     '🔢  Numbers & Sym', 'Number row and punctuation'),
]

PRACTICE_MODES = [
    ('completion', '📝  Completion', 'Type the full text'),
    ('timed_30',   '⏱  30 Seconds',  'Speed test — 30s'),
    ('timed_60',   '⏱  60 Seconds',  'Speed test — 60s'),
    ('timed_120',  '⏱  2 Minutes',   'Speed test — 120s'),
]

# ─── Custom Widgets ───────────────────────────────────────────────────────────

class KeyWidget(Button):
    key_label = StringProperty('')
    finger_idx = NumericProperty(0)
    is_home = BooleanProperty(False)
    highlighted = BooleanProperty(False)
    pressed_anim = BooleanProperty(False)

    def __init__(self, key_label='', width_units=1, finger_idx=0, is_home=False, on_tap=None, **kw):
        self._on_tap = on_tap
        self.width_units = width_units
        super().__init__(**kw)
        self.key_label = key_label
        self.finger_idx = finger_idx
        self.is_home = is_home
        self.size_hint_x = width_units
        self.size_hint_y = None
        self.height = key_h()
        self.background_normal = ''
        self.background_down = ''
        self.always_release = True
        self.halign = 'center'
        self.valign = 'middle'
        display = key_label if key_label != 'SPACE' else '⎵ SPACE'
        self.text = display
        self.font_size = key_fs(display)
        self._update_color()

    def _update_color(self):
        if self.highlighted:
            self.background_color = (*T('YELLOW')[:3], 0.92)
            self.color = (0.1, 0.1, 0.15, 1)
        elif self.pressed_anim:
            self.background_color = (*T('ACCENT')[:3], 0.85)
            self.color = T('TXT')
        else:
            fc = FINGER_COLS[self.finger_idx] if 0 <= self.finger_idx < 9 else (0.3,0.3,0.4)
            self.background_color = (*fc, 0.45)
            self.color = T('TXT')
        self.canvas.after.clear()
        if self.is_home and not self.highlighted:
            with self.canvas.after:
                Color(1,1,1,0.6)
                RoundedRectangle(pos=(self.center_x-dp(6), self.y+dp(4)),
                                 size=(dp(12),dp(3)), radius=[dp(1.5)])

    def set_highlighted(self, val):
        self.highlighted = val; self._update_color()

    def flash_press(self):
        self.pressed_anim = True; self._update_color()
        Clock.schedule_once(lambda dt: self._unflash(), 0.10)

    def _unflash(self):
        self.pressed_anim = False; self._update_color()

    def on_press(self):
        if self._on_tap: self._on_tap(self.key_label)

    def on_highlighted(self, *a): self._update_color()


class VisualKeyboard(BoxLayout):
    layout_name = StringProperty('QWERTY')
    highlight_char = StringProperty('')

    def __init__(self, **kw):
        super().__init__(orientation='vertical', spacing=dp(3), padding=dp(4), **kw)
        self.key_widgets = {}
        self._on_key_tap = None
        self.size_hint_y = None
        self.height = key_h() * 5 + dp(20)
        self.bind(layout_name=self._rebuild, highlight_char=self._update_highlight)
        self._rebuild()

    def set_tap_callback(self, cb):
        self._on_key_tap = cb

    def _rebuild(self, *a):
        self.clear_widgets(); self.key_widgets = {}
        layout = LAYOUTS.get(self.layout_name, LAYOUTS['QWERTY'])
        home_keys = set(layout.get('home_keys', []))
        offsets = layout.get('offsets', [0]*5)
        total_units = max(sum(w for _,w in row)+offsets[i] for i,row in enumerate(layout['rows']))
        for ri, row in enumerate(layout['rows']):
            kh = key_h()
            row_box = BoxLayout(spacing=dp(2), size_hint_y=None, height=kh)
            off = offsets[ri] if ri < len(offsets) else 0
            if off > 0: row_box.add_widget(Widget(size_hint_x=off))
            for lbl, wu in row:
                fi = get_finger(self.layout_name, lbl)
                ih = lbl in home_keys
                kw = KeyWidget(key_label=lbl, width_units=wu, finger_idx=fi, is_home=ih, on_tap=self._handle_tap)
                self.key_widgets[lbl] = kw
                row_box.add_widget(kw)
            used = off + sum(w for _,w in row)
            if used < total_units: row_box.add_widget(Widget(size_hint_x=total_units-used))
            self.add_widget(row_box)
        self._update_highlight()

    def _handle_tap(self, label):
        if self._on_key_tap:
            ch = ' ' if label == 'SPACE' else label.lower()
            self._on_key_tap(ch)

    def _update_highlight(self, *a):
        for lbl, kw in self.key_widgets.items(): kw.set_highlighted(False)
        ch = self.highlight_char
        if not ch: return
        target = find_key_label(self.layout_name, ch)
        if target and target in self.key_widgets:
            self.key_widgets[target].set_highlighted(True)
        if ch.isupper():
            for lbl, kw in self.key_widgets.items():
                if lbl == '⇧': kw.set_highlighted(True)

    def flash_key(self, char):
        target = find_key_label(self.layout_name, char)
        if target and target in self.key_widgets:
            self.key_widgets[target].flash_press()

    def refresh_theme(self):
        for kw in self.key_widgets.values():
            kw._update_color()


class RoundedCard(BoxLayout):
    """A card with rounded corners and theme background."""
    def __init__(self, color_key='CARD', radius=dp(10), **kw):
        super().__init__(**kw)
        self._color_key = color_key
        self._radius = radius
        with self.canvas.before:
            Color(*T(color_key))
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, inst, val):
        self._bg.pos = inst.pos; self._bg.size = inst.size

    def refresh_theme(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*T(self._color_key))
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[self._radius])


class StatBar(Widget):
    """Horizontal bar showing a stat percentage."""
    def __init__(self, label='', value=0, max_val=100, color_key='GREEN', **kw):
        super().__init__(**kw)
        self._label = label; self._value = value; self._max = max_val; self._ck = color_key
        self.size_hint_y = None; self.height = dp(28)
        self.bind(size=self._draw, pos=self._draw)

    def _draw(self, *a):
        self.canvas.after.clear()
        with self.canvas.after:
            Color(*T('CARD3'))
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(4)])
            pct = min(1.0, self._value / max(1, self._max))
            Color(*T(self._ck))
            RoundedRectangle(pos=self.pos, size=(self.width*pct, self.height), radius=[dp(4)])

    def set_value(self, value, max_val=None):
        self._value = value
        if max_val is not None: self._max = max_val
        self._draw()


# ─── Screens ──────────────────────────────────────────────────────────────────

class MenuScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._build_ui()

    def _build_ui(self):
        self.root_box = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(8))
        scroll = ScrollView(bar_width=dp(4))
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
        content.bind(minimum_height=content.setter('height'))

        # Title
        title = Label(text='⌨️  Keyboard Trainer', font_size=sp(30), size_hint_y=None,
                       height=dp(55), color=T('TXT'))
        content.add_widget(title)
        subtitle = Label(text='Learn to type fast & accurately on any layout',
                          font_size=sp(13), size_hint_y=None, height=dp(26), color=T('DIM'))
        content.add_widget(subtitle)

        # Layout selection
        content.add_widget(self._section('Select Keyboard Layout'))
        self._layout_btns = {}
        layout_grid = GridLayout(cols=2, spacing=dp(6), size_hint_y=None, height=dp(44)*2+dp(6))
        sel_layout = settings_mgr.get('layout', 'QWERTY')
        for name, data in LAYOUTS.items():
            b = ToggleButton(text=data['display'], group='layout', font_size=sp(12),
                             background_normal='', background_down='', background_color=T('CARD2'), color=T('TXT'))
            if name == sel_layout: b.state = 'down'; b.background_color = T('ACCENT')
            b.bind(state=lambda s,v,n=name: self._pick('layout',n,v))
            b.bind(state=self._style_toggle)
            self._layout_btns[name] = b
            layout_grid.add_widget(b)
        content.add_widget(layout_grid)

        # Lesson selection
        content.add_widget(self._section('Choose Lesson'))
        self._lesson_btns = {}
        lesson_grid = GridLayout(cols=2, spacing=dp(5), size_hint_y=None)
        sel_lesson = settings_mgr.get('lesson', 'home_row')
        for ltype, lname, ldesc in LESSON_TYPES:
            b = ToggleButton(text=lname, group='lesson', font_size=sp(11),
                             background_normal='', background_down='', background_color=T('CARD2'),
                             color=T('TXT'), size_hint_y=None, height=dp(42))
            if ltype == sel_lesson: b.state = 'down'; b.background_color = T('ACCENT')
            b.bind(state=lambda s,v,t=ltype: self._pick('lesson',t,v))
            b.bind(state=self._style_toggle)
            self._lesson_btns[ltype] = b
            lesson_grid.add_widget(b)
        lesson_grid.height = dp(42)*4 + dp(15)
        content.add_widget(lesson_grid)

        # Practice mode
        content.add_widget(self._section('Practice Mode'))
        self._mode_btns = {}
        mode_grid = GridLayout(cols=2, spacing=dp(5), size_hint_y=None, height=dp(42)*2+dp(5))
        sel_mode = settings_mgr.get('mode', 'completion')
        for mtype, mname, mdesc in PRACTICE_MODES:
            b = ToggleButton(text=mname, group='mode', font_size=sp(11),
                             background_normal='', background_down='', background_color=T('CARD2'),
                             color=T('TXT'), size_hint_y=None, height=dp(42))
            if mtype == sel_mode: b.state = 'down'; b.background_color = T('ACCENT')
            b.bind(state=lambda s,v,t=mtype: self._pick('mode',t,v))
            b.bind(state=self._style_toggle)
            self._mode_btns[mtype] = b
            mode_grid.add_widget(b)
        content.add_widget(mode_grid)

        # Buttons
        content.add_widget(Widget(size_hint_y=None, height=dp(12)))
        start_btn = Button(text='▶  Start Typing', font_size=sp(18), size_hint_y=None, height=btn_h(),
                           background_normal='', background_down='', background_color=T('ACCENT'), color=T('TXT'))
        start_btn.bind(on_press=self._start)
        content.add_widget(start_btn)

        custom_btn = Button(text='✏️  Custom Text Practice', font_size=sp(14), size_hint_y=None, height=dp(44),
                            background_normal='', background_down='', background_color=T('CARD3'), color=T('TXT'))
        custom_btn.bind(on_press=lambda *a: setattr(self.manager, 'current', 'custom'))
        content.add_widget(custom_btn)

        btn_row = BoxLayout(spacing=dp(8), size_hint_y=None, height=dp(44))
        stats_btn = Button(text='📊  Statistics', font_size=sp(13),
                           background_normal='', background_down='', background_color=T('CARD2'), color=T('TXT'))
        stats_btn.bind(on_press=lambda *a: setattr(self.manager, 'current', 'stats'))
        settings_btn = Button(text='⚙️  Settings', font_size=sp(13),
                              background_normal='', background_down='', background_color=T('CARD2'), color=T('TXT'))
        settings_btn.bind(on_press=lambda *a: setattr(self.manager, 'current', 'settings'))
        btn_row.add_widget(stats_btn); btn_row.add_widget(settings_btn)
        content.add_widget(btn_row)

        scroll.add_widget(content)
        self.root_box.add_widget(scroll)
        self.add_widget(self.root_box)

    def _section(self, text):
        l = Label(text=text, font_size=sp(14), size_hint_y=None, height=dp(28),
                  halign='left', valign='middle', color=T('ACCENT'))
        l.bind(size=lambda *a: l.setter('text_size')(l, l.size))
        return l

    def _style_toggle(self, btn, val):
        btn.background_color = T('ACCENT') if val == 'down' else T('CARD2')

    def _pick(self, key, name, state):
        if state == 'down':
            settings_mgr.set(key, name)

    def _start(self, *a):
        app = App.get_running_app()
        app.current_layout = settings_mgr.get('layout', 'QWERTY')
        app.current_lesson = settings_mgr.get('lesson', 'home_row')
        app.current_mode = settings_mgr.get('mode', 'completion')
        ts = self.manager.get_screen('typing')
        ts.start_lesson(app.current_layout, app.current_lesson, app.current_mode)
        self.manager.current = 'typing'

    def refresh_theme(self):
        # Rebuild would be complex; user can restart for full theme change
        pass


class TypingScreen(Screen):
    wpm = NumericProperty(0)
    accuracy_p = NumericProperty(100)
    elapsed = NumericProperty(0)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.layout_name = 'QWERTY'
        self.lesson_text = ''
        self.typed = []
        self.char_idx = 0
        self.start_time = None
        self.errors = 0
        self.total_keystrokes = 0
        self.streak = 0
        self._keyboard = None
        self._timer_event = None
        self._finished = False
        self.mode = 'completion'
        self.timer_secs = 0
        self._build_ui()

    def _build_ui(self):
        self.root_box = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(4))

        # Top bar
        top = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        back_btn = Button(text='← Back', size_hint_x=None, width=dp(76),
                          background_normal='', background_down='', background_color=T('CARD2'), color=T('TXT'), font_size=sp(12))
        back_btn.bind(on_press=self._go_back)
        top.add_widget(back_btn)
        self.lbl_lesson = Label(text='', font_size=sp(12), color=T('DIM'), halign='left')
        self.lbl_lesson.bind(size=lambda *a: self.lbl_lesson.setter('text_size')(self.lbl_lesson, self.lbl_lesson.size))
        top.add_widget(self.lbl_lesson)

        stat_box = BoxLayout(size_hint_x=None, width=dp(300) if not IS_MOBILE else dp(240), spacing=dp(4))
        self.lbl_wpm = Label(text='WPM: 0', font_size=sp(13), color=T('GREEN'), bold=True)
        self.lbl_acc = Label(text='ACC: 100%', font_size=sp(13), color=T('ACCENT'), bold=True)
        self.lbl_time = Label(text='⏱ 0:00', font_size=sp(13), color=T('ORANGE'))
        self.lbl_streak = Label(text='🔥 0', font_size=sp(13), color=T('YELLOW'))
        stat_box.add_widget(self.lbl_wpm); stat_box.add_widget(self.lbl_acc)
        stat_box.add_widget(self.lbl_time); stat_box.add_widget(self.lbl_streak)
        top.add_widget(stat_box)
        self.root_box.add_widget(top)

        # Progress bar
        self.progress = Widget(size_hint_y=None, height=dp(6))
        self.root_box.add_widget(self.progress)

        # Finger hint
        self.lbl_finger = Label(text='', font_size=sp(13), size_hint_y=None, height=dp(24), color=T('DIM'))
        self.root_box.add_widget(self.lbl_finger)

        # Typing area
        th = typing_h()
        typing_frame = BoxLayout(size_hint_y=None, height=th, padding=dp(10))
        with typing_frame.canvas.before:
            Color(*T('CARD'))
            self._typing_bg = RoundedRectangle(pos=typing_frame.pos, size=typing_frame.size, radius=[dp(10)])
        typing_frame.bind(pos=self._upd_bg, size=self._upd_bg)
        self.lbl_text = Label(text='', font_size=sp(18 if IS_MOBILE else 20), halign='left', valign='middle',
                              markup=True, color=T('TXT'))
        self.lbl_text.bind(size=lambda *a: self.lbl_text.setter('text_size')(self.lbl_text, self.lbl_text.size))
        typing_frame.add_widget(self.lbl_text)
        self.root_box.add_widget(typing_frame)

        self.root_box.add_widget(Widget(size_hint_y=0.2))

        # Visual keyboard
        self.keyboard = VisualKeyboard()
        self.keyboard.set_tap_callback(self._handle_tap)
        self.root_box.add_widget(self.keyboard)

        # Hint
        hint_text = 'Tap the highlighted key or type on your keyboard.' if IS_MOBILE else \
                    'Type the highlighted character. Press Escape to quit.'
        self.lbl_hint = Label(text=hint_text, font_size=sp(10), size_hint_y=None, height=dp(20), color=T('DIM'))
        self.root_box.add_widget(self.lbl_hint)

        self.add_widget(self.root_box)

    def _upd_bg(self, inst, val):
        self._typing_bg.pos = inst.pos; self._typing_bg.size = inst.size

    def start_lesson(self, layout_name, lesson_type, mode='completion', custom_text=''):
        self.layout_name = layout_name
        self.mode = mode
        self.timer_secs = 0
        if mode.startswith('timed_'):
            self.timer_secs = int(mode.split('_')[1])
            self.lesson_text = gen_lesson(layout_name, lesson_type, 500)
        elif lesson_type == 'custom':
            self.lesson_text = custom_text if custom_text else 'The quick brown fox jumps over the lazy dog.'
        else:
            self.lesson_text = gen_lesson(layout_name, lesson_type, 140)

        self.typed = []; self.char_idx = 0; self.start_time = None
        self.errors = 0; self.total_keystrokes = 0; self.streak = 0
        self._finished = False; self.wpm = 0; self.accuracy_p = 100; self.elapsed = 0

        mode_disp = mode.replace('_',' ').title()
        self.lbl_lesson.text = f'{LAYOUTS[layout_name]["display"]}  •  {lesson_type.replace("_"," ").title()}  •  {mode_disp}'
        self.keyboard.layout_name = layout_name
        self._refresh_display()
        self._start_listening()

        if self._timer_event: self._timer_event.cancel()
        self._timer_event = Clock.schedule_interval(self._tick, 0.25)

    def _start_listening(self):
        self._stop_listening()
        try:
            self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
            self._keyboard.bind(on_key_down=self._on_key_down)
        except: pass

    def _stop_listening(self):
        if self._keyboard:
            try: self._keyboard.unbind(on_key_down=self._on_key_down); self._keyboard.release()
            except: pass
            self._keyboard = None

    def _keyboard_closed(self): self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        self._process_key(keycode, text, modifiers)

    def _process_key(self, keycode, text, modifiers):
        if self._finished: return
        key_name = keycode[1] if isinstance(keycode, (list,tuple)) and len(keycode)>1 else ''
        if key_name == 'escape': self._go_back(); return
        if key_name == 'backspace': self._handle_backspace(); return
        skip = ('lshift','rshift','shift','capslock','tab','ctrl','lctrl','rctrl',
                'alt','lalt','ralt','super','lsuper','rsuper','alt-gr',
                'up','down','left','right','insert','delete','home','end',
                'pageup','pagedown','numlock','scrolllock','print','sysreq','pause','break')
        skip += tuple(f'f{i}' for i in range(1,13))
        if key_name in skip: return
        if text and len(text) == 1:
            self._handle_char(text)

    def _handle_tap(self, char):
        if not self._finished: self._handle_char(char)

    def _handle_char(self, ch):
        if self.char_idx >= len(self.lesson_text): return
        if self.start_time is None: self.start_time = time.time()

        expected = self.lesson_text[self.char_idx]
        correct = (ch == expected)
        self.typed.append((ch, correct))
        self.total_keystrokes += 1

        if correct:
            self.streak += 1
            sound_mgr.play('click')
            if settings_mgr.get('vibration') and HAS_VIBRATOR: vibrate(15)
        else:
            self.errors += 1; self.streak = 0
            sound_mgr.play('error')
            if settings_mgr.get('vibration') and HAS_VIBRATOR: vibrate(40)

        self.keyboard.flash_key(ch if correct else expected)
        self.char_idx += 1
        self._refresh_display()
        self._update_stats()

        if self.mode == 'completion' and self.char_idx >= len(self.lesson_text):
            self._finish()

    def _handle_backspace(self):
        if self.char_idx > 0 and self.typed:
            self.char_idx -= 1
            ch, correct = self.typed.pop()
            self.total_keystrokes -= 1
            if not correct: self.errors -= 1
            self.streak = 0
            self._refresh_display(); self._update_stats()

    def _refresh_display(self):
        text = self.lesson_text; parts = []
        for i, (ch, correct) in enumerate(self.typed):
            c = text[i]
            if correct:
                parts.append(f'[color=22dd55]{self._esc(c)}[/color]')
            else:
                parts.append(f'[color=ff3333][s]{self._esc(c)}[/s][/color]')
        if self.char_idx < len(text):
            cur = text[self.char_idx]
            parts.append(f'[u][color=ffd822]{self._esc(cur)}[/color][/u]')
            self.keyboard.highlight_char = cur
            fi = get_finger(self.layout_name, cur)
            self.lbl_finger.text = f'👉 {FINGER_NAMES[fi]}' if 0<=fi<9 else ''
            self.lbl_finger.color = (*FINGER_COLS[fi],1) if 0<=fi<9 else T('DIM')
        else:
            self.keyboard.highlight_char = ''
            self.lbl_finger.text = '✅ Complete!'
            self.lbl_finger.color = T('GREEN')

        for i in range(self.char_idx+1, min(len(text), self.char_idx+80)):
            parts.append(f'[color=707078]{self._esc(text[i])}[/color]')
        self.lbl_text.text = ''.join(parts)

        # Progress bar
        self.progress.canvas.after.clear()
        with self.progress.canvas.after:
            Color(*T('CARD3'))
            RoundedRectangle(pos=self.progress.pos, size=self.progress.size, radius=[dp(3)])
            if self.mode.startswith('timed_') and self.start_time:
                elapsed_s = time.time() - self.start_time
                pct = min(1.0, elapsed_s / self.timer_secs)
                Color(*T('ORANGE'))
            else:
                pct = self.char_idx / max(1, len(text))
                Color(*T('GREEN'))
            RoundedRectangle(pos=self.progress.pos,
                             size=(self.width*pct, self.progress.height), radius=[dp(3)])

    @staticmethod
    def _esc(ch):
        return ch.replace('&','&amp;').replace('[','&bl;').replace(']','&br;')

    def _update_stats(self):
        if self.start_time is None:
            self.lbl_wpm.text = 'WPM: 0'; self.lbl_acc.text = 'ACC: 100%'; return
        elapsed = max(0.1, time.time()-self.start_time)
        correct_chars = sum(1 for _,ok in self.typed if ok)
        wpm = (correct_chars/5)/(elapsed/60)
        acc = (correct_chars/max(1,self.total_keystrokes))*100
        self.wpm = wpm; self.accuracy_p = acc
        self.lbl_wpm.text = f'WPM: {int(wpm)}'
        self.lbl_wpm.color = T('GREEN') if wpm>=30 else T('ORANGE') if wpm>=15 else T('RED')
        self.lbl_acc.text = f'ACC: {acc:.1f}%'
        self.lbl_acc.color = T('GREEN') if acc>=95 else T('ORANGE') if acc>=85 else T('RED')
        self.lbl_streak.text = f'🔥 {self.streak}'

    def _tick(self, dt):
        if self.start_time is None:
            if self.mode.startswith('timed_'):
                self.lbl_time.text = f'⏱ 0:{self.timer_secs:02d}'
            else:
                self.lbl_time.text = '⏱ 0:00'
            return
        elapsed_s = time.time() - self.start_time
        if self.mode.startswith('timed_'):
            remaining = max(0, self.timer_secs - elapsed_s)
            m, s = divmod(int(remaining), 60)
            self.lbl_time.text = f'⏱ {m}:{s:02d}'
            self.lbl_time.color = T('RED') if remaining < 10 else T('ORANGE')
            self._refresh_display()
            if remaining <= 0 and not self._finished:
                self._finish()
        else:
            m, s = divmod(int(elapsed_s), 60)
            self.lbl_time.text = f'⏱ {m}:{s:02d}'
        self.elapsed = int(elapsed_s)
        self._update_stats()

    def _finish(self):
        self._finished = True
        if self._timer_event: self._timer_event.cancel()
        sound_mgr.play('done')
        if settings_mgr.get('vibration') and HAS_VIBRATOR: vibrate(80)

        elapsed = max(0.1, time.time()-self.start_time) if self.start_time else 1
        correct = sum(1 for _,ok in self.typed if ok)
        wpm = (correct/5)/(elapsed/60)
        acc = (correct/max(1,self.total_keystrokes))*100

        app = App.get_running_app()
        app.save_stat(self.layout_name, settings_mgr.get('lesson','home_row'), wpm, acc, elapsed)

        rs = self.manager.get_screen('results')
        rs.set_results(wpm, acc, elapsed, correct, self.errors, self.total_keystrokes, self.layout_name)
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'results'), 0.6)

    def _go_back(self, *a):
        self._stop_listening()
        if self._timer_event: self._timer_event.cancel()
        self.manager.current = 'menu'


class ResultsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._build_ui()

    def _build_ui(self):
        self.root = BoxLayout(orientation='vertical', padding=dp(24), spacing=dp(12))
        self.lbl_title = Label(text='🎉  Lesson Complete!', font_size=sp(26),
                               size_hint_y=None, height=dp(55), color=T('YELLOW'))
        self.root.add_widget(self.lbl_title)

        self.stats_grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(220))
        self.root.add_widget(self.stats_grid)

        self.root.add_widget(Widget(size_hint_y=1))

        self.lbl_rating = Label(text='', font_size=sp(20), size_hint_y=None, height=dp(50), color=T('TXT'))
        self.root.add_widget(self.lbl_rating)

        self.lbl_stars = Label(text='', font_size=sp(32), size_hint_y=None, height=dp(50), color=T('YELLOW'))
        self.root.add_widget(self.lbl_stars)

        btn_box = BoxLayout(spacing=dp(10), size_hint_y=None, height=btn_h())
        retry_btn = Button(text='🔄  Try Again', font_size=sp(15), background_normal='',
                           background_down='', background_color=T('ACCENT'), color=T('TXT'))
        retry_btn.bind(on_press=self._retry)
        menu_btn = Button(text='🏠  Menu', font_size=sp(15), background_normal='',
                          background_down='', background_color=T('CARD2'), color=T('TXT'))
        menu_btn.bind(on_press=self._menu)
        btn_box.add_widget(retry_btn); btn_box.add_widget(menu_btn)
        self.root.add_widget(btn_box)
        self.add_widget(self.root)

    def set_results(self, wpm, acc, elapsed, correct, errors, total, layout):
        self.stats_grid.clear_widgets()
        stats = [
            ('⌨️ Layout',     LAYOUTS[layout]['display']),
            ('⚡ Speed',       f'{int(wpm)} WPM'),
            ('🎯 Accuracy',   f'{acc:.1f}%'),
            ('⏱ Time',        f'{int(elapsed//60)}:{int(elapsed%60):02d}'),
            ('✅ Correct',     str(correct)),
            ('❌ Errors',      str(errors)),
            ('📊 Keystrokes',  str(total)),
            ('📈 Chars/min',   f'{int(correct/max(1,elapsed)*60)}'),
        ]
        for label, value in stats:
            l = Label(text=label, font_size=sp(13), color=T('DIM'), halign='right', valign='middle')
            l.bind(size=lambda *a,w=l: w.setter('text_size')(w, w.size))
            v = Label(text=value, font_size=sp(15), color=T('TXT'), bold=True, halign='left', valign='middle')
            v.bind(size=lambda *a,w=v: w.setter('text_size')(v, v.size))
            self.stats_grid.add_widget(l); self.stats_grid.add_widget(v)

        # Star rating
        if acc >= 98 and wpm >= 50:   stars, rating, rc = 5, '🏆 PERFECT! Typing master!', T('YELLOW')
        elif acc >= 95 and wpm >= 35: stars, rating, rc = 4, '⭐ Excellent!', T('GREEN')
        elif acc >= 90:               stars, rating, rc = 3, '👍 Good job!', T('ACCENT')
        elif acc >= 80:               stars, rating, rc = 2, '💪 Keep at it!', T('ORANGE')
        else:                         stars, rating, rc = 1, '📚 Practice more!', T('RED')
        self.lbl_rating.text = rating; self.lbl_rating.color = rc
        self.lbl_stars.text = '★' * stars + '☆' * (5-stars)

        # Compare with best
        app = App.get_running_app()
        best = app.get_best_stat(layout)
        if best and best.get('wpm', 0) > 0:
            diff = int(wpm) - int(best.get('wpm', 0))
            if diff > 0:
                self.lbl_rating.text += f'  (+{diff} WPM vs best!)'

    def _retry(self, *a):
        app = App.get_running_app()
        ts = self.manager.get_screen('typing')
        ts.start_lesson(app.current_layout, settings_mgr.get('lesson','home_row'), app.current_mode)
        self.manager.current = 'typing'

    def _menu(self, *a):
        self.manager.current = 'menu'


class StatsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._build_ui()

    def _build_ui(self):
        self.root = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(8))
        header = BoxLayout(size_hint_y=None, height=dp(44))
        back_btn = Button(text='← Back', size_hint_x=None, width=dp(76),
                          background_normal='', background_down='', background_color=T('CARD2'), color=T('TXT'), font_size=sp(12))
        back_btn.bind(on_press=lambda *a: setattr(self.manager, 'current', 'menu'))
        header.add_widget(back_btn)
        header.add_widget(Label(text='📊  Your Statistics', font_size=sp(20), color=T('TXT')))
        self.root.add_widget(header)

        # Summary
        self.summary_box = BoxLayout(size_hint_y=None, height=dp(80), spacing=dp(6))
        self.root.add_widget(self.summary_box)

        self.scroll = ScrollView()
        self.stats_content = GridLayout(cols=1, spacing=dp(6), size_hint_y=None, padding=dp(4))
        self.stats_content.bind(minimum_height=self.stats_content.setter('height'))
        self.scroll.add_widget(self.stats_content)
        self.root.add_widget(self.scroll)

        clear_btn = Button(text='🗑  Clear All Stats', size_hint_y=None, height=dp(42),
                           background_normal='', background_down='', background_color=T('RED'), color=T('TXT'), font_size=sp(12))
        clear_btn.bind(on_press=self._clear_stats)
        self.root.add_widget(clear_btn)
        self.add_widget(self.root)

    def on_pre_enter(self, *a):
        self._refresh()

    def _refresh(self):
        # Summary
        self.summary_box.clear_widgets()
        app = App.get_running_app()
        stats = app.load_stats()

        if not stats:
            self.summary_box.add_widget(Label(text='No statistics yet.\nComplete a lesson to see your progress!',
                                              font_size=sp(13), color=T('DIM')))
        else:
            wpms = [s.get('wpm',0) for s in stats]
            accs = [s.get('acc',0) for s in stats]
            total_sessions = len(stats)
            avg_wpm = sum(wpms)/len(wpms)
            best_wpm = max(wpms)
            avg_acc = sum(accs)/len(accs)
            for label, val in [('Sessions', str(total_sessions)), ('Avg WPM', f'{avg_wpm:.0f}'),
                               ('Best WPM', f'{best_wpm:.0f}'), ('Avg Acc', f'{avg_acc:.1f}%')]:
                card = BoxLayout(orientation='vertical', padding=dp(4))
                with card.canvas.before:
                    Color(*T('CARD'))
                    bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(6)])
                card.bind(pos=lambda i,bg=bg: setattr(bg,'pos',i.pos), size=lambda i,bg=bg: setattr(bg,'size',i.size))
                l = Label(text=label, font_size=sp(9), color=T('DIM'), size_hint_y=0.4)
                v = Label(text=val, font_size=sp(16), color=T('TXT'), bold=True, size_hint_y=0.6)
                card.add_widget(l); card.add_widget(v)
                self.summary_box.add_widget(card)

        # History
        self.stats_content.clear_widgets()
        if not stats:
            return

        for entry in reversed(stats[-30:]):
            box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(64), padding=dp(6), spacing=dp(1))
            with box.canvas.before:
                Color(*T('CARD'))
                bg = RoundedRectangle(pos=box.pos, size=box.size, radius=[dp(8)])
            box.bind(pos=lambda i,bg=bg: setattr(bg,'pos',i.pos), size=lambda i,bg=bg: setattr(bg,'size',i.size))

            layout_disp = LAYOUTS.get(entry.get('layout',''),{}).get('display', entry.get('layout',''))
            line1 = f'{layout_disp}  •  {entry.get("lesson","").replace("_"," ").title()}  •  {entry.get("date","")}'
            wpm_val = entry.get('wpm',0); acc_val = entry.get('acc',0)
            line2 = f'WPM: {int(wpm_val)}   |   Accuracy: {acc_val:.1f}%   |   Time: {int(entry.get("time",0)//60)}:{int(entry.get("time",0)%60):02d}'

            l1 = Label(text=line1, font_size=sp(9), color=T('DIM'), halign='left', valign='middle', size_hint_y=None, height=dp(18))
            l1.bind(size=lambda *a,w=l1: w.setter('text_size')(w, w.size))

            # WPM bar
            bar_row = BoxLayout(size_hint_y=None, height=dp(20), spacing=dp(4))
            l2 = Label(text=f'{int(wpm_val)}', font_size=sp(11), color=T('GREEN') if wpm_val>=30 else T('ORANGE'),
                       size_hint_x=None, width=dp(32), halign='right', valign='middle')
            l2.bind(size=lambda *a,w=l2: w.setter('text_size')(w, w.size))
            bar = StatBar(value=wpm_val, max_val=80, color_key='GREEN')
            bar_row.add_widget(l2); bar_row.add_widget(bar)

            l3 = Label(text=line2, font_size=sp(10), color=T('TXT'), halign='left', valign='middle', size_hint_y=None, height=dp(18))
            l3.bind(size=lambda *a,w=l3: w.setter('text_size')(w, w.size))

            box.add_widget(l1); box.add_widget(bar_row); box.add_widget(l3)
            self.stats_content.add_widget(box)

    def _clear_stats(self, *a):
        App.get_running_app().clear_stats()
        self._refresh()


class SettingsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._build_ui()

    def _build_ui(self):
        self.root = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10))
        header = BoxLayout(size_hint_y=None, height=dp(44))
        back_btn = Button(text='← Back', size_hint_x=None, width=dp(76),
                          background_normal='', background_down='', background_color=T('CARD2'), color=T('TXT'), font_size=sp(12))
        back_btn.bind(on_press=lambda *a: setattr(self.manager, 'current', 'menu'))
        header.add_widget(back_btn)
        header.add_widget(Label(text='⚙️  Settings', font_size=sp(20), color=T('TXT')))
        self.root.add_widget(header)

        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        content.bind(minimum_height=content.setter('height'))

        # Theme
        content.add_widget(self._section('Theme'))
        self._theme_btns = {}
        theme_grid = GridLayout(cols=2, spacing=dp(6), size_hint_y=None, height=dp(42)*2+dp(6))
        cur_theme = settings_mgr.get('theme', 'dark')
        theme_names = {'dark':'🌙 Dark','midnight':'🌌 Midnight','ocean':'🌊 Ocean','warm':'🔥 Warm'}
        for tname, tdisp in theme_names.items():
            b = ToggleButton(text=tdisp, group='theme', font_size=sp(12),
                             background_normal='', background_down='', background_color=T('CARD2'), color=T('TXT'))
            if tname == cur_theme: b.state = 'down'; b.background_color = T('ACCENT')
            b.bind(state=lambda s,v,t=tname: self._pick_theme(t,v))
            b.bind(state=self._style_toggle)
            self._theme_btns[tname] = b
            theme_grid.add_widget(b)
        content.add_widget(theme_grid)

        # Sound
        content.add_widget(self._section('Sound & Feedback'))
        sound_row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        self._sound_btn = ToggleButton(
            text='🔊 Sound: ON' if settings_mgr.get('sound',True) else '🔇 Sound: OFF',
            group='sound', font_size=sp(13),
            background_normal='', background_down='', background_color=T('ACCENT') if settings_mgr.get('sound',True) else T('CARD2'),
            color=T('TXT'))
        self._sound_btn.bind(on_press=self._toggle_sound)
        sound_row.add_widget(self._sound_btn)

        self._vibrate_btn = ToggleButton(
            text='📳 Vibrate: ON' if settings_mgr.get('vibration',True) else '📴 Vibrate: OFF',
            group='vibrate', font_size=sp(13),
            background_normal='', background_down='',
            background_color=T('ACCENT') if settings_mgr.get('vibration',True) else T('CARD2'),
            color=T('TXT'))
        self._vibrate_btn.bind(on_press=self._toggle_vibrate)
        if not HAS_VIBRATOR:
            self._vibrate_btn.disabled = True
            self._vibrate_btn.text = '📳 Vibrate: N/A'
        sound_row.add_widget(self._vibrate_btn)
        content.add_widget(sound_row)

        # About
        content.add_widget(self._section('About'))
        about = Label(text='Keyboard Trainer v2.0\n\nLearn to type fast and accurately\non QWERTY, AZERTY, DVORAK & Colemak.\n\n'
                           'Works on Desktop and Android.\nTap the on-screen keyboard or\ntype on a physical keyboard.',
                      font_size=sp(12), color=T('DIM'), halign='left', valign='top',
                      size_hint_y=None, height=dp(140))
        about.bind(size=lambda *a,w=about: w.setter('text_size')(w, w.size))
        content.add_widget(about)

        scroll.add_widget(content)
        self.root.add_widget(scroll)
        self.add_widget(self.root)

    def _section(self, text):
        l = Label(text=text, font_size=sp(14), size_hint_y=None, height=dp(28),
                  halign='left', valign='middle', color=T('ACCENT'))
        l.bind(size=lambda *a: l.setter('text_size')(l, l.size))
        return l

    def _style_toggle(self, btn, val):
        btn.background_color = T('ACCENT') if val == 'down' else T('CARD2')

    def _pick_theme(self, tname, state):
        if state == 'down':
            settings_mgr.set('theme', tname)
            # Update window background
            Window.clearcolor = T('BG')

    def _toggle_sound(self, *a):
        new_val = not settings_mgr.get('sound', True)
        settings_mgr.set('sound', new_val)
        self._sound_btn.text = '🔊 Sound: ON' if new_val else '🔇 Sound: OFF'
        self._sound_btn.background_color = T('ACCENT') if new_val else T('CARD2')

    def _toggle_vibrate(self, *a):
        new_val = not settings_mgr.get('vibration', True)
        settings_mgr.set('vibration', new_val)
        self._vibrate_btn.text = '📳 Vibrate: ON' if new_val else '📴 Vibrate: OFF'
        self._vibrate_btn.background_color = T('ACCENT') if new_val else T('CARD2')


class CustomTextScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._build_ui()

    def _build_ui(self):
        self.root = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10))
        header = BoxLayout(size_hint_y=None, height=dp(44))
        back_btn = Button(text='← Back', size_hint_x=None, width=dp(76),
                          background_normal='', background_down='', background_color=T('CARD2'), color=T('TXT'), font_size=sp(12))
        back_btn.bind(on_press=lambda *a: setattr(self.manager, 'current', 'menu'))
        header.add_widget(back_btn)
        header.add_widget(Label(text='✏️  Custom Text', font_size=sp(20), color=T('TXT')))
        self.root.add_widget(header)

        info = Label(text='Enter any text below to practice typing it.\nYou can paste from clipboard or type your own.',
                     font_size=sp(12), color=T('DIM'), size_hint_y=None, height=dp(44), halign='left', valign='middle')
        info.bind(size=lambda *a,w=info: w.setter('text_size')(w, w.size))
        self.root.add_widget(info)

        self.text_input = TextInput(
            hint_text='Type or paste your practice text here...',
            multiline=True, font_size=sp(16),
            size_hint_y=None, height=dp(200),
            background_color=T('CARD2'), foreground_color=T('TXT'),
            cursor_color=T('ACCENT'), hint_text_color=T('DIM'))
        self.root.add_widget(self.text_input)

        # Preset texts
        content.add_widget = None  # placeholder logic removed
        self.root.add_widget(Label(text='Quick Presets:', font_size=sp(12), color=T('ACCENT'),
                                   size_hint_y=None, height=dp(24), halign='left'))
        preset_row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(6))
        for pname, ptext in [('Pangram','The quick brown fox jumps over the lazy dog.'),
                             ('Code','def hello_world(): print("Hello, World!")'),
                             ('Numbers','1 2 3 4 5 6 7 8 9 0')]:
            b = Button(text=pname, font_size=sp(11), background_normal='', background_down='',
                       background_color=T('CARD3'), color=T('TXT'))
            b.bind(on_press=lambda *a, t=ptext: self._set_preset(t))
            preset_row.add_widget(b)
        self.root.add_widget(preset_row)

        self.root.add_widget(Widget(size_hint_y=1))

        start_btn = Button(text='▶  Start Practice', font_size=sp(18), size_hint_y=None, height=btn_h(),
                           background_normal='', background_down='', background_color=T('ACCENT'), color=T('TXT'))
        start_btn.bind(on_press=self._start)
        self.root.add_widget(start_btn)
        self.add_widget(self.root)

    def _set_preset(self, text):
        self.text_input.text = text

    def _start(self, *a):
        text = self.text_input.text.strip()
        if not text:
            text = 'The quick brown fox jumps over the lazy dog.'
        app = App.get_running_app()
        app.current_layout = settings_mgr.get('layout', 'QWERTY')
        app.current_lesson = 'custom'
        app.current_mode = 'completion'
        ts = self.manager.get_screen('typing')
        ts.start_lesson(app.current_layout, 'custom', 'completion', custom_text=text)
        self.manager.current = 'typing'


# ─── App ──────────────────────────────────────────────────────────────────────

class KeyboardTrainerApp(App):
    current_layout = 'QWERTY'
    current_lesson = 'home_row'
    current_mode = 'completion'
    stats_file = 'typing_stats.json'

    def build(self):
        # Initialize settings and sounds with proper data directory
        data_dir = self.user_data_dir
        os.makedirs(data_dir, exist_ok=True)
        settings_mgr.init(data_dir)
        sound_mgr.init(data_dir)

        # Set theme background
        Window.clearcolor = T('BG')

        # Desktop window size
        if not IS_MOBILE:
            Window.size = (960, 720)
            Window.minimum_width = 640
            Window.minimum_height = 520

        # Android back button
        Window.bind(on_keyboard=self._on_global_key)

        self.stats_file = os.path.join(data_dir, self.stats_file)

        sm = ScreenManager(transition=SlideTransition(duration=0.25))
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(TypingScreen(name='typing'))
        sm.add_widget(ResultsScreen(name='results'))
        sm.add_widget(StatsScreen(name='stats'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(CustomTextScreen(name='custom'))
        return sm

    def _on_global_key(self, window, key, *args):
        """Handle Android back button and Escape key globally."""
        if key == 27:  # Android back or Escape
            sm = self.root
            if sm.current == 'typing':
                sm.get_screen('typing')._go_back()
                return True
            elif sm.current in ('results', 'stats', 'settings', 'custom'):
                sm.current = 'menu'
                return True
            elif sm.current == 'menu':
                return True  # Consume to prevent app exit
        return False

    def on_pause(self):
        """Android: save state when app is paused."""
        settings_mgr.save()
        return True

    def on_resume(self):
        """Android: restore when app is resumed."""
        pass

    def save_stat(self, layout, lesson, wpm, acc, time_s):
        stats = self.load_stats()
        stats.append({
            'layout': layout, 'lesson': lesson,
            'wpm': wpm, 'acc': acc, 'time': time_s,
            'date': time.strftime('%Y-%m-%d %H:%M')
        })
        # Keep last 200 entries
        if len(stats) > 200:
            stats = stats[-200:]
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(stats, f)
        except: pass

    def load_stats(self):
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except: return []
        return []

    def clear_stats(self):
        try:
            if os.path.exists(self.stats_file):
                os.remove(self.stats_file)
        except: pass

    def get_best_stat(self, layout):
        stats = self.load_stats()
        layout_stats = [s for s in stats if s.get('layout') == layout]
        if not layout_stats: return None
        return max(layout_stats, key=lambda s: s.get('wpm', 0))


if __name__ == '__main__':
    KeyboardTrainerApp().run()