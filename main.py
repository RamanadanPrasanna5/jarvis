"""Run the native desktop shell, or --browser for the dependency-free UI."""
import argparse
import os
import threading
import webbrowser

from jarvis.server import Server
from jarvis.storage import Store


def main():
    parser = argparse.ArgumentParser(description='JARVIS personal desktop assistant')
    parser.add_argument('--browser', action='store_true', help='Open in the default browser')
    parser.add_argument('--headless', action='store_true', help='Run the local server without opening a window')
    parser.add_argument('--port', type=int, default=0, help='Local port; default selects a free port')
    args = parser.parse_args()
    server = Server(Store(), args.port)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    print(f'JARVIS is running at {server.origin}', flush=True)
    print('Keep this process running for reminders. Press Ctrl+C to quit.', flush=True)
    try:
        if not args.browser and not args.headless:
            try:
                import webview
                webview.create_window('JARVIS — Personal assistant', server.origin, width=1440, height=940, min_size=(1000, 720), background_color='#080d14')
                webview.start(gui='edgechromium' if os.name == 'nt' else None, private_mode=True)
                return
            except Exception as exc:
                print(f'Desktop shell unavailable ({type(exc).__name__}). Opening browser mode.', flush=True)
        if not args.headless:
            webbrowser.open(server.origin)
        threading.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    main()
