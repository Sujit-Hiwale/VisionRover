from vision import vision_state

# priority order (higher index = higher priority)
PRIORITY = {
    "idle": 0,
    "scan": 1,
    "face": 2,
    "object": 3
}


def can_run(mode: str) -> bool:
    """
    Decide if a module is allowed to run.
    """

    with vision_state.vision_lock:

        current = vision_state.active_mode

        # always allow same mode
        if current == mode:
            return True

        # check priority
        return PRIORITY[mode] >= PRIORITY[current]


def set_mode(mode: str):
    with vision_state.vision_lock:
        vision_state.active_mode = mode


def force_mode(mode: str):
    """
    overrides everything (use carefully)
    """
    with vision_state.vision_lock:
        vision_state.active_mode = mode
        vision_state.request = mode