#!/usr/bin/env python3
"""
Keyboard Learning App — Learn to type fast and accurately on multiple layouts.
Supports: QWERTY, AZERTY, DVORAK, Colemak
Requirements: pip install kivy
"""

import time
import random
import json
import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.togglebutton import ToggleButton
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.properties import (
    StringProperty, NumericProperty, BooleanProperty, ListProperty
)
from kivy.metrics import dp, sp

# ─── Theme ────────────────────────────────────────────────────────────────────
BG          = (0.11, 0.11, 0.16, 1)
CARD        = (0.17, 0.18, 0.24, 1)
CARD2       = (0.22, 0.23, 0.30, 1)
ACCENT      = (0.28, 0.56, 1.00, 1)
GREEN       = (0.22, 0.88, 0.42, 1)
RED         = (0.92, 0.26, 0.26, 1)
YELLOW      = (1.00, 0.86, 0.20, 1)
ORANGE      = (1.00, 0.55, 0.15, 1)
TXT         = (0.93, 0.93, 0.97, 1)
DIM         = (0.44, 0.44, 0.52, 1)

FINGER_COLS = [
    (0.85, 0.30, 0.30),  # 0 L-pinky
    (0.90, 0.55, 0.20),  # 1 L-ring
    (0.88, 0.82, 0.22),  # 2 L-middle
    (0.28, 0.78, 0.32),  # 3 L-index
    (0.20, 0.76, 0.82),  # 4 R-index
    (0.30, 0.46, 0.92),  # 5 R-middle
    (0.58, 0.30, 0.82),  # 6 R-ring
    (0.82, 0.30, 0.70),  # 7 R-pinky
    (0.50, 0.50, 0.56),  # 8 thumbs
]

FINGER_NAMES = [
    "Left Pinky", "Left Ring", "Left Middle", "Left Index",
    "Right Index", "Right Middle", "Right Ring", "Right Pinky", "Thumb"
]

# ─── Keyboard Layouts ────────────────────────────────────────────────────────
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
    layout = LAYOUTS[layout_name]
    for row in layout['rows']:
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

def gen_lesson(layout_name, lesson_type, length=120):
    layout = LAYOUTS[layout_name]
    if lesson_type == 'home_row':
        keys = [k.lower() for k in layout['home_keys']]
        t = ''
        for i in range(length):
            t += random.choice(keys)
            if random.random() < 0.18: t += ' '
        return t.strip()
    elif lesson_type == 'top_row':
        row = layout['rows'][1]
        keys = [lbl.lower() for lbl,_ in row if len(lbl)==1 and lbl.isalpha()]
        t = ''
        for i in range(length):
            t += random.choice(keys)
            if random.random() < 0.18: t += ' '
        return t.strip()
    elif lesson_type == 'bottom_row':
        row = layout['rows'][3]
        keys = [lbl.lower() for lbl,_ in row if len(lbl)==1 and lbl.isalpha()]
        t = ''
        for i in range(length):
            t += random.choice(keys)
            if random.random() < 0.18: t += ' '
        return t.strip()
    elif lesson_type == 'all_letters':
        keys = []
        for row in layout['rows'][1:4]:
            keys += [lbl.lower() for lbl,_ in row if len(lbl)==1 and lbl.isalpha()]
        t = ''
        for i in range(length):
            t += random.choice(keys)
            if random.random() < 0.18: t += ' '
        return t.strip()
    elif lesson_type == 'common_words':
        ws = random.choices(WORDS, k=22)
        return ' '.join(ws)
    elif lesson_type == 'sentences':
        ss = random.sample(SENTENCES, min(3, len(SENTENCES)))
        return ' '.join(ss)
    elif lesson_type == 'numbers':
        row = layout['rows'][0]
        keys = [lbl for lbl,_ in row if len(lbl)==1]
        t = ''
        for i in range(length):
            t += random.choice(keys)
            if random.random() < 0.15: t += ' '
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

# ─── Custom Widgets ───────────────────────────────────────────────────────────

class KeyWidget(Button):
    key_label = StringProperty('')
    finger_idx = NumericProperty(0)
    is_home = BooleanProperty(False)
    highlighted = BooleanProperty(False)
    pressed_anim = BooleanProperty(False)

    def __init__(self, key_label='', width_units=1, finger_idx=0, is_home=False, on_tap=None, **kw):
        self._on_tap = on_tap
        super().__init__(**kw)
        self.key_label = key_label
        self.finger_idx = finger_idx
        self.is_home = is_home
        self.width_units = width_units
        self.size_hint_x = width_units
        self.size_hint_y = None
        self.height = dp(42)
        self.background_normal = ''
        self.background_down = ''
        self.halign = 'center'
        self.valign = 'middle'
        self.padding = (dp(2), dp(2))
        display = key_label if key_label != 'SPACE' else '⎵ SPACE'
        self.text = display
        self.font_size = sp(11) if len(display) <= 2 else sp(9)
        self._update_color()

    def _update_color(self):
        if self.highlighted:
            self.background_color = (*YELLOW[:3], 0.92)
            self.color = (0.1, 0.1, 0.15, 1)
        elif self.pressed_anim:
            self.background_color = (*ACCENT[:3], 0.8)
            self.color = TXT
        else:
            fc = FINGER_COLS[self.finger_idx] if 0 <= self.finger_idx < 9 else (0.3,0.3,0.4)
            self.background_color = (*fc, 0.45)
            self.color = TXT
        self.canvas.after.clear()
        if self.is_home and not self.highlighted:
            with self.canvas.after:
                Color(1, 1, 1, 0.6)
                RoundedRectangle(
                    pos=(self.center_x - dp(6), self.y + dp(4)),
                    size=(dp(12), dp(3)), radius=[dp(1.5)])

    def set_highlighted(self, val):
        self.highlighted = val
        self._update_color()

    def flash_press(self):
        self.pressed_anim = True
        self._update_color()
        Clock.schedule_once(lambda dt: self._unflash(), 0.12)

    def _unflash(self):
        self.pressed_anim = False
        self._update_color()

    def on_press(self):
        if self._on_tap:
            self._on_tap(self.key_label)

    def on_is_home(self, *a):
        self._update_color()

    def on_highlighted(self, *a):
        self._update_color()


class VisualKeyboard(BoxLayout):
    layout_name = StringProperty('QWERTY')
    highlight_char = StringProperty('')

    def __init__(self, **kw):
        super().__init__(orientation='vertical', spacing=dp(3), padding=dp(4), **kw)
        self.key_widgets = {}
        self._on_key_tap = None
        self.size_hint_y = None
        self.height = dp(230)
        self.bind(layout_name=self._rebuild, highlight_char=self._update_highlight)
        self._rebuild()

    def set_tap_callback(self, cb):
        self._on_key_tap = cb

    def _rebuild(self, *a):
        self.clear_widgets()
        self.key_widgets = {}
        layout = LAYOUTS.get(self.layout_name, LAYOUTS['QWERTY'])
        home_keys = set(layout.get('home_keys', []))
        offsets = layout.get('offsets', [0]*5)
        total_units = max(
            sum(w for _,w in row) + offsets[i]
            for i, row in enumerate(layout['rows'])
        )

        for ri, row in enumerate(layout['rows']):
            row_box = BoxLayout(spacing=dp(2), size_hint_y=None, height=dp(42))
            off = offsets[ri] if ri < len(offsets) else 0
            if off > 0:
                spacer = Widget(size_hint_x=off)
                row_box.add_widget(spacer)
            for lbl, wu in row:
                fi = get_finger(self.layout_name, lbl)
                ih = lbl in home_keys
                kw = KeyWidget(key_label=lbl, width_units=wu, finger_idx=fi, is_home=ih, on_tap=self._handle_tap)
                self.key_widgets[lbl] = kw
                row_box.add_widget(kw)
            used = off + sum(w for _,w in row)
            if used < total_units:
                spacer = Widget(size_hint_x=total_units - used)
                row_box.add_widget(spacer)
            self.add_widget(row_box)
        self._update_highlight()

    def _handle_tap(self, label):
        if self._on_key_tap:
            ch = ' ' if label == 'SPACE' else label.lower()
            self._on_key_tap(ch)

    def _update_highlight(self, *a):
        for lbl, kw in self.key_widgets.items():
            kw.set_highlighted(False)
        ch = self.highlight_char
        if not ch:
            return
        target = find_key_label(self.layout_name, ch)
        if target and target in self.key_widgets:
            self.key_widgets[target].set_highlighted(True)
        if ch.isupper():
            for lbl, kw in self.key_widgets.items():
                if lbl == '⇧':
                    kw.set_highlighted(True)

    def flash_key(self, char):
        target = find_key_label(self.layout_name, char)
        if target and target in self.key_widgets:
            self.key_widgets[target].flash_press()


# ─── Screens ──────────────────────────────────────────────────────────────────

class MenuScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.selected_layout = 'QWERTY'
        self.selected_lesson = 'home_row'
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(12))

        title = Label(text='⌨️  Keyboard Trainer', font_size=sp(32),
                       size_hint_y=None, height=dp(60), color=TXT)
        root.add_widget(title)
        subtitle = Label(text='Learn to type fast & accurately on any layout',
                          font_size=sp(14), size_hint_y=None, height=dp(30), color=DIM)
        root.add_widget(subtitle)

        root.add_widget(self._section('Select Keyboard Layout'))
        layout_grid = GridLayout(cols=2, spacing=dp(8), size_hint_y=None, height=dp(44)*2 + dp(8))
        self._layout_btns = {}
        for name, data in LAYOUTS.items():
            b = ToggleButton(text=data['display'], group='layout',
                             font_size=sp(13), background_normal='', background_down='', background_color=CARD2, color=TXT)
            if name == self.selected_layout:
                b.state = 'down'
                b.background_color = ACCENT
            b.bind(state=lambda s, v, n=name: self._pick_layout(n, v))
            b.bind(state=self._style_toggle)
            self._layout_btns[name] = b
            layout_grid.add_widget(b)
        root.add_widget(layout_grid)

        root.add_widget(self._section('Choose Lesson'))
        lesson_grid = GridLayout(cols=2, spacing=dp(6), size_hint_y=None, height=dp(44)*4)
        self._lesson_btns = {}
        for ltype, lname, ldesc in LESSON_TYPES:
            b = ToggleButton(text=lname, group='lesson',
                             font_size=sp(12), background_normal='', background_down='', background_color=CARD2, color=TXT, size_hint_y=None, height=dp(44))
            if ltype == self.selected_lesson:
                b.state = 'down'
                b.background_color = ACCENT
            b.bind(state=lambda s, v, t=ltype: self._pick_lesson(t, v))
            b.bind(state=self._style_toggle)
            self._lesson_btns[ltype] = b
            lesson_grid.add_widget(b)
        root.add_widget(lesson_grid)

        root.add_widget(Widget(size_hint_y=1))

        start_btn = Button(text='▶  Start Typing', font_size=sp(20),
                           size_hint_y=None, height=dp(56),
                           background_normal='', background_down='', background_color=ACCENT, color=TXT)
        start_btn.bind(on_press=self._start)
        root.add_widget(start_btn)

        stats_btn = Button(text='📊  View Statistics', font_size=sp(14),
                           size_hint_y=None, height=dp(44),
                           background_normal='', background_down='', background_color=CARD2, color=TXT)
        stats_btn.bind(on_press=self._show_stats)
        root.add_widget(stats_btn)

        self.add_widget(root)

    def _section(self, text):
        l = Label(text=text, font_size=sp(15), size_hint_y=None, height=dp(30), halign='left', valign='middle', color=ACCENT)
        l.bind(size=lambda *a: l.setter('text_size')(l, l.size))
        return l

    def _style_toggle(self, btn, val):
        if val == 'down':
            btn.background_color = ACCENT
        else:
            btn.background_color = CARD2

    def _pick_layout(self, name, state):
        if state == 'down': self.selected_layout = name

    def _pick_lesson(self, ltype, state):
        if state == 'down': self.selected_lesson = ltype

    def _start(self, *a):
        app = App.get_running_app()
        app.current_layout = self.selected_layout
        app.current_lesson = self.selected_lesson
        ts = self.manager.get_screen('typing')
        ts.start_lesson(self.selected_layout, self.selected_lesson)
        self.manager.current = 'typing'

    def _show_stats(self, *a):
        self.manager.current = 'stats'


class TypingScreen(Screen):
    wpm = NumericProperty(0)
    accuracy_p = NumericProperty(100)
    elapsed = NumericProperty(0)

    def __init__(self, **kw):
        super().__init__(**kw)
        self.layout_name = 'QWERTY'
        self.lesson_text = ''
        self.typed = []
        self.char_idx = 0           # ← renamed from self.pos to avoid Kivy conflict
        self.start_time = None
        self.errors = 0
        self.total_keystrokes = 0
        self.streak = 0
        self._keyboard = None
        self._timer_event = None
        self._finished = False
        self._build_ui()

    def _build_ui(self):
        self.root_box = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(6))

        # Top bar
        top = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(8))
        back_btn = Button(text='← Back', size_hint_x=None, width=dp(80),
                          background_normal='', background_down='', background_color=CARD2, color=TXT, font_size=sp(13))
        back_btn.bind(on_press=self._go_back)
        top.add_widget(back_btn)
        self.lbl_lesson = Label(text='', font_size=sp(13), color=DIM, halign='left')
        self.lbl_lesson.bind(size=lambda *a: self.lbl_lesson.setter('text_size')(self.lbl_lesson, self.lbl_lesson.size))
        top.add_widget(self.lbl_lesson)

        stat_box = BoxLayout(size_hint_x=None, width=dp(320), spacing=dp(6))
        self.lbl_wpm = Label(text='WPM: 0', font_size=sp(14), color=GREEN, bold=True)
        self.lbl_acc = Label(text='ACC: 100%', font_size=sp(14), color=ACCENT, bold=True)
        self.lbl_time = Label(text='⏱ 0:00', font_size=sp(14), color=ORANGE)
        self.lbl_streak = Label(text='🔥 0', font_size=sp(14), color=YELLOW)
        stat_box.add_widget(self.lbl_wpm)
        stat_box.add_widget(self.lbl_acc)
        stat_box.add_widget(self.lbl_time)
        stat_box.add_widget(self.lbl_streak)
        top.add_widget(stat_box)
        self.root_box.add_widget(top)

        # Progress bar
        self.progress = Widget(size_hint_y=None, height=dp(8))
        self.root_box.add_widget(self.progress)

        # Finger hint
        self.lbl_finger = Label(text='', font_size=sp(14), size_hint_y=None, height=dp(28), color=DIM)
        self.root_box.add_widget(self.lbl_finger)

        # Typing area
        typing_frame = BoxLayout(size_hint_y=None, height=dp(150), padding=dp(10))
        with typing_frame.canvas.before:
            Color(*CARD)
            self._typing_bg = RoundedRectangle(pos=typing_frame.pos, size=typing_frame.size, radius=[dp(10)])
        typing_frame.bind(pos=self._update_typing_bg, size=self._update_typing_bg)
        self.lbl_text = Label(text='', font_size=sp(20), halign='left', valign='middle', markup=True, color=TXT)
        self.lbl_text.bind(size=lambda *a: self.lbl_text.setter('text_size')(self.lbl_text, self.lbl_text.size))
        typing_frame.add_widget(self.lbl_text)
        self.root_box.add_widget(typing_frame)

        self.root_box.add_widget(Widget(size_hint_y=0.3))

        # Visual keyboard
        self.keyboard = VisualKeyboard()
        self.keyboard.set_tap_callback(self._handle_tap)
        self.root_box.add_widget(self.keyboard)

        self.lbl_hint = Label(text='Type the highlighted character. Press Escape to quit.',
                              font_size=sp(11), size_hint_y=None, height=dp(24), color=DIM)
        self.root_box.add_widget(self.lbl_hint)

        self.add_widget(self.root_box)

    def _update_typing_bg(self, inst, val):
        self._typing_bg.pos = inst.pos
        self._typing_bg.size = inst.size

    def start_lesson(self, layout_name, lesson_type):
        self.layout_name = layout_name
        self.lesson_text = gen_lesson(layout_name, lesson_type, 140)
        self.typed = []
        self.char_idx = 0
        self.start_time = None
        self.errors = 0
        self.total_keystrokes = 0
        self.streak = 0
        self._finished = False
        self.wpm = 0
        self.accuracy_p = 100
        self.elapsed = 0

        self.lbl_lesson.text = f'{LAYOUTS[layout_name]["display"]}  •  {lesson_type.replace("_"," ").title()}'
        self.keyboard.layout_name = layout_name
        self._refresh_display()
        self._start_listening()

        if self._timer_event:
            self._timer_event.cancel()
        self._timer_event = Clock.schedule_interval(self._tick, 0.25)

    def _start_listening(self):
        self._stop_listening()
        try:
            self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
            self._keyboard.bind(on_key_down=self._on_key_down)
        except Exception:
            pass

    def _stop_listening(self):
        if self._keyboard:
            try:
                self._keyboard.unbind(on_key_down=self._on_key_down)
                self._keyboard.release()
            except Exception:
                pass
            self._keyboard = None

    def _keyboard_closed(self):
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, text, modifiers):
        self._process_key(keycode, text, modifiers)

    def _process_key(self, keycode, text, modifiers):
        if self._finished:
            return
        key_name = keycode[1] if isinstance(keycode, (list, tuple)) and len(keycode) > 1 else ''

        if key_name == 'escape':
            self._go_back()
            return
        if key_name == 'backspace':
            self._handle_backspace()
            return
        if key_name in ('lshift', 'rshift', 'shift', 'capslock', 'tab',
                        'ctrl', 'lctrl', 'rctrl', 'alt', 'lalt', 'ralt',
                        'super', 'lsuper', 'rsuper', 'alt-gr',
                        'up', 'down', 'left', 'right',
                        'f1','f2','f3','f4','f5','f6','f7','f8','f9','f10','f11','f12',
                        'insert', 'delete', 'home', 'end', 'pageup', 'pagedown',
                        'numlock', 'scrolllock', 'print', 'sysreq', 'pause', 'break'):
            return
        if text and len(text) == 1:
            self._handle_char(text)

    def _handle_tap(self, char):
        if self._finished:
            return
        self._handle_char(char)

    def _handle_char(self, ch):
        if self.char_idx >= len(self.lesson_text):
            return
        if self.start_time is None:
            self.start_time = time.time()

        expected = self.lesson_text[self.char_idx]
        correct = (ch == expected)
        self.typed.append((ch, correct))
        self.total_keystrokes += 1

        if correct:
            self.streak += 1
        else:
            self.errors += 1
            self.streak = 0

        self.keyboard.flash_key(ch if correct else expected)
        self.char_idx += 1
        self._refresh_display()
        self._update_stats()

        if self.char_idx >= len(self.lesson_text):
            self._finish()

    def _handle_backspace(self):
        if self.char_idx > 0 and self.typed:
            self.char_idx -= 1
            ch, correct = self.typed.pop()
            self.total_keystrokes -= 1
            if not correct:
                self.errors -= 1
            self.streak = 0
            self._refresh_display()
            self._update_stats()

    def _refresh_display(self):
        text = self.lesson_text
        parts = []
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
            self.lbl_finger.text = f'👉 {FINGER_NAMES[fi]}' if 0 <= fi < 9 else ''
            self.lbl_finger.color = (*FINGER_COLS[fi], 1) if 0 <= fi < 9 else DIM
        else:
            self.keyboard.highlight_char = ''
            self.lbl_finger.text = '✅ Complete!'

        for i in range(self.char_idx + 1, min(len(text), self.char_idx + 60)):
            parts.append(f'[color=707078]{self._esc(text[i])}[/color]')

        self.lbl_text.text = ''.join(parts)

        # progress bar
        self.progress.canvas.after.clear()
        with self.progress.canvas.after:
            Color(*CARD2)
            RoundedRectangle(pos=self.progress.pos, size=self.progress.size, radius=[dp(4)])
            pct = self.char_idx / max(1, len(text))
            Color(*GREEN)
            RoundedRectangle(
                pos=self.progress.pos,
                size=(self.progress.width * pct, self.progress.height),
                radius=[dp(4)])

    @staticmethod
    def _esc(ch):
        return ch.replace('&', '&amp;').replace('[', '&bl;').replace(']', '&br;')

    def _update_stats(self):
        if self.start_time is None:
            self.lbl_wpm.text = 'WPM: 0'
            self.lbl_acc.text = 'ACC: 100%'
            return
        elapsed = max(0.1, time.time() - self.start_time)
        correct_chars = sum(1 for _, ok in self.typed if ok)
        wpm = (correct_chars / 5) / (elapsed / 60)
        acc = (correct_chars / max(1, self.total_keystrokes)) * 100
        self.wpm = wpm
        self.accuracy_p = acc
        self.lbl_wpm.text = f'WPM: {int(wpm)}'
        self.lbl_wpm.color = GREEN if wpm >= 30 else ORANGE if wpm >= 15 else RED
        self.lbl_acc.text = f'ACC: {acc:.1f}%'
        self.lbl_acc.color = GREEN if acc >= 95 else ORANGE if acc >= 85 else RED
        self.lbl_streak.text = f'🔥 {self.streak}'

    def _tick(self, dt):
        if self.start_time is None:
            self.lbl_time.text = '⏱ 0:00'
            return
        elapsed = int(time.time() - self.start_time)
        m, s = divmod(elapsed, 60)
        self.lbl_time.text = f'⏱ {m}:{s:02d}'
        self.elapsed = elapsed
        self._update_stats()

    def _finish(self):
        self._finished = True
        if self._timer_event:
            self._timer_event.cancel()
        elapsed = max(0.1, time.time() - self.start_time) if self.start_time else 1
        correct = sum(1 for _, ok in self.typed if ok)
        wpm = (correct / 5) / (elapsed / 60)
        acc = (correct / max(1, self.total_keystrokes)) * 100

        app = App.get_running_app()
        app.save_stat(self.layout_name, self.manager.get_screen('menu').selected_lesson, wpm, acc, elapsed)

        rs = self.manager.get_screen('results')
        rs.set_results(wpm, acc, elapsed, correct, self.errors, self.total_keystrokes, self.layout_name)
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'results'), 0.5)

    def _go_back(self, *a):
        self._stop_listening()
        if self._timer_event:
            self._timer_event.cancel()
        self.manager.current = 'menu'


class ResultsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._build_ui()

    def _build_ui(self):
        self.root = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(14))
        self.lbl_title = Label(text='🎉  Lesson Complete!', font_size=sp(28), size_hint_y=None, height=dp(60), color=YELLOW)
        self.root.add_widget(self.lbl_title)

        self.stats_grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(200))
        self.root.add_widget(self.stats_grid)

        self.root.add_widget(Widget(size_hint_y=1))

        self.lbl_rating = Label(text='', font_size=sp(22), size_hint_y=None, height=dp(50), color=TXT)
        self.root.add_widget(self.lbl_rating)

        btn_box = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(56))
        retry_btn = Button(text='🔄  Try Again', font_size=sp(16), background_normal='', background_down='', background_color=ACCENT, color=TXT)
        retry_btn.bind(on_press=self._retry)
        menu_btn = Button(text='🏠  Menu', font_size=sp(16), background_normal='', background_down='', background_color=CARD2, color=TXT)
        menu_btn.bind(on_press=self._menu)
        btn_box.add_widget(retry_btn)
        btn_box.add_widget(menu_btn)
        self.root.add_widget(btn_box)

        self.add_widget(self.root)

    def set_results(self, wpm, acc, elapsed, correct, errors, total, layout):
        self.stats_grid.clear_widgets()
        stats = [
            ('⌨️ Layout', LAYOUTS[layout]['display']),
            ('⚡ Speed', f'{int(wpm)} WPM'),
            ('🎯 Accuracy', f'{acc:.1f}%'),
            ('⏱ Time', f'{int(elapsed//60)}:{int(elapsed%60):02d}'),
            ('✅ Correct', str(correct)),
            ('❌ Errors', str(errors)),
            ('📊 Keystrokes', str(total)),
            ('📈 Chars/min', f'{int(correct / max(1, elapsed) * 60)}'),
        ]
        for label, value in stats:
            l = Label(text=label, font_size=sp(14), color=DIM, halign='right', valign='middle')
            l.bind(size=lambda *a, w=l: l.setter('text_size')(l, l.size))
            v = Label(text=value, font_size=sp(16), color=TXT, bold=True, halign='left', valign='middle')
            v.bind(size=lambda *a, w=v: v.setter('text_size')(v, v.size))
            self.stats_grid.add_widget(l)
            self.stats_grid.add_widget(v)

        if acc >= 98 and wpm >= 50:
            rating, rc = '🏆  PERFECT! You are a typing master!', YELLOW
        elif acc >= 95 and wpm >= 35:
            rating, rc = '⭐  Excellent! Great speed and accuracy!', GREEN
        elif acc >= 90:
            rating, rc = '👍  Good job! Keep practicing for speed.', ACCENT
        elif acc >= 80:
            rating, rc = '💪  Not bad! Focus on accuracy first.', ORANGE
        else:
            rating, rc = '📚  Keep practicing! Accuracy comes before speed.', RED
        self.lbl_rating.text = rating
        self.lbl_rating.color = rc

    def _retry(self, *a):
        app = App.get_running_app()
        ts = self.manager.get_screen('typing')
        ts.start_lesson(app.current_layout, app.current_lesson)
        self.manager.current = 'typing'

    def _menu(self, *a):
        self.manager.current = 'menu'


class StatsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self._build_ui()

    def _build_ui(self):
        self.root = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        header = BoxLayout(size_hint_y=None, height=dp(44))
        back_btn = Button(text='← Back', size_hint_x=None, width=dp(80), background_normal='', background_down='', background_color=CARD2, color=TXT, font_size=sp(13))
        back_btn.bind(on_press=lambda *a: setattr(self.manager, 'current', 'menu'))
        header.add_widget(back_btn)
        header.add_widget(Label(text='📊  Your Statistics', font_size=sp(22), color=TXT))
        self.root.add_widget(header)

        self.scroll = ScrollView()
        self.stats_content = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, padding=dp(8))
        self.stats_content.bind(minimum_height=self.stats_content.setter('height'))
        self.scroll.add_widget(self.stats_content)
        self.root.add_widget(self.scroll)

        clear_btn = Button(text='🗑  Clear All Stats', size_hint_y=None, height=dp(44), background_normal='', background_down='', background_color=RED, color=TXT, font_size=sp(13))
        clear_btn.bind(on_press=self._clear_stats)
        self.root.add_widget(clear_btn)

        self.add_widget(self.root)

    def on_pre_enter(self, *a):
        self._refresh()

    def _refresh(self):
        self.stats_content.clear_widgets()
        app = App.get_running_app()
        stats = app.load_stats()
        if not stats:
            self.stats_content.add_widget(Label(text='No statistics yet.\nComplete a lesson to see your progress!', font_size=sp(14), color=DIM, size_hint_y=None, height=dp(100)))
            return

        for entry in reversed(stats[-30:]):
            box = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(70), padding=dp(8), spacing=dp(2))
            with box.canvas.before:
                Color(*CARD)
                bg = RoundedRectangle(pos=box.pos, size=box.size, radius=[dp(8)])
            box.bind(pos=lambda i, bg=bg: setattr(bg, 'pos', i.pos), size=lambda i, bg=bg: setattr(bg, 'size', i.size))

            layout_disp = LAYOUTS.get(entry.get('layout', ''), {}).get('display', entry.get('layout', ''))
            line1 = f'{layout_disp}  •  {entry.get("lesson","").replace("_"," ").title()}'
            line2 = (f'WPM: {int(entry.get("wpm",0))}   |   '
                     f'Accuracy: {entry.get("acc",0):.1f}%   |   '
                     f'Time: {int(entry.get("time",0)//60)}:{int(entry.get("time",0)%60):02d}')

            l1 = Label(text=line1, font_size=sp(11), color=DIM, halign='left', valign='middle', size_hint_y=None, height=dp(24))
            l1.bind(size=lambda *a, w=l1: l1.setter('text_size')(l1, l1.size))
            l2 = Label(text=line2, font_size=sp(14), color=TXT, halign='left', valign='middle', size_hint_y=None, height=dp(30))
            l2.bind(size=lambda *a, w=l2: l2.setter('text_size')(l2, l2.size))

            box.add_widget(l1)
            box.add_widget(l2)
            self.stats_content.add_widget(box)

    def _clear_stats(self, *a):
        app = App.get_running_app()
        app.clear_stats()
        self._refresh()


# ─── App ──────────────────────────────────────────────────────────────────────

class KeyboardTrainerApp(App):
    current_layout = 'QWERTY'
    current_lesson = 'home_row'
    stats_file = 'typing_stats.json'

    def build(self):
        Window.clearcolor = BG
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(TypingScreen(name='typing'))
        sm.add_widget(ResultsScreen(name='results'))
        sm.add_widget(StatsScreen(name='stats'))
        return sm

    def save_stat(self, layout, lesson, wpm, acc, time_s):
        stats = self.load_stats()
        stats.append({
            'layout': layout,
            'lesson': lesson,
            'wpm': wpm,
            'acc': acc,
            'time': time_s,
            'date': time.strftime('%Y-%m-%d %H:%M')
        })
        with open(self.stats_file, 'w') as f:
            json.dump(stats, f)

    def load_stats(self):
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def clear_stats(self):
        if os.path.exists(self.stats_file):
            os.remove(self.stats_file)


if __name__ == '__main__':
    KeyboardTrainerApp().run()