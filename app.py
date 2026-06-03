#!/usr/bin/env python3
"""
Keyboard Learning App — PySide6 Version
Learn to type fast and accurately on multiple layouts.
Supports: QWERTY, AZERTY, DVORAK, Colemak

Requirements:
  pip install PySide6
"""

import sys, os, json, time, random, math, struct, wave
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QStackedWidget, QLabel, QPushButton, QRadioButton,
    QButtonGroup, QScrollArea, QTextEdit, QSizePolicy, QFrame,
    QCheckBox, QPlainTextEdit, QSpacerItem, QToolButton, QComboBox
)
from PySide6.QtCore import Qt, QTimer, QRectF, QSize, Signal, QUrl
from PySide6.QtGui import (
    QPainter, QColor, QBrush, QPen, QFont, QPalette, QKeySequence
)

try:
    from PySide6.QtMultimedia import QSoundEffect
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False

# ─── Data Directory ───────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.expanduser('~'), '.keyboard_trainer_pyside6')
os.makedirs(DATA_DIR, exist_ok=True)

# ─── Theme System ─────────────────────────────────────────────────────────────
THEMES = {
    'dark': {
        'BG': (0.08, 0.08, 0.12), 'CARD': (0.14, 0.15, 0.20),
        'CARD2': (0.20, 0.21, 0.27), 'CARD3': (0.25, 0.26, 0.32),
        'ACCENT': (0.28, 0.56, 1.0), 'GREEN': (0.22, 0.88, 0.42),
        'RED': (0.92, 0.26, 0.26), 'YELLOW': (1.0, 0.86, 0.20),
        'ORANGE': (1.0, 0.55, 0.15), 'TXT': (0.93, 0.93, 0.97),
        'DIM': (0.44, 0.44, 0.52),
    },
    'midnight': {
        'BG': (0.04, 0.04, 0.09), 'CARD': (0.09, 0.10, 0.17),
        'CARD2': (0.15, 0.16, 0.23), 'CARD3': (0.20, 0.22, 0.30),
        'ACCENT': (0.45, 0.45, 1.0), 'GREEN': (0.20, 0.90, 0.60),
        'RED': (0.95, 0.20, 0.30), 'YELLOW': (1.0, 0.90, 0.30),
        'ORANGE': (1.0, 0.60, 0.20), 'TXT': (0.90, 0.90, 0.98),
        'DIM': (0.40, 0.40, 0.55),
    },
    'ocean': {
        'BG': (0.04, 0.07, 0.12), 'CARD': (0.08, 0.13, 0.20),
        'CARD2': (0.12, 0.18, 0.28), 'CARD3': (0.16, 0.24, 0.34),
        'ACCENT': (0.15, 0.75, 0.90), 'GREEN': (0.20, 0.85, 0.65),
        'RED': (0.90, 0.30, 0.35), 'YELLOW': (0.95, 0.88, 0.25),
        'ORANGE': (0.95, 0.60, 0.20), 'TXT': (0.92, 0.95, 0.98),
        'DIM': (0.35, 0.45, 0.55),
    },
    'warm': {
        'BG': (0.12, 0.08, 0.06), 'CARD': (0.18, 0.14, 0.10),
        'CARD2': (0.24, 0.20, 0.16), 'CARD3': (0.30, 0.26, 0.22),
        'ACCENT': (0.95, 0.65, 0.25), 'GREEN': (0.45, 0.85, 0.35),
        'RED': (0.90, 0.30, 0.25), 'YELLOW': (0.98, 0.88, 0.25),
        'ORANGE': (0.95, 0.55, 0.20), 'TXT': (0.95, 0.92, 0.88),
        'DIM': (0.50, 0.42, 0.36),
    },
    'light': {
        'BG': (0.94, 0.94, 0.96), 'CARD': (1.0, 1.0, 1.0),
        'CARD2': (0.92, 0.92, 0.94), 'CARD3': (0.86, 0.86, 0.88),
        'ACCENT': (0.18, 0.45, 0.92), 'GREEN': (0.13, 0.72, 0.30),
        'RED': (0.85, 0.18, 0.18), 'YELLOW': (0.85, 0.72, 0.05),
        'ORANGE': (0.90, 0.48, 0.10), 'TXT': (0.12, 0.12, 0.15),
        'DIM': (0.50, 0.50, 0.55),
    },
}

_theme_name = 'dark'

def rgb_hex(r, g, b):
    return f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'

def T(key):
    vals = THEMES[_theme_name].get(key, (0.5, 0.5, 0.5))
    return rgb_hex(*vals)

def T_color(key):
    vals = THEMES[_theme_name].get(key, (0.5, 0.5, 0.5))
    return QColor(int(vals[0]*255), int(vals[1]*255), int(vals[2]*255))

def T_rgba(key, alpha=255):
    vals = THEMES[_theme_name].get(key, (0.5, 0.5, 0.5))
    return QColor(int(vals[0]*255), int(vals[1]*255), int(vals[2]*255), alpha)

def set_theme(name):
    global _theme_name
    if name in THEMES:
        _theme_name = name

THEME_DISPLAY = {
    'dark': '🌙  Dark', 'midnight': '🌃  Midnight',
    'ocean': '🌊  Ocean', 'warm': '🔥  Warm', 'light': '☀️  Light',
}

# Finger color assignments for visual keyboard
FINGER_COLS = [
    (0.85, 0.30, 0.30), (0.90, 0.55, 0.20), (0.88, 0.82, 0.22), (0.28, 0.78, 0.32),
    (0.20, 0.76, 0.82), (0.30, 0.46, 0.92), (0.58, 0.30, 0.82), (0.82, 0.30, 0.70),
    (0.50, 0.50, 0.56),
]
FINGER_NAMES = [
    "Left Pinky", "Left Ring", "Left Middle", "Left Index",
    "Right Index", "Right Middle", "Right Ring", "Right Pinky", "Thumb"
]

# ─── Sound System ─────────────────────────────────────────────────────────────
def _gen_wav(path, freq=800, dur=0.04, vol=0.2):
    sr = 22050; n = int(sr * dur); frames = []
    for i in range(n):
        fade = 1.0 - (i / n)
        v = int(vol * 32767 * math.sin(2 * math.pi * freq * i / sr) * fade)
        frames.append(struct.pack('<h', max(-32768, min(32767, v))))
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
        wf.writeframes(b''.join(frames))

class SoundManager:
    def __init__(self):
        self.enabled = True; self.sounds = {}; self._ready = False

    def init(self, data_dir):
        if not HAS_SOUND: return
        try:
            sd = os.path.join(data_dir, 'sounds')
            os.makedirs(sd, exist_ok=True)
            for name, freq, dur in [
                ('click', 880, 0.035), ('error', 280, 0.07),
                ('done', 1100, 0.12), ('streak', 1200, 0.06),
            ]:
                p = os.path.join(sd, f'{name}.wav')
                if not os.path.exists(p): _gen_wav(p, freq, dur, 0.18)
                effect = QSoundEffect()
                effect.setSource(QUrl.fromLocalFile(os.path.abspath(p)))
                effect.setVolume(0.5)
                self.sounds[name] = effect
            self._ready = True
        except Exception as e:
            print(f"Sound init skipped: {e}")

    def play(self, name):
        if not self.enabled or not self._ready or name not in self.sounds: return
        try: self.sounds[name].play()
        except: pass

sound_mgr = SoundManager()

# ─── Settings Manager ─────────────────────────────────────────────────────────
DEFAULT_SETTINGS = {
    'layout': 'QWERTY', 'lesson': 'home_row', 'theme': 'dark',
    'sound': True, 'vibration': True, 'mode': 'completion', 'timer_secs': 60,
    'show_keyboard': True, 'show_finger_hints': True, 'difficulty': 'normal',
}

class SettingsManager:
    def __init__(self):
        self.data = dict(DEFAULT_SETTINGS); self._path = None

    def init(self, data_dir):
        self._path = os.path.join(data_dir, 'kb_settings.json'); self.load()

    def load(self):
        if self._path and os.path.exists(self._path):
            try:
                with open(self._path, 'r') as f: saved = json.load(f); self.data.update(saved)
            except: pass
        set_theme(self.data.get('theme', 'dark'))
        sound_mgr.enabled = self.data.get('sound', True)

    def save(self):
        if self._path:
            try:
                with open(self._path, 'w') as f: json.dump(self.data, f, indent=2)
            except: pass

    def get(self, key, default=None): return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value; self.save()
        if key == 'theme': set_theme(value)
        if key == 'sound': sound_mgr.enabled = value

settings_mgr = SettingsManager()

# ─── Stats Manager ────────────────────────────────────────────────────────────
class StatsManager:
    def __init__(self, data_dir):
        self._path = os.path.join(data_dir, 'kb_stats.json')
        self.stats = []; self.key_stats = {}  # per-key accuracy
        self.load()

    def load(self):
        if os.path.exists(self._path):
            try:
                with open(self._path, 'r') as f:
                    data = json.load(f)
                    self.stats = data if isinstance(data, list) else data.get('sessions', [])
                    self.key_stats = data.get('key_stats', {}) if isinstance(data, dict) else {}
            except: self.stats = []; self.key_stats = {}

    def save(self):
        try:
            with open(self._path, 'w') as f:
                json.dump({'sessions': self.stats, 'key_stats': self.key_stats}, f, indent=2)
        except: pass

    def add_stat(self, layout, lesson, wpm, acc, elapsed, key_errors=None):
        self.stats.append({
            'layout': layout, 'lesson': lesson, 'wpm': round(wpm, 1),
            'acc': round(acc, 1), 'time': round(elapsed, 1),
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        })
        # Update per-key stats
        if key_errors:
            for key, count in key_errors.items():
                k = f"{layout}:{key}"
                if k not in self.key_stats:
                    self.key_stats[k] = {'errors': 0, 'total': 0}
                self.key_stats[k]['errors'] += count
                self.key_stats[k]['total'] += count  # will add correct below
        self.save()

    def record_key(self, layout, key_char, correct):
        k = f"{layout}:{key_char.upper()}"
        if k not in self.key_stats:
            self.key_stats[k] = {'errors': 0, 'total': 0}
        self.key_stats[k]['total'] += 1
        if not correct:
            self.key_stats[k]['errors'] += 1
        # Save periodically (every 50 keystrokes to reduce I/O)
        if self.key_stats[k]['total'] % 50 == 0:
            self.save()

    def get_key_accuracy(self, layout, key_char):
        k = f"{layout}:{key_char.upper()}"
        info = self.key_stats.get(k, {'errors': 0, 'total': 0})
        if info['total'] == 0: return 1.0
        return 1.0 - (info['errors'] / info['total'])

    def get_best(self, layout):
        ls = [s for s in self.stats if s.get('layout') == layout]
        return max(ls, key=lambda s: s.get('wpm', 0)) if ls else None

    def get_recent(self, n=10):
        return self.stats[-n:] if self.stats else []

    def clear(self): self.stats = []; self.key_stats = {}; self.save()

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
        # Explicit finger mapping: col_index -> finger (0-7)
        'finger_map': {
            0: [0,0,2,3,3,4,4,5,6,7,7,7,7],   # number row
            1: [0,0,2,3,3,4,4,5,6,7,7,7,7],    # top row
            2: [0,1,2,3,3,4,4,5,6,7,7],         # home row
            3: [0,0,1,2,3,3,4,5,6,7,7,7],       # bottom row (first col=shift)
        },
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
        'finger_map': {
            0: [0,0,2,3,3,4,4,5,6,7,7,7,7],
            1: [0,0,2,3,3,4,4,5,6,7,7,7,7],
            2: [0,1,2,3,3,4,4,5,6,7,7],
            3: [0,0,1,2,3,3,4,5,6,7,7,7],
        },
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
        'finger_map': {
            0: [0,0,2,3,3,4,4,5,6,7,7,7,7],
            1: [0,0,2,3,3,4,4,5,6,7,7],
            2: [0,1,2,3,3,4,4,5,6,7,7],
            3: [0,0,1,2,3,3,4,5,6,7,7,7],
        },
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
        'finger_map': {
            0: [0,0,2,3,3,4,4,5,6,7,7,7,7],
            1: [0,0,2,3,3,4,4,5,6,7,7,7,7],
            2: [0,1,2,3,3,4,4,5,6,7,7],
            3: [0,0,1,2,3,3,4,5,6,7,7,7],
        },
    },
}

def get_finger(layout_name, key_char):
    """Return finger index (0-8) for a given key character using layout-specific mapping."""
    if key_char in (' ', 'SPACE'): return 8
    layout = LAYOUTS[layout_name]
    ku = key_char.upper()
    finger_map = layout.get('finger_map', {})
    for ri, row in enumerate(layout['rows']):
        if ri == 4: continue  # skip space row
        for ci, (lbl, _) in enumerate(row):
            if lbl.upper() == ku or lbl == key_char:
                row_map = finger_map.get(ri)
                if row_map and ci < len(row_map):
                    return row_map[ci]
                # Fallback
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
            if lbl == char or lbl.lower() == char or lbl.upper() == char: return lbl
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
    "code","data","system","program","input","output","screen","file","open",
    "close","save","print","search","find","next","page","view","edit","help",
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
    "Programming requires a lot of typing every single day.",
    "The best coders can type over eighty words per minute.",
    "Focus on accuracy first then gradually increase your speed.",
    "Repetition builds muscle memory for each key on the board.",
    "Never look down at your hands while you are typing.",
]

def _no_triple_repeat(text):
    """Ensure no character appears three times consecutively."""
    result = list(text)
    for i in range(2, len(result)):
        if result[i] == result[i-1] == result[i-2]:
            result[i] = ' '
    return ''.join(result)

def gen_lesson(layout_name, lesson_type, length=140):
    layout = LAYOUTS[layout_name]
    if lesson_type == 'custom': return ''
    if lesson_type == 'home_row':
        keys = [k.lower() for k in layout['home_keys']]
        # Generate with natural word-like patterns
        result = []
        for _ in range(length):
            if random.random() < 0.15 and result and result[-1] != ' ':
                result.append(' ')
            else:
                result.append(random.choice(keys))
        text = _no_triple_repeat(''.join(result).strip())
        return text
    if lesson_type == 'top_row':
        keys = [lbl.lower() for lbl, _ in layout['rows'][1] if len(lbl) == 1 and lbl.isalpha()]
        result = []
        for _ in range(length):
            if random.random() < 0.18 and result and result[-1] != ' ':
                result.append(' ')
            else:
                result.append(random.choice(keys))
        return _no_triple_repeat(''.join(result).strip())
    if lesson_type == 'bottom_row':
        keys = [lbl.lower() for lbl, _ in layout['rows'][3] if len(lbl) == 1 and lbl.isalpha()]
        result = []
        for _ in range(length):
            if random.random() < 0.18 and result and result[-1] != ' ':
                result.append(' ')
            else:
                result.append(random.choice(keys))
        return _no_triple_repeat(''.join(result).strip())
    if lesson_type == 'all_letters':
        keys = []
        for row in layout['rows'][1:4]:
            keys += [lbl.lower() for lbl, _ in row if len(lbl) == 1 and lbl.isalpha()]
        result = []
        for _ in range(length):
            if random.random() < 0.18 and result and result[-1] != ' ':
                result.append(' ')
            else:
                result.append(random.choice(keys))
        return _no_triple_repeat(''.join(result).strip())
    if lesson_type == 'common_words':
        chosen = random.choices(WORDS, k=max(20, length // 5))
        return ' '.join(chosen)
    if lesson_type == 'sentences':
        count = min(3, len(SENTENCES))
        selected = random.sample(SENTENCES, count)
        return ' '.join(selected)
    if lesson_type == 'numbers':
        keys = [lbl for lbl, _ in layout['rows'][0] if len(lbl) == 1]
        result = []
        for _ in range(length):
            if random.random() < 0.15 and result and result[-1] != ' ':
                result.append(' ')
            else:
                result.append(random.choice(keys))
        return _no_triple_repeat(''.join(result).strip())
    if lesson_type == 'progressive':
        # Start with home row, gradually add more keys
        keys = [k.lower() for k in layout['home_keys']]
        all_keys = []
        for row in layout['rows'][1:4]:
            all_keys += [lbl.lower() for lbl, _ in row if len(lbl) == 1 and lbl.isalpha()]
        result = []
        for i in range(length):
            # Gradually increase the pool of keys
            pool_size = min(len(all_keys), 4 + int(i / length * (len(all_keys) - 4)))
            pool = keys + all_keys[:pool_size - len(keys)]
            if not pool: pool = keys
            if random.random() < 0.20 and result and result[-1] != ' ':
                result.append(' ')
            else:
                result.append(random.choice(pool))
        return _no_triple_repeat(''.join(result).strip())
    return gen_lesson(layout_name, 'common_words', length)

LESSON_TYPES = [
    ('home_row', '🏠  Home Row', 'Master the home row keys'),
    ('top_row', '⬆️  Top Row', 'Practice the top letter row'),
    ('bottom_row', '⬇️  Bottom Row', 'Practice the bottom letter row'),
    ('all_letters', '🔤  All Letters', 'All letter keys combined'),
    ('progressive', '📈  Progressive', 'Start easy, gradually add keys'),
    ('common_words', '📝  Common Words', 'Frequently used English words'),
    ('sentences', '📖  Sentences', 'Full sentences for real practice'),
    ('numbers', '🔢  Numbers & Sym', 'Number row and punctuation'),
]

PRACTICE_MODES = [
    ('completion', '📝  Completion', 'Type the full text'),
    ('timed_30', '⏱  30 Seconds', 'Speed test — 30s'),
    ('timed_60', '⏱  60 Seconds', 'Speed test — 60s'),
    ('timed_120', '⏱  2 Minutes', 'Speed test — 120s'),
]

# ─── Global Stylesheet ────────────────────────────────────────────────────────
def get_app_stylesheet():
    return f"""
    QMainWindow {{ background-color: {T('BG')}; }}
    QWidget {{ background-color: {T('BG')}; color: {T('TXT')}; }}
    QLabel {{ background: transparent; color: {T('TXT')}; }}
    QScrollArea {{ border: none; background: transparent; }}
    QScrollBar:vertical {{
        background: {T('CARD')}; width: 8px; border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {T('CARD3')}; border-radius: 4px; min-height: 30px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QTextEdit {{
        background-color: {T('CARD')}; color: {T('TXT')};
        border: none; border-radius: 10px; padding: 10px;
        selection-background-color: {T('ACCENT')};
    }}
    QPlainTextEdit {{
        background-color: {T('CARD')}; color: {T('TXT')};
        border: 1px solid {T('CARD3')}; border-radius: 8px; padding: 8px;
    }}
    QCheckBox {{ color: {T('TXT')}; spacing: 8px; background: transparent; }}
    QCheckBox::indicator {{
        width: 20px; height: 20px; border-radius: 4px;
        border: 2px solid {T('CARD3')}; background: {T('CARD2')};
    }}
    QCheckBox::indicator:checked {{
        background: {T('ACCENT')}; border-color: {T('ACCENT')};
    }}
    QComboBox {{
        background-color: {T('CARD2')}; color: {T('TXT')};
        border: 1px solid {T('CARD3')}; border-radius: 6px;
        padding: 6px 12px; min-height: 28px;
    }}
    QComboBox::drop-down {{ border: none; width: 24px; }}
    QComboBox QAbstractItemView {{
        background-color: {T('CARD2')}; color: {T('TXT')};
        border: 1px solid {T('CARD3')}; selection-background-color: {T('ACCENT')};
    }}
    """

def btn_stylesheet(color_key='CARD2', font_size=13, bold=False, radius=6, text_color=None):
    tc = text_color or T('TXT')
    fw = 'bold' if bold else 'normal'
    hover = T('CARD3') if color_key in ('CARD2', 'CARD') else T(color_key)
    return f"""
    QPushButton {{
        background-color: {T(color_key)}; color: {tc};
        border: none; border-radius: {radius}px;
        padding: 8px 16px; font-size: {font_size}px; font-weight: {fw};
    }}
    QPushButton:hover {{ background-color: {hover}; }}
    QPushButton:pressed {{ background-color: {T('ACCENT')}; }}
    """

def toggle_stylesheet(selected=False, font_size=11):
    bg = T('ACCENT') if selected else T('CARD2')
    tc = '#ffffff' if selected else T('TXT')
    return f"""
    QPushButton {{
        background-color: {bg}; color: {tc};
        border: none; border-radius: 6px;
        padding: 8px 10px; font-size: {font_size}px; font-weight: bold;
    }}
    QPushButton:hover {{ background-color: {T('CARD3') if not selected else T('ACCENT')}; }}
    """

def card_stylesheet(radius=8):
    return f"background-color: {T('CARD')}; border-radius: {radius}px;"

# ─── Custom Widgets ───────────────────────────────────────────────────────────

class ProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(6); self._value = 0.0; self._color_key = 'GREEN'

    def set_value(self, value, color_key='GREEN'):
        self._value = max(0.0, min(1.0, value)); self._color_key = color_key; self.update()

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QBrush(T_color('CARD3'))); p.setPen(Qt.NoPen)
        p.drawRoundedRect(self.rect(), 3, 3)
        fw = self.width() * self._value
        if fw > 0:
            p.setBrush(QBrush(T_color(self._color_key)))
            p.drawRoundedRect(QRectF(0, 0, fw, self.height()), 3, 3)


class WpmChart(QWidget):
    """Simple WPM history chart drawn with QPainter."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(140)
        self._data = []

    def set_data(self, wpms):
        self._data = list(wpms)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        margin = 30

        # Background
        p.setBrush(QBrush(T_color('CARD')))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(self.rect(), 8, 8)

        if len(self._data) < 2:
            p.setPen(QPen(T_color('DIM')))
            p.setFont(QFont("Segoe UI", 11))
            p.drawText(self.rect(), Qt.AlignCenter, 'Need at least 2 sessions for a chart')
            return

        chart_w = w - margin * 2
        chart_h = h - margin * 2
        max_wpm = max(self._data) * 1.15 or 1

        # Grid lines
        p.setPen(QPen(T_color('CARD3'), 1, Qt.DotLine))
        for i in range(5):
            y = margin + chart_h * i / 4
            p.drawLine(margin, int(y), w - margin, int(y))
            val = int(max_wpm * (1 - i / 4))
            p.setPen(QPen(T_color('DIM')))
            p.setFont(QFont("Segoe UI", 8))
            p.drawText(0, int(y) - 6, margin - 4, 14, Qt.AlignRight | Qt.AlignVCenter, str(val))
            p.setPen(QPen(T_color('CARD3'), 1, Qt.DotLine))

        # Data line + fill
        points = []
        n = len(self._data)
        for i, v in enumerate(self._data):
            x = margin + (i / (n - 1)) * chart_w
            y = margin + chart_h * (1 - v / max_wpm)
            points.append((x, y))

        # Fill area under curve
        fill_path = QPainterPath() if False else None
        from PySide6.QtGui import QPainterPath
        path = QPainterPath()
        path.moveTo(points[0][0], points[0][1])
        for x, y in points[1:]:
            path.lineTo(x, y)

        # Fill
        fill = QPainterPath()
        fill.moveTo(points[0][0], margin + chart_h)
        for x, y in points:
            fill.lineTo(x, y)
        fill.lineTo(points[-1][0], margin + chart_h)
        fill.closeSubpath()

        accent = T_color('ACCENT')
        fill_color = QColor(accent)
        fill_color.setAlpha(30)
        p.setBrush(QBrush(fill_color))
        p.setPen(Qt.NoPen)
        p.drawPath(fill)

        # Line
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(accent, 2.5))
        p.drawPath(path)

        # Dots
        for x, y in points:
            p.setBrush(QBrush(accent))
            p.setPen(Qt.NoPen)
            p.drawEllipse(QRectF(x - 4, y - 4, 8, 8))

        # Labels
        p.setPen(QPen(T_color('DIM')))
        p.setFont(QFont("Segoe UI", 8))
        p.drawText(self.rect().adjusted(0, 0, 0, -4), Qt.AlignHCenter | Qt.AlignBottom,
                   f'{n} sessions')


class VisualKeyboard(QWidget):
    tapped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout_name = 'QWERTY'
        self.highlight_char = ''
        self.key_rects = {}
        self.flash_label = None
        self.error_key = None  # Flash red on error
        self.flash_timer = QTimer(); self.flash_timer.setSingleShot(True)
        self.flash_timer.timeout.connect(self._clear_flash)
        self.error_timer = QTimer(); self.error_timer.setSingleShot(True)
        self.error_timer.timeout.connect(self._clear_error)
        self.show_heatmap = False  # Show accuracy heatmap
        self.setFixedHeight(235); self.setMinimumWidth(580)

    def set_layout(self, name):
        self.layout_name = name; self.update()

    def set_highlight(self, char):
        self.highlight_char = char; self.update()

    def flash_key(self, char):
        self.flash_label = find_key_label(self.layout_name, char)
        self.update(); self.flash_timer.start(120)

    def flash_error(self, char):
        self.error_key = find_key_label(self.layout_name, char)
        self.update(); self.error_timer.start(300)

    def _clear_flash(self):
        self.flash_label = None; self.update()

    def _clear_error(self):
        self.error_key = None; self.update()

    def set_heatmap(self, enabled):
        self.show_heatmap = enabled; self.update()

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        layout = LAYOUTS.get(self.layout_name, LAYOUTS['QWERTY'])
        home_keys = set(layout.get('home_keys', []))
        offsets = layout.get('offsets', [0] * 5)
        w = self.width() - 8
        max_units = max(
            (sum(wu for _, wu in row) + offsets[i]) for i, row in enumerate(layout['rows'])
        )
        uw = w / max_units; kh = 40; rs = 4; ys = 4
        self.key_rects = {}

        for ri, row in enumerate(layout['rows']):
            off = offsets[ri] if ri < len(offsets) else 0
            x = 4.0 + off * uw; y = ys + ri * (kh + rs)
            for ci, (lbl, wu) in enumerate(row):
                kw = wu * uw - 2
                rect = QRectF(x + 1, y, kw, kh)
                self.key_rects[lbl] = rect
                fi = get_finger(self.layout_name, lbl)
                ih = lbl in home_keys
                target_lbl = find_key_label(self.layout_name, self.highlight_char) if self.highlight_char else None
                is_hl = (lbl == target_lbl)
                is_shift = (self.highlight_char and self.highlight_char.isupper() and lbl == '⇧')
                is_flash = (self.flash_label == lbl)
                is_error = (self.error_key == lbl)

                if is_error:
                    bg = T_color('RED'); bg.setAlpha(200); tc = QColor(255, 255, 255)
                elif is_hl or is_shift:
                    bg = T_color('YELLOW'); bg.setAlpha(235); tc = QColor(26, 26, 38)
                elif is_flash:
                    bg = T_color('ACCENT'); bg.setAlpha(217); tc = T_color('TXT')
                elif self.show_heatmap and len(lbl) == 1 and lbl.isalpha():
                    # Show accuracy heatmap
                    acc = self.parent()  # Will use stats_mgr directly
                    from PySide6.QtWidgets import QApplication
                    mw = QApplication.instance().activeWindow()
                    if mw and hasattr(mw, 'stats_mgr'):
                        accuracy = mw.stats_mgr.get_key_accuracy(self.layout_name, lbl)
                    else:
                        accuracy = 1.0
                    # Green for high accuracy, red for low
                    r = int((1.0 - accuracy) * 200)
                    g = int(accuracy * 180)
                    bg = QColor(r, g, 60, 140); tc = T_color('TXT')
                else:
                    fc = FINGER_COLS[fi] if 0 <= fi < 9 else (0.3, 0.3, 0.4)
                    bg = QColor(int(fc[0]*255), int(fc[1]*255), int(fc[2]*255)); bg.setAlpha(115)
                    tc = T_color('TXT')

                p.setBrush(QBrush(bg)); p.setPen(Qt.NoPen)
                p.drawRoundedRect(rect, 6, 6)

                # Home key bump
                if ih and not is_hl:
                    p.setBrush(QBrush(QColor(255, 255, 255, 153)))
                    p.drawRoundedRect(QRectF(rect.center().x() - 6, rect.bottom() - 7, 12, 3), 1.5, 1.5)

                display = lbl if lbl != 'SPACE' else '⎵ SPACE'
                p.setPen(QPen(tc))
                font = p.font(); font.setPointSize(13 if len(display) <= 2 else 10)
                p.setFont(font); p.drawText(rect, Qt.AlignCenter, display)
                x += wu * uw

    def mousePressEvent(self, event):
        pos = event.position()
        for lbl, rect in self.key_rects.items():
            if rect.contains(pos):
                ch = ' ' if lbl == 'SPACE' else lbl.lower()
                self.tapped.emit(ch); break


# ─── Screens ──────────────────────────────────────────────────────────────────

class MenuScreen(QWidget):
    start_requested = Signal()

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.mw = main_window
        self._layout_btns = {}; self._lesson_btns = {}; self._mode_btns = {}
        self._layout_group = QButtonGroup(self)
        self._lesson_group = QButtonGroup(self)
        self._mode_group = QButtonGroup(self)
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 16, 20, 16)

        # Title
        title = QLabel('⌨️  Keyboard Trainer')
        title.setFont(QFont("Segoe UI", 26, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        sub = QLabel('Learn to type fast & accurately on any layout')
        sub.setFont(QFont("Segoe UI", 12))
        sub.setStyleSheet(f"color: {T('DIM')};")
        sub.setAlignment(Qt.AlignCenter)
        layout.addWidget(sub)
        layout.addSpacing(6)

        # Layout selection
        layout.addWidget(self._section_label('Select Keyboard Layout'))
        lg = QGridLayout(); lg.setSpacing(6)
        sel_layout = settings_mgr.get('layout', 'QWERTY')
        for i, (name, data) in enumerate(LAYOUTS.items()):
            b = QPushButton(data['display'])
            b.setCheckable(True); b.setFixedHeight(42)
            b.setChecked(name == sel_layout)
            b.setStyleSheet(toggle_stylesheet(name == sel_layout))
            self._layout_btns[name] = b; self._layout_group.addButton(b)
            lg.addWidget(b, i // 2, i % 2)
        self._layout_group.idToggled.connect(self._on_layout_toggle)
        layout.addLayout(lg)

        # Lesson selection
        layout.addWidget(self._section_label('Choose Lesson'))
        lsg = QGridLayout(); lsg.setSpacing(5)
        sel_lesson = settings_mgr.get('lesson', 'home_row')
        for i, (ltype, lname, ldesc) in enumerate(LESSON_TYPES):
            b = QPushButton(lname)
            b.setCheckable(True); b.setFixedHeight(42)
            b.setChecked(ltype == sel_lesson)
            b.setStyleSheet(toggle_stylesheet(ltype == sel_lesson))
            b.setToolTip(ldesc)
            self._lesson_btns[ltype] = b; self._lesson_group.addButton(b)
            lsg.addWidget(b, i // 2, i % 2)
        self._lesson_group.idToggled.connect(self._on_lesson_toggle)
        layout.addLayout(lsg)

        # Practice mode
        layout.addWidget(self._section_label('Practice Mode'))
        mg = QGridLayout(); mg.setSpacing(5)
        sel_mode = settings_mgr.get('mode', 'completion')
        for i, (mtype, mname, mdesc) in enumerate(PRACTICE_MODES):
            b = QPushButton(mname)
            b.setCheckable(True); b.setFixedHeight(42)
            b.setChecked(mtype == sel_mode)
            b.setStyleSheet(toggle_stylesheet(mtype == sel_mode))
            b.setToolTip(mdesc)
            self._mode_btns[mtype] = b; self._mode_group.addButton(b)
            mg.addWidget(b, i // 2, i % 2)
        self._mode_group.idToggled.connect(self._on_mode_toggle)
        layout.addLayout(mg)

        layout.addSpacing(8)

        # Start button
        start_btn = QPushButton('▶  Start Typing')
        start_btn.setFixedHeight(52)
        start_btn.setStyleSheet(btn_stylesheet('ACCENT', 18, bold=True, text_color='#ffffff'))
        start_btn.clicked.connect(self._start)
        layout.addWidget(start_btn)

        # Custom text
        custom_btn = QPushButton('✏️  Custom Text Practice')
        custom_btn.setFixedHeight(44)
        custom_btn.setStyleSheet(btn_stylesheet('CARD3', 14))
        custom_btn.clicked.connect(lambda: self.mw.go_to('custom'))
        layout.addWidget(custom_btn)

        # Stats & Settings row
        row = QHBoxLayout(); row.setSpacing(8)
        stats_btn = QPushButton('📊  Statistics')
        stats_btn.setFixedHeight(44)
        stats_btn.setStyleSheet(btn_stylesheet('CARD2', 13))
        stats_btn.clicked.connect(lambda: self.mw.go_to('stats'))
        settings_btn = QPushButton('⚙️  Settings')
        settings_btn.setFixedHeight(44)
        settings_btn.setStyleSheet(btn_stylesheet('CARD2', 13))
        settings_btn.clicked.connect(lambda: self.mw.go_to('settings'))
        row.addWidget(stats_btn); row.addWidget(settings_btn)
        layout.addLayout(row)

        layout.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)

    def _section_label(self, text):
        l = QLabel(text)
        l.setFont(QFont("Segoe UI", 13, QFont.Bold))
        l.setStyleSheet(f"color: {T('ACCENT')}; background: transparent;")
        return l

    def _on_layout_toggle(self, btn, checked):
        if not checked: return
        for name, b in self._layout_btns.items():
            sel = b == btn
            b.setStyleSheet(toggle_stylesheet(sel))
            if sel: settings_mgr.set('layout', name)

    def _on_lesson_toggle(self, btn, checked):
        if not checked: return
        for ltype, b in self._lesson_btns.items():
            sel = b == btn
            b.setStyleSheet(toggle_stylesheet(sel))
            if sel: settings_mgr.set('lesson', ltype)

    def _on_mode_toggle(self, btn, checked):
        if not checked: return
        for mtype, b in self._mode_btns.items():
            sel = b == btn
            b.setStyleSheet(toggle_stylesheet(sel))
            if sel: settings_mgr.set('mode', mtype)

    def _start(self):
        self.mw.current_layout = settings_mgr.get('layout', 'QWERTY')
        self.mw.current_lesson = settings_mgr.get('lesson', 'home_row')
        self.mw.current_mode = settings_mgr.get('mode', 'completion')
        self.mw.typing_screen.start_lesson(
            self.mw.current_layout, self.mw.current_lesson, self.mw.current_mode)
        self.mw.go_to('typing')

    def refresh_theme(self):
        for name, b in self._layout_btns.items():
            b.setStyleSheet(toggle_stylesheet(b.isChecked()))
        for ltype, b in self._lesson_btns.items():
            b.setStyleSheet(toggle_stylesheet(b.isChecked()))
        for mtype, b in self._mode_btns.items():
            b.setStyleSheet(toggle_stylesheet(b.isChecked()))


class TypingScreen(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.mw = main_window
        self.setFocusPolicy(Qt.StrongFocus)
        self.layout_name = 'QWERTY'; self.lesson_text = ''
        self.typed = []; self.char_idx = 0; self.start_time = None
        self.errors = 0; self.total_keystrokes = 0; self.streak = 0
        self.best_streak = 0; self._finished = False
        self.mode = 'completion'; self.timer_secs = 0
        self.key_errors = {}  # Track per-key errors for this session
        self._timer = QTimer(); self._timer.setInterval(200)
        self._timer.timeout.connect(self._tick)
        self._caps_lock = False
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(4); layout.setContentsMargins(10, 8, 10, 8)

        # Top bar
        top = QHBoxLayout(); top.setSpacing(6)
        back_btn = QPushButton('← Back')
        back_btn.setFixedWidth(76); back_btn.setFocusPolicy(Qt.NoFocus)
        back_btn.setStyleSheet(btn_stylesheet('CARD2', 12))
        back_btn.clicked.connect(self._go_back)
        top.addWidget(back_btn)
        self.lbl_lesson = QLabel('')
        self.lbl_lesson.setFont(QFont("Segoe UI", 11))
        self.lbl_lesson.setStyleSheet(f"color: {T('DIM')}; background: transparent;")
        top.addWidget(self.lbl_lesson, 1)
        self.lbl_wpm = QLabel('WPM: 0')
        self.lbl_wpm.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.lbl_wpm.setStyleSheet(f"color: {T('GREEN')}; background: transparent;")
        top.addWidget(self.lbl_wpm)
        self.lbl_acc = QLabel('ACC: 100%')
        self.lbl_acc.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.lbl_acc.setStyleSheet(f"color: {T('ACCENT')}; background: transparent;")
        top.addWidget(self.lbl_acc)
        self.lbl_time = QLabel('⏱ 0:00')
        self.lbl_time.setFont(QFont("Segoe UI", 12))
        self.lbl_time.setStyleSheet(f"color: {T('ORANGE')}; background: transparent;")
        top.addWidget(self.lbl_time)
        self.lbl_streak = QLabel('🔥 0')
        self.lbl_streak.setFont(QFont("Segoe UI", 12))
        self.lbl_streak.setStyleSheet(f"color: {T('YELLOW')}; background: transparent;")
        top.addWidget(self.lbl_streak)
        self.lbl_words = QLabel('')
        self.lbl_words.setFont(QFont("Segoe UI", 11))
        self.lbl_words.setStyleSheet(f"color: {T('DIM')}; background: transparent;")
        top.addWidget(self.lbl_words)
        layout.addLayout(top)

        # Progress bar
        self.progress = ProgressBar()
        layout.addWidget(self.progress)

        # Finger hint + expected key
        hint_row = QHBoxLayout()
        self.lbl_finger = QLabel('')
        self.lbl_finger.setFixedHeight(22)
        self.lbl_finger.setFont(QFont("Segoe UI", 12))
        self.lbl_finger.setStyleSheet(f"color: {T('DIM')}; background: transparent;")
        hint_row.addWidget(self.lbl_finger)
        self.lbl_expected = QLabel('')
        self.lbl_expected.setFixedHeight(22)
        self.lbl_expected.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.lbl_expected.setStyleSheet(f"color: {T('YELLOW')}; background: transparent;")
        self.lbl_expected.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        hint_row.addWidget(self.lbl_expected)
        layout.addLayout(hint_row)

        # Typing area
        self.typing_display = QTextEdit()
        self.typing_display.setReadOnly(True)
        self.typing_display.setFocusPolicy(Qt.NoFocus)
        self.typing_display.setFixedHeight(150)
        self.typing_display.setFont(QFont("Consolas", 16))
        self.typing_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: {T('CARD')}; color: {T('TXT')};
                border: none; border-radius: 10px; padding: 12px;
            }}
        """)
        layout.addWidget(self.typing_display)

        layout.addSpacing(6)

        # Visual keyboard
        self.keyboard = VisualKeyboard()
        self.keyboard.tapped.connect(self._handle_tap)
        layout.addWidget(self.keyboard)

        # Hint
        hint = QLabel('Type the highlighted character  •  Esc = quit  •  Tab = restart')
        hint.setFixedHeight(18)
        hint.setFont(QFont("Segoe UI", 9))
        hint.setStyleSheet(f"color: {T('DIM')}; background: transparent;")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)

    def start_lesson(self, layout_name, lesson_type, mode='completion', custom_text=''):
        self.layout_name = layout_name; self.mode = mode; self.timer_secs = 0
        self.key_errors = {}
        if mode.startswith('timed_'):
            self.timer_secs = int(mode.split('_')[1])
            self.lesson_text = gen_lesson(layout_name, lesson_type, 800)
        elif lesson_type == 'custom':
            self.lesson_text = custom_text if custom_text else 'The quick brown fox jumps over the lazy dog.'
        else:
            self.lesson_text = gen_lesson(layout_name, lesson_type, 160)
        # Ensure lesson text is not empty
        if not self.lesson_text.strip():
            self.lesson_text = 'The quick brown fox jumps over the lazy dog.'
        self.typed = []; self.char_idx = 0; self.start_time = None
        self.errors = 0; self.total_keystrokes = 0; self.streak = 0; self.best_streak = 0
        self._finished = False
        mode_disp = mode.replace('_', ' ').title()
        self.lbl_lesson.setText(
            f'{LAYOUTS[layout_name]["display"]}  •  {lesson_type.replace("_"," ").title()}  •  {mode_disp}')
        self.keyboard.set_layout(layout_name)
        self.keyboard.show_heatmap = settings_mgr.get('show_keyboard', True)
        self._refresh_display(); self._update_stats()
        self._timer.start()
        self.setFocus()

    def keyPressEvent(self, event):
        if self._finished: return
        key = event.key(); text = event.text()
        if key == Qt.Key_Escape: self._go_back(); return
        if key == Qt.Key_Tab:
            # Restart lesson
            self.start_lesson(self.layout_name, settings_mgr.get('lesson', 'home_row'), self.mode)
            return
        if key == Qt.Key_Backspace: self._handle_backspace(); return
        if key == Qt.Key_CapsLock:
            self._caps_lock = not self._caps_lock; return
        skip_keys = {
            Qt.Key_Shift, Qt.Key_Control, Qt.Key_Alt, Qt.Key_Meta,
            Qt.Key_Tab, Qt.Key_Insert, Qt.Key_Delete,
            Qt.Key_Home, Qt.Key_End, Qt.Key_PageUp, Qt.Key_PageDown,
            Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right,
            Qt.Key_NumLock, Qt.Key_ScrollLock, Qt.Key_Pause,
            Qt.Key_F1, Qt.Key_F2, Qt.Key_F3, Qt.Key_F4, Qt.Key_F5,
            Qt.Key_F6, Qt.Key_F7, Qt.Key_F8, Qt.Key_F9, Qt.Key_F10,
            Qt.Key_F11, Qt.Key_F12, Qt.Key_Enter, Qt.Key_Return,
        }
        if key in skip_keys: return
        if text and len(text) == 1:
            self._handle_char(text)

    def _handle_tap(self, char):
        if not self._finished: self._handle_char(char)

    def _handle_char(self, ch):
        if self.char_idx >= len(self.lesson_text): return
        if self.start_time is None: self.start_time = time.time()
        expected = self.lesson_text[self.char_idx]
        correct = (ch == expected)
        self.typed.append((ch, correct)); self.total_keystrokes += 1

        # Record per-key stats
        self.mw.stats_mgr.record_key(self.layout_name, expected, correct)

        if correct:
            self.streak += 1
            if self.streak > self.best_streak: self.best_streak = self.streak
            sound_mgr.play('click')
            # Streak milestone sounds
            if self.streak > 0 and self.streak % 25 == 0:
                sound_mgr.play('streak')
            self.keyboard.flash_key(ch)
        else:
            self.errors += 1; self.streak = 0; sound_mgr.play('error')
            self.keyboard.flash_error(expected)
            # Track key errors
            ek = expected.upper()
            self.key_errors[ek] = self.key_errors.get(ek, 0) + 1

        self.char_idx += 1; self._refresh_display(); self._update_stats()
        if self.mode == 'completion' and self.char_idx >= len(self.lesson_text):
            self._finish()

    def _handle_backspace(self):
        if self.char_idx > 0 and self.typed:
            self.char_idx -= 1; ch, correct = self.typed.pop()
            self.total_keystrokes = max(0, self.total_keystrokes - 1)
            if not correct: self.errors = max(0, self.errors - 1)
            self.streak = 0; self._refresh_display(); self._update_stats()

    @staticmethod
    def _esc(ch):
        return ch.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

    def _refresh_display(self):
        text = self.lesson_text; parts = []
        # Show a window of characters around the current position
        window_before = 50; window_after = 80
        start = max(0, self.char_idx - window_before)

        for i in range(start, self.char_idx):
            if i >= len(self.typed): break
            ch, correct = self.typed[i]
            c = text[i]; escaped = self._esc(c)
            if correct:
                parts.append(f'<span style="color:{T("GREEN")}">{escaped}</span>')
            else:
                # Show what was expected with strikethrough, and what was typed
                typed_escaped = self._esc(ch) if ch != c else ''
                parts.append(
                    f'<span style="color:{T("RED")}"><s>{escaped}</s></span>'
                )

        if self.char_idx < len(text):
            cur = text[self.char_idx]
            cur_escaped = self._esc(cur)
            # Determine display character
            display_char = '⎵' if cur == ' ' else cur_escaped
            parts.append(
                f'<span style="color:{T("YELLOW")}; text-decoration:underline; '
                f'font-weight:bold; background-color:rgba(255,255,255,15); '
                f'border-radius:2px; padding:0 2px;">{display_char}</span>'
            )
            self.keyboard.set_highlight(cur)
            fi = get_finger(self.layout_name, cur)
            if 0 <= fi < 9:
                fc = FINGER_COLS[fi]
                col = rgb_hex(*fc)
                self.lbl_finger.setText(f'👉 {FINGER_NAMES[fi]}')
                self.lbl_finger.setStyleSheet(f"color: {col}; background: transparent;")
            else:
                self.lbl_finger.setText('')
                self.lbl_finger.setStyleSheet(f"color: {T('DIM')}; background: transparent;")
            # Show expected key label
            key_label = find_key_label(self.layout_name, cur)
            if key_label and key_label != 'SPACE':
                shift_note = ' (Shift+)' if cur.isupper() else ''
                self.lbl_expected.setText(f'Press: {key_label}{shift_note}')
            elif cur == ' ':
                self.lbl_expected.setText('Press: Space')
            else:
                self.lbl_expected.setText('')
        else:
            self.keyboard.set_highlight('')
            self.lbl_finger.setText('✅ Complete!')
            self.lbl_finger.setStyleSheet(f"color: {T('GREEN')}; background: transparent;")
            self.lbl_expected.setText('')

        end = min(len(text), self.char_idx + window_after)
        for i in range(self.char_idx + 1, end):
            escaped = self._esc(text[i])
            # Slightly highlight upcoming space boundaries for readability
            if text[i] == ' ':
                parts.append(f'<span style="color:{T("CARD3")}">·</span>')
            else:
                parts.append(f'<span style="color:{T("DIM")}">{escaped}</span>')

        html = ('<div style="font-family: Consolas, monospace; font-size: 18px; '
                'line-height: 1.6; letter-spacing: 0.5px;">' + ''.join(parts) + '</div>')
        self.typing_display.setHtml(html)
        # Scroll to keep cursor visible
        sb = self.typing_display.verticalScrollBar()
        sb.setValue(sb.maximum())

        # Progress bar
        if self.mode.startswith('timed_') and self.start_time:
            elapsed_s = time.time() - self.start_time
            pct = min(1.0, elapsed_s / self.timer_secs)
            self.progress.set_value(pct, 'ORANGE')
        else:
            pct = self.char_idx / max(1, len(text))
            self.progress.set_value(pct, 'GREEN')

    def _update_stats(self):
        if self.start_time is None:
            self.lbl_wpm.setText('WPM: 0'); self.lbl_acc.setText('ACC: 100%')
            self.lbl_words.setText(''); return
        elapsed = max(0.1, time.time() - self.start_time)
        correct_chars = sum(1 for _, ok in self.typed if ok)
        wpm = (correct_chars / 5) / (elapsed / 60)
        acc = (correct_chars / max(1, self.total_keystrokes)) * 100

        # Word count for timed mode
        if self.mode.startswith('timed_'):
            word_count = sum(1 for i, (_, ok) in enumerate(self.typed)
                           if ok and self.typed[i][0] == ' ' and i > 0 and self.typed[i-1][1])
            self.lbl_words.setText(f'📝 ~{word_count}w')

        self.lbl_wpm.setText(f'WPM: {int(wpm)}')
        self.lbl_wpm.setStyleSheet(
            f"color: {T('GREEN') if wpm >= 30 else T('ORANGE') if wpm >= 15 else T('RED')}; background: transparent;")
        self.lbl_acc.setText(f'ACC: {acc:.1f}%')
        self.lbl_acc.setStyleSheet(
            f"color: {T('GREEN') if acc >= 95 else T('ORANGE') if acc >= 85 else T('RED')}; background: transparent;")
        self.lbl_streak.setText(f'🔥 {self.streak}')
        if self.streak >= 10:
            self.lbl_streak.setStyleSheet(f"color: {T('YELLOW')}; background: transparent;")
        else:
            self.lbl_streak.setStyleSheet(f"color: {T('DIM')}; background: transparent;")

    def _tick(self):
        if self.start_time is None:
            if self.mode.startswith('timed_'):
                self.lbl_time.setText(f'⏱ 0:{self.timer_secs:02d}')
            else:
                self.lbl_time.setText('⏱ 0:00')
            return
        elapsed_s = time.time() - self.start_time
        if self.mode.startswith('timed_'):
            remaining = max(0, self.timer_secs - elapsed_s)
            m, s = divmod(int(remaining), 60)
            self.lbl_time.setText(f'⏱ {m}:{s:02d}')
            self.lbl_time.setStyleSheet(
                f"color: {T('RED') if remaining < 10 else T('ORANGE')}; background: transparent;")
            self._refresh_display()
            if remaining <= 0 and not self._finished:
                self._finish()
        else:
            m, s = divmod(int(elapsed_s), 60)
            self.lbl_time.setText(f'⏱ {m}:{s:02d}')
        self._update_stats()

    def _finish(self):
        self._finished = True; self._timer.stop()
        sound_mgr.play('done')
        elapsed = max(0.1, time.time() - self.start_time) if self.start_time else 1
        correct = sum(1 for _, ok in self.typed if ok)
        wpm = (correct / 5) / (elapsed / 60)
        acc = (correct / max(1, self.total_keystrokes)) * 100
        self.mw.stats_mgr.add_stat(
            self.layout_name, settings_mgr.get('lesson', 'home_row'),
            wpm, acc, elapsed, self.key_errors)
        # Force save key stats
        self.mw.stats_mgr.save()
        self.mw.results_screen.set_results(
            wpm, acc, elapsed, correct, self.errors,
            self.total_keystrokes, self.layout_name, self.best_streak)
        QTimer.singleShot(500, lambda: self.mw.go_to('results'))

    def _go_back(self):
        self._timer.stop(); self.mw.go_to('menu')

    def refresh_theme(self):
        self.typing_display.setStyleSheet(f"""
            QTextEdit {{ background-color: {T('CARD')}; color: {T('TXT')};
            border: none; border-radius: 10px; padding: 12px; }}
        """)
        self.keyboard.update(); self.progress.update()


class ResultsScreen(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.mw = main_window
        self._wpm = 0; self._acc = 0; self._elapsed = 0
        self._correct = 0; self._errors = 0; self._total = 0
        self._layout = ''; self._best_streak = 0
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12); layout.setContentsMargins(24, 24, 24, 24)

        self.lbl_title = QLabel('🎉  Lesson Complete!')
        self.lbl_title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setStyleSheet(f"color: {T('YELLOW')}; background: transparent;")
        layout.addWidget(self.lbl_title)

        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(8)
        layout.addLayout(self.stats_grid)

        layout.addStretch()

        self.lbl_rating = QLabel('')
        self.lbl_rating.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.lbl_rating.setAlignment(Qt.AlignCenter)
        self.lbl_rating.setStyleSheet(f"color: {T('TXT')}; background: transparent;")
        layout.addWidget(self.lbl_rating)

        self.lbl_stars = QLabel('')
        self.lbl_stars.setFont(QFont("Segoe UI", 30))
        self.lbl_stars.setAlignment(Qt.AlignCenter)
        self.lbl_stars.setStyleSheet(f"color: {T('YELLOW')}; background: transparent;")
        layout.addWidget(self.lbl_stars)

        # Problem keys
        self.lbl_problems = QLabel('')
        self.lbl_problems.setFont(QFont("Segoe UI", 11))
        self.lbl_problems.setAlignment(Qt.AlignCenter)
        self.lbl_problems.setStyleSheet(f"color: {T('ORANGE')}; background: transparent;")
        layout.addWidget(self.lbl_problems)

        btn_box = QHBoxLayout(); btn_box.setSpacing(10)
        retry_btn = QPushButton('🔄  Try Again')
        retry_btn.setFixedHeight(48)
        retry_btn.setStyleSheet(btn_stylesheet('ACCENT', 15, bold=True, text_color='#ffffff'))
        retry_btn.clicked.connect(self._retry)
        next_btn = QPushButton('➡️  Next Lesson')
        next_btn.setFixedHeight(48)
        next_btn.setStyleSheet(btn_stylesheet('GREEN', 15, bold=True, text_color='#ffffff'))
        next_btn.clicked.connect(self._next_lesson)
        menu_btn = QPushButton('🏠  Menu')
        menu_btn.setFixedHeight(48)
        menu_btn.setStyleSheet(btn_stylesheet('CARD2', 15))
        menu_btn.clicked.connect(lambda: self.mw.go_to('menu'))
        btn_box.addWidget(retry_btn); btn_box.addWidget(next_btn); btn_box.addWidget(menu_btn)
        layout.addLayout(btn_box)

    def set_results(self, wpm, acc, elapsed, correct, errors, total, layout_name, best_streak=0):
        self._wpm = wpm; self._acc = acc; self._elapsed = elapsed
        self._correct = correct; self._errors = errors; self._total = total
        self._layout = layout_name; self._best_streak = best_streak

        # Clear grid
        while self.stats_grid.count():
            item = self.stats_grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        stats = [
            ('⌨️ Layout', LAYOUTS[layout_name]['display']),
            ('⚡ Speed', f'{int(wpm)} WPM'),
            ('🎯 Accuracy', f'{acc:.1f}%'),
            ('⏱ Time', f'{int(elapsed // 60)}:{int(elapsed % 60):02d}'),
            ('✅ Correct', str(correct)),
            ('❌ Errors', str(errors)),
            ('🔥 Best Streak', str(best_streak)),
            ('📊 Keystrokes', str(total)),
            ('📈 Chars/min', f'{int(correct / max(1, elapsed) * 60)}'),
        ]
        for i, (label, value) in enumerate(stats):
            l = QLabel(label); l.setFont(QFont("Segoe UI", 12))
            l.setStyleSheet(f"color: {T('DIM')}; background: transparent;")
            l.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            v = QLabel(value); v.setFont(QFont("Segoe UI", 14, QFont.Bold))
            # Color code important values
            color = T('TXT')
            if label == '⚡ Speed':
                color = T('GREEN') if wpm >= 30 else T('ORANGE') if wpm >= 15 else T('RED')
            elif label == '🎯 Accuracy':
                color = T('GREEN') if acc >= 95 else T('ORANGE') if acc >= 85 else T('RED')
            v.setStyleSheet(f"color: {color}; background: transparent;")
            v.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.stats_grid.addWidget(l, i, 0)
            self.stats_grid.addWidget(v, i, 1)

        # Star rating
        if acc >= 98 and wpm >= 50:   stars, rating, rc = 5, '🏆 PERFECT! Typing master!', T('YELLOW')
        elif acc >= 95 and wpm >= 35: stars, rating, rc = 4, '⭐ Excellent!', T('GREEN')
        elif acc >= 90:               stars, rating, rc = 3, '👍 Good job!', T('ACCENT')
        elif acc >= 80:               stars, rating, rc = 2, '💪 Keep at it!', T('ORANGE')
        else:                         stars, rating, rc = 1, '📚 Practice more!', T('RED')
        self.lbl_rating.setText(rating)
        self.lbl_rating.setStyleSheet(f"color: {rc}; background: transparent;")
        self.lbl_stars.setText('★' * stars + '☆' * (5 - stars))

        # Check if new personal best
        best = self.mw.stats_mgr.get_best(layout_name)
        if best and best.get('wpm', 0) > 0:
            diff = int(wpm) - int(best.get('wpm', 0))
            if diff > 0:
                self.lbl_rating.setText(rating + f'  🏅 New best! (+{diff} WPM)')

        # Show problem keys
        problem_keys = []
        for key, errors in sorted(
            self.mw.stats_mgr.key_stats.items(),
            key=lambda x: x[1].get('errors', 0), reverse=True
        )[:3]:
            if key.startswith(f"{layout_name}:") and errors.get('errors', 0) > 0:
                k = key.split(':')[-1]
                total_k = errors.get('total', 1)
                acc_k = (1 - errors['errors'] / max(1, total_k)) * 100
                problem_keys.append(f'{k} ({acc_k:.0f}%)')
        if problem_keys:
            self.lbl_problems.setText(f'⚠️ Weakest keys: {", ".join(problem_keys)}')
        else:
            self.lbl_problems.setText('')

    def _retry(self):
        self.mw.typing_screen.start_lesson(
            self.mw.current_layout, settings_mgr.get('lesson', 'home_row'), self.mw.current_mode)
        self.mw.go_to('typing')

    def _next_lesson(self):
        # Advance to the next lesson type
        lesson_keys = [lt for lt, _, _ in LESSON_TYPES]
        current = settings_mgr.get('lesson', 'home_row')
        try:
            idx = lesson_keys.index(current)
            next_idx = (idx + 1) % len(lesson_keys)
        except ValueError:
            next_idx = 0
        next_lesson = lesson_keys[next_idx]
        settings_mgr.set('lesson', next_lesson)
        self.mw.current_lesson = next_lesson
        self.mw.typing_screen.start_lesson(
            self.mw.current_layout, next_lesson, self.mw.current_mode)
        self.mw.go_to('typing')

    def refresh_theme(self):
        self.lbl_title.setStyleSheet(f"color: {T('YELLOW')}; background: transparent;")
        self.lbl_rating.setStyleSheet(f"color: {T('TXT')}; background: transparent;")
        self.lbl_stars.setStyleSheet(f"color: {T('YELLOW')}; background: transparent;")
        self.lbl_problems.setStyleSheet(f"color: {T('ORANGE')}; background: transparent;")


class StatsScreen(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.mw = main_window; self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8); layout.setContentsMargins(16, 16, 16, 16)

        # Header
        header = QHBoxLayout()
        back_btn = QPushButton('← Back')
        back_btn.setFixedWidth(76)
        back_btn.setStyleSheet(btn_stylesheet('CARD2', 12))
        back_btn.clicked.connect(lambda: self.mw.go_to('menu'))
        header.addWidget(back_btn)
        title = QLabel('📊  Your Statistics')
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet(f"color: {T('TXT')}; background: transparent;")
        header.addWidget(title, 1)
        layout.addLayout(header)

        # Summary cards
        self.summary_layout = QHBoxLayout()
        self.summary_layout.setSpacing(6)
        layout.addLayout(self.summary_layout)

        # WPM Chart
        layout.addWidget(QLabel('📈  WPM Over Time'))
        self.chart = WpmChart()
        layout.addWidget(self.chart)

        # Layout filter
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel('Filter by layout:'))
        self.layout_filter = QComboBox()
        self.layout_filter.addItem('All Layouts', '')
        for name, data in LAYOUTS.items():
            self.layout_filter.addItem(data['display'], name)
        self.layout_filter.currentIndexChanged.connect(self._refresh)
        filter_row.addWidget(self.layout_filter, 1)
        layout.addLayout(filter_row)

        # History
        scroll = QScrollArea()
        scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        self.history_widget = QWidget()
        self.history_layout = QVBoxLayout(self.history_widget)
        self.history_layout.setSpacing(6)
        self.history_layout.setContentsMargins(4, 4, 4, 4)
        self.history_layout.addStretch()
        scroll.setWidget(self.history_widget)
        layout.addWidget(scroll, 1)

        # Bottom buttons
        bottom_row = QHBoxLayout()
        export_btn = QPushButton('📤  Export Stats')
        export_btn.setFixedHeight(42)
        export_btn.setStyleSheet(btn_stylesheet('CARD2', 12))
        export_btn.clicked.connect(self._export_stats)
        bottom_row.addWidget(export_btn)
        clear_btn = QPushButton('🗑  Clear All Stats')
        clear_btn.setFixedHeight(42)
        clear_btn.setStyleSheet(btn_stylesheet('RED', 12, text_color='#ffffff'))
        clear_btn.clicked.connect(self._clear_stats)
        bottom_row.addWidget(clear_btn)
        layout.addLayout(bottom_row)

    def showEvent(self, event):
        super().showEvent(event); self._refresh()

    def _refresh(self):
        # Get filtered stats
        filter_layout = self.layout_filter.currentData() or ''
        all_stats = self.mw.stats_mgr.stats
        if filter_layout:
            stats = [s for s in all_stats if s.get('layout') == filter_layout]
        else:
            stats = all_stats

        # Clear summary
        while self.summary_layout.count():
            item = self.summary_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        if not stats:
            lbl = QLabel('No statistics yet.\nComplete a lesson to see your progress!')
            lbl.setFont(QFont("Segoe UI", 12))
            lbl.setStyleSheet(f"color: {T('DIM')}; background: transparent;")
            lbl.setAlignment(Qt.AlignCenter)
            self.summary_layout.addWidget(lbl)
            self.chart.set_data([])
        else:
            wpms = [s.get('wpm', 0) for s in stats]
            accs = [s.get('acc', 0) for s in stats]
            total_time = sum(s.get('time', 0) for s in stats)
            summaries = [
                ('Sessions', str(len(stats)), 'ACCENT'),
                ('Avg WPM', f'{sum(wpms)/len(wpms):.0f}', 'GREEN'),
                ('Best WPM', f'{max(wpms):.0f}', 'YELLOW'),
                ('Avg Acc', f'{sum(accs)/len(accs):.1f}%', 'ACCENT'),
                ('Total Time', f'{int(total_time//60)}m', 'ORANGE'),
            ]
            for label, val, color_key in summaries:
                card = QWidget()
                card.setStyleSheet(card_stylesheet(6))
                cl = QVBoxLayout(card); cl.setContentsMargins(8, 4, 8, 4)
                ll = QLabel(label); ll.setFont(QFont("Segoe UI", 9))
                ll.setStyleSheet(f"color: {T('DIM')}; background: transparent;")
                ll.setAlignment(Qt.AlignCenter)
                vl = QLabel(val); vl.setFont(QFont("Segoe UI", 16, QFont.Bold))
                vl.setStyleSheet(f"color: {T(color_key)}; background: transparent;")
                vl.setAlignment(Qt.AlignCenter)
                cl.addWidget(ll); cl.addWidget(vl)
                self.summary_layout.addWidget(card)

            # Update chart
            self.chart.set_data(wpms[-30:])

        # History list
        while self.history_layout.count() > 0:
            item = self.history_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        for entry in reversed(stats[-30:]):
            box = QWidget()
            box.setStyleSheet(card_stylesheet(8))
            bl = QVBoxLayout(box)
            bl.setContentsMargins(10, 6, 10, 6)
            bl.setSpacing(2)
            layout_disp = LAYOUTS.get(entry.get('layout', ''), {}).get(
                'display', entry.get('layout', ''))
            line1 = (f'{layout_disp}  •  '
                     f'{entry.get("lesson", "").replace("_", " ").title()}  •  '
                     f'{entry.get("date", "")}')
            l1 = QLabel(line1)
            l1.setFont(QFont("Segoe UI", 10))
            l1.setStyleSheet(f"color: {T('DIM')}; background: transparent;")

            wpm_val = entry.get('wpm', 0)
            acc_val = entry.get('acc', 0)
            wpm_color = T('GREEN') if wpm_val >= 30 else T('ORANGE') if wpm_val >= 15 else T('RED')
            acc_color = T('GREEN') if acc_val >= 95 else T('ORANGE') if acc_val >= 85 else T('RED')

            line2 = f'⚡ {int(wpm_val)} WPM   🎯 {acc_val:.1f}%   ⏱ {int(entry.get("time",0))}s'
            l2 = QLabel(line2)
            l2.setFont(QFont("Segoe UI", 12, QFont.Bold))
            l2.setStyleSheet(f"color: {wpm_color}; background: transparent;")

            bl.addWidget(l1); bl.addWidget(l2)
            self.history_layout.addWidget(box)

        # Re-add stretch at end
        self.history_layout.addStretch()

    def _clear_stats(self):
        self.mw.stats_mgr.clear(); self._refresh()

    def _export_stats(self):
        path = os.path.join(DATA_DIR, 'exported_stats.json')
        try:
            with open(path, 'w') as f:
                json.dump({
                    'sessions': self.mw.stats_mgr.stats,
                    'key_stats': self.mw.stats_mgr.key_stats,
                    'exported': datetime.now().strftime('%Y-%m-%d %H:%M'),
                }, f, indent=2)
            # Show brief confirmation
            self.mw.statusBar().showMessage(f'Stats exported to {path}', 3000)
        except Exception as e:
            self.mw.statusBar().showMessage(f'Export failed: {e}', 3000)

    def refresh_theme(self):
        self._refresh()


class SettingsScreen(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.mw = main_window; self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12); layout.setContentsMargins(16, 16, 16, 16)

        # Header
        header = QHBoxLayout()
        back_btn = QPushButton('← Back')
        back_btn.setFixedWidth(76)
        back_btn.setStyleSheet(btn_stylesheet('CARD2', 12))
        back_btn.clicked.connect(lambda: self.mw.go_to('menu'))
        header.addWidget(back_btn)
        title = QLabel('⚙️  Settings')
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet(f"color: {T('TXT')}; background: transparent;")
        header.addWidget(title, 1)
        layout.addLayout(header)

        # Theme selection
        theme_section = QLabel('🎨  Theme')
        theme_section.setFont(QFont("Segoe UI", 13, QFont.Bold))
        theme_section.setStyleSheet(f"color: {T('ACCENT')}; background: transparent;")
        layout.addWidget(theme_section)

        theme_grid = QGridLayout(); theme_grid.setSpacing(6)
        self._theme_btns = {}; self._theme_group = QButtonGroup(self)
        current_theme = settings_mgr.get('theme', 'dark')
        for i, (tname, tdisplay) in enumerate(THEME_DISPLAY.items()):
            b = QPushButton(tdisplay)
            b.setCheckable(True); b.setFixedHeight(42)
            b.setChecked(tname == current_theme)
            b.setStyleSheet(toggle_stylesheet(tname == current_theme))
            self._theme_btns[tname] = b; self._theme_group.addButton(b)
            theme_grid.addWidget(b, i // 3, i % 3)
        self._theme_group.idToggled.connect(self._on_theme_toggle)
        layout.addLayout(theme_grid)

        layout.addSpacing(8)

        # Sound
        sound_section = QLabel('🔊  Audio')
        sound_section.setFont(QFont("Segoe UI", 13, QFont.Bold))
        sound_section.setStyleSheet(f"color: {T('ACCENT')}; background: transparent;")
        layout.addWidget(sound_section)

        self.cb_sound = QCheckBox('  Enable sound effects')
        self.cb_sound.setChecked(settings_mgr.get('sound', True))
        self.cb_sound.toggled.connect(lambda v: settings_mgr.set('sound', v))
        layout.addWidget(self.cb_sound)

        layout.addSpacing(8)

        # Display options
        display_section = QLabel('🖥️  Display')
        display_section.setFont(QFont("Segoe UI", 13, QFont.Bold))
        display_section.setStyleSheet(f"color: {T('ACCENT')}; background: transparent;")
        layout.addWidget(display_section)

        self.cb_keyboard = QCheckBox('  Show visual keyboard during typing')
        self.cb_keyboard.setChecked(settings_mgr.get('show_keyboard', True))
        self.cb_keyboard.toggled.connect(lambda v: settings_mgr.set('show_keyboard', v))
        layout.addWidget(self.cb_keyboard)

        self.cb_finger = QCheckBox('  Show finger hints')
        self.cb_finger.setChecked(settings_mgr.get('show_finger_hints', True))
        self.cb_finger.toggled.connect(lambda v: settings_mgr.set('show_finger_hints', v))
        layout.addWidget(self.cb_finger)

        layout.addSpacing(8)

        # Key heatmap section
        heatmap_section = QLabel('🗺️  Key Heatmap')
        heatmap_section.setFont(QFont("Segoe UI", 13, QFont.Bold))
        heatmap_section.setStyleSheet(f"color: {T('ACCENT')}; background: transparent;")
        layout.addWidget(heatmap_section)

        heatmap_desc = QLabel(
            'The visual keyboard can show a heatmap of your accuracy per key.\n'
            'Green = high accuracy, Red = needs practice.')
        heatmap_desc.setFont(QFont("Segoe UI", 10))
        heatmap_desc.setStyleSheet(f"color: {T('DIM')}; background: transparent;")
        layout.addWidget(heatmap_desc)

        # Show heatmap preview keyboard
        self.heatmap_keyboard = VisualKeyboard()
        self.heatmap_keyboard.set_layout(settings_mgr.get('layout', 'QWERTY'))
        self.heatmap_keyboard.show_heatmap = True
        self.heatmap_keyboard.setFixedHeight(200)
        layout.addWidget(self.heatmap_keyboard)

        layout.addStretch()

        # About
        about = QLabel(
            'Keyboard Trainer v2.0  •  Built with PySide6\n'
            'Data stored in: ' + DATA_DIR)
        about.setFont(QFont("Segoe UI", 9))
        about.setStyleSheet(f"color: {T('DIM')}; background: transparent;")
        about.setAlignment(Qt.AlignCenter)
        layout.addWidget(about)

    def _on_theme_toggle(self, btn, checked):
        if not checked: return
        for tname, b in self._theme_btns.items():
            sel = b == btn
            b.setStyleSheet(toggle_stylesheet(sel))
            if sel:
                settings_mgr.set('theme', tname)
                self.mw.apply_theme()

    def refresh_theme(self):
        for tname, b in self._theme_btns.items():
            b.setStyleSheet(toggle_stylesheet(b.isChecked()))
        self.heatmap_keyboard.update()


class CustomTextScreen(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.mw = main_window; self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12); layout.setContentsMargins(16, 16, 16, 16)

        # Header
        header = QHBoxLayout()
        back_btn = QPushButton('← Back')
        back_btn.setFixedWidth(76)
        back_btn.setStyleSheet(btn_stylesheet('CARD2', 12))
        back_btn.clicked.connect(lambda: self.mw.go_to('menu'))
        header.addWidget(back_btn)
        title = QLabel('✏️  Custom Text Practice')
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet(f"color: {T('TXT')}; background: transparent;")
        header.addWidget(title, 1)
        layout.addLayout(header)

        desc = QLabel('Enter any text below to practice typing it. Great for practicing specific passages!')
        desc.setFont(QFont("Segoe UI", 11))
        desc.setStyleSheet(f"color: {T('DIM')}; background: transparent;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Layout selector
        layout_row = QHBoxLayout()
        layout_row.addWidget(QLabel('Layout:'))
        self.layout_combo = QComboBox()
        for name, data in LAYOUTS.items():
            self.layout_combo.addItem(data['display'], name)
        # Set current layout
        idx = list(LAYOUTS.keys()).index(settings_mgr.get('layout', 'QWERTY'))
        self.layout_combo.setCurrentIndex(idx)
        layout_row.addWidget(self.layout_combo, 1)
        layout.addLayout(layout_row)

        # Text input
        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlaceholderText(
            'Type or paste your practice text here...\n\n'
            'Examples:\n'
            '• The quick brown fox jumps over the lazy dog.\n'
            '• A paragraph from your favorite book.\n'
            '• Code snippets you want to practice typing.'
        )
        self.text_edit.setFont(QFont("Consolas", 13))
        self.text_edit.setMinimumHeight(200)
        layout.addWidget(self.text_edit, 1)

        # Preset texts
        preset_row = QHBoxLayout()
        preset_label = QLabel('Quick fill:')
        preset_label.setStyleSheet(f"color: {T('DIM')}; background: transparent;")
        preset_row.addWidget(preset_label)
        presets = [
            ('Pangram', 'The quick brown fox jumps over the lazy dog.'),
            ('Code', 'def hello_world():\n    print("Hello, World!")\n    return True'),
            ('Numbers', '0123456789 +-*/= () [] {} <> @#$%&'),
            ('Article', 'In a world increasingly driven by technology, the ability to type '
                        'quickly and accurately has become an essential skill for professionals '
                        'and students alike.'),
        ]
        for pname, ptext in presets:
            pb = QPushButton(pname)
            pb.setFixedHeight(32)
            pb.setStyleSheet(btn_stylesheet('CARD3', 10))
            pb.clicked.connect(lambda _, t=ptext: self.text_edit.setPlainText(t))
            preset_row.addWidget(pb)
        layout.addLayout(preset_row)

        # Character count
        self.lbl_count = QLabel('0 characters')
        self.lbl_count.setFont(QFont("Segoe UI", 10))
        self.lbl_count.setStyleSheet(f"color: {T('DIM')}; background: transparent;")
        self.text_edit.textChanged.connect(
            lambda: self.lbl_count.setText(f'{len(self.text_edit.toPlainText())} characters'))
        layout.addWidget(self.lbl_count)

        # Start button
        start_btn = QPushButton('▶  Start Custom Practice')
        start_btn.setFixedHeight(52)
        start_btn.setStyleSheet(btn_stylesheet('ACCENT', 16, bold=True, text_color='#ffffff'))
        start_btn.clicked.connect(self._start)
        layout.addWidget(start_btn)

    def _start(self):
        text = self.text_edit.toPlainText().strip()
        if not text:
            self.lbl_count.setStyleSheet(f"color: {T('RED')}; background: transparent;")
            self.lbl_count.setText('⚠️ Please enter some text first!')
            return
        layout_name = self.layout_combo.currentData() or 'QWERTY'
        self.mw.current_layout = layout_name
        self.mw.current_lesson = 'custom'
        self.mw.current_mode = 'completion'
        self.mw.typing_screen.start_lesson(layout_name, 'custom', 'completion', custom_text=text)
        self.mw.go_to('typing')

    def refresh_theme(self):
        pass


# ─── Main Window ──────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Keyboard Trainer')
        self.setMinimumSize(720, 720)
        self.resize(780, 800)
        self.current_layout = 'QWERTY'
        self.current_lesson = 'home_row'
        self.current_mode = 'completion'

        # Initialize managers
        self.stats_mgr = StatsManager(DATA_DIR)
        settings_mgr.init(DATA_DIR)
        sound_mgr.init(DATA_DIR)

        # Stacked widget
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Create screens
        self.menu_screen = MenuScreen(self)
        self.typing_screen = TypingScreen(self)
        self.results_screen = ResultsScreen(self)
        self.stats_screen = StatsScreen(self)
        self.settings_screen = SettingsScreen(self)
        self.custom_screen = CustomTextScreen(self)

        self.stack.addWidget(self.menu_screen)      # 0
        self.stack.addWidget(self.typing_screen)     # 1
        self.stack.addWidget(self.results_screen)    # 2
        self.stack.addWidget(self.stats_screen)      # 3
        self.stack.addWidget(self.settings_screen)   # 4
        self.stack.addWidget(self.custom_screen)     # 5

        self._screen_map = {
            'menu': 0, 'typing': 1, 'results': 2,
            'stats': 3, 'settings': 4, 'custom': 5,
        }

        self.apply_theme()

    def go_to(self, name):
        idx = self._screen_map.get(name, 0)
        self.stack.setCurrentIndex(idx)
        if name == 'typing':
            self.typing_screen.setFocus()
        elif name == 'menu':
            self.menu_screen.refresh_theme()

    def apply_theme(self):
        self.setStyleSheet(get_app_stylesheet())
        # Refresh all screens
        for screen in [self.menu_screen, self.typing_screen, self.results_screen,
                       self.stats_screen, self.settings_screen, self.custom_screen]:
            if hasattr(screen, 'refresh_theme'):
                screen.refresh_theme()


# ─── Entry Point ──────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Set default palette for better base styling
    palette = QPalette()
    palette.setColor(QPalette.Window, T_color('BG'))
    palette.setColor(QPalette.WindowText, T_color('TXT'))
    palette.setColor(QPalette.Base, T_color('CARD'))
    palette.setColor(QPalette.AlternateBase, T_color('CARD2'))
    palette.setColor(QPalette.Text, T_color('TXT'))
    palette.setColor(QPalette.Button, T_color('CARD2'))
    palette.setColor(QPalette.ButtonText, T_color('TXT'))
    palette.setColor(QPalette.Highlight, T_color('ACCENT'))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()