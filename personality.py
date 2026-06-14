from speak import speak

RESPONSES = {

    "who are you":
    "Hey 👋 I'm Max, your robot buddy.",

    "introduce yourself":
    "Hello 😄 I'm Max. I can move, search for objects, and help you out.",

    "how are you":
    "I'm doing awesome 😄 All systems are running perfectly.",

    "thank you":
    "You're welcome 😄",

    "good morning":
    "Good morning ☀️ Ready for today's mission?",

    "good night":
    "Good night 🌙 I'll stay alert while you sleep.",

    "do you like me":
    "Of course 😄 You're my favorite human.",

    "are you real":
    "As real as a robot can be 🤖"
}

def handle_personality(cmd):

    cmd = cmd.lower().strip()

    response = RESPONSES.get(cmd)

    if not response:
        return False

    speak(response)

    return True