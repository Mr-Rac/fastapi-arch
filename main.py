import signal
import subprocess
import time

fastapi_proc = subprocess.Popen(["fastapi", "run", "app/main.py"],)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping services...")

    for proc in [fastapi_proc]:
        proc.send_signal(signal.SIGTERM)
        proc.wait()

    print("All services stopped.")
