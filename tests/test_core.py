import datetime as dt
import json
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch
from jarvis.assistant import Assistant, parse_reminder
from jarvis.server import Server
from jarvis.storage import Store

class CoreTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.store=Store(self.temp.name); self.agent=Assistant(self.store)
    def tearDown(self): self.temp.cleanup()
    def test_reminder_times(self):
        now=dt.datetime(2026,9,28,19,30,tzinfo=dt.timezone(dt.timedelta(hours=5,minutes=30)))
        title, when=parse_reminder('remind me at 7 pm to gym',now)
        self.assertEqual(title,'gym'); self.assertEqual(dt.datetime.fromtimestamp(when,now.tzinfo),now.replace(day=29,hour=19,minute=0))
        self.assertEqual(parse_reminder('remind me in 10 minutes to hydrate',now)[1],now.timestamp()+600)
        self.assertEqual(dt.datetime.fromtimestamp(parse_reminder('remind me tomorrow at 12 am to sleep',now)[1],now.tzinfo).hour,0)
        for text in ['remind me at 25:00 to sleep','remind me at 15 pm to sleep','remind me in 0 minutes to sleep','remind me at 5:99 to sleep']:
            with self.assertRaises(ValueError): parse_reminder(text,now)
    def test_persistence_unicode(self):
        self.agent.chat('remember தமிழ் விளக்கம் வேண்டும்'); self.agent.chat('add task Finish Angular project')
        saved=Store(self.temp.name)
        self.assertEqual(saved.memories()[0]['content'],'தமிழ் விளக்கம் வேண்டும்')
        self.assertEqual(saved.tasks()[0]['title'],'Finish Angular project'); self.assertEqual(len(saved.messages()),4)
    def test_reminder_recovery_ack(self):
        task_id=self.store.add_task('Due while closed',time.time()-90)
        self.assertEqual(Store(self.temp.name).pending_alerts()[0]['id'],task_id)
        self.assertEqual(len(self.store.pending_alerts()),1)
        self.store.execute('UPDATE tasks SET alerted=1 WHERE id=?',(task_id,)); self.assertEqual(self.store.pending_alerts(),[])
    def test_no_arbitrary_execution(self):
        with patch('jarvis.assistant.subprocess.Popen') as popen,patch('jarvis.assistant.os.name','nt'),patch('jarvis.assistant.subprocess.CREATE_NO_WINDOW',0,create=True):
            self.assertIn('Supported apps',self.agent.chat('open calculator & whoami')['reply']); popen.assert_not_called()
    def test_ai_offline(self):
        with patch('jarvis.assistant.HTTP.open',side_effect=OSError()): result=self.agent.chat('Explain Angular DI')['reply']
        self.assertIn('not connected',result);self.assertEqual(self.store.messages()[-1]['content'],result)
    def test_ai_contract(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def read(self): return b'{"message":{"content":"Injected dependency."}}'
        self.agent.chat('remember I like short answers')
        with patch('jarvis.assistant.HTTP.open',return_value=Response()) as request:
            self.assertEqual(self.agent.chat('Explain DI')['reply'],'Injected dependency.')
        body=json.loads(request.call_args.args[0].data)
        self.assertFalse(body['stream']);self.assertIn('I like short answers',body['messages'][0]['content']);self.assertEqual(body['messages'][-1]['content'],'Explain DI')

class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.server=Server(Store(cls.temp.name));threading.Thread(target=cls.server.serve_forever,daemon=True).start()
    @classmethod
    def tearDownClass(cls): cls.server.shutdown();cls.server.server_close();cls.temp.cleanup()
    def request(self,path,data=None,token=True,origin=None,host=None):
        headers={'Content-Type':'application/json'}
        if token:headers['X-Jarvis-Token']=self.server.token
        if origin:headers['Origin']=origin
        if host:headers['Host']=host
        req=urllib.request.Request(self.server.origin+path,data=json.dumps(data).encode() if data is not None else None,headers=headers)
        try:
            with urllib.request.urlopen(req) as response:return response.status,response.read()
        except urllib.error.HTTPError as error:return error.code,error.read()
    def test_token(self):
        self.assertEqual(self.request('/api/state',token=False)[0],403)
        self.assertEqual(self.request('/api/chat',{'text':'hello'},token=False)[0],403)
        self.assertEqual(self.request('/api/state')[0],200)
    def test_origin_host_paths(self):
        self.assertEqual(self.request('/',origin='https://attacker.example')[0],403)
        self.assertEqual(self.request('/',host='evil.example')[0],403)
        self.assertEqual(self.request('/api/chat',{'text':'open notepad'},origin='https://attacker.example')[0],403)
        self.assertEqual(self.request('/../main.py')[0],404)
    def test_bad_input(self):
        for data in [{'title':'past','due':1},{'title':''},{'title':'nan','due':'nan'},{'title':'bad','due':'x'}]:self.assertEqual(self.request('/api/tasks/add',data)[0],400)
        self.assertEqual(self.request('/api/settings',{'name':'P','model':'bad;whoami','language':'English','speak':False})[0],400)
    def test_task_lifecycle(self):
        self.assertEqual(self.request('/api/tasks/add',{'title':'Read chapter 1'})[0],200)
        item=next(t for t in json.loads(self.request('/api/state')[1])['tasks'] if t['title']=='Read chapter 1')
        self.request('/api/tasks/toggle',{'id':item['id']})
        self.assertEqual(next(t for t in json.loads(self.request('/api/state')[1])['tasks'] if t['id']==item['id'])['done'],1)
        self.request('/api/chat',{'text':'hello'});self.request('/api/chat/clear',{})
        state=json.loads(self.request('/api/state')[1]);self.assertEqual(state['messages'],[]);self.assertTrue(state['tasks'])
        self.request('/api/tasks/delete',{'id':item['id']})
        self.assertFalse(any(t['id']==item['id'] for t in json.loads(self.request('/api/state')[1])['tasks']))
if __name__=='__main__':unittest.main()
