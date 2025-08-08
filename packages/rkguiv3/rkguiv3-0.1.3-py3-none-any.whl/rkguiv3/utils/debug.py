_debug_mode = False

def set_debug_mode(enable):
    global _debug_mode
    _debug_mode = enable

def log_debug(message):
    if _debug_mode:
        print(f"[DEBUG] {message}")