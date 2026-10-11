import json
import os
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path


def data_directory():
    root = os.environ.get('JARVIS_DATA_DIR')
    if root:
        return Path(root)
    return Path(os.environ.get('LOCALAPPDATA', str(Path.home() / '.local/share'))) / 'JarvisDesktop'


class Store:
    def __init__(self, directory=None):
        self.directory = Path(directory) if directory else data_directory()
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / 'jarvis.sqlite3'
        with self.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, role TEXT, content TEXT, created REAL);
                CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY, title TEXT, due REAL, done INTEGER DEFAULT 0, alerted INTEGER DEFAULT 0);
                CREATE TABLE IF NOT EXISTS memories(id INTEGER PRIMARY KEY, content TEXT, created REAL);
                CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
            ''')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=15)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def rows(self, sql, args=()):
        with self.connect() as db:
            return [dict(row) for row in db.execute(sql, args)]

    def execute(self, sql, args=()):
        with self.connect() as db:
            return db.execute(sql, args).lastrowid

    def settings(self):
        values = {'name': 'Prasanna', 'model': 'qwen2.5:3b', 'language': 'English', 'speak': False}
        values.update({x['key']: json.loads(x['value']) for x in self.rows('SELECT * FROM settings')})
        return values

    def save_settings(self, values):
        with self.connect() as db:
            for key, value in values.items():
                db.execute('INSERT OR REPLACE INTO settings VALUES (?,?)', (key, json.dumps(value)))
        return self.settings()

    def add_message(self, role, content):
        self.execute('INSERT INTO messages(role, content, created) VALUES (?,?,?)', (role, content, time.time()))

    def messages(self):
        return self.rows('SELECT * FROM (SELECT * FROM messages ORDER BY id DESC LIMIT 100) ORDER BY id')

    def tasks(self):
        return self.rows('SELECT * FROM tasks ORDER BY done, due IS NULL, due, id DESC')

    def add_task(self, title, due=None):
        return self.execute('INSERT INTO tasks(title,due) VALUES (?,?)', (title, due))

    def pending_alerts(self):
        return self.rows('SELECT * FROM tasks WHERE done=0 AND alerted=0 AND due IS NOT NULL AND due<=? ORDER BY due', (time.time(),))

    def memories(self):
        return self.rows('SELECT * FROM memories ORDER BY id DESC')

    def state(self):
        return {'messages': self.messages(), 'tasks': self.tasks(), 'memories': self.memories(), 'settings': self.settings()}
