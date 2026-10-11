"""Windows offline speech. Text is data, never interpolated into a command."""
import base64
import os
import subprocess
import threading
from pathlib import Path

LOCK = threading.Lock()
SCRIPT = Path(__file__).resolve().parent.parent / 'scripts' / 'voice.ps1'


def run(mode, text=''):
    if os.name != 'nt':
        raise ValueError('Voice is available on Windows. You can use text chat here.')
    if not LOCK.acquire(blocking=False):
        raise ValueError('Voice is busy. Wait for it to finish, then try again.')
    try:
        payload = base64.b64encode(text[:2500].encode('utf-8')).decode('ascii')
        result = subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File', str(SCRIPT), '-Mode', mode, '-TextBase64', payload], capture_output=True, timeout=90 if mode == 'speak' else 22, creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode:
            raise ValueError('Windows voice is unavailable. Enable desktop microphone access and install an English speech pack in Windows Settings → Time & language → Speech. Text chat still works.')
        return result.stdout.decode('utf-8-sig', errors='replace').strip()
    except subprocess.TimeoutExpired:
        raise ValueError('Voice timed out. Try a shorter phrase and check your microphone.') from None
    finally:
        LOCK.release()
