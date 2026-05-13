import subprocess
import smallFaces

# ---------------------------------
# Speak Function
# ---------------------------------

def speak(text):

    # Save current state
    previous_mode = smallFaces.current_mode

    # Talking animation
    smallFaces.set_mode("talking")

    process = subprocess.Popen([
        'espeak-ng',
        '-s', '125',
        '-p', '70',
        '-a', '180',
        text
    ])

    # Wait until speech finishes
    process.wait()

    # Restore previous face
    smallFaces.set_mode(previous_mode)