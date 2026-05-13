import streamlit as st
import time
import random
import string

# --- Page Configuration ---
st.set_page_config(
    page_title="Type Tutor Pro",
    page_icon="⌨️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data: Practice Texts, Words, and Focused Modes ---
PRACTICE_TEXTS = {
    "Beginner": [
        "dad sad lad fall fad", "a sad lad had a fad", "fall fad dad sad lad",
        "all salad salads are bad", "a sly fox jumps over a lazy dog"
    ],
    "Intermediate": [
        "The quick brown fox jumps over the lazy dog.",
        "A journey of a thousand miles begins with a single step.",
        "To be or not to be, that is the question.", "Practice makes perfect."
    ],
    "Advanced": [
        "Streamlit's open-source framework enables rapid development of data applications.",
        "The password must be at least 12 characters long, including uppercase, lowercase, numbers, and symbols (!@#$%).",
        "The IP address 192.168.1.1 is a default gateway for many routers."
    ]
}

COMMON_WORDS = [
    "the","be","to","of","and","a","in","that","have","I","it","for","not","on","with","he","as","you","do","at",
    "this","but","his","by","from","they","we","say","her","she","or","an","will","my","one","all","would","there","their",
    "what","so","up","out","if","about","who","get","which","go","me","when","make","can","like","time","no","just","him","know",
    "take","people","into","year","your","good","some","could","them","see","other","than","then","now","look","only","come","its","over","think"
]

# --- New: Data for Focused Practice Modes ---
FOCUSED_MODES = {
    "Home Row": "asdfghjkl;",
    "Top Row": "qwertyuiop",
    "Bottom Row": "zxcvbnm,./",
    "Numbers": "1234567890",
    "Symbols": "!@#$%^&*()_+-=[]{}|;':\",./<>?"
}

# --- Helper Functions ---

def initialize_session():
    """Initializes all session state variables."""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.practice_mode = "Text Completion"
        st.session_state.difficulty_level = "Intermediate"
        st.session_state.custom_text_active = False
        st.session_state.custom_text_content = ""
        st.session_state.dark_mode = False
        st.session_state.wpm_history = []
        st.session_state.time_history = []
        
        # --- New: State for appearance and pause ---
        st.session_state.font_size = 1.5
        st.session_state.line_height = 2.0
        st.session_state.is_paused = False
        st.session_state.paused_duration = 0.0
        st.session_state.focused_mode_selection = "Home Row"


def start_new_session():
    """Resets the typing-specific state for a new attempt."""
    st.session_state.user_input = ""
    st.session_state.start_time = None
    st.session_state.end_time = None
    st.session_state.is_finished = False
    st.session_state.correct_chars = 0
    st.session_state.incorrect_chars = 0
    st.session_state.last_key_pressed = ""
    st.session_state.wpm_history = []
    st.session_state.time_history = []
    st.session_state.is_paused = False # Reset pause state
    st.session_state.paused_duration = 0.0
    
    # Generate the target text based on current settings
    if st.session_state.custom_text_active:
        st.session_state.current_text = st.session_state.custom_text_content
    elif st.session_state.practice_mode == "Timed Sprint":
        words = random.sample(COMMON_WORDS, k=100)
        st.session_state.current_text = ' '.join(words)
    elif st.session_state.practice_mode == "Focused Practice":
        # Generate a random string of characters from the selected mode
        chars = FOCUSED_MODES[st.session_state.focused_mode_selection]
        st.session_state.current_text = ' '.join(''.join(random.choice(chars) for _ in range(random.randint(4, 8))) for _ in range(15))
    elif st.session_state.practice_mode == "Zen Mode":
        # Generate a very long string of words for endless typing
        words = random.choices(COMMON_WORDS, k=250) # Use choices to allow repeats
        st.session_state.current_text = ' '.join(words)
    else: # Text Completion mode
        st.session_state.current_text = random.choice(PRACTICE_TEXTS[st.session_state.difficulty_level])


def calculate_wpm():
    """Calculates Words Per Minute."""
    if not st.session_state.start_time or st.session_state.is_paused:
        return 0
    # Adjust start time for any pauses
    effective_start_time = st.session_state.start_time - st.session_state.paused_duration
    time_elapsed = max(1, (time.time() - effective_start_time) / 60)
    words_typed = st.session_state.correct_chars / 5
    return round(words_typed / time_elapsed, 2)

def calculate_accuracy():
    """Calculates typing accuracy."""
    total_chars = st.session_state.correct_chars + st.session_state.incorrect_chars
    if total_chars == 0:
        return 100.0
    return round((st.session_state.correct_chars / total_chars) * 100, 2)

def get_rendered_text():
    """Renders the practice text with color-coded feedback."""
    rendered_text = ""
    user_input_len = len(st.session_state.user_input)
    
    for i, char in enumerate(st.session_state.current_text):
        if i < user_input_len:
            if st.session_state.user_input[i] == char:
                rendered_text += f'<span class="correct-char">{char}</span>'
            else:
                rendered_text += f'<span class="incorrect-char">{char}</span>'
        elif i == user_input_len:
            rendered_text += f'<span class="current-char">{char}</span>'
        else:
            rendered_text += char
            
    return f"<p class='typing-font'>{rendered_text}</p>"

# --- Callbacks ---

def on_input_change():
    """Handles logic whenever the user types in the input box."""
    # --- New: Do nothing if paused ---
    if st.session_state.is_paused:
        return

    user_input = st.session_state.typed_input
    
    if st.session_state.start_time is None and len(user_input) == 1:
        st.session_state.start_time = time.time()

    if st.session_state.start_time and not st.session_state.is_finished:
        st.session_state.correct_chars = 0
        st.session_state.incorrect_chars = 0
        
        for i, char_typed in enumerate(user_input):
            if i < len(st.session_state.current_text):
                if char_typed == st.session_state.current_text[i]:
                    st.session_state.correct_chars += 1
                else:
                    st.session_state.incorrect_chars += 1
        
        if user_input:
            st.session_state.last_key_pressed = user_input[-1]
        else:
            st.session_state.last_key_pressed = ""

        # Check for completion conditions
        is_text_complete = (st.session_state.practice_mode in ["Text Completion", "Focused Practice"] and user_input == st.session_state.current_text)
        is_time_up = (st.session_state.practice_mode == "Timed Sprint" and (time.time() - st.session_state.start_time) >= 60)
        
        # Zen mode has no completion condition

        if is_text_complete or is_time_up:
            st.session_state.is_finished = True
            st.session_state.end_time = time.time()
            st.session_state.typed_input = ""

        # Update history for live graph
        if not st.session_state.is_finished:
            current_wpm = calculate_wpm()
            effective_start_time = st.session_state.start_time - st.session_state.paused_duration
            elapsed_time = round(time.time() - effective_start_time, 1)
            st.session_state.wpm_history.append(current_wpm)
            st.session_state.time_history.append(elapsed_time)

def on_settings_change():
    """Called when any setting in the sidebar is changed."""
    start_new_session()
    st.rerun()

def on_use_custom_text():
    """Activates the custom text provided by the user."""
    if st.session_state.custom_text_area:
        st.session_state.custom_text_content = st.session_state.custom_text_area
        st.session_state.custom_text_active = True
        on_settings_change()

# --- New: Callback for Pause/Resume ---
def toggle_pause():
    st.session_state.is_paused = not st.session_state.is_paused
    if st.session_state.is_paused:
        # When pausing, record the time elapsed so far
        if st.session_state.start_time:
            st.session_state.paused_duration += time.time() - st.session_state.start_time
    else:
        # When resuming, set a new start time
        st.session_state.start_time = time.time()


# --- Main App Logic ---
initialize_session()

# --- CSS for Styling (with Dynamic Appearance) ---
theme = "dark" if st.session_state.dark_mode else "light"
bg_color = "#2b2b2b" if theme == "dark" else "#ffffff"
text_color = "#ffffff" if theme == "dark" else "#000000"
correct_bg = "#1e4620" if theme == "dark" else "#e8f5e9"
incorrect_bg = "#5c1e1e" if theme == "dark" else "#ffebee"
current_bg = "#795548" if theme == "dark" else "#ffeb3b"
key_bg = "#3c3c3c" if theme == "dark" else "#f0f0f0"
key_text_color = "#ffffff" if theme == "dark" else "#000000"

# --- New: Inject font size and line height from session state ---
st.markdown(f"""
<style>
body {{ background-color: {bg_color}; color: {text_color}; }}
.stApp {{ background-color: {bg_color}; color: {text_color}; }}
.typing-font {{
    font-family: 'Courier New', Courier, monospace;
    font-size: {st.session_state.font_size}rem;
    line-height: {st.session_state.line_height}rem;
    color: {text_color};
}}
.correct-char {{ color: #4caf50; background-color: {correct_bg}; }}
.incorrect-char {{ color: #f44336; background-color: {incorrect_bg}; text-decoration: line-through; }}
.current-char {{ color: {text_color}; background-color: {current_bg}; font-weight: bold; animation: blink 1s infinite; }}
.key {{ text-align: center; padding: 0.5rem; border-radius: 5px; border: 1px solid #ccc; background-color: {key_bg}; color: {key_text_color}; font-weight: bold; min-height: 50px; display: flex; align-items: center; justify-content: center; }}
.key-highlight {{ background-color: #90caf9; border-color: #1976d2; animation: pulse 1s infinite; }}
.key-correct {{ background-color: #a5d6a7; border-color: #388e3c; }}
.key-incorrect {{ background-color: #ef9a9a; border-color: #c62828; }}
.key-space {{ min-width: 250px; }}
@keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0; }} 100% {{ opacity: 1; }} }}
@keyframes pulse {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.05); }} 100% {{ transform: scale(1); }} }}
</style>
""", unsafe_allow_html=True)


# --- Sidebar for Settings ---
with st.sidebar:
    st.header("⚙️ Settings")

    st.session_state.dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode, on_change=on_settings_change)
    
    st.markdown("---")
    
    # Practice Mode
    st.session_state.practice_mode = st.radio(
        "Practice Mode",
        ["Text Completion", "Timed Sprint", "Focused Practice", "Zen Mode"],
        on_change=on_settings_change
    )

    # --- New: Focused Practice Selector ---
    if st.session_state.practice_mode == "Focused Practice":
        st.session_state.focused_mode_selection = st.selectbox(
            "Select Focus Area",
            list(FOCUSED_MODES.keys()),
            on_change=on_settings_change
        )

    # Difficulty Level (only for Text Completion mode)
    if st.session_state.practice_mode == "Text Completion":
        st.session_state.difficulty_level = st.selectbox(
            "Difficulty Level",
            ["Beginner", "Intermediate", "Advanced"],
            index=["Beginner", "Intermediate", "Advanced"].index(st.session_state.difficulty_level),
            on_change=on_settings_change
        )

    st.markdown("---")
    
    # --- New: Appearance Settings ---
    st.subheader("🎨 Appearance")
    st.session_state.font_size = st.slider("Font Size", 1.0, 3.0, value=st.session_state.font_size, step=0.1, on_change=on_settings_change)
    st.session_state.line_height = st.slider("Line Height", 1.5, 3.5, value=st.session_state.line_height, step=0.1, on_change=on_settings_change)

    st.markdown("---")
    
    # Custom Text
    with st.expander("📝 Custom Text"):
        st.text_area("Paste your text here:", key="custom_text_area", height=150)
        st.button("Use Custom Text", on_click=on_use_custom_text, type="primary")
        if st.session_state.custom_text_active:
            st.info("Custom text is active.", icon="✅")
            if st.button("Clear Custom Text"):
                st.session_state.custom_text_active = False
                st.session_state.custom_text_content = ""
                on_settings_change()

# --- Initialize the first session ---
if 'current_text' not in st.session_state:
    start_new_session()

# --- UI Header ---
st.title("⌨️ Type Tutor Pro")
st.write("Improve your typing speed and accuracy.")
st.markdown("---")

# --- Main Content Area ---
col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    # Display the text to be typed
    st.markdown(get_rendered_text(), unsafe_allow_html=True)
    
    # --- New: Pause/Resume Button ---
    if st.session_state.practice_mode != "Zen Mode" and st.session_state.start_time and not st.session_state.is_finished:
        pause_button_label = "▶️ Resume" if st.session_state.is_paused else "⏸️ Pause"
        st.button(pause_button_label, on_click=toggle_pause, type="secondary")

    # The text input field
    st.text_input(
        "Start typing here:", 
        key="typed_input", 
        on_change=on_input_change,
        disabled=st.session_state.is_finished or st.session_state.is_paused, # Disable if paused
        label_visibility="collapsed"
    )

st.markdown("---")

# --- Live WPM Graph ---
if st.session_state.wpm_history:
    chart_data = {
        "Time (s)": st.session_state.time_history,
        "WPM": st.session_state.wpm_history
    }
    st.line_chart(chart_data, x="Time (s)", y="WPM")

# --- Statistics and Controls ---
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

with col_stat1:
    time_metric = 0.0
    if st.session_state.practice_mode == "Timed Sprint" and st.session_state.start_time and not st.session_state.is_paused:
        time_metric = max(0, 60.0 - (time.time() - st.session_state.start_time + st.session_state.paused_duration))
    elif st.session_state.start_time and not st.session_state.is_paused:
        time_metric = round(time.time() - st.session_state.start_time + st.session_state.paused_duration, 1)
    st.metric("⏱️ Time (s)", round(time_metric, 1))
with col_stat2:
    st.metric("🎯 Accuracy (%)", calculate_accuracy())
with col_stat3:
    st.metric("⚡ WPM", calculate_wpm())
with col_stat4:
    st.button("🔄 Reset Session", on_click=start_new_session, type="primary")

# --- Completion Message ---
if st.session_state.is_finished:
    st.success(f"🎉 Session Complete!")
    st.balloons()
    final_wpm = calculate_wpm()
    final_accuracy = calculate_accuracy()
    if st.session_state.practice_mode == "Timed Sprint":
        words_typed = len(st.session_state.user_input.split())
        st.info(f"**Final Stats:** You typed **{words_typed} words** in 60 seconds at **{final_wpm} WPM** with **{final_accuracy}%** accuracy.")
    else:
        st.info(f"**Final Stats:** {final_wpm} WPM with {final_accuracy}% accuracy.")