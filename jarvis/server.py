import hmac
import json
import math
import os
import re
import secrets
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .assistant import Assistant, clean, ollama_models
from . import voice

UI = Path(__file__).resolve().parent.parent / 'ui'


class Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, store, port=0):
        super().__init__(('127.0.0.1', port), Handler)
        self.store = store
        self.assistant = Assistant(store)
        self.token = secrets.token_urlsafe(32)
        self.origin = f'http://127.0.0.1:{self.server_port}'


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # Never log conversation text or session credentials.

    def reply(self, data, status=200, mime='application/json; charset=utf-8'):
        payload = json.dumps(data, ensure_ascii=False).encode() if mime.startswith('application/json') else data
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        self.end_headers()
        try:
            self.wfile.write(payload)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def allowed(self, token=False):
        if self.headers.get('Host') != f'127.0.0.1:{self.server.server_port}':
            return False
        origin = self.headers.get('Origin')
        if origin and origin != self.server.origin:
            return False
        if self.headers.get('Sec-Fetch-Site') == 'cross-site':
            return False
        return not token or hmac.compare_digest(self.headers.get('X-Jarvis-Token', ''), self.server.token)

    def do_GET(self):
        if not self.allowed(token=self.path.startswith('/api/')):
            return self.reply({'error': 'Access denied.'}, 403)
        if self.path == '/api/state':
            return self.reply({**self.server.store.state(), 'windows': os.name == 'nt', 'data_dir': str(self.server.store.directory)})
        if self.path == '/api/alerts':
            return self.reply({'alerts': self.server.store.pending_alerts()})
        if self.path == '/api/models':
            return self.reply(ollama_models())
        files = {'/': ('index.html', 'text/html; charset=utf-8'), '/app.js': ('app.js', 'text/javascript; charset=utf-8'), '/style.css': ('style.css', 'text/css; charset=utf-8')}
        if self.path not in files:
            return self.reply({'error': 'Not found.'}, 404)
        name, mime = files[self.path]
        data = (UI / name).read_bytes()
        if name == 'index.html':
            data = data.replace(b'__SESSION_TOKEN__', self.server.token.encode())
        self.reply(data, mime=mime)

    def do_POST(self):
        if not self.allowed(token=True):
            return self.reply({'error': 'Access denied.'}, 403)
        try:
            length = int(self.headers.get('Content-Length', 0))
            if not 0 < length <= 40000:
                raise ValueError('Invalid request size.')
            if self.headers.get_content_type() != 'application/json':
                raise ValueError('Expected JSON.')
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError('Expected an object.')
            result = self.action(data)
            self.reply(result)
        except (ValueError, TypeError, KeyError, OverflowError) as exc:
            self.reply({'error': str(exc) if isinstance(exc, ValueError) else 'Invalid input. Please check your entries.'}, 400)
        except Exception:
            self.reply({'error': 'The request could not finish. Please restart JARVIS and try again.'}, 500)

    def action(self, d):
        store = self.server.store
        if self.path == '/api/chat':
            return self.server.assistant.chat(d.get('text'))
        if self.path == '/api/tasks/add':
            title = clean(d.get('title'), 300)
            due = d.get('due')
            if due is not None:
                due = float(due)
                if not math.isfinite(due) or due <= time.time() or due > time.time() + 366 * 86400:
                    raise ValueError('Choose a future reminder time within the next year.')
            store.add_task(title, due)
        elif self.path in ('/api/tasks/toggle', '/api/tasks/delete', '/api/tasks/ack'):
            item_id = int(d['id'])
            if self.path.endswith('toggle'):
                store.execute('UPDATE tasks SET done=1-done WHERE id=?', (item_id,))
            elif self.path.endswith('delete'):
                store.execute('DELETE FROM tasks WHERE id=?', (item_id,))
            else:
                store.execute('UPDATE tasks SET alerted=1 WHERE id=?', (item_id,))
        elif self.path == '/api/memories/add':
            store.execute('INSERT INTO memories(content,created) VALUES (?,?)', (clean(d.get('content')), time.time()))
        elif self.path == '/api/memories/delete':
            store.execute('DELETE FROM memories WHERE id=?', (int(d['id']),))
        elif self.path == '/api/settings':
            values = {'name': clean(d.get('name'), 60), 'model': clean(d.get('model'), 120), 'language': d.get('language'), 'speak': d.get('speak')}
            if not re.fullmatch(r'[a-zA-Z0-9._:/-]+', values['model']) or 'cloud' in values['model'].lower():
                raise ValueError('Enter a valid local Ollama model name (cloud tags are not supported).')
            if values['language'] not in ('English', 'Tamil', 'Tamil and English') or not isinstance(values['speak'], bool):
                raise ValueError('Choose a supported language and voice setting.')
            store.save_settings(values)
        elif self.path == '/api/chat/clear':
            # Do not race an in-flight reply.
            if not self.server.assistant.lock.acquire(blocking=False):
                raise ValueError('Wait for the current reply before clearing chat.')
            try:
                store.execute('DELETE FROM messages')
            finally:
                self.server.assistant.lock.release()
        elif self.path == '/api/voice/listen':
            return {'text': voice.run('listen')}
        elif self.path == '/api/voice/speak':
            voice.run('speak', clean(d.get('text'), 12000))
            return {'ok': True}
        else:
            raise ValueError('Unknown action.')
        return {'ok': True}
