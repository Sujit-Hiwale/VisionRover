import threading

vision_lock = threading.Lock()

active_mode = "idle"
priority = "object"

request = None 