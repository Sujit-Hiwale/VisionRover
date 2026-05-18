from upperNode import send

current_mode = "neutral"

# ==============================
# FACE SENDER
# ==============================

def set_mode(mode):

    global current_mode

    current_mode = mode

    send(
        f"FACE:{mode.upper()}"
    )

# ==============================
# EXPRESSIONS
# ==============================

def happy():
    set_mode("happy")

def neutral():
    set_mode("neutral")

def angry():
    set_mode("angry")

def blink():
    set_mode("blink")

def searching():
    set_mode("searching")

def found():
    set_mode("found")

def not_found():
    set_mode("not_found")

def turning():
    set_mode("turning")

def talking():
    set_mode("talking")

def clear():
    set_mode("clear")

# Startup face
neutral()