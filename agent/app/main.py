import asyncio,json,logging,os,platform,sqlite3,time,uuid
from pathlib import Path
from datetime import datetime,timezone
import httpx
class OfflineQueue:
 def __init__(self,path=None):
  queue_path=Path(path) if path else Path.home()/'.ai-learning-guardian'/'queue.sqlite3'
  queue_path.parent.mkdir(parents=True,exist_ok=True)
  self.db=sqlite3.connect(queue_path,check_same_thread=False)
  self.db.execute('CREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY, body TEXT NOT NULL, created REAL NOT NULL)')
  self.db.commit()
 def enqueue(self,event):
  self.db.execute('INSERT OR IGNORE INTO events VALUES(?,?,?)',(event['event_id'],json.dumps(event),time.time()));self.db.commit()
 def pending(self,limit=100):return [json.loads(r[0]) for r in self.db.execute('SELECT body FROM events ORDER BY created LIMIT ?',(limit,))]
 def acknowledge(self,ids):self.db.executemany('DELETE FROM events WHERE id=?',[(x,) for x in ids]);self.db.commit()
class AgentClient:
 def __init__(self,base_url,device_token,queue):self.base=base_url.rstrip('/');self.token=device_token;self.queue=queue
 async def sync(self):
  events=self.queue.pending()
  if not events:return 0
  async with httpx.AsyncClient(timeout=20) as c:
   r=await c.post(self.base+'/api/v1/agent/events/batch',json={'events':events},headers={'Authorization':'Bearer '+self.token});r.raise_for_status();self.queue.acknowledge([e['event_id'] for e in events]);return len(events)
def event(event_type,payload):return {'event_id':str(uuid.uuid4()),'event_type':event_type,'occurred_at':datetime.now(timezone.utc).isoformat(),'agent_version':'0.1.0','payload':payload}
def platform_info():return {'os':platform.platform(),'machine':platform.machine(),'agent_version':'0.1.0','mode':'visible_user_process'}
async def run():
 print('AI Learning Guardian Monitoring Agent');print(json.dumps(platform_info(),indent=2));print('Agent is a visible user process. Configure GUARDIAN_API_URL and GUARDIAN_DEVICE_TOKEN to connect. No background monitoring starts without explicit credentials and policy.')
 base_url=os.getenv('GUARDIAN_API_URL','')
 device_token=os.getenv('GUARDIAN_DEVICE_TOKEN','')
 queue_path=os.getenv('GUARDIAN_AGENT_QUEUE',str(Path.home()/'.ai-learning-guardian'/'queue.sqlite3'))
 queue=OfflineQueue(queue_path)
 client=AgentClient(base_url,device_token,queue) if base_url and device_token else None
 if client:
  print('Device credential found. Heartbeats will synchronize only through the configured backend.')
 else:
  print('Pairing credential missing. Agent is monitoring no activity and will not send events.')
 while True:
  if client:
   queue.enqueue(event('HEARTBEAT',platform_info()))
   try:
    synchronized=await client.sync()
    if synchronized:
     print(f'Synchronized {synchronized} queued event(s)')
   except Exception as exc:
    print(f'Sync deferred; event remains queued: {type(exc).__name__}')
  await asyncio.sleep(60)
if __name__=='__main__':asyncio.run(run())
