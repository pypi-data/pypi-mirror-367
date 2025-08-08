import os
import time
import threading
import importlib

def watch_files(files, callback, interval=1):
    last_modified = {f: os.path.getmtime(f) for f in files}
    
    def watcher():
        while True:
            time.sleep(interval)
            for f in files:
                current_mtime = os.path.getmtime(f)
                if current_mtime != last_modified[f]:
                    last_modified[f] = current_mtime
                    callback()
                    break
    
    thread = threading.Thread(target=watcher, daemon=True)
    thread.start()