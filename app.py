#!/usr/bin/env python3
"""
Keyboard Learning App — PySide6 Version
Learn to type fast and accurately on multiple layouts.
Supports: QWERTY, AZERTY, DVORAK, Colemak

Requirements:
  pip install PySide6
"""

import sys, os, json, time, random, math, struct, wave, logging
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QStackedWidget, QLabel, QPushButton, QRadioButton,
    QButtonGroup, QScrollArea, QTextEdit, QSizePolicy, QFrame,
    QCheckBox, QPlainTextEdit, QSpacerItem, QToolButton, QComboBox,
    QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QRectF, QSize, Signal, QUrl
from PySide6.QtGui import (
    QPainter, QColor, QBrush, QPen, QFont, QPalette, QPainterPath
)

try:
    from PySide6.QtMultimedia import QSoundEffect
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False

# ─── Logging Setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)-5s] %(name)s: %(message)s',
    datefmt='%H:%M:%S',
)
log = logging.getLogger('KbTrainer')
log.info("Keyboard Trainer starting up")

# ─── Data Directory ───────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.expanduser('~'), '.keyboard_trainer_pyside6')
os.makedirs(DATA_DIR, exist_ok=True)
log.info("Data directory: %s", DATA_DIR)

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
        old = _theme_name
        _theme_name = name
        log.info("Theme changed: %s → %s", old, name)
    else:
        log.warning("Unknown theme requested: %s (keeping %s)", name, _theme_name)


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
snd_log = logging.getLogger('KbTrainer.Sound')


def _gen_wav(path, freq=800, dur=0.04, vol=0.2):
    sr = 22050
    n = int(sr * dur)
    frames = []
    for i in range(n):
        fade = 1.0 - (i / n)
        v = int(vol * 32767 * math.sin(2 * math.pi * freq * i / sr) * fade)
        frames.append(struct.pack('<h', max(-32768, min(32767, v))))
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(b''.join(frames))


class SoundManager:
    def __init__(self):
        self.enabled = True
        self.sounds = {}
        self._ready = False

    def init(self, data_dir):
        if not HAS_SOUND:
            snd_log.warning("QtMultimedia not available — sounds disabled")
            return
        try:
            sd = os.path.join(data_dir, 'sounds')
            os.makedirs(sd, exist_ok=True)
            for name, freq, dur in [
                ('click', 880, 0.035), ('error', 280, 0.07),
                ('done', 1100, 0.12), ('streak', 1200, 0.06),
            ]:
                p = os.path.join(sd, f'{name}.wav')
                if not os.path.exists(p):
                    _gen_wav(p, freq, dur, 0.18)
                    snd_log.debug("Generated wav: %s (%dHz, %.3fs)", name, freq, dur)
                effect = QSoundEffect()
                effect.setSource(QUrl.fromLocalFile(os.path.abspath(p)))
                effect.setVolume(0.5)
                self.sounds[name] = effect
            self._ready = True
            snd_log.info("Sound system initialised — %d effects loaded", len(self.sounds))
        except Exception as e:
            snd_log.error("Sound init failed: %s", e)

    def play(self, name):
        if not self.enabled or not self._ready or name not in self.sounds:
            return
        try:
            self.sounds[name].play()
            snd_log.debug("Played sound: %s", name)
        except Exception as e:
            snd_log.warning("Sound play error (%s): %s", name, e)


sound_mgr = SoundManager()

# ─── Settings Manager ─────────────────────────────────────────────────────────
DEFAULT_SETTINGS = {
    'layout': 'QWERTY', 'lesson': 'home_row', 'theme': 'dark',
    'sound': True, 'vibration': True, 'mode': 'completion', 'timer_secs': 60,
    'show_keyboard': True, 'show_finger_hints': True, 'show_heatmap': False,
}

set_log = logging.getLogger('KbTrainer.Settings')


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
                set_log.info("Settings loaded from %s", self._path)
                set_log.debug("Settings values: %s", self.data)
            except Exception as e:
                set_log.error("Failed to load settings: %s", e)
        else:
            set_log.info("No saved settings found — using defaults")
        set_theme(self.data.get('theme', 'dark'))
        sound_mgr.enabled = self.data.get('sound', True)

    def save(self):
        if self._path:
            try:
                with open(self._path, 'w') as f:
                    json.dump(self.data, f, indent=2)
                set_log.debug("Settings saved to %s", self._path)
            except Exception as e:
                set_log.error("Failed to save settings: %s", e)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        old = self.data.get(key)
        self.data[key] = value
        self.save()
        set_log.info("Setting changed: %s = %r (was %r)", key, value, old)
        if key == 'theme':
            set_theme(value)
        if key == 'sound':
            sound_mgr.enabled = value


settings_mgr = SettingsManager()

# ─── Stats Manager ────────────────────────────────────────────────────────────
stats_log = logging.getLogger('KbTrainer.Stats')


class StatsManager:
    def __init__(self, data_dir):
        self._path = os.path.join(data_dir, 'kb_stats.json')
        self.stats = []
        self.key_stats = {}
        self._data_dir = data_dir
        self.load()

    def load(self):
        if os.path.exists(self._path):
            try:
                with open(self._path, 'r') as f:
                    data = json.load(f)
                    self.stats = data if isinstance(data, list) else data.get('sessions', [])
                    self.key_stats = data.get('key_stats', {}) if isinstance(data, dict) else {}
                stats_log.info("Stats loaded: %d sessions, %d key entries",
                               len(self.stats), len(self.key_stats))
            except Exception as e:
                stats_log.error("Failed to load stats: %s", e)
                self.stats = []
                self.key_stats = {}
        else:
            stats_log.info("No stats file found — starting fresh")

    def save(self):
        try:
            with open(self._path, 'w') as f:
                json.dump({'sessions': self.stats, 'key_stats': self.key_stats}, f, indent=2)
            stats_log.debug("Stats saved (%d sessions)", len(self.stats))
        except Exception as e:
            stats_log.error("Failed to save stats: %s", e)

    def add_stat(self, layout, lesson, wpm, acc, elapsed, key_errors=None):
        self.stats.append({
            'layout': layout, 'lesson': lesson, 'wpm': round(wpm, 1),
            'acc': round(acc, 1), 'time': round(elapsed, 1),
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        })
        if key_errors:
            for key, count in key_errors.items():
                k = f"{layout}:{key}"
                if k not in self.key_stats:
                    self.key_stats[k] = {'errors': 0, 'total': 0}
                self.key_stats[k]['errors'] += count
                self.key_stats[k]['total'] += count
        stats_log.info("Session recorded: layout=%s lesson=%s wpm=%.1f acc=%.1f%% time=%.1fs",
                       layout, lesson, wpm, acc, elapsed)
        if key_errors:
            stats_log.debug("Key errors this session: %s", key_errors)
        self.save()

    def record_key(self, layout, key_char, correct):
        k = f"{layout}:{key_char.upper()}"
        if k not in self.key_stats:
            self.key_stats[k] = {'errors': 0, 'total': 0}
        self.key_stats[k]['total'] += 1
        if not correct:
            self.key_stats[k]['errors'] += 1
        if self.key_stats[k]['total'] % 50 == 0:
            self.save()

    def get_key_accuracy(self, layout, key_char):
        k = f"{layout}:{key_char.upper()}"
        info = self.key_stats.get(k, {'errors': 0, 'total': 0})
        if info['total'] == 0:
            return 1.0
        return 1.0 - (info['errors'] / info['total'])

    def get_best(self, layout):
        ls = [s for s in self.stats if s.get('layout') == layout]
        return max(ls, key=lambda s: s.get('wpm', 0)) if ls else None

    def get_recent(self, n=10):
        return self.stats[-n:] if self.stats else []

    def clear(self):
        stats_log.warning("Stats cleared!")
        self.stats = []
        self.key_stats = {}
        self.save()


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
        'finger_map': {
            0: [0, 0, 1, 2, 3, 3, 4, 4, 5, 6, 7, 7, 7],
            1: [0, 1, 2, 3, 3, 4, 4, 5, 6, 7, 7, 7, 7],
            2: [0, 1, 2, 3, 3, 4, 4, 5, 6, 7, 7],
            3: [0, 0, 1, 2, 3, 3, 4, 4, 5, 6, 7, 7],
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
            0: [0, 0, 1, 2, 3, 3, 4, 4, 5, 6, 7, 7, 7],
            1: [0, 1, 2, 3, 3, 4, 4, 5, 6, 7, 7, 7, 7],
            2: [0, 1, 2, 3, 3, 4, 4, 5, 6, 7, 7],
            3: [0, 0, 1, 2, 3, 3, 4, 4, 5, 6, 7, 7],
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
            0: [0, 0, 1, 2, 3, 3, 4, 4, 5, 6, 7, 7, 7],
            1: [0, 1, 2, 3, 3, 4, 4, 5, 6, 7, 7],
            2: [0, 1, 2, 3, 3, 4, 4, 5, 6, 7, 7],
            3: [0, 0, 1, 2, 3, 3, 4, 4, 5, 6, 7, 7],
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
            0: [0, 0, 1, 2, 3, 3, 4, 4, 5, 6, 7, 7, 7],
            1: [0, 1, 2, 3, 3, 4, 4, 5, 6, 7, 7, 7, 7],
            2: [0, 1, 2, 3, 3, 4, 4, 5, 6, 7, 7],
            3: [0, 0, 1, 2, 3, 3, 4, 4, 5, 6, 7, 7],
        },
    },
}


def get_finger(layout_name, key_char):
    if key_char in (' ', 'SPACE'):
        return 8
    layout = LAYOUTS[layout_name]
    ku = key_char.upper()
    finger_map = layout.get('finger_map', {})
    for ri, row in enumerate(layout['rows']):
        if ri >= 4:
            continue
        for ci, (lbl, _) in enumerate(row):
            if lbl.upper() == ku or lbl == key_char:
                row_map = finger_map.get(ri)
                if row_map and ci < len(row_map):
                    return row_map[ci]
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
    if char == ' ':
        return 'SPACE'
    for row in LAYOUTS[layout_name]['rows']:
        for lbl, _ in row:
            if lbl == char or lbl.lower() == char or lbl.upper() == char:
                return lbl
    return None


# ─── Lesson Generation ────────────────────────────────────────────────────────
lesson_log = logging.getLogger('KbTrainer.Lesson')

WORDS = [
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "it", "for", "not", "on",
    "with", "he", "as", "you", "do", "at", "this", "but", "his", "by", "from", "they",
    "we", "say", "her", "she", "or", "an", "will", "my", "one", "all", "would", "there",
    "their", "what", "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
    "when", "make", "can", "like", "time", "no", "just", "him", "know", "take", "into",
    "year", "your", "good", "some", "could", "them", "see", "other", "than", "then",
    "now", "look", "only", "come", "its", "over", "think", "also", "back", "after",
    "use", "two", "how", "our", "work", "first", "well", "way", "even", "new", "want",
    "because", "any", "these", "give", "day", "most", "us", "great", "between", "need",
    "large", "often", "hand", "high", "place", "find", "here", "thing", "many", "home",
    "still", "world", "long", "right", "small", "part", "through", "each", "much",
    "before", "line", "end", "turn", "move", "play", "run", "read", "write", "learn",
    "type", "fast", "key", "home", "row", "top", "bottom", "finger", "practice",
    "code", "data", "system", "program", "input", "output", "screen", "file", "open",
    "close", "save", "print", "search", "next", "page", "view", "edit", "help",
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
    result = list(text)
    for i in range(2, len(result)):
        if result[i] == result[i - 1] == result[i - 2]:
            result[i] = ' '
    return ''.join(result)


def gen_lesson(layout_name, lesson_type, length=140):
    layout = LAYOUTS[layout_name]
    if lesson_type == 'custom':
        lesson_log.debug("Custom lesson requested (empty text)")
        return ''

    if lesson_type == 'home_row':
        keys = [k.lower() for k in layout['home_keys']]
        result = []
        for _ in range(length):
            if random.random() < 0.15 and result and result[-1] != ' ':
                result.append(' ')
            else:
                result.append(random.choice(keys))
        text = _no_triple_repeat(''.join(result).strip())
        lesson_log.info("Generated home_row lesson (%d chars, keys=%s)", len(text), keys)
        return text

    if lesson_type == 'top_row':
        keys = [lbl.lower() for lbl, _ in layout['rows'][1] if len(lbl) == 1 and lbl.isalpha()]
        result = []
        for _ in range(length):
            if random.random() < 0.18 and result and result[-1] != ' ':
                result.append(' ')
            else:
                result.append(random.choice(keys))
        text = _no_triple_repeat(''.join(result).strip())
        lesson_log.info("Generated top_row lesson (%d chars)", len(text))
        return text

    if lesson_type == 'bottom_row':
        keys = [lbl.lower() for lbl, _ in layout['rows'][3] if len(lbl) == 1 and lbl.isalpha()]
        result = []
        for _ in range(length):
            if random.random() < 0.18 and result and result[-1] != ' ':
                result.append(' ')
            else:
                result.append(random.choice(keys))
        text = _no_triple_repeat(''.join(result).strip())
        lesson_log.info("Generated bottom_row lesson (%d chars)", len(text))
        return text

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
        text = _no_triple_repeat(''.join(result).strip())
        lesson_log.info("Generated all_letters lesson (%d chars)", len(text))
        return text

    if lesson_type == 'progressive':
        keys = [k.lower() for k in layout['home_keys']]
        all_keys = []
        for row in layout['rows'][1:4]:
            all_keys += [lbl.lower() for lbl, _ in row if len(lbl) == 1 and lbl.isalpha()]
        result = []
        for i in range(length):
            pool_size = min(len(all_keys), 4 + int(i / length * (len(all_keys) - 4)))
            pool = keys + all_keys[:max(0, pool_size - len(keys))]
            if not pool:
                pool = keys
            if random.random() < 0.20 and result and result[-1] != ' ':
                result.append(' ')
            else:
                result.append(random.choice(pool))
        text = _no_triple_repeat(''.join(result).strip())
        lesson_log.info("Generated progressive lesson (%d chars)", len(text))
        return text

    if lesson_type == 'common_words':
        chosen = random.choices(WORDS, k=max(20, length // 5))
        text = ' '.join(chosen)
        lesson_log.info("Generated common_words lesson (%d chars, %d words)", len(text), len(chosen))
        return text

    if lesson_type == 'sentences':
        count = min(3, len(SENTENCES))
        selected = random.sample(SENTENCES, count)
        text = ' '.join(selected)
        lesson_log.info("Generated sentences lesson (%d chars, %d sentences)", len(text), count)
        return text

    if lesson_type == 'numbers':
        keys = [lbl for lbl, _ in layout['rows'][0] if len(lbl) == 1]
        result = []
        for _ in range(length):
            if random.random() < 0.15 and result and result[-1] != ' ':
                result.append(' ')
            else:
                result.append(random.choice(keys))
        text = _no_triple_repeat(''.join(result).strip())
        lesson_log.info("Generated numbers lesson (%d chars)", len(text))
        return text

    lesson_log.warning("Unknown lesson type '%s' — falling back to common_words", lesson_type)
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
    QStatusBar {{ background-color: {T('CARD')}; color: {T('DIM')}; font-size: 11px; }}
    """


def btn_stylesheet(color_key='CARD2', font_size=13, bold=False, radius=6, text_color=None):
    tc = text_color or T('TXT')
    fw = 'bold' if bold else 'normal'
    # Bug Fix: Proper hover colors for ACCENT and other keys
    if color_key in ('CARD2', 'CARD'):
        hover = T('CARD3')
    else:
        hover_rgb = [min(1.0, c * 1.15) for c in THEMES[_theme_name].get(color_key, (0.5, 0.5, 0.5))]
        hover = rgb_hex(*hover_rgb)
        
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
    # Bug Fix: Proper hover color when selected
    if selected:
        hover_rgb = [min(1.0, c * 1.15) for c in THEMES[_theme_name]['ACCENT']]
        hover = rgb_hex(*hover_rgb)
    else:
        hover = T('CARD3')
        
    return f"""
    QPushButton {{
        background-color: {bg}; color: {tc};
        border: none; border-radius: 6px;
        padding: 8px 10px; font-size: {font_size}px; font-weight: bold;
    }}
    QPushButton:hover {{ background-color: {hover}; }}
    """


def card_stylesheet(radius=8):
    return f"background-color: {T('CARD')}; border-radius: {radius}px;"


# ─── Custom Widgets ───────────────────────────────────────────────────────────

class ProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(6)
        self._value = 0.0
        self._color_key = 'GREEN'

    def set_value(self, value, color_key='GREEN'):
        self._value = max(0.0, min(1.0, value))
        self._color_key = color_key
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QBrush(T_color('CARD3')))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(self.rect(), 3, 3)
        fw = self.width() * self._value
        if fw > 0:
            p.setBrush(QBrush(T_color(self._color_key)))
            p.drawRoundedRect(QRectF(0, 0, fw, self.height()), 3, 3)


class WpmChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(140)
        self._data = []

    def set_data(self, wpms):
        self._data = list(wpms)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        margin = 30

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

        for i in range(5):
            y = margin + chart_h * i / 4
            p.setPen(QPen(T_color('CARD3'), 1, Qt.DotLine))
            p.drawLine(margin, int(y), w - margin, int(y))
            val = int(max_wpm * (1 - i / 4))
            p.setPen(QPen(T_color('DIM')))
            p.setFont(QFont("Segoe UI", 8))
            p.drawText(0, int(y) - 6, margin - 4, 14,
                       Qt.AlignRight | Qt.AlignVCenter, str(val))

        points = []
        n = len(self._data)
        for i, v in enumerate(self._data):
            x = margin + (i / (n - 1)) * chart_w
            y = margin + chart_h * (1 - v / max_wpm)
            points.append((x, y))

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

        path = QPainterPath()
        path.moveTo(points[0][0], points[0][1])
        for x, y in points[1:]:
            path.lineTo(x, y)
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(accent, 2.5))
        p.drawPath(path)

        for x, y in points:
            p.setBrush(QBrush(accent))
            p.setPen(Qt.NoPen)
            p.drawEllipse(QRectF(x - 4, y - 4, 8, 8))

        p.setPen(QPen(T_color('DIM')))
        p.setFont(QFont("Segoe UI", 8))
        p.drawText(self.rect().adjusted(0, 0, 0, -4),
                   Qt.AlignHCenter | Qt.AlignBottom, f'{n} sessions')


class VisualKeyboard(QWidget):
    tapped = Signal(str)

    def __init__(self, stats_mgr_ref=None, parent=None):
        super().__init__(parent)
        self.layout_name = 'QWERTY'
        self.highlight_char = ''
        self.key_rects = {}
        self.flash_label = None
        self.error_key = None
        self.show_heatmap = False
        self._stats_mgr = stats_mgr_ref
        self.flash_timer = QTimer()
        self.flash_timer.setSingleShot(True)
        self.flash_timer.timeout.connect(self._clear_flash)
        self.error_timer = QTimer()
        self.error_timer.setSingleShot(True)
        self.error_timer.timeout.connect(self._clear_error)
        self.setFixedHeight(235)
        self.setMinimumWidth(580)

    def set_stats_mgr(self, mgr):
        self._stats_mgr = mgr

    def set_layout(self, name):
        self.layout_name = name
        log.debug("VisualKeyboard layout set to %s", name)
        self.update()

    def set_highlight(self, char):
        self.highlight_char = char
        self.update()

    def flash_key(self, char):
        self.flash_label = find_key_label(self.layout_name, char)
        self.update()
        self.flash_timer.start(120)

    def flash_error(self, char):
        self.error_key = find_key_label(self.layout_name, char)
        self.update()
        self.error_timer.start(300)

    def _clear_flash(self):
        self.flash_label = None
        self.update()

    def _clear_error(self):
        self.error_key = None
        self.update()

    def set_heatmap(self, enabled):
        self.show_heatmap = enabled
        log.debug("Heatmap %s", "enabled" if enabled else "disabled")
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        layout = LAYOUTS.get(self.layout_name, LAYOUTS['QWERTY'])
        home_keys = set(layout.get('home_keys', []))
        offsets = layout.get('offsets', [0] * 5)
        w = self.width() - 8
        max_units = max(
            (sum(wu for _, wu in row) + offsets[i])
            for i, row in enumerate(layout['rows'])
        )
        uw = w / max_units
        kh = 40
        rs = 4
        ys = 4
        self.key_rects = {}

        for ri, row in enumerate(layout['rows']):
            off = offsets[ri] if ri < len(offsets) else 0
            x = 4.0 + off * uw
            y = ys + ri * (kh + rs)
            for ci, (lbl, wu) in enumerate(row):
                kw = wu * uw - 2
                rect = QRectF(x + 1, y, kw, kh)
                self.key_rects[lbl] = rect
                fi = get_finger(self.layout_name, lbl)
                ih = lbl in home_keys
                target_lbl = (find_key_label(self.layout_name, self.highlight_char)
                              if self.highlight_char else None)
                is_hl = (lbl == target_lbl)
                is_shift = (self.highlight_char and self.highlight_char.isupper()
                            and lbl == '⇧')
                is_flash = (self.flash_label == lbl)
                is_error = (self.error_key == lbl)

                if is_error:
                    bg = T_color('RED')
                    bg.setAlpha(200)
                    tc = QColor(255, 255, 255)
                elif is_hl or is_shift:
                    bg = T_color('YELLOW')
                    bg.setAlpha(235)
                    tc = QColor(26, 26, 38)
                elif is_flash:
                    bg = T_color('ACCENT')
                    bg.setAlpha(217)
                    tc = T_color('TXT')
                elif self.show_heatmap and len(lbl) == 1 and lbl.isalpha():
                    accuracy = 1.0
                    if self._stats_mgr:
                        accuracy = self._stats_mgr.get_key_accuracy(
                            self.layout_name, lbl)
                    r = int((1.0 - accuracy) * 200)
                    g = int(accuracy * 180)
                    bg = QColor(r, g, 60, 140)
                    tc = T_color('TXT')
                else:
                    fc = FINGER_COLS[fi] if 0 <= fi < 9 else (0.3, 0.3, 0.4)
                    bg = QColor(int(fc[0]*255), int(fc[1]*255), int(fc[2]*255))
                    bg.setAlpha(115)
                    tc = T_color('TXT')

                p.setBrush(QBrush(bg))
                p.setPen(Qt.NoPen)
                p.drawRoundedRect(rect, 6, 6)

                if ih and not is_hl:
                    p.setBrush(QBrush(QColor(255, 255, 255, 153)))
                    p.drawRoundedRect(
                        QRectF(rect.center().x() - 6, rect.bottom() - 7, 12, 3),
                        1.5, 1.5)

                display = lbl if lbl != 'SPACE' else '⎵ SPACE'
                p.setPen(QPen(tc))
                font = p.font()
                font.setPointSize(13 if len(display) <= 2 else 10)
                p.setFont(font)
                p.drawText(rect, Qt.AlignCenter, display)
                x += wu * uw

    def mousePressEvent(self, event):
        pos = event.position()
        for lbl, rect in self.key_rects.items():
            if rect.contains(pos):
                ch = ' ' if lbl == 'SPACE' else lbl.lower()
                log.debug("VisualKeyboard tapped: %s → '%s'", lbl, ch)
                self.tapped.emit(ch)
                break


# ─── Screens ──────────────────────────────────────────────────────────────────
ui_log = logging.getLogger('KbTrainer.UI')


class MenuScreen(QWidget):
    start_requested = Signal()

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.mw = main_window
        self._layout_btns = {}
        self._lesson_btns = {}
        self._mode_btns = {}
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
        lay = QVBoxLayout(content)
        lay.setSpacing(10)
        lay.setContentsMargins(20, 16, 20, 16)

        title = QLabel('⌨️  Keyboard Trainer')
        title.setFont(QFont("Segoe UI", 26, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        lay.addWidget(title)
        sub = QLabel('Learn to type fast & accurately on any layout')
        sub.setFont(QFont("Segoe UI", 12))
        sub.setStyleSheet(f"color: {T('DIM')};")
        sub.setAlignment(Qt.AlignCenter)
        lay.addWidget(sub)
        lay.addSpacing(6)

        lay.addWidget(self._section_label('Select Keyboard Layout'))
        lg = QGridLayout()
        lg.setSpacing(6)
        sel_layout = settings_mgr.get('layout', 'QWERTY')
        for i, (name, data) in enumerate(LAYOUTS.items()):
            b = QPushButton(data['display'])
            b.setCheckable(True)
            b.setFixedHeight(42)
            b.setChecked(name == sel_layout)
            b.setStyleSheet(toggle_stylesheet(name == sel_layout))
            self._layout_btns[name] = b
            self._layout_group.addButton(b, i)  # Bug Fix: Explicit ID
            lg.addWidget(b, i // 2, i % 2)
        # Bug Fix: Connect to buttonToggled instead of idToggled
        self._layout_group.buttonToggled.connect(self._on_layout_toggle)
        lay.addLayout(lg)

        lay.addWidget(self._section_label('Choose Lesson'))
        lsg = QGridLayout()
        lsg.setSpacing(5)
        sel_lesson = settings_mgr.get('lesson', 'home_row')
        for i, (ltype, lname, ldesc) in enumerate(LESSON_TYPES):
            b = QPushButton(lname)
            b.setCheckable(True)
            b.setFixedHeight(42)
            b.setChecked(ltype == sel_lesson)
            b.setStyleSheet(toggle_stylesheet(ltype == sel_lesson))
            b.setToolTip(ldesc)
            self._lesson_btns[ltype] = b
            self._lesson_group.addButton(b, i)  # Bug Fix: Explicit ID
            lsg.addWidget(b, i // 2, i % 2)
        # Bug Fix: Connect to buttonToggled instead of idToggled
        self._lesson_group.buttonToggled.connect(self._on_lesson_toggle)
        lay.addLayout(lsg)

        lay.addWidget(self._section_label('Practice Mode'))
        mg = QGridLayout()
        mg.setSpacing(5)
        sel_mode = settings_mgr.get('mode', 'completion')
        for i, (mtype, mname, mdesc) in enumerate(PRACTICE_MODES):
            b = QPushButton(mname)
            b.setCheckable(True)
            b.setFixedHeight(42)
            b.setChecked(mtype == sel_mode)
            b.setStyleSheet(toggle_stylesheet(mtype == sel_mode))
            b.setToolTip(mdesc)
            self._mode_btns[mtype] = b
            self._mode_group.addButton(b, i)  # Bug Fix: Explicit ID
            mg.addWidget(b, i // 2, i % 2)
        # Bug Fix: Connect to buttonToggled instead of idToggled
        self._mode_group.buttonToggled.connect(self._on_mode_toggle)
        lay.addLayout(mg)

        lay.addSpacing(8)

        start_btn = QPushButton('▶  Start Typing')
        start_btn.setFixedHeight(52)
        start_btn.setStyleSheet(
            btn_stylesheet('ACCENT', 18, bold=True, text_color='#ffffff'))
        start_btn.clicked.connect(self._start)
        lay.addWidget(start_btn)

        custom_btn = QPushButton('✏️  Custom Text Practice')
        custom_btn.setFixedHeight(44)
        custom_btn.setStyleSheet(btn_stylesheet('CARD3', 14))
        custom_btn.clicked.connect(lambda: self.mw.go_to('custom'))
        lay.addWidget(custom_btn)

        row = QHBoxLayout()
        row.setSpacing(8)
        stats_btn = QPushButton('📊  Statistics')
        stats_btn.setFixedHeight(44)
        stats_btn.setStyleSheet(btn_stylesheet('CARD2', 13))
        stats_btn.clicked.connect(lambda: self.mw.go_to('stats'))
        settings_btn = QPushButton('⚙️  Settings')
        settings_btn.setFixedHeight(44)
        settings_btn.setStyleSheet(btn_stylesheet('CARD2', 13))
        settings_btn.clicked.connect(lambda: self.mw.go_to('settings'))
        row.addWidget(stats_btn)
        row.addWidget(settings_btn)
        lay.addLayout(row)

        lay.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll)
        ui_log.debug("MenuScreen built")

    def _section_label(self, text):
        l = QLabel(text)
        l.setFont(QFont("Segoe UI", 13, QFont.Bold))
        l.setStyleSheet(f"color: {T('ACCENT')}; background: transparent;")
        return l

    def _on_layout_toggle(self, btn, checked):
        if not checked:
            return
        for name, b in self._layout_btns.items():
            sel = (b == btn)  # Bug Fix: btn is now correctly a QPushButton instance
            b.setStyleSheet(toggle_stylesheet(sel))
            if sel:
                settings_mgr.set('layout', name)
                ui_log.info("Layout selected: %s", name)

    def _on_lesson_toggle(self, btn, checked):
        if not checked:
            return
        for ltype, b in self._lesson_btns.items():
            sel = (b == btn)  # Bug Fix
            b.setStyleSheet(toggle_stylesheet(sel))
            if sel:
                settings_mgr.set('lesson', ltype)
                ui_log.info("Lesson selected: %s", ltype)

    def _on_mode_toggle(self, btn, checked):
        if not checked:
            return
        for mtype, b in self._mode_btns.items():
            sel = (b == btn)  # Bug Fix
            b.setStyleSheet(toggle_stylesheet(sel))
            if sel:
                settings_mgr.set('mode', mtype)
                ui_log.info("Mode selected: %s", mtype)

    def _start(self):
        self.mw.current_layout = settings_mgr.get('layout', 'QWERTY')
        self.mw.current_lesson = settings_mgr.get('lesson', 'home_row')
        self.mw.current_mode = settings_mgr.get('mode', 'completion')
        self.mw.current_custom_text = ''
        ui_log.info("Starting lesson: layout=%s lesson=%s mode=%s",
                    self.mw.current_layout, self.mw.current_lesson, self.mw.current_mode)
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


typing_log = logging.getLogger('KbTrainer.Typing')


class TypingScreen(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.mw = main_window
        self.setFocusPolicy(Qt.StrongFocus)
        self.layout_name = 'QWERTY'
        self.lesson_text = ''
        self.typed = []
        self.char_idx = 0
        self.start_time = None
        self.errors = 0
        self.total_keystrokes = 0
        self.streak = 0
        self.best_streak = 0
        self._finished = False
        self.mode = 'completion'
        self.timer_secs = 0
        self.key_errors = {}
        self._timer = QTimer()
        self._timer.setInterval(200)
        self._timer.timeout.connect(self._tick)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(10, 8, 10, 8)

        top = QHBoxLayout()
        top.setSpacing(6)
        back_btn = QPushButton('← Back')
        back_btn.setFixedWidth(76)
        back_btn.setFocusPolicy(Qt.NoFocus)
        back_btn.setStyleSheet(btn_stylesheet('CARD2', 12))
        back_btn.clicked.connect(self._go_back)
        top.addWidget(back_btn)
        self.lbl_lesson = QLabel('')
        self.lbl_lesson.setFont(QFont("Segoe UI", 11))
        self.lbl_lesson.setStyleSheet(
            f"color: {T('DIM')}; background: transparent;")
        top.addWidget(self.lbl_lesson, 1)
        self.lbl_wpm = QLabel('WPM: 0')
        self.lbl_wpm.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.lbl_wpm.setStyleSheet(
            f"color: {T('GREEN')}; background: transparent;")
        top.addWidget(self.lbl_wpm)
        self.lbl_acc = QLabel('ACC: 100%')
        self.lbl_acc.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.lbl_acc.setStyleSheet(
            f"color: {T('ACCENT')}; background: transparent;")
        top.addWidget(self.lbl_acc)
        self.lbl_time = QLabel('⏱ 0:00')
        self.lbl_time.setFont(QFont("Segoe UI", 12))
        self.lbl_time.setStyleSheet(
            f"color: {T('ORANGE')}; background: transparent;")
        top.addWidget(self.lbl_time)
        self.lbl_streak = QLabel('🔥 0')
        self.lbl_streak.setFont(QFont("Segoe UI", 12))
        self.lbl_streak.setStyleSheet(
            f"color: {T('YELLOW')}; background: transparent;")
        top.addWidget(self.lbl_streak)
        layout.addLayout(top)

        self.progress = ProgressBar()
        layout.addWidget(self.progress)

        hint_row = QHBoxLayout()
        self.lbl_finger = QLabel('')
        self.lbl_finger.setFixedHeight(22)
        self.lbl_finger.setFont(QFont("Segoe UI", 12))
        self.lbl_finger.setStyleSheet(
            f"color: {T('DIM')}; background: transparent;")
        hint_row.addWidget(self.lbl_finger)
        self.lbl_expected = QLabel('')
        self.lbl_expected.setFixedHeight(22)
        self.lbl_expected.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.lbl_expected.setStyleSheet(
            f"color: {T('YELLOW')}; background: transparent;")
        self.lbl_expected.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        hint_row.addWidget(self.lbl_expected)
        layout.addLayout(hint_row)

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

        self.keyboard = VisualKeyboard(stats_mgr_ref=self.mw.stats_mgr)
        self.keyboard.tapped.connect(self._handle_tap)
        layout.addWidget(self.keyboard)

        hint = QLabel('Type the highlighted character  •  Esc = quit  •  Tab = restart')
        hint.setFixedHeight(18)
        hint.setFont(QFont("Segoe UI", 9))
        hint.setStyleSheet(f"color: {T('DIM')}; background: transparent;")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)
        typing_log.debug("TypingScreen built")

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(50, self.setFocus)

    def start_lesson(self, layout_name, lesson_type, mode='completion',
                     custom_text=''):
        self.layout_name = layout_name
        self.mode = mode
        self.timer_secs = 0
        self.key_errors = {}
        if mode.startswith('timed_'):
            self.timer_secs = int(mode.split('_')[1])
            self.lesson_text = gen_lesson(layout_name, lesson_type, 800)
        elif lesson_type == 'custom':
            self.lesson_text = (custom_text if custom_text
                                else 'The quick brown fox jumps over the lazy dog.')
        else:
            self.lesson_text = gen_lesson(layout_name, lesson_type, 160)
        if not self.lesson_text.strip():
            self.lesson_text = 'The quick brown fox jumps over the lazy dog.'
        self.typed = []
        self.char_idx = 0
        self.start_time = None
        self.errors = 0
        self.total_keystrokes = 0
        self.streak = 0
        self.best_streak = 0
        self._finished = False
        mode_disp = mode.replace('_', ' ').title()
        self.lbl_lesson.setText(
            f'{LAYOUTS[layout_name]["display"]}  •  '
            f'{lesson_type.replace("_", " ").title()}  •  {mode_disp}')
        self.keyboard.set_layout(layout_name)
        # Bug Fix: Complete truncated property `self.ke`
        self.keyboard.set_highlight(
            self.lesson_text[0] if self.lesson_text else '')
        self._update_display()
        self._update_stats()
        self._timer.start()

    def _go_back(self):
        self._timer.stop()
        self.mw.go_to('menu')

    def _handle_tap(self, char):
        self._process_char(char)

    def keyPressEvent(self, event):
        if self._finished:
            if event.key() in (Qt.Key_Escape, Qt.Key_Return, Qt.Key_Enter):
                self._go_back()
            return

        if event.key() == Qt.Key_Escape:
            self._go_back()
            return
        if event.key() == Qt.Key_Tab:
            self.start_lesson(self.layout_name,
                              settings_mgr.get('lesson', 'home_row'),
                              self.mode)
            return
        if event.key() in (Qt.Key_Shift, Qt.Key_Control, Qt.Key_Alt, Qt.Key_Meta, Qt.Key_CapsLock):
            return  # Ignore pure modifier keys

        text = event.text()
        if text:
            self._process_char(text)

    def _process_char(self, char):
        if self._finished or self.char_idx >= len(self.lesson_text):
            return

        if self.start_time is None:
            self.start_time = time.time()

        expected = self.lesson_text[self.char_idx]
        correct = (char == expected)
        self.total_keystrokes += 1

        if correct:
            self.typed.append(char)
            self.char_idx += 1
            self.streak += 1
            self.best_streak = max(self.best_streak, self.streak)
            self.keyboard.flash_key(char)
            sound_mgr.play('click')

            if self.streak > 0 and self.streak % 10 == 0:
                sound_mgr.play('streak')
        else:
            self.errors += 1
            self.streak = 0
            self.keyboard.flash_error(char)
            sound_mgr.play('error')
            ek = expected.upper()
            self.key_errors[ek] = self.key_errors.get(ek, 0) + 1

        if self.mw.stats_mgr:
            self.mw.stats_mgr.record_key(self.layout_name, expected, correct)

        self.keyboard.set_highlight(
            self.lesson_text[self.char_idx]
            if self.char_idx < len(self.lesson_text) else '')

        self._update_display()
        self._update_stats()
        self.progress.set_value(self.char_idx / max(1, len(self.lesson_text)))

        if self.mode == 'completion' and self.char_idx >= len(self.lesson_text):
            self._finish()
        elif self.mode.startswith('timed_') and self.char_idx >= len(self.lesson_text):
            extra = gen_lesson(self.layout_name,
                               settings_mgr.get('lesson', 'home_row'), 200)
            self.lesson_text += ' ' + extra

    def _tick(self):
        if self.start_time is None or self._finished:
            return
        elapsed = time.time() - self.start_time
        if self.mode.startswith('timed_') and elapsed >= self.timer_secs:
            self._finish()
            return
        self._update_stats()

    def _update_stats(self):
        if self.start_time is None:
            self.lbl_wpm.setText('WPM: 0')
            self.lbl_acc.setText('ACC: 100%')
            self.lbl_time.setText('⏱ 0:00')
            self.lbl_streak.setText(f'🔥 {self.streak}')
            return
        elapsed = time.time() - self.start_time
        mins = elapsed / 60.0
        wpm = (len(self.typed) / 5.0) / mins if mins > 0 else 0
        acc = ((self.total_keystrokes - self.errors)
               / max(1, self.total_keystrokes)) * 100
        if self.mode.startswith('timed_'):
            remaining = max(0, self.timer_secs - elapsed)
            m, s = divmod(int(remaining), 60)
            self.lbl_time.setText(f'⏱ {m}:{s:02d}')
        else:
            m, s = divmod(int(elapsed), 60)
            self.lbl_time.setText(f'⏱ {m}:{s:02d}')
        self.lbl_wpm.setText(f'WPM: {int(wpm)}')
        self.lbl_acc.setText(f'ACC: {int(acc)}%')
        self.lbl_streak.setText(f'🔥 {self.streak}')

        if self.char_idx < len(self.lesson_text):
            ch = self.lesson_text[self.char_idx]
            fi = get_finger(self.layout_name, ch)
            fname = FINGER_NAMES[fi] if fi < len(FINGER_NAMES) else ''
            self.lbl_finger.setText(f'👉 {fname}')
            display = ch if ch != ' ' else 'SPACE'
            self.lbl_expected.setText(f'Press: {display}')
        else:
            self.lbl_finger.setText('')
            self.lbl_expected.setText('')

    def _update_display(self):
        cursor = self.char_idx
        text = self.lesson_text
        html_parts = []
        for i, ch in enumerate(text[:cursor]):
            if i < len(self.typed):
                if self.typed[i] == text[i]:
                    html_parts.append(
                        f'<span style="color:{T("GREEN")}">{_esc(ch)}</span>')
                else:
                    html_parts.append(
                        f'<span style="color:{T("RED")}">'
                        f'<s>{_esc(text[i])}</s>{_esc(ch)}</span>')
            else:
                html_parts.append(_esc(ch))
        if cursor < len(text):
            html_parts.append(
                f'<span style="background-color:{T("YELLOW")};'
                f'color:#1a1a26;border-radius:3px;padding:0 2px">'
                f'{_esc(text[cursor])}</span>')
        for ch in text[cursor + 1:]:
            html_parts.append(
                f'<span style="color:{T("DIM")}">{_esc(ch)}</span>')
        self.typing_display.setHtml(''.join(html_parts))
        sb = self.typing_display.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _finish(self):
        self._finished = True
        self._timer.stop()
        elapsed = time.time() - self.start_time if self.start_time else 1
        mins = elapsed / 60.0
        wpm = (len(self.typed) / 5.0) / mins if mins > 0 else 0
        acc = ((self.total_keystrokes - self.errors)
               / max(1, self.total_keystrokes)) * 100
        sound_mgr.play('done')

        if self.mw.stats_mgr:
            self.mw.stats_mgr.add_stat(
                self.layout_name,
                settings_mgr.get('lesson', 'home_row'),
                wpm, acc, elapsed, self.key_errors)

        self.mw.result_screen.set_results(wpm, acc, elapsed, self.best_streak,
                                           self.errors, self.total_keystrokes,
                                           self.layout_name)
        self.mw.go_to('result')


def _esc(ch):
    """Escape HTML special characters."""
    if ch == ' ':
        return '&nbsp;'
    if ch == '\n':
        return '<br>'
    return ch.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# ─── Missing Screens Implemented Below ────────────────────────────────────────

class ResultScreen(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.mw = main_window
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignCenter)

        self.title = QLabel('🎉  Lesson Complete!')
        self.title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)

        self.stats_box = QWidget()
        self.stats_box.setStyleSheet(card_stylesheet(12))
        sl = QGridLayout(self.stats_box)
        sl.setSpacing(15)
        sl.setContentsMargins(25, 20, 25, 20)

        labels = ['WPM', 'Accuracy', 'Time', 'Best Streak', 'Errors', 'Keystrokes']
        self.val_labels = {}
        for i, lb in enumerate(labels):
            key_label = QLabel(lb)
            key_label.setFont(QFont("Segoe UI", 12))
            key_label.setStyleSheet(f"color: {T('DIM')}; background: transparent;")
            val_label = QLabel('0')
            val_label.setFont(QFont("Segoe UI", 22, QFont.Bold))
            val_label.setStyleSheet(f"color: {T('ACCENT')}; background: transparent;")
            val_label.setAlignment(Qt.AlignCenter)
            sl.addWidget(key_label, 0, i)
            sl.addWidget(val_label, 1, i)
            self.val_labels[lb] = val_label

        layout.addWidget(self.stats_box)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        
        retry_btn = QPushButton('🔄  Try Again')
        retry_btn.setFixedHeight(50)
        retry_btn.setStyleSheet(btn_stylesheet('CARD2', 15, bold=True))
        retry_btn.clicked.connect(self._retry)
        btn_row.addWidget(retry_btn)

        menu_btn = QPushButton('🏠  Main Menu')
        menu_btn.setFixedHeight(50)
        menu_btn.setStyleSheet(btn_stylesheet('ACCENT', 15, bold=True, text_color='#ffffff'))
        menu_btn.clicked.connect(lambda: self.mw.go_to('menu'))
        btn_row.addWidget(menu_btn)

        layout.addLayout(btn_row)

    def set_results(self, wpm, acc, elapsed, best_streak, errors, total_keystrokes, layout_name):
        self.val_labels['WPM'].setText(f'{int(wpm)}')
        self.val_labels['Accuracy'].setText(f'{int(acc)}%')
        m, s = divmod(int(elapsed), 60)
        self.val_labels['Time'].setText(f'{m}:{s:02d}')
        self.val_labels['Best Streak'].setText(f'{best_streak}')
        self.val_labels['Errors'].setText(f'{errors}')
        self.val_labels['Keystrokes'].setText(f'{total_keystrokes}')

        if acc >= 95:
            color = 'GREEN'
        elif acc >= 80:
            color = 'YELLOW'
        else:
            color = 'RED'
        self.val_labels['Accuracy'].setStyleSheet(f"color: {T(color)}; background: transparent;")

    def _retry(self):
        self.mw.typing_screen.start_lesson(
            self.mw.current_layout, self.mw.current_lesson, self.mw.current_mode)
        self.mw.go_to('typing')


class CustomScreen(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.mw = main_window
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        back_btn = QPushButton('← Back')
        back_btn.setFixedWidth(90)
        back_btn.setFocusPolicy(Qt.NoFocus)
        back_btn.setStyleSheet(btn_stylesheet('CARD2', 12))
        back_btn.clicked.connect(lambda: self.mw.go_to('menu'))
        layout.addWidget(back_btn)

        title = QLabel('✏️  Custom Text Practice')
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        desc = QLabel('Enter any text below to practice typing it.')
        desc.setFont(QFont("Segoe UI", 11))
        desc.setStyleSheet(f"color: {T('DIM')};")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)

        self.text_edit = QPlainTextEdit()
        self.text_edit.setFont(QFont("Consolas", 14))
        self.text_edit.setPlaceholderText('Type or paste your custom text here...')
        self.text_edit.setMinimumHeight(250)
        layout.addWidget(self.text_edit)

        start_btn = QPushButton('▶  Start Custom Practice')
        start_btn.setFixedHeight(50)
        start_btn.setStyleSheet(btn_stylesheet('ACCENT', 16, bold=True, text_color='#ffffff'))
        start_btn.clicked.connect(self._start)
        layout.addWidget(start_btn)

    def _start(self):
        custom_text = self.text_edit.toPlainText().strip()
        if not custom_text:
            QMessageBox.warning(self, 'Empty Text', 'Please enter some text to practice.')
            return
        self.mw.current_layout = settings_mgr.get('layout', 'QWERTY')
        self.mw.current_lesson = 'custom'
        self.mw.current_mode = 'completion'
        self.mw.current_custom_text = custom_text
        self.mw.typing_screen.start_lesson(
            self.mw.current_layout, 'custom', 'completion', custom_text)
        self.mw.go_to('typing')


class StatsScreen(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.mw = main_window
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        back_btn = QPushButton('← Back')
        back_btn.setFixedWidth(90)
        back_btn.setFocusPolicy(Qt.NoFocus)
        back_btn.setStyleSheet(btn_stylesheet('CARD2', 12))
        back_btn.clicked.connect(lambda: self.mw.go_to('menu'))
        layout.addWidget(back_btn)

        title = QLabel('📊  Statistics')
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.chart = WpmChart()
        layout.addWidget(self.chart)

        self.history_box = QTextEdit()
        self.history_box.setReadOnly(True)
        self.history_box.setFont(QFont("Consolas", 11))
        self.history_box.setMaximumHeight(220)
        layout.addWidget(self.history_box)

        btn_row = QHBoxLayout()
        
        clear_btn = QPushButton('🗑️  Clear Stats')
        clear_btn.setFixedHeight(40)
        clear_btn.setStyleSheet(btn_stylesheet('RED', 13, text_color='#ffffff'))
        clear_btn.clicked.connect(self._clear)
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

    def refresh(self):
        if not self.mw.stats_mgr:
            return
        recent = self.mw.stats_mgr.get_recent(20)
        wpms = [s['wpm'] for s in recent if 'wpm' in s]
        self.chart.set_data(wpms)

        html = '<table width="100%" style="color:' + T('TXT') + '">'
        html += '<tr><b><td>Date</td><td>Layout</td><td>Lesson</td><td>WPM</td><td>Acc</td></b></tr>'
        for s in reversed(recent):
            html += f"<tr><td>{s.get('date','')}</td>" \
                    f"<td>{s.get('layout','')}</td>" \
                    f"<td>{s.get('lesson','')}</td>" \
                    f"<td>{s.get('wpm',0)}</td>" \
                    f"<td>{s.get('acc',0)}%</td></tr>"
        html += '</table>'
        self.history_box.setHtml(html)

    def _clear(self):
        reply = QMessageBox.question(self, 'Clear Stats',
                                     'Are you sure you want to delete all statistics?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.mw.stats_mgr.clear()
            self.refresh()


class SettingsScreen(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.mw = main_window
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        back_btn = QPushButton('← Back')
        back_btn.setFixedWidth(90)
        back_btn.setFocusPolicy(Qt.NoFocus)
        back_btn.setStyleSheet(btn_stylesheet('CARD2', 12))
        back_btn.clicked.connect(lambda: self.mw.go_to('menu'))
        layout.addWidget(back_btn)

        title = QLabel('⚙️  Settings')
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form = QWidget()
        form.setStyleSheet(card_stylesheet(10))
        fl = QVBoxLayout(form)
        fl.setSpacing(15)
        fl.setContentsMargins(20, 20, 20, 20)

        # Theme
        theme_row = QHBoxLayout()
        theme_lbl = QLabel('Theme:')
        theme_lbl.setFixedWidth(120)
        self.theme_combo = QComboBox()
        for val, name in THEME_DISPLAY.items():
            self.theme_combo.addItem(name, val)
        self.theme_combo.currentIndexChanged.connect(self._theme_changed)
        theme_row.addWidget(theme_lbl)
        theme_row.addWidget(self.theme_combo, 1)
        fl.addLayout(theme_row)

        # Sound
        self.sound_cb = QCheckBox('🔊  Enable Sound Effects')
        self.sound_cb.setChecked(settings_mgr.get('sound', True))
        self.sound_cb.toggled.connect(lambda v: settings_mgr.set('sound', v))
        fl.addWidget(self.sound_cb)

        # Show Keyboard
        self.kb_cb = QCheckBox('⌨️  Show Visual Keyboard')
        self.kb_cb.setChecked(settings_mgr.get('show_keyboard', True))
        self.kb_cb.toggled.connect(lambda v: settings_mgr.set('show_keyboard', v))
        fl.addWidget(self.kb_cb)

        # Show Finger Hints
        self.finger_cb = QCheckBox('👉  Show Finger Hints')
        self.finger_cb.setChecked(settings_mgr.get('show_finger_hints', True))
        self.finger_cb.toggled.connect(lambda v: settings_mgr.set('show_finger_hints', v))
        fl.addWidget(self.finger_cb)

        # Heatmap
        self.heatmap_cb = QCheckBox('🌡️  Show Accuracy Heatmap on Keys')
        self.heatmap_cb.setChecked(settings_mgr.get('show_heatmap', False))
        self.heatmap_cb.toggled.connect(lambda v: settings_mgr.set('show_heatmap', v))
        fl.addWidget(self.heatmap_cb)

        layout.addWidget(form)
        layout.addStretch()

    def refresh_theme(self):
        idx = self.theme_combo.findData(settings_mgr.get('theme', 'dark'))
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)
        self.sound_cb.setChecked(settings_mgr.get('sound', True))
        self.kb_cb.setChecked(settings_mgr.get('show_keyboard', True))
        self.finger_cb.setChecked(settings_mgr.get('show_finger_hints', True))
        self.heatmap_cb.setChecked(settings_mgr.get('show_heatmap', False))

    def _theme_changed(self, index):
        val = self.theme_combo.currentData()
        settings_mgr.set('theme', val)
        self.mw.apply_theme()


# ─── Main Window ──────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Keyboard Trainer')
        self.resize(820, 720)
        
        self.stats_mgr = StatsManager(DATA_DIR)
        self.current_layout = 'QWERTY'
        self.current_lesson = 'home_row'
        self.current_mode = 'completion'
        self.current_custom_text = ''

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.menu_screen = MenuScreen(self)
        self.typing_screen = TypingScreen(self)
        self.result_screen = ResultScreen(self)
        self.custom_screen = CustomScreen(self)
        self.stats_screen = StatsScreen(self)
        self.settings_screen = SettingsScreen(self)

        self.stack.addWidget(self.menu_screen)
        self.stack.addWidget(self.typing_screen)
        self.stack.addWidget(self.result_screen)
        self.stack.addWidget(self.custom_screen)
        self.stack.addWidget(self.stats_screen)
        self.stack.addWidget(self.settings_screen)

        self.go_to('menu')
        self.apply_theme()

    def go_to(self, name):
        screens = {
            'menu': self.menu_screen,
            'typing': self.typing_screen,
            'result': self.result_screen,
            'custom': self.custom_screen,
            'stats': self.stats_screen,
            'settings': self.settings_screen,
        }
        if name in screens:
            self.stack.setCurrentWidget(screens[name])
        if name == 'typing':
            self.typing_screen.setFocus()
        if name == 'menu':
            self.menu_screen.refresh_theme()
        if name == 'stats':
            self.stats_screen.refresh()
        if name == 'settings':
            self.settings_screen.refresh_theme()

    def apply_theme(self):
        self.setStyleSheet(get_app_stylesheet())
        self.menu_screen.refresh_theme()
        self.settings_screen.refresh_theme()


# ─── Entry Point ──────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Initialize Managers
    settings_mgr.init(DATA_DIR)
    sound_mgr.init(DATA_DIR)
    
    window = MainWindow()
    window.show()
    
    log.info("Application event loop starting")
    sys.exit(app.exec())


if __name__ == '__main__':
    main()