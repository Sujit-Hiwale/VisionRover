from RPLCD.i2c import CharLCD
from time import sleep
import threading

# ---------------------------------
# LCD Setup
# ---------------------------------

lcd = CharLCD(
    i2c_expander='PCF8574',
    address=0x27,
    port=1,
    cols=16,
    rows=2,
    charmap='A00'
)

# ---------------------------------
# Eyes
# ---------------------------------

eye_open = [
    0b00000,
    0b01110,
    0b10001,
    0b10101,
    0b10001,
    0b01110,
    0b00000,
    0b00000
]

eye_closed = [
    0b00000,
    0b00000,
    0b11111,
    0b00000,
    0b11111,
    0b00000,
    0b00000,
    0b00000
]

eye_search = [
    0b00000,
    0b01110,
    0b10001,
    0b10011,
    0b10001,
    0b01110,
    0b00000,
    0b00000
]

# ---------------------------------
# Mouths
# ---------------------------------

mouth_happy = [
    0b00000,
    0b00000,
    0b00000,
    0b10001,
    0b01110,
    0b00000,
    0b00000,
    0b00000
]

mouth_neutral = [
    0b00000,
    0b00000,
    0b11111,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000
]

mouth_angry = [
    0b00000,
    0b01110,
    0b10001,
    0b00000,
    0b00000,
    0b00000,
    0b00000,
    0b00000
]

# Talking mouth
mouth_talk = [
    0b00000,
    0b00000,
    0b01110,
    0b10001,
    0b01110,
    0b00000,
    0b00000,
    0b00000
]

# ---------------------------------
# State
# ---------------------------------

current_mode = "neutral"

animation_running = False

# ---------------------------------
# Draw Face
# ---------------------------------

def show_face(eye, mouth):

    lcd.clear()

    lcd.create_char(0, eye)
    lcd.create_char(1, eye)
    lcd.create_char(2, mouth)

    # Eyes
    lcd.cursor_pos = (0, 5)

    lcd.write_string(chr(0))
    lcd.write_string(" ")
    lcd.write_string(chr(1))

    # Mouth
    lcd.cursor_pos = (1, 6)

    lcd.write_string(chr(2))

# ---------------------------------
# Base Expressions
# ---------------------------------

def happy():
    show_face(eye_open, mouth_happy)

def neutral():
    show_face(eye_open, mouth_neutral)

def angry():
    show_face(eye_open, mouth_angry)

def blink():
    show_face(eye_closed, mouth_neutral)

def searching():
    show_face(eye_search, mouth_neutral)

def found():
    show_face(eye_open, mouth_happy)

def not_found():
    show_face(eye_closed, mouth_angry)

def turning():
    show_face(eye_search, mouth_angry)

def talking():
    show_face(eye_open, mouth_talk)

def clear():
    lcd.clear()

# ---------------------------------
# Talking Animation
# ---------------------------------

def talking_animation(duration=3):

    global animation_running

    animation_running = True

    end_time = sleep_time = duration

    start = 0

    while start < end_time and animation_running:

        talking()
        sleep(0.25)

        happy()
        sleep(0.25)

        start += 0.5

    neutral()

# ---------------------------------
# Mode Controller
# ---------------------------------

def set_mode(mode):

    global current_mode
    global animation_running

    current_mode = mode

    animation_running = False

    if mode == "neutral":
        neutral()

    elif mode == "happy":
        happy()

    elif mode == "angry":
        angry()

    elif mode == "searching":
        searching()

    elif mode == "found":
        found()

    elif mode == "not_found":
        not_found()

    elif mode == "turning":
        turning()

    elif mode == "blink":
        blink()

    elif mode == "talking":

        thread = threading.Thread(
            target=talking_animation,
            daemon=True
        )

        thread.start()

    elif mode == "sleep":
        show_face(eye_closed, mouth_neutral)

# ---------------------------------
# Startup Face
# ---------------------------------

set_mode("neutral")