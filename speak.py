import subprocess
import threading
import queue
import asyncio
import io

import edge_tts
import pygame

# ==============================
# SPEECH QUEUE
# ==============================
smallFacesModule = None
speech_queue = queue.Queue()

is_speaking = False

speech_lock = threading.Lock()

# ==============================
# SPEECH WORKER
# ==============================

def speech_worker():

    global is_speaking

    while True:

        text = speech_queue.get()

        if not text:
            continue

        with speech_lock:

            is_speaking = True

            print(f"🗣 Speaking: {text}")

            global smallFacesModule

            try:

                if smallFacesModule is None:

                    import smallFaces

                    smallFacesModule = smallFaces

                previous_mode = (
                    smallFacesModule.current_mode
                )

                # ==========================
                # TALKING FACE
                # ==========================

                try:

                    smallFacesModule.set_mode(
                        "talking"
                    )

                except:
                    pass

                # ==========================
                # SPEAK
                # ==========================

                async def play_voice(text):

                    communicate = edge_tts.Communicate(
                        text,
                        "en-US-AvaNeural"
                    )

                    audio_data = b""

                    async for chunk in communicate.stream():

                        if chunk["type"] == "audio":

                            audio_data += chunk["data"]

                    pygame.mixer.init()

                    pygame.mixer.music.load(
                        io.BytesIO(audio_data)
                    )

                    pygame.mixer.music.play()

                    while pygame.mixer.music.get_busy():

                        await asyncio.sleep(0.1)

                asyncio.run(
                    play_voice(text)
                )

                # ==========================
                # RESTORE FACE
                # ==========================

                try:

                    smallFacesModule.set_mode(
                        previous_mode
                    )

                except:
                    pass

            except Exception as e:

                print(
                    f"Speech error: {e}"
                )

            is_speaking = False

# ==============================
# START THREAD
# ==============================

threading.Thread(

    target=speech_worker,

    daemon=True

).start()

# ==============================
# PUBLIC SPEAK
# ==============================

def speak(text):

    if not text:
        return

    speech_queue.put(text)